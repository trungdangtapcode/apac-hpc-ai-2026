#!/usr/bin/env python3
"""Rebuild the bounded 24928 review from retained local run evidence."""
from __future__ import annotations

import csv
import ast
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path

ROOT = Path("/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments")
OUT = Path(__file__).resolve().parent / "REVIEW.json"
JOBS = ("24926", "24927", "24928")
SEAL = ROOT / "runs/24928/artifact-manifest.json"


def read_json(path: Path):
    return json.loads(path.read_text())


def metric(doc, key):
    value = doc.get(key)
    return value.get("avg") if isinstance(value, dict) else None


def score(job: str):
    run = ROOT / "runs" / job
    summary = read_json(run / "summary.json")[0]
    export_path = run / "confirm/n60/artifacts/profile_export_aiperf.json"
    export = read_json(export_path)
    goodput = metric(export, "goodput")
    if goodput is None:
        raise ValueError(f"AIPerf exported goodput missing for {job}")
    # Ranking protocol fixes output length at 200 tokens. Keep the exported
    # goodput (requests/s) and its canonical conversion explicit.
    canonical = goodput * 200.0
    if not math.isclose(canonical, summary["good_output_tokens_s"], rel_tol=1e-9):
        raise ValueError(f"summary/AIPerf goodput mismatch for {job}")
    phase = read_json(run / "confirm/n60/artifacts/phase_manifest.json")
    return {
        "job": job,
        "summary_path": str(run / "summary.json"),
        "aiperf_export_path": str(export_path),
        "phase_manifest_path": str(run / "confirm/n60/artifacts/phase_manifest.json"),
        "concurrency": summary["concurrency"],
        "aiperf_goodput_requests_s": goodput,
        "canonical_good_output_tokens_s_goodput_times_200": canonical,
        "raw_output_tokens_s": metric(export, "output_token_throughput"),
        "good_request_fraction": metric(export, "good_request_fraction"),
        "summary_good_request_fraction": summary["good_request_fraction"],
        "sla_pass_at_90_percent_gate": summary["sla_pass"],
        "requests": summary["requests"],
        "good_requests_derived": round(summary["requests"] * summary["good_request_fraction"]),
        "errors": summary["errors"],
        "cancelled_requests": summary["cancelled_requests"],
        "ttft_avg_ms": metric(export, "time_to_first_token"),
        "ttft_p95_ms": export["time_to_first_token"]["p95"],
        "ttft_p99_ms": export["time_to_first_token"]["p99"],
        "ttft_max_ms": export["time_to_first_token"]["max"],
        "itl_avg_ms": metric(export, "inter_token_latency"),
        "itl_p95_ms": export["inter_token_latency"]["p95"],
        "itl_p99_ms": export["inter_token_latency"]["p99"],
        "itl_max_ms": export["inter_token_latency"]["max"],
        "phase_manifest": phase,
    }


def delta(a, b):
    return 100.0 * (a / b - 1.0)


