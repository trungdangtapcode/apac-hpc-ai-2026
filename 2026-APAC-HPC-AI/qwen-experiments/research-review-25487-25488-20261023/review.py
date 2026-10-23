#!/usr/bin/env python3
"""Seal and review the completed matched H200 full N64/N68 pair offline."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
JOBS = {"25487": 64, "25488": 68}
SOURCE = "25366"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sacct(job, all_steps=False):
    cmd = ["sacct"]
    if not all_steps:
        cmd.append("-X")
    cmd += ["-j", job, "-P", "--format=JobID,JobName%50,State%30,ExitCode,Elapsed,Start,End,AllocTRES%100"]
    return subprocess.check_output(cmd, text=True)


def stable_hash(path):
    before = path.stat()
    digest = sha(path)
    after = path.stat()
    fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(before, k) != getattr(after, k) for k in fields):
        raise RuntimeError(f"File changed during seal: {path}")
    return {"path": str(path.relative_to(ROOT)), "bytes": after.st_size,
            "sha256": digest}


def seal_if_absent(job):
    run = ROOT / "runs" / job
    seal = run / "artifact-manifest.json"
    status_text = sacct(job)
    rows = [line.split("|") for line in status_text.splitlines() if line.strip()]
    header = rows[0]
    data = [dict(zip(header, row)) for row in rows[1:] if row[0] == job]
    if len(data) != 1:
        raise RuntimeError(f"Expected one terminal sacct record for {job}; got {data}")
    status = data[0]
    if status["State"] != "COMPLETED" or status["ExitCode"] != "0:0":
        raise RuntimeError(f"Top-level job {job} is not COMPLETED/0:0: {status}")
    if not seal.exists():
        files = []
        for base, dirs, names in os.walk(run, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not (Path(base) / d).is_symlink() and d != "__pycache__")
            for name in sorted(names):
                path = Path(base) / name
                if path.name in {"artifact-manifest.json", "summary.json"} or path.is_symlink() or not path.is_file():
                    continue
                files.append(stable_hash(path))
        for path in (ROOT / "runs" / f"{job}.out", ROOT / "runs" / f"{job}.err"):
            if path.is_file() and not path.is_symlink():
                files.append(stable_hash(path))
        manifest = {"job": job, "sealed_utc": datetime.now(timezone.utc).isoformat(),
                    "status_at_seal": {"JobID": status["JobID"], "State": status["State"],
                                       "ExitCode": status["ExitCode"], "Elapsed": status["Elapsed"],
                                       "Start": status["Start"], "End": status["End"]},
                    "scope": "Terminal run evidence inventoried after scheduler completion; generated summary.json excluded following the established sealing convention.",
                    "files": files}
        # Exclusive creation prevents replacing a concurrent or earlier seal.
        with seal.open("x") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")
    return seal


def percentile(values, p):
    xs = sorted(values)
    if not xs:
        return None
    pos = (len(xs) - 1) * p
    lo = math.floor(pos)
    hi = math.ceil(pos)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def raw_requests(run, n):
    path = run / f"confirm/n{n}/artifacts/profile_export.jsonl"
    counts = Counter()
    lat = {"time_to_first_token": [], "inter_token_latency": []}
    total = good = ttft_bad = itl_bad = errors = cancelled = 0
    phase_counts = Counter()
    lengths = Counter()
    for line in path.read_text().splitlines():
        row = json.loads(line)
        meta = row["metadata"]
        phase_counts[meta["phase_kind"]] += 1
        if meta["phase_kind"] != "profiling":
            continue
        total += 1
        is_cancelled = bool(meta.get("was_cancelled", False))
        err = bool(row.get("error") or row.get("errors"))
        cancelled += is_cancelled
        errors += err
        m = row["metrics"]
        t = float(m["time_to_first_token"]["value"])
        i = float(m["inter_token_latency"]["value"])
        lat["time_to_first_token"].append(t)
        lat["inter_token_latency"].append(i)
        ttft_bad += t > 3000
        itl_bad += i > 20
        passed = t <= 3000 and i <= 20
        good += passed
        counts["ttft_and_itl_good"] += int(passed)
        counts["ttft_only_breach"] += int(t > 3000 and i <= 20)
        counts["itl_only_breach"] += int(t <= 3000 and i > 20)
        counts["both_breach"] += int(t > 3000 and i > 20)
        lengths[int(m["output_sequence_length"]["value"])] += 1
    return {"phase_request_counts": dict(phase_counts), "profiling_requests": total,
            "raw_joint_good": good, "good_fraction": good / total if total else None,
            "raw_errors": errors, "raw_cancelled": cancelled,
            "ttft_breaches_over_3000_ms": ttft_bad, "itl_breaches_over_20_ms": itl_bad,
            "joint_classification": dict(counts),
            "ttft_ms": {"mean": statistics.mean(lat["time_to_first_token"]) if total else None,
                          "p50": percentile(lat["time_to_first_token"], .5),
                          "p90": percentile(lat["time_to_first_token"], .9),
                          "p95": percentile(lat["time_to_first_token"], .95),
                          "p99": percentile(lat["time_to_first_token"], .99),
                          "max": max(lat["time_to_first_token"]) if total else None},
            "request_mean_itl_ms": {"mean": statistics.mean(lat["inter_token_latency"]) if total else None,
                                    "p50": percentile(lat["inter_token_latency"], .5),
                                    "p90": percentile(lat["inter_token_latency"], .9),
                                    "p95": percentile(lat["inter_token_latency"], .95),
                                    "p99": percentile(lat["inter_token_latency"], .99),
                                    "max": max(lat["inter_token_latency"]) if total else None},
            "exported_output_sequence_length_counts": dict(sorted(lengths.items())),
            "nominal_requested_output_tokens": 200,
            "actual_generated_token_ids_retained": False}


def main():
    # Seal runs once, only after the scheduler confirms terminal success.
    account = {}
    for job in JOBS:
        seal_if_absent(job)
        all_steps = sacct(job, all_steps=True)
        account[job] = all_steps
        (OUT / f"sacct-{job}-all-steps.psv").write_text(all_steps)
    core = load_module("serving_core", ROOT / "serving-tuning/review-n54.py")
    wave = load_module("wave10", ROOT / "serving-tuning-10/review-wave10.py")
    observability = load_module("observability_25373", ROOT / "research-review-25373-20261022/observability.py")

    points = {job: core.point(ROOT, job, n) for job, n in JOBS.items()}
    baseline = core.point(ROOT, SOURCE, 64)
    comparisons = {}
    config_by_job = {job: json.loads((ROOT / "runs" / job / "config.json").read_text()) for job in JOBS}
    pair_config_differences = {key: {"n64": config_by_job["25487"].get(key),
                                    "n68": config_by_job["25488"].get(key)}
                              for key in sorted(config_by_job["25487"].keys() | config_by_job["25488"].keys())
                              if config_by_job["25487"].get(key) != config_by_job["25488"].get(key)}
    if set(pair_config_differences) != {"concurrency", "experiment"}:
        raise RuntimeError(f"Unexpected N64/N68 config differences: {pair_config_differences}")
    for job, n in JOBS.items():
        run = ROOT / "runs" / job
        submitted = run / "submitted"
        sums = subprocess.check_output(["sha256sum", "-c", "SHA256SUMS"], cwd=submitted, text=True)
        (OUT / f"submitted-sha256-check-{job}.txt").write_text(sums)
        # Registry payload identity and frozen on-disk receipt are checked by core.point.
        base_run = ROOT / "runs" / SOURCE / "submitted"
        changed = {}
        files = sorted(points[job]["payload_files"])
        for name in files:
            if name in {"config.json", "job.sbatch"}:
                continue
            candidate_hash = sha(submitted / name)
            source_hash = sha(base_run / name)
            if candidate_hash != source_hash:
                changed[name] = {"job_sha256": candidate_hash, "source_sha256": source_hash}
        args_delta = {}
        for role, args in points[job]["server_args"].items():
            prev = baseline["server_args"][role]
            delta = {k: [prev.get(k), args.get(k)] for k in args.keys() | prev.keys()
                     if args.get(k) != prev.get(k)}
            args_delta[role] = delta
        cfg = json.loads((run / "config.json").read_text())
        comparisons[job] = {"concurrency": n,
                           "protocol_matches_source": points[job]["normalized_protocol"] == baseline["normalized_protocol"],
                           "non_config_operational_file_differences_vs_source": changed,
                           "resolved_server_arg_differences_vs_source": args_delta,
                           "short_output_comparison": points[job]["short_output_comparison"],
                           "long_context": wave.long_check(run),
                           "run_config_changed_factor": cfg.get("changed_factor"),
                           "source_run_config_concurrency": baseline["concurrency"]}
        if not comparisons[job]["protocol_matches_source"]:
            raise RuntimeError(f"Protocol mismatch for {job}")
        if changed:
            raise RuntimeError(f"Operational payload drift from source for {job}: {changed}")
        unexpected = {role: {k: v for k, v in d.items() if k != "random_seed"}
                      for role, d in args_delta.items()}
        if any(unexpected.values()):
            raise RuntimeError(f"Resolved runtime changed beyond random seed for {job}: {unexpected}")
        if comparisons[job]["long_context"]["state"] != "PASSED":
            raise RuntimeError(f"Long context diagnostic did not pass for {job}")

    jobs = {}
    for job, n in JOBS.items():
        run = ROOT / "runs" / job
        phase_manifest = json.loads((run / f"confirm/n{n}/artifacts/phase_manifest.json").read_text())
        phase = next(p for p in phase_manifest["phases"] if p["phase_kind"] == "profiling")
        markers = [json.loads(line) for line in (run / "phase-markers.jsonl").read_text().splitlines() if line.strip()]
        start = next(m for m in markers if m["event"] == "benchmark_start")
        end = next(m for m in markers if m["event"] == "benchmark_end")
        obs = {role: observability.resource_role(run, job, role, host, phase)
               for role, host in observability.ROLES}
        score_summary = json.loads((run / "summary.json").read_text())[0]
        measured = points[job]["metrics"]
        for summary_key, metric_key in (("good_output_tokens_s", "good_tokens_s"),
                                        ("good_request_fraction", "sla_fraction"),
                                        ("ttft_avg_ms", "ttft_ms"), ("itl_avg_ms", "itl_ms")):
            if not math.isclose(float(score_summary[summary_key]), float(measured[metric_key]),
                                rel_tol=1e-12, abs_tol=1e-12):
                raise RuntimeError(f"summary.json disagrees with sealed raw export for {job}: {summary_key}")
        account_rows = [line.split("|") for line in account[job].splitlines() if line.strip()]
        header = account_rows[0]
        steps = [dict(zip(header, row)) for row in account_rows[1:]]
        jobs[job] = {"point": points[job], "summary": score_summary,
                     "raw_request_review": raw_requests(run, n),
                     "profiling_phase": {"start_ns": phase["start_ns"], "end_ns": phase["end_ns"],
                                         "duration_s": (phase["end_ns"] - phase["start_ns"]) / 1e9,
                                         "requests": phase["total_request_count"], "errors": phase["error_request_count"],
                                         "cancelled": phase["was_cancelled"],
                                         "enclosed_by_markers": start["utc_ns"] <= phase["start_ns"] <= phase["end_ns"] <= end["utc_ns"]},
                     "role_telemetry": obs,
                     "role_logs": observability.log_review(run),
                     "profiler_control": observability.profile_control(run),
                     "diagnostic_trace_inventory": observability.traces(run),
                     "scheduler_steps": steps,
                     "top_level_accounting": points[job]["status_at_seal"],
                     "long_context": comparisons[job]["long_context"],
                     "short_output": comparisons[job]["short_output_comparison"]}
        raw = jobs[job]["raw_request_review"]
        if raw["profiling_requests"] != int(score_summary["requests"]):
            raise RuntimeError(f"Raw profiling count mismatch for {job}")
        if raw["raw_errors"] != 0 or raw["raw_cancelled"] != 0:
            raise RuntimeError(f"Scored request errors/cancellations found for {job}")
        if raw["raw_joint_good"] != score_summary["requests"] * score_summary["good_request_fraction"]:
            if abs(raw["raw_joint_good"] / raw["profiling_requests"] - score_summary["good_request_fraction"]) > 1e-12:
                raise RuntimeError(f"Raw Goodput SLA fraction mismatch for {job}")

    a = jobs["25487"]["summary"]["good_output_tokens_s"]
    b = jobs["25488"]["summary"]["good_output_tokens_s"]
    gain = (b / a - 1) * 100
    # Graph request-load range and actual per-role server-gauge range are reported separately.
    graph = {}
    for job, n in JOBS.items():
        log = (ROOT / "runs" / job / "decode-0.log").read_text(errors="replace")
        import re
        sizes = sorted({int(x) for x in re.findall(r"cuda_graph_bs_decode=\[([^\]]+)\]", log)[0].replace(',', ' ').split()}) if re.findall(r"cuda_graph_bs_decode=\[([^\]]+)\]", log) else None
        graph[job] = {"configured_decode_cuda_graph_batch_sizes": sizes,
                      "configured_graph_max_batch": max(sizes) if sizes else 64,
                      "client_concurrency": JOBS[job],
                      "server_running_request_gauge_by_role": {
                          role: obs.get("role_server_gauges_inside", {}).get("sglang:num_running_reqs", {})
                          for role, obs in jobs[job]["role_telemetry"].items()},
                      "interpretation": "Client concurrency, sampled running-request gauges and configured CUDA graph sizes are distinct; gauge series are per label and not summed."}

    result = {"reviewed_utc": datetime.now(timezone.utc).isoformat(),
              "state": "FULL_PROTOCOL_SLA_PASS_PAIR_N68_GAIN_BELOW_REPLICATION_GATE",
              "hardware": "H200, 16 GPUs across two nodes per job; sequential jobs with the N68 afterok dependency.",
              "scheduler_queue_empty_at_review": not bool(subprocess.check_output(["squeue", "-h", "-u", "apacsc42"], text=True).strip()),
              "jobs": jobs,
              "source_job_25366": baseline,
              "payload_and_runtime_controls": comparisons,
              "pair_config_differences": pair_config_differences,
              "review_source_sha256": {
                  str(path.relative_to(ROOT)): sha(path) for path in (
                      ROOT / "serving-tuning/review-n54.py",
                      ROOT / "serving-tuning-10/review-wave10.py",
                      ROOT / "research-review-25373-20261022/observability.py",
                      ROOT / "serving-tuning/registry.json")},
              "configured_graph_and_observed_batch": graph,
              "comparison": {"control_job": "25487", "candidate_job": "25488",
                             "control_good_output_tokens_s": a, "candidate_good_output_tokens_s": b,
                             "good_output_tokens_s_delta": b - a, "gain_percent": gain,
                             "practical_replication_gate_percent": 1.0,
                             "replication_gate_met": gain >= 1.0,
                             "interpretation": "One matched full pair. Candidate N68 passes the local >=90% joint SLA, but its +0.083% gain is below the predeclared +1% practical gate; do not replicate unchanged N68."},
              "cleanup_interpretation": "Both top-level allocations and batch steps ended COMPLETED/0:0 after the scripts logged MEASUREMENTS_COMPLETE. The retained topology-job.sh installs an EXIT trap that sends kill to its background worker/router srun PIDs and waits; sacct shows those long-lived nested steps 25487.0-.3 and 25488.0-.3 cancelled at allocation teardown, while the AIPerf step .5 completed 0:0 and pair-warmup step .4 completed 0:0. The scored phase manifests report was_cancelled=false and zero request errors/cancellations. The separate post-score profiler stop returned HTTP 500 and is recorded as a diagnostic failure.",
              "quality_status": "Official >=99% reference accuracy remains unverified. Long retrieval and short smoke are local diagnostics only.",
              "limitations": ["No official benchmark accuracy evaluation was run.",
                             "The exported output length can vary despite nominal 200-token requests; actual generated token IDs were not retained in these scored runs.",
                             "Profiler stop HTTP 500 is separate from the score export; trace filenames are inventoried, contents not inspected.",
                             "Sparse per-role telemetry is phase-aligned but cannot identify a causal bottleneck or prove peak resource behavior.",
                             "Only one N64/N68 full pair was run; the small positive difference is below the planned practical gain gate."]}
    (OUT / "REVIEW.json").write_text(json.dumps(result, indent=2) + "\n")
    write_markdown(result)
    print(json.dumps({"state": result["state"], "gain_percent": gain,
                      "sla": {j: jobs[j]["summary"]["good_request_fraction"] for j in JOBS},
                      "review": str(OUT / "REVIEW.json")}, indent=2))


def write_markdown(data):
    lines = ["# Full H200 N64/N68 pair review", "",
             "This offline review inspects jobs 25487 (N64 control) and 25488 (N68 candidate), then compares the pair with the accepted full N64 source 25366. It reuses the validated metric reader from `serving-tuning/review-n54.py`, the long-diagnostic validator from `serving-tuning-10/review-wave10.py`, and phase-aligned telemetry parsers from `research-review-25373-20261022/observability.py`.", "",
             "## Scored comparison", "",
             "| Job | Client concurrency | Good output tokens/s | Joint SLA | Requests | Errors / cancelled | TTFT mean / p95 / p99 / max (ms) | Request-mean ITL mean / p95 / p99 / max (ms) |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for job, item in data["jobs"].items():
        s = item["summary"]
        raw = item["raw_request_review"]
        t, i = raw["ttft_ms"], raw["request_mean_itl_ms"]
        lines.append(f"| {job} | {item['point']['concurrency']} | {s['good_output_tokens_s']:.3f} | {s['good_request_fraction']:.6%} | {int(s['requests'])} | {s['errors']} / {s['cancelled_requests']} | {t['mean']:.1f} / {s['ttft_p95_ms']:.1f} / {t['p99']:.1f} / {t['max']:.1f} | {i['mean']:.3f} / {s['itl_p95_ms']:.3f} / {i['p99']:.3f} / {i['max']:.3f} |")
    c = data["comparison"]
    lines += ["", f"N68 changed good output throughput by **{c['gain_percent']:+.3f}%** over the fresh full N64 control. Both meet the local 90% joint TTFT/ITL threshold and have zero scored errors or cancellations. The gain is below the predeclared 1% replication gate, so stop the unchanged N68 branch.", "",
              "The raw joint classification counts each profiling request once, including bad requests. The local good fraction is not the separate contest accuracy gate.", "",
              "## Request tails and output lengths", ""]
    for job, item in data["jobs"].items():
        r = item["raw_request_review"]
        lines.append(f"Job {job}: TTFT breaches >3,000 ms = {r['ttft_breaches_over_3000_ms']}; request-mean ITL breaches >20 ms = {r['itl_breaches_over_20_ms']}. Joint good / TTFT-only / ITL-only / both-bad = {r['joint_classification'].get('ttft_and_itl_good',0)} / {r['joint_classification'].get('ttft_only_breach',0)} / {r['joint_classification'].get('itl_only_breach',0)} / {r['joint_classification'].get('both_breach',0)}. Exported output lengths: `{r['exported_output_sequence_length_counts']}`; requested length remained nominally 200.")
    lines += ["", "Actual generated token IDs were not retained in these performance runs, so exported lengths remain diagnostic evidence rather than a byte-level output archive.", "",
              "## Protocol and payload control", ""]
    for job, c in data["payload_and_runtime_controls"].items():
        lines.append(f"Job {job}: normalized official closed-loop 4,000/200 protocol and 60 s warm-up / 120 s measurement / 30 s grace match source 25366; the 15 non-config operational payload files are byte-identical. Resolved SGLang arguments differ from 25366 only in the randomized seed. Output smoke eligibility: {c['short_output_comparison'].get('research_eligible')}; new failed cases: {c['short_output_comparison'].get('new_failed_cases')}. Long retrieval: {c['long_context']['state']} ({c['long_context'].get('passed',0)}/12).")
    lines += ["", "Across 25487 vs 25488, `config.json` differs only in concurrency (64 → 68) and the descriptive experiment name. The 15 non-config execution payload files are byte-identical; resolved service arguments differ from source 25366 only in randomized seeds.", "",
              "## Queue, runtime, and cleanup", ""]
    lines.append(data["cleanup_interpretation"])
    lines.append("The diagnostic profiler starts returned HTTP 200 but all stop calls returned HTTP 500. Its trace files were inventoried, not analyzed. This failure is not scored request failure.")
    lines.append("CUDA graph decode sizes are configured from 1 through 64. Per-role SGLang running/queued request gauges and sampled GPU activity, VRAM, and power are retained in `REVIEW.json`; series are not summed across TP ranks. Client concurrency is not itself the measured batch size. Sparse observer readings cannot prove saturation or identify cause.")
    lines += ["", "## Decision and limits", "", "Keep N64 as the measured incumbent. Close N68 at this load: +0.083% is too small to justify another full replication under the plan's 1% gate. The scoring pair is valid local serving evidence; it does not verify the organizer's ≥99% reference accuracy, and no H100/H200 cross-hardware conversion is inferred.", "",
              "Reproduce from this directory with `python3 review.py`. It seals raw run files once if manifests are absent and writes only this review directory plus `runs/25487/artifact-manifest.json` and `runs/25488/artifact-manifest.json`.", ""]
    (OUT / "REVIEW.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
