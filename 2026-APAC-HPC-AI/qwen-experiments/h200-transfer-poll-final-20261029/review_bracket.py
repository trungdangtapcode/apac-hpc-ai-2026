#!/usr/bin/env python3
"""Build the final read-only comparison for H200 decode polling intervals 1/2/4."""
from pathlib import Path
import ast, datetime, json, math, statistics, subprocess

Q = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
JOBS = (27270, 27272, 27274)
PAIR = json.loads((Q / "h200-transfer-poll-study-20261029/pair-review-27270-27272.json").read_text())
REVIEWS = {j: json.loads((Q / f"h200-full-load-review-20261026/review-{j}.json").read_text()) for j in JOBS}


def percentile(values, p):
    xs = sorted(values)
    assert xs
    x = (len(xs) - 1) * p
    lo, hi = math.floor(x), math.ceil(x)
    return xs[lo] + (xs[hi] - xs[lo]) * (x - lo)


def distribution(values):
    xs = sorted(values)
    return {
        "count": len(xs), "min": xs[0], "mean": statistics.mean(xs),
        "p50": percentile(xs, .50), "p95": percentile(xs, .95),
        "p99": percentile(xs, .99), "max": xs[-1],
    }


def raw_profile(job):
    path = Q / f"runs/{job}/confirm/n64/artifacts/profile_export.jsonl"
    rows = [json.loads(line) for line in path.open()]
    return [r for r in rows if r["metadata"]["benchmark_phase"] == "profiling"]


def account(job):
    text = subprocess.check_output([
        "sacct", "-X", "-j", str(job), "-P", "--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList,AllocTRES"
    ], text=True)
    lines = [x.split("|") for x in text.strip().splitlines()]
    rows = [dict(zip(lines[0], r)) for r in lines[1:] if r[0] == str(job)]
    assert len(rows) == 1 and rows[0]["State"] == "COMPLETED" and rows[0]["ExitCode"] == "0:0"
    return rows[0]


def sampled_hardware(job, lo_ns, hi_ns):
    result = {}
    for path in sorted((Q / f"runs/{job}/resource-telemetry").glob("*.jsonl")):
        lines = [json.loads(line) for line in path.open()]
        role = lines[0]["role"]
        samples = [r for r in lines if r.get("kind") == "sample" and lo_ns <= r["utc_ns"] <= hi_ns]
        fields = {}
        for name in ("utilization.gpu", "utilization.memory", "memory.used", "power.draw", "temperature.gpu", "clocks.sm", "clocks.mem"):
            vals = []
            for row in samples:
                for gpu in row.get("gpus", []):
                    try:
                        val = float(gpu[name])
                        if math.isfinite(val): vals.append(val)
                    except (KeyError, TypeError, ValueError):
                        pass
            fields[name] = distribution(vals) if vals else None
        result[role] = {"sample_rows": len(samples), "gpu_sample_count": sum(len(r.get("gpus", [])) for r in samples), "fields": fields}
    return result


def source_args(job, role):
    text = (Q / f"runs/{job}/{role}.log").read_text(errors="replace")
    rows = [x.split("server_args=", 1)[1] for x in text.splitlines() if "server_args=ServerArgs(" in x]
    assert len(rows) == 1
    call = ast.parse(rows[0], mode="eval").body
    result = {}
    for kw in call.keywords:
        if not kw.arg:
            continue
        try:
            result[kw.arg] = ast.literal_eval(kw.value)
        except (ValueError, TypeError):
            result[kw.arg] = ast.dump(kw.value, include_attributes=False)
    return result