def telemetry(job: str):
    run = ROOT / "runs" / job
    markers = [json.loads(s) for s in (run / "phase-markers.jsonl").read_text().splitlines()]
    client_start = next(x["utc_ns"] for x in markers if x["event"] == "benchmark_start")
    client_end = next(x["utc_ns"] for x in markers if x["event"] == "benchmark_end")
    phase = read_json(run / "confirm/n60/artifacts/phase_manifest.json")["phases"][1]
    profile_cfg = read_json(run / "confirm/n60/artifacts/profile_export_aiperf.json")["input_config"]
    duration_s = next(p["duration"] for p in profile_cfg["phases"] if p["kind"] == "profiling")
    phase_start, phase_end = phase["start_ns"], phase["end_ns"]
    measurement_end = phase_start + int(duration_s * 1_000_000_000)
    windows = {
        "full_client_interval_including_warmup_and_scored_phase": (client_start, client_end),
        "aiperf_scored_phase_including_grace_drain": (phase_start, phase_end),
        "configured_120s_measurement_send_interval": (phase_start, measurement_end),
    }
    roles = {}
    for path in sorted((run / "resource-telemetry").glob("*.jsonl")):
        rows = [json.loads(s) for s in path.read_text().splitlines()]
        all_samples = [x for x in rows if x.get("kind") == "sample"]
        if not all_samples:
            continue
        scopes = {}
        for scope, (start, end) in windows.items():
            samples = [x for x in all_samples if start <= x["utc_ns"] < end]
            gpus = [gpu for sample in samples for gpu in sample.get("gpus", [])]
            metrics = {}
            for key in ("utilization.gpu", "utilization.memory", "memory.used", "power.draw"):
                values = [float(g[key]) for g in gpus if g.get(key) not in (None, "")]
                if values:
                    metrics[key] = {"mean": sum(values) / len(values), "max": max(values), "n": len(values)}
            names = {}
            for sample in samples:
                for line in sample.get("server_metrics", []):
                    m = re.match(r"sglang:([^ {]+).*?\s+([-+0-9.eE]+)$", line)
                    if m:
                        names.setdefault(m.group(1), []).append(float(m.group(2)))
            gauges = {k: {"mean": sum(v) / len(v), "max": max(v), "samples": len(v)} for k, v in names.items()}
            statuses = {}
            for sample in samples:
                status = sample.get("server_http_status")
                statuses[str(status)] = statuses.get(str(status), 0) + 1
            scopes[scope] = {
                "window_start_utc_ns": start, "window_end_utc_ns_exclusive": end,
                "sample_count": len(samples),
                "gpu_metrics_pooled_over_gpu_samples": metrics,
                "sglang_sampled_gauges": gauges,
                "server_http_status_counts": statuses,
            }
        gpus = [gpu for sample in all_samples for gpu in sample.get("gpus", [])]
        roles[path.name] = {
            "raw_samples_excluding_metadata": len(rows) - 1,
            "gpu_uuid_count": len({g.get("uuid") for g in gpus}),
            "gpu_uuids": sorted({g.get("uuid") for g in gpus}),
            "windows": scopes,
        }
    return {
        "window_definitions": {
            "full_client_interval_including_warmup_and_scored_phase": "Top-level phase markers; not scored-only.",
            "aiperf_scored_phase_including_grace_drain": "phase_manifest start_ns through end_ns; includes up to the grace drain and is wider than the configured send interval.",
            "configured_120s_measurement_send_interval": "phase_manifest start_ns through start_ns + configured profiling duration (120 s); exact fixed-duration measurement/send window.",
        },
        "roles": roles,
    }


def profile_coverage(job: str):
    run = ROOT / "runs" / job
    log_path = run / "diagnostic-profile.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    try:
        entries = json.loads("\n".join(line for line in log.splitlines() if line.lstrip().startswith("{")))
    except Exception:
        entries = {}
    traces = [str(p.relative_to(run)) for p in sorted((run / "diagnostic-profile").rglob("*.trace.json.gz"))]
    return {
        "log_path": str(log_path),
        "trace_file_count": len(traces),
        "trace_paths": traces,
        "profile_request_count": entries.get("diagnostic_requests"),
        "profile_start_controls": [x.get("response") for x in entries.get("control", []) if "response" in x],
        "profile_stop_errors": [x.get("stop_error") for x in entries.get("control", []) if "stop_error" in x],
        "scope": "Post-score diagnostic, GPU activities only; not ranked and no CPU traces.",
    }


def server_args(job: str, role: str):
    path = ROOT / "runs" / job / f"{role}.log"
    line = next(line.split("server_args=ServerArgs(", 1)[1][:-1]
                for line in path.read_text(errors="replace").splitlines()
                if "server_args=ServerArgs(" in line)
    expression = ast.parse("f(" + line + ")", mode="eval").body
    return {kw.arg: ast.unparse(kw.value) for kw in expression.keywords}


def protocol_config(job: str):
    data = read_json(ROOT / "runs" / job / "confirm/n60/artifacts/profile_export_aiperf.json")
    cfg = data["input_config"]
    cfg["endpoint"].pop("urls", None)
    cfg["artifacts"].pop("dir", None)
    return cfg


def raw_workload_gate(job: str):
    run = ROOT / "runs" / job
    export = read_json(run / "confirm/n60/artifacts/profile_export_aiperf.json")
    manifest = read_json(run / "confirm/n60/artifacts/phase_manifest.json")
    phases = manifest["phases"]
    if (len(phases) != 2 or [p["phase_kind"] for p in phases] != ["warmup", "profiling"]
            or any(p["total_request_count"] != p["successful_request_count"]
                   or p["error_request_count"] != 0 or p["was_cancelled"] for p in phases)
            or phases[1]["total_request_count"] != int(export["request_count"]["avg"])):
        raise ValueError(f"phase request/error/cancel gate failed for {job}")
    inputs = export["input_config"]
    wanted_phases = [("warmup", 60.0, 60), ("profiling", 120.0, 60)]
    actual_phases = [(p["kind"], p["duration"], p["concurrency"]) for p in inputs["phases"]]
    if actual_phases != wanted_phases or inputs["runtime"]["workers"] != 60:
        raise ValueError(f"workload concurrency/duration mismatch for {job}")
    if inputs["slos"] != {"time_to_first_token": 3000.0, "inter_token_latency": 20.0}:
        raise ValueError(f"joint-SLA thresholds mismatch for {job}")
    expected_extra = {"min_tokens": 200, "max_tokens": 200, "ignore_eos": True,
                      "temperature": 0.0, "repetition_penalty": 1.0}
    if inputs["endpoint"]["extra"] != expected_extra or not inputs["endpoint"]["streaming"]:
        raise ValueError(f"output/stream protocol mismatch for {job}")
    if inputs["datasets"][0]["prompts"] != {
        "isl": {"mean": 4000.0, "stddev": 0.0}, "osl": {"mean": 200.0, "stddev": 0.0},
        "cache_bust": {"target": "first_turn_prefix"}} or inputs["datasets"][0]["random_seed"] != 2026:
        raise ValueError(f"synthetic workload mismatch for {job}")
    raw_counts = {"warmup": 0, "profiling": 0}
    raw_good = 0
    with (run / "confirm/n60/artifacts/profile_export.jsonl").open() as f:
        for line in f:
            row = json.loads(line)
            if row["metadata"]["was_cancelled"] or row.get("error") or row.get("errors"):
                raise ValueError(f"raw request error/cancellation in {job}")
            kind = row["metadata"]["phase_kind"]
            if kind not in raw_counts:
                raise ValueError(f"unexpected raw phase {kind}")
            raw_counts[kind] += 1
            if kind == "profiling":
                raw_good += row["metrics"]["good_request_count"]["value"]
    if raw_counts != {p["phase_kind"]: p["total_request_count"] for p in phases}:
        raise ValueError(f"raw request totals mismatch for {job}")
    if not math.isclose(raw_good / phases[1]["total_request_count"],
                        export["good_request_fraction"]["avg"], rel_tol=1e-9):
        raise ValueError(f"raw joint-good fraction mismatch for {job}")
    return {"phase_counts_from_raw_jsonl": raw_counts, "good_requests_from_raw_jsonl": int(raw_good),
            "joint_good_fraction_recomputed": raw_good / phases[1]["total_request_count"],
            "configured_workload_validated": True, "zero_error_and_cancellation_gate": True}


def create_or_verify_run_manifest():
    run = ROOT / "runs/24928"
    if SEAL.exists():
        seal = read_json(SEAL)
        if seal.get("job") != "24928":
            raise ValueError("24928 seal job mismatch")
        return seal
    files = []
    for path in sorted(p for p in run.rglob("*") if p.is_file() and p != SEAL):
        files.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
                      "sha256": sha256(path)})
    seal = {
        "job": "24928",
        "status_at_seal": {"state": "COMPLETED", "exit": "0:0",
                            "observed_utc": "2026-10-21T14:39:15Z",
                            "source": "Parent-provided fresh Slurm terminal result; this review did not query scheduler."},
        "manifest_kind": "derived local artifact seal; raw and submitted files remain unchanged",
        "files": files,
    }
    SEAL.write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n")
    return seal


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def hashes():
    result = []
    # Seal every retained 24928 file without copying it. For controls, seal
    # configs, summaries, exports, protocol manifests, and frozen submitted bytes.
    for job in JOBS:
        run = ROOT / "runs" / job
        if job == "24928":
            paths = sorted(p for p in run.rglob("*") if p.is_file())
        else:
            paths = [run / "config.json", run / "summary.json", run / "submitted/SHA256SUMS",
                     run / "confirm/n60/artifacts/profile_export_aiperf.json",
                     run / "confirm/n60/artifacts/phase_manifest.json",
                     run / "confirm/n60/client.log"]
            paths += sorted((run / "submitted").glob("*"))
            paths = [p for p in paths if p.is_file()]
        for p in paths:
            result.append({"job": job, "path": str(p), "bytes": p.stat().st_size, "sha256": sha256(p)})
    result.append({"job": "24928", "path": str(SEAL), "bytes": SEAL.stat().st_size,
                   "sha256": sha256(SEAL), "kind": "derived run seal"})
    return result