arms = {}
for job in JOBS:
    review = REVIEWS[job]
    cfg = json.loads((Q / f"runs/{job}/config.json").read_text())
    rows = raw_profile(job)
    assert len(rows) == int(review["raw_fixed_workload"]["completed"])
    start = min(r["metadata"]["request_start_ns"] for r in rows)
    end = max(r["metadata"]["request_start_ns"] for r in rows)
    latency = {key: distribution([float(r["metrics"][key]["value"]) for r in rows]) for key in (
        "time_to_first_token", "inter_token_latency", "request_latency", "input_sequence_length", "output_sequence_length"
    )}
    output_hist = {}
    for row in rows:
        key = str(int(row["metrics"]["output_sequence_length"]["value"]))
        output_hist[key] = output_hist.get(key, 0) + 1
    acct = account(job)
    elapsed = int(acct["ElapsedRaw"])
    outputs = {
        "smoke": json.loads((Q / f"runs/{job}/output-smoke.json").read_text()),
        "head_gate": json.loads((Q / f"runs/{job}/head-performance-check.json").read_text()),
    }
    roles = {}
    for role in ("prefill-0", "prefill-1", "decode-0"):
        log = (Q / f"runs/{job}/{role}.log").read_text(errors="replace")
        args = source_args(job, role)
        roles[role] = {
            "mode": role.split("-", 1)[0],
            "tp": args["tp_size"],
            "ep": args["ep_size"],
            "decode_poll_interval": args["disaggregation_decode_polling_interval"],
            "poll_source_marker_count": log.count("TRANSFER_POLL_SOURCE_VERIFIED"),
            "nixl_patch_marker_count": log.count("NIXL_PATCH_VERIFIED"),
            "traceback_count": log.count("Traceback (most recent call last)"),
            "selected_transfer_errors": sum(log.count(term) for term in (
                "KVTransferError", "NIXL transport error", "CUDA out of memory", "Unexpected transfer worker error"
            )),
            "invalid_http_request_warnings": log.count("Invalid HTTP request received."),
        }
        assert roles[role]["poll_source_marker_count"] == 1 and roles[role]["nixl_patch_marker_count"] == 1
    low = review["telemetry_in_admission_envelope"]
    arms[str(job)] = {
        "job_id": job,
        "label": cfg["label"],
        "decode_poll_interval": cfg["decode_transfer_polling_interval"],
        "prefill_poll_interval": cfg["prefill_transfer_polling_interval"],
        "scheduler": acct,
        "allocated_gpu_hours": 16 * elapsed / 3600,
        "maximum_reserved_gpu_hours": 16 * 17 / 60,
        "pbs_su": 0,
        "config": {k: cfg[k] for k in (
            "topology", "gpus", "decode_tp", "decode_ep", "prefill_tp", "prefill_gpus",
            "concurrency", "warmup_seconds", "measure_seconds", "grace_seconds",
            "synthetic_input_tokens_mean", "output_tokens_mean", "random_seed", "prefill_policy",
            "decode_max_running_requests", "prefill_max_running_requests", "image_sha256",
            "client_image_sha256", "native_nixl_patch_base_sha256", "nixl_conn_wrapper_sha256"
        )},
        "score_and_gate": {
            "raw_profiled_requests": len(rows),
            "good_requests": round(review["summary"]["good_request_fraction"] * len(rows)),
            "errors": review["raw_fixed_workload"]["errors"],
            "cancelled": review["raw_fixed_workload"]["cancelled"],
            "good_request_fraction": review["summary"]["good_request_fraction"],
            "goodput_requests_per_second": review["raw_fixed_workload"]["goodput_req_s"],
            "good_output_tokens_per_second": review["summary"]["good_output_tokens_s"],
            "official_multiplier_tokens_per_request": 200,
            "ttft_breaches_over_3000ms": review["ttft_breaches"],
            "itl_breaches_over_20ms": review["itl_breaches"],
            "sla_pass": review["summary"]["sla_pass"],
            "smoke_passed": outputs["smoke"]["passed"],
            "smoke_total": outputs["smoke"]["total"],
            "smoke_failures": [x["name"] for x in outputs["smoke"]["cases"] if not x["passed"]],
            "smoke_regressions": review["smoke"]["regressions"],
            "retrieval_passed": review["retrieval"]["passed"],
            "retrieval_total": review["retrieval"]["total"],
            "quality_evaluation": "UNKNOWN_NOT_EVALUATED",
            "official_accuracy": "UNKNOWN",
        },
        "latency_ms_and_reported_lengths": latency,
        "reported_output_length_histogram_tokens": output_hist,
        "telemetry": {
            "sample_window": low["limits"],
            "roles": low["roles"],
            "host_summaries": low["hosts"],
            "poll_status_counts": low["server_http_and_error_poll_counts"],
            "role_gauges": low["rank_local_server_gauges"],
            "hardware_distribution": sampled_hardware(job, start, end),
            "gpu_samples_total": low["all_role_gpu_samples"],
            "mean_gpu_active_pct_all_roles": low["all_role_mean_gpu_active_pct"],
            "mean_vram_gib_all_roles": low["all_role_mean_vram_gib"],
        },
        "runtime_roles": roles,
        "limits": review["limits"],
    }

base = arms["27270"]["score_and_gate"]["good_output_tokens_per_second"]
for job in (27272, 27274):
    score = arms[str(job)]["score_and_gate"]["good_output_tokens_per_second"]
    arms[str(job)]["delta_vs_interval1_pct"] = 100 * (score / base - 1)
arms["27274"]["delta_vs_interval2_pct"] = 100 * (
    arms["27274"]["score_and_gate"]["good_output_tokens_per_second"] /
    arms["27272"]["score_and_gate"]["good_output_tokens_per_second"] - 1
)

configs = {j: json.loads((Q / f"runs/{j}/config.json").read_text()) for j in JOBS}
ignored_config = {"experiment", "label", "study_arm", "decode_transfer_polling_interval"}
config_diffs = {}
for job in (27272, 27274):
    config_diffs[str(job)] = {
        key: [configs[27270].get(key), configs[job].get(key)]
        for key in configs[27270].keys() | configs[job].keys()
        if key not in ignored_config and configs[27270].get(key) != configs[job].get(key)
    }
assert all(not diff for diff in config_diffs.values())
args_diffs = {}
ignore_args = {"random_seed", "nccl_port", "port", "dist_init_addr", "disaggregation_bootstrap_port", "engine_info_bootstrap_port", "host"}
for role in ("prefill-0", "prefill-1", "decode-0"):
    base_args = source_args(27270, role)
    for job in (27272, 27274):
        candidate = source_args(job, role)
        diffs = {k: [base_args.get(k), candidate.get(k)] for k in base_args.keys() | candidate.keys()
                 if k not in ignore_args and base_args.get(k) != candidate.get(k)}
        args_diffs[f"{role}:27270->{job}"] = diffs

score1 = arms["27270"]["score_and_gate"]["good_output_tokens_per_second"]
score2 = arms["27272"]["score_and_gate"]["good_output_tokens_per_second"]
score4 = arms["27274"]["score_and_gate"]["good_output_tokens_per_second"]
result = {
    "reviewed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "experiment": "H200 native Qwen decode transfer completion-poll interval bracket",
    "state": "COMPLETE_LOCAL_PERFORMANCE_BRACKET_NO_USEFUL_GAIN",
    "comparison_basis": {
        "control": 27270, "interval2": 27272, "interval4": 27274,
        "only_configured_experiment_difference": "decode transfer polling interval (1, 2, 4); prefill polling remains 1",
        "config_differences_other_than_expected": config_diffs,
        "runtime_server_args_differences_other_than_poll_interval_and_ephemeral_fields": args_diffs,
        "same_workload": "N64, synthetic input 4000/stddev0, output 200/stddev0, seed 2026, warmup 60s + score 120s + grace 30s, cold-prefix AIPerf command",
        "official_score_formula": "good output tokens/s = AIPerf Goodput (requests/s) * 200 fixed output tokens/request",
        "useful_gain_threshold": ">1% versus matched control; all three one-shot point estimates are within 1%",
    },
    "arms": arms,
    "bracket_summary": {
        "interval1_score_tokens_per_second": score1,
        "interval2_score_tokens_per_second": score2,
        "interval4_score_tokens_per_second": score4,
        "interval2_vs_interval1_pct": 100 * (score2 / score1 - 1),
        "interval4_vs_interval1_pct": 100 * (score4 / score1 - 1),
        "interval4_vs_interval2_pct": 100 * (score4 / score2 - 1),
        "direction": "Point estimates decline monotonically as decode polling interval rises from 1 to 2 to 4, but the entire spread is under 1%; latency tails are not monotonic.",
        "decision": "Close the polling-interval branch. Interval 1 remains the best of the three observed settings; none shows a useful >1% gain over the interval-1 control. No confirmation or wider interval sweep is justified from these one-run results.",
        "causal_claim": False,
    },
    "accounting": {
        "allocated_gpu_hours_all_three": sum(arms[str(j)]["allocated_gpu_hours"] for j in JOBS),
        "maximum_reserved_gpu_hours_all_three": sum(arms[str(j)]["maximum_reserved_gpu_hours"] for j in JOBS),
        "pbs_su": 0,
        "gpu_hour_definition": "16 allocated H200 GPUs multiplied by Slurm elapsed seconds; not energy, SU or exclusive GPU utilization.",
    },
    "limitations": [
        "One full run per interval; queue order and run-to-run variation are not replicated, so sub-1% differences are not established causal effects.",
        "Hardware and server gauges are sparse five-second samples bounded by first-to-last profiling request start; they exclude warmup and final drain and have uncalibrated cross-host clock skew.",
        "GPU active percentage is time with kernel activity, not FLOPS or bandwidth utilization. Xid/throttling reasons, per-process hot-thread CPU and heavy profiling were not collected.",
        "AIPerf uses client-side text re-tokenization in this pinned setup. It reports three output rows at 199 tokens and input rows at 3986/3987; actual token IDs/server usage are not retained, so the exact cause is unknown. Official score continues to use fixed multiplier 200, not this per-run count.",
        "Local smoke and retrieval checks are not MMLU-Pro/GPQA or the official accuracy evaluation; official model accuracy remains UNKNOWN.",
        "Non-fatal 'Invalid HTTP request received' warnings appear in role logs during probe windows; all captured metric polls returned HTTP 200, zero client errors, no selected transport errors and no traceback. Warning origin is not attributed.",
    ],
}
(OUT / "comparison.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"output": str(OUT / "comparison.json"), "state": result["state"], "scores": [score1, score2, score4], "delta_pct": [0.0, result["bracket_summary"]["interval2_vs_interval1_pct"], result["bracket_summary"]["interval4_vs_interval1_pct"]], "cost_gpu_hours": result["accounting"]["allocated_gpu_hours_all_three"]}, indent=2))