def core_review_gates():
    helper = ROOT / "serving-tuning-10/review-wave10.py"
    spec = importlib.util.spec_from_file_location("wave10_review_core", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    point = module.core.point(ROOT, "24928", 60)
    long_result = module.long_check(ROOT / "runs/24928")
    if long_result.get("state") != "PASSED" or long_result.get("errors") != 0:
        raise ValueError(f"sealed long-context gate failed: {long_result}")
    return {
        "state": "LOCAL_PROTOCOL_SLA_OUTPUT_PASS",
        "helper_path": str(helper),
        "core_point": {
            "job": point["job"], "concurrency": point["concurrency"],
            "metrics": point["metrics"], "sealed_files": point["sealed_files"],
            "seal_sha256": point["seal_sha256"],
            "short_output_comparison": point["short_output_comparison"],
            "resolved_server_args_roles": sorted(point["server_args"]),
        },
        "long_context_gate": long_result,
        "accuracy_verified": False,
        "scheduler_refreshed_by_this_review": False,
        "submission_authorized": False,
    }


def main():
    create_or_verify_run_manifest()
    scores = {job: score(job) for job in JOBS}
    candidate = scores["24928"]["canonical_good_output_tokens_s_goodput_times_200"]
    observed = scores["24927"]["canonical_good_output_tokens_s_goodput_times_200"]
    off = scores["24926"]["canonical_good_output_tokens_s_goodput_times_200"]
    config = read_json(ROOT / "runs/24928/config.json")
    worker = (ROOT / "runs/24928/submitted/worker.sh").read_text()
    topology = (ROOT / "runs/24928/submitted/topology-job.sh").read_text()
    protocol_equal = protocol_config("24928") == protocol_config("24927")
    if not protocol_equal:
        raise ValueError("24928 and 24927 input protocol differs")
    args_diff = {}
    for role in ("prefill-0", "prefill-1", "decode-0"):
        candidate_args = server_args("24928", role)
        control_args = server_args("24927", role)
        changes = {k: [control_args.get(k), candidate_args.get(k)]
                   for k in control_args.keys() | candidate_args.keys()
                   if control_args.get(k) != candidate_args.get(k)}
        allowed = {"random_seed"} | ({"scheduler_recv_interval"} if role == "decode-0" else set())
        if set(changes) - allowed:
            raise ValueError(f"unexpected resolved ServerArgs differences for {role}: {changes}")
        if role == "decode-0" and changes.get("scheduler_recv_interval") != ["1", "2"]:
            raise ValueError("decode receive interval is not the sole intended runtime change")
        if role != "decode-0" and "scheduler_recv_interval" in changes:
            raise ValueError(f"prefill receive interval changed on {role}")
        args_diff[role] = changes
    payload_diffs = []
    for path in sorted((ROOT / "runs/24928/submitted").iterdir()):
        other = ROOT / "runs/24927/submitted" / path.name
        if path.is_file() and other.is_file() and sha256(path) != sha256(other):
            payload_diffs.append(path.name)
    if payload_diffs != ["SHA256SUMS", "config.json", "job.sbatch", "worker.sh"]:
        raise ValueError(f"unexpected frozen payload differences: {payload_diffs}")
    smoke28 = read_json(ROOT / "runs/24928/output-smoke.json")
    smoke27 = read_json(ROOT / "runs/24927/output-smoke.json")
    if ([x["name"] for x in smoke28["cases"] if not x["passed"]]
            != [x["name"] for x in smoke27["cases"] if not x["passed"]]):
        raise ValueError("output-smoke failure set differs from observed control")
    result = {
        "review_id": "h200-24928-recv2-review-20261021",
        "state": "LOCAL_REVIEW_INCOMPLETE",
        "generated_by": str(Path(__file__).resolve()),
        "metric_definition": "Canonical local score is AIPerf exported goodput (requests/s) multiplied by fixed 200 output tokens; not raw throughput.",
        "scores": scores,
        "comparisons": {
            "24928_vs_observed_interval1_24927_percent": delta(candidate, observed),
            "24928_vs_observer_off_interval1_24926_percent": delta(candidate, off),
            "24927_observed_vs_24926_off_percent": delta(observed, off),
            "interpretation": "Single-run descriptive comparisons; not replicated causal estimates.",
        },
        "protocol_and_gates": {
            "fixed_workload": "closed-loop synthetic 4000 input / 200 output tokens, seed 2026, cold first-turn cache prefix; N60; confirm 60 s warm-up + 120 s measurement + 30 s grace",
            "joint_sla_thresholds": {"TTFT_ms_max": 3000, "request_mean_ITL_ms_max": 20, "good_request_fraction_min": 0.90},
            "scored_gate": "AIPerf summary says SLA pass; all requests drained; 0 errors and 0 cancellations.",
            "timeout_note": "AIPerf fixed-duration client reports timeout_triggered=true at planned termination; this is not treated as an error because raw phase shows all requests completed and no cancellation/error.",
            "official_accuracy": "Unverified; local output checks are not organiser accuracy.",
        },
        "actual_configuration": {
            "config_path": str(ROOT / "runs/24928/config.json"),
            "experiment": config["experiment"],
            "hardware": "H200; 2 prefill workers TP4 each (8 GPUs), 1 decode worker TP8 (8 GPUs); N60",
            "prefill_flags": config["prefill_extra_flags"],
            "decode_flags": config["decode_extra_flags"] + ["--scheduler-recv-interval", str(config["scheduler_recv_interval_decode"])],
            "router_flags": config["router_extra_flags"],
            "native_worker_evidence": {"worker_path": str(ROOT / "runs/24928/submitted/worker.sh"),
                "prefill_command": "--chunked-prefill-size 8192 --moe-runner-backend deep_gemm",
                "decode_command": "--scheduler-recv-interval 2; graph batch sizes 1..64; MNNVL fusion; FlashInfer attention; HPC-Ops MoE",
                "router_command": "--prefill-policy round_robin",
                "worker_contains_scheduler_recv_2": "--scheduler-recv-interval 2" in worker,
                "topology_contains_round_robin": "--prefill-policy round_robin" in topology},
            "unchanged_numerical_work": "Only decode scheduler receive interval was changed against 24927. Same checkpoint/precision/KV, native kernels/backends, NIXL patch, graph shapes, router policy, workload and quality checks.",
        },
        "resource_observability": telemetry("24928"),
        "raw_workload_gates": {job: raw_workload_gate(job) for job in JOBS},
        "control_match": {
            "protocol_config_equal_after_artifact_path_and_url_normalization": protocol_equal,
            "resolved_server_args_differences_vs_24927": args_diff,
            "submitted_payload_file_differences_vs_24927": payload_diffs,
            "output_smoke_failed_cases_equal_24927": [x["name"] for x in smoke28["cases"] if not x["passed"]],
            "comparison_limits": "24927 is a matched observer-on interval-1 control; 24926 is a separate observer-off interval-1 run. Raw environmental/run-order differences remain.",
        },
        "profile_coverage": profile_coverage("24928"),
        "output_checks": {
            "smoke_path": str(ROOT / "runs/24928/output-smoke.json"),
            "smoke_passed": read_json(ROOT / "runs/24928/output-smoke.json")["passed"],
            "smoke_total": read_json(ROOT / "runs/24928/output-smoke.json")["total"],
            "failed_case": [x["name"] for x in read_json(ROOT / "runs/24928/output-smoke.json")["cases"] if not x["passed"]],
            "matched_control_note": "Same reverse case also fails on 24927; local sanity only.",
            "long_context_path": str(ROOT / "runs/24928/long-context-check.json"),
            "long_context_passed": read_json(ROOT / "runs/24928/long-context-check.json")["passed"],
            "long_context_total": read_json(ROOT / "runs/24928/long-context-check.json")["total"],
            "quality_limit": "Neither hand-written test set proves full model accuracy or formal PD equivalence.",
        },
        "provenance": {
            "runs_24928_artifact_manifest": "Missing run-level artifact-manifest.json; retain this caveat and do not claim a complete run seal.",
            "hash_policy": "Hash retained paths in place; this review copies no run payloads or large raw artifacts.",
            "sealed_files": hashes(),
        },
    }
    result["validation_gates"] = core_review_gates()
    result["state"] = result["validation_gates"]["state"]
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT} with {len(result['provenance']['sealed_files'])} hashes")


if __name__ == "__main__":
    main()
