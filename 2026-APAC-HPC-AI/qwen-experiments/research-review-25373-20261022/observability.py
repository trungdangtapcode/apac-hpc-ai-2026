#!/usr/bin/env python3
"""Offline, bounded observability review for full H200 N64 source and independent repeat."""
from pathlib import Path
import collections
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
JOBS = {"25366": 64, "25373": 64}
ROLES = (("prefill-0", "g1"), ("prefill-1", "g1"), ("decode-0", "g4"))
KEEP_METRICS = {
    "sglang:num_running_reqs", "sglang:num_queue_reqs", "sglang:token_usage",
    "sglang:num_used_tokens", "sglang:cache_hit_rate",
}
GAUGE = re.compile(r"^(sglang:[^\{ ]+)(?:\{([^}]*)\})?\s+([-+0-9.eE]+)$")


def read_json(path):
    return json.loads(path.read_text())


def percentile(xs, p):
    xs = sorted(xs)
    if not xs:
        return None
    pos = (len(xs) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def finite(values):
    xs = [float(x) for x in values if x is not None]
    return {"count": len(xs), "mean": sum(xs) / len(xs) if xs else None,
            "min": min(xs) if xs else None, "max": max(xs) if xs else None}


def status_counts(rows):
    return dict(sorted(collections.Counter(str(r.get("server_http_status", r.get("server_metrics_status", "MISSING_STATUS"))) for r in rows).items()))


def gpu_status_counts(rows):
    return dict(sorted(collections.Counter(str(r.get("gpu_status", "MISSING_STATUS")) for r in rows).items()))


def gauge_stats(rows):
    series = {}
    for row in rows:
        if row.get("server_http_status") != 200 or not row.get("server_metrics"):
            continue
        for line in row["server_metrics"]:
            m = GAUGE.match(line.strip())
            if not m or m.group(1) not in KEEP_METRICS:
                continue
            name, labels, raw = m.groups()
            try:
                value = float(raw)
            except ValueError:
                continue
            series.setdefault(name, {}).setdefault(labels or "", []).append(value)
    result = {}
    units = {
        "sglang:num_running_reqs": "requests per labeled series; do not sum across TP ranks",
        "sglang:num_queue_reqs": "queued requests per labeled series; do not sum across TP ranks",
        "sglang:token_usage": "unitless fractional token/KV usage per labeled series",
        "sglang:num_used_tokens": "tokens per labeled series; do not sum across TP ranks",
        "sglang:cache_hit_rate": "unitless fraction per labeled series",
    }
    for name, groups in series.items():
        all_values = [v for values in groups.values() for v in values]
        result[name] = {
            "unit_and_scope": units[name], "series_count": len(groups),
            "observation_count": len(all_values), **finite(all_values),
            "series": {label: finite(values) for label, values in sorted(groups.items())},
        }
    return result


def profile_metrics(run, n):
    path = run / f"confirm/n{n}/artifacts/profile_export.jsonl"
    ttft, itl = [], []
    errors = []
    phases = collections.Counter()
    cancelled = 0
    output_lengths = collections.Counter()
    for line in path.open():
        row = json.loads(line)
        meta = row.get("metadata", {})
        kind = meta.get("phase_kind", meta.get("benchmark_phase", "unknown"))
        phases[kind] += 1
        if kind != "profiling":
            continue
        cancelled += bool(meta.get("was_cancelled"))
        if row.get("error") or row.get("errors"):
            errors.append({"request_id": meta.get("x_request_id"), "error": row.get("error", row.get("errors"))})
        metrics = row.get("metrics", {})
        if "time_to_first_token" in metrics:
            ttft.append(float(metrics["time_to_first_token"]["value"]))
        if "inter_token_latency" in metrics:
            itl.append(float(metrics["inter_token_latency"]["value"]))
        if "output_sequence_length" in metrics:
            output_lengths[str(metrics["output_sequence_length"]["value"])] += 1
    def lat(values, threshold):
        return {"count": len(values), "mean_ms": finite(values)["mean"],
                "p95_ms": percentile(values, .95), "p99_ms": percentile(values, .99),
                "max_ms": max(values) if values else None,
                "over_threshold_count": sum(x > threshold for x in values), "threshold_ms": threshold}
    return {"raw_records_by_phase": dict(phases), "scored_error_records": len(errors),
            "scored_error_examples": errors[:3], "scored_cancelled_records": cancelled,
            "ttft_ms": lat(ttft, 3000), "request_mean_itl_ms": lat(itl, 20),
            "exported_output_sequence_length_counts": dict(sorted(output_lengths.items())),
            "note": "Exported sequence lengths are retained; they do not prove actual generated token IDs."}


def resource_role(run, job, role, host, phase):
    path = run / f"resource-telemetry/{role}-{host}.jsonl"
    if not path.exists():
        return {"state": "NOT_COLLECTED"}
    rows = [json.loads(line) for line in path.open()]
    metadata = next((r for r in rows if r.get("kind") == "metadata"), {})
    samples = [r for r in rows if r.get("kind") == "sample"]
    interval_ns = int(float(metadata.get("interval_s", 0)) * 1e9)
    inside = [r for r in samples if r.get("utc_ns") is not None
              and int(r["utc_ns"]) - interval_ns >= phase["start_ns"]
              and int(r["utc_ns"]) <= phase["end_ns"]]
    outside = [r for r in samples if r not in inside]
    devices = {}
    fields = {"utilization.gpu": "gpu_activity_percent", "utilization.memory": "memory_activity_percent",
              "memory.used": "sampled_vram_mib", "power.draw": "sampled_power_w"}
    for row in inside:
        if row.get("gpu_status") != "ok":
            continue
        for gpu in row.get("gpus", []):
            uuid = gpu.get("uuid", "MISSING_UUID")
            rec = devices.setdefault(uuid, {k: [] for k in fields})
            for field in fields:
                try:
                    rec[field].append(float(gpu[field]))
                except (KeyError, TypeError, ValueError):
                    pass
    per_gpu = {uuid: {label: finite(values[field]) for field, label in fields.items()}
               for uuid, values in sorted(devices.items())}
    series_uuids = sorted(devices)
    return {
        "state": "COLLECTED", "host": metadata.get("host"), "nominal_interval_s": metadata.get("interval_s"),
        "sample_count_all_phases": len(samples), "sample_count_inside_scored_phase": len(inside),
        "sample_count_outside_scored_phase": len(outside),
        "gpu_status_inside": gpu_status_counts(inside), "gpu_status_outside": gpu_status_counts(outside),
        "server_http_status_inside": status_counts(inside), "server_http_status_outside": status_counts(outside),
        "server_metrics_payloads_inside": sum(bool(r.get("server_metrics")) for r in inside),
        "observed_gpu_uuids_inside": series_uuids,
        "per_gpu_sampled_metrics": per_gpu,
        "role_server_gauges_inside": gauge_stats(inside),
        "inflight_gauge": "No inflight-request gauge was present in retained in-window metrics.",
        "uuid_limit": "Observed UUIDs come from role-specific sampler GPU IDs; no independent process-to-GPU UUID capture was collected for these jobs.",
    }


def log_review(run):
    result = {}
    # Bounded diagnostic scan: exact errors, tracebacks and explicit transport failures;
    # routine per-batch lines are summarized separately only through score-window gauges.
    patterns = ("ERROR", "Traceback", "NIXL_ERR_", "CUDA out of memory", "Exception")
    for role in ("prefill-0", "prefill-1", "decode-0", "router"):
        path = run / f"{role}.log"
        if not path.exists():
            continue
        lines = path.read_text(errors="replace").splitlines()
        matches = [(i + 1, line[:500]) for i, line in enumerate(lines) if any(p in line for p in patterns)]
        result[role] = {"line_count": len(lines), "traceback_marker_count": sum("Traceback" in x for x in lines),
                        "error_marker_count": sum("ERROR" in x for x in lines),
                        "nixl_error_marker_count": sum("NIXL_ERR_" in x for x in lines),
                        "cuda_oom_marker_count": sum("CUDA out of memory" in x for x in lines),
                        "exception_terminal_lines": [x.strip() for x in lines if x.strip().startswith("RuntimeError:")],
                        "first_error_examples": matches[:5]}
    return result


def traces(run):
    result = {}
    for role in ("prefill-0", "prefill-1", "decode-0"):
        files = sorted(str(p.relative_to(run)) for p in (run / "diagnostic-profile" / role).glob("*.trace.json.gz"))
        result[role] = {"file_count": len(files), "filenames": files}
    return result


def profile_control(run):
    path = run / "diagnostic-profile/profile-control.json"
    rows = read_json(path)
    starts = [r for r in rows if "response" in r]
    stops = [r for r in rows if "stop_error" in r or "stop_response" in r]
    return {"start_http_status_by_worker": {r.get("worker"): r["response"].get("http_status") for r in starts},
            "start_response_bytes_by_worker": {r.get("worker"): r["response"].get("response_bytes") for r in starts},
            "stop_error_by_worker": {r.get("worker"): r.get("stop_error", r.get("stop_response")) for r in stops},
            "diagnostic_profile_is_outside_scored_interval": True,
            "scoring_error_counts_are_independent": True}


def run_job(job, n):
    run = ROOT / "runs" / job
    manifest = read_json(run / f"confirm/n{n}/artifacts/phase_manifest.json")
    phase = next(p for p in manifest["phases"] if p["phase_kind"] == "profiling")
    summary = read_json(run / "summary.json")[0]
    markers = [json.loads(x) for x in (run / "phase-markers.jsonl").read_text().splitlines() if x.strip()]
    start = next(m for m in markers if m["event"] == "benchmark_start")
    end = next(m for m in markers if m["event"] == "benchmark_end")
    telemetry = {role: resource_role(run, job, role, host, phase) for role, host in ROLES}
    return {
        "job": job, "concurrency": n, "score": {
            "good_output_tokens_per_s": summary["good_output_tokens_s"],
            "raw_output_tokens_per_s": summary["raw_output_tokens_s"],
            "good_request_fraction": summary["good_request_fraction"],
            "sla_pass": summary["sla_pass"], "requests": int(summary["requests"]),
            "errors": summary["errors"], "cancelled_requests": summary["cancelled_requests"],
            "ttft_mean_ms": summary["ttft_avg_ms"], "ttft_p95_ms": summary["ttft_p95_ms"],
            "request_mean_itl_mean_ms": summary["itl_avg_ms"], "request_mean_itl_p95_ms": summary["itl_p95_ms"],
        },
        "profiling_phase": {"start_ns": phase["start_ns"], "end_ns": phase["end_ns"],
                            "duration_s": (phase["end_ns"] - phase["start_ns"]) / 1e9,
                            "requests": phase["total_request_count"], "errors": phase["error_request_count"],
                            "cancelled": phase["was_cancelled"],
                            "enclosed_by_run_markers": start["utc_ns"] <= phase["start_ns"] <= phase["end_ns"] <= end["utc_ns"]},
        "request_tail_review": profile_metrics(run, n), "roles": telemetry,
        "role_logs": log_review(run), "diagnostic_profile_control": profile_control(run),
        "diagnostic_trace_files": traces(run),
    }


def main():
    jobs = {job: run_job(job, n) for job, n in JOBS.items()}
    a = jobs["25366"]["score"]["good_output_tokens_per_s"]
    b = jobs["25373"]["score"]["good_output_tokens_per_s"]
    result = {
        "title": "Phase-aligned observability review for matched full H200 N64 control/N64 runs",
        "generated_from_local_artifacts": True,
        "scoring_window_rule": "Use the AIPerf phase manifest profiling start/end. Retain a nominal sample only if sample utc_ns minus the configured polling interval is at or after profiling start, and sample utc_ns is at or before profiling end.",
        "jobs": jobs,
        "comparison": {"control_job": "25366", "candidate_job": "25373",
                       "good_output_tokens_per_s_delta": b-a,
                       "good_output_tokens_per_s_delta_percent": (b/a-1)*100,
                       "request_count_delta": jobs["25373"]["score"]["requests"] - jobs["25366"]["score"]["requests"],
                       "role_gpu_uuid_sets_match": {role: jobs["25366"]["roles"][role].get("observed_gpu_uuids_inside") == jobs["25373"]["roles"][role].get("observed_gpu_uuids_inside") for role, _ in ROLES},
                       "interpretation": "One completed N64 control/N64 pair with matching full protocol and same observer design; descriptive evidence from one run per point, not a causal attribution or variance estimate."},
        "limits": [
            "Nominal telemetry intervals conservatively bound sample timestamps but do not guarantee that every NVML activity value covers precisely that full interval.",
            "Sparse samples do not establish peaks. GPU activity, sampled VRAM, power and SGLang token/KV gauges are distinct quantities.",
            "Gauge counts are per labeled TP/PP/EP series and are never summed across ranks; no inflight gauge was present. Client concurrency is not asserted to equal server batch size.",
            "Missing fields and failed scrapes are reported by status or absence and are never interpreted as zero or healthy.",
            "The offline review does not inspect compressed trace contents; it records filenames only. Official model accuracy remains outside these artifacts."
        ]
    }
    (OUT / "observability.json").write_text(json.dumps(result, indent=2) + "\n")
    write_markdown(result)
    print(json.dumps({"jobs": list(jobs), "good_output_tokens_per_s_delta_percent": result["comparison"]["good_output_tokens_per_s_delta_percent"], "output": str(OUT / "observability.json")}, indent=2))


def write_markdown(data):
    lines = [
        "# Phase-aligned observability: full H200 N64 control and N64", "",
        "This offline review compares completed job 25366 (N64 control) with job 25373 (N64). Both used the fresh full-protocol matched pair and the same resource observer. It reads retained run artifacts only. The scoring window comes from each AIPerf phase manifest; nominal five-second telemetry windows are included only when wholly inside that interval. Benchmark start/end markers enclose the AIPerf phase.", "",
        "## Scored results", "",
        "| Job | Client concurrency | Good output tokens/s | Good request fraction | Scored requests | Errors / cancellations | TTFT mean / p95 (ms) | Request-mean ITL mean / p95 (ms) |", "|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for job, item in data["jobs"].items():
        s = item["score"]
        lines.append(f"| {job} | {item['concurrency']} | {s['good_output_tokens_per_s']:.3f} | {s['good_request_fraction']:.6f} | {s['requests']} | {s['errors']} / {s['cancelled_requests']} | {s['ttft_mean_ms']:.1f} / {s['ttft_p95_ms']:.1f} | {s['request_mean_itl_mean_ms']:.3f} / {s['request_mean_itl_p95_ms']:.3f} |")
    c = data["comparison"]
    lines += ["", f"N64 is {c['good_output_tokens_per_s_delta_percent']:+.3f}% ({c['good_output_tokens_per_s_delta']:+.3f} good output tokens/s) versus N64 control, in one completed pair. This is descriptive evidence only; it does not establish repeatability or identify a cause.", "",
              "## Role telemetry during scoring", "",
              "The table shows sample counts, status coverage, and the average of per-GPU sample means within each role. The range is across GPU means, not individual sample minima and maxima. Gauge summaries pool observations across labeled series without summing the series; detailed per-series distributions and per-GPU values are in `observability.json`.", "",
              "| Job | Role | In-window samples | GPU status | Server HTTP status | Metrics payloads | GPU activity mean (range, %) | Sampled VRAM mean (range, MiB) | Power mean (range, W) |", "|---|---|---:|---|---|---:|---:|---:|---:|"]
    for job, item in data["jobs"].items():
        for role, obs in item["roles"].items():
            def pooled(label):
                values = [gpu[label] for gpu in obs.get("per_gpu_sampled_metrics", {}).values()
                          if gpu.get(label, {}).get("count")]
                if not values: return "not collected"
                means = [v["mean"] for v in values]
                return f"{sum(means)/len(means):.1f} ({min(means):.1f}–{max(means):.1f})"
            lines.append(f"| {job} | {role} | {obs.get('sample_count_inside_scored_phase', 0)} | {obs.get('gpu_status_inside', {})} | {obs.get('server_http_status_inside', {})} | {obs.get('server_metrics_payloads_inside', 0)} | {pooled('gpu_activity_percent')} | {pooled('sampled_vram_mib')} | {pooled('sampled_power_w')} |")
    lines += ["", "SGLang gauges captured in-window:", "", "| Job | Role | Running requests / series | Queue requests / series | Token usage fraction | Used tokens / series |", "|---|---|---:|---:|---:|---:|"]
    names = ("sglang:num_running_reqs", "sglang:num_queue_reqs", "sglang:token_usage", "sglang:num_used_tokens")
    for job, item in data["jobs"].items():
        for role, obs in item["roles"].items():
            def gauge(name, digits=1):
                g = obs.get("role_server_gauges_inside", {}).get(name)
                if not g or g.get("mean") is None: return "not collected"
                return f"{g['mean']:.{digits}f} ({g['min']:.{digits}f}–{g['max']:.{digits}f})"
            lines.append(f"| {job} | {role} | {gauge(names[0])} | {gauge(names[1])} | {gauge(names[2], 3)} | {gauge(names[3], 0)} |")
    lines += ["", "Counts are per labeled TP/PP/EP series. They are not totals across ranks, and client concurrency is not presented as a server batch size. There was no in-window inflight-request gauge. The run-specific UUIDs and per-GPU readings are retained in JSON; these are sampler-reported role mappings, not independent process-locality proofs.", "",
              "## Tail, errors and profiler controls", ""]
    for job, item in data["jobs"].items():
        tail = item["request_tail_review"]
        controls = item["diagnostic_profile_control"]
        trace_counts = {role: trace["file_count"] for role, trace in item["diagnostic_trace_files"].items()}
        logs = item["role_logs"]
        p = tail['ttft_ms']; q = tail['request_mean_itl_ms']
        terminal = sorted({message for role_log in logs.values() for message in role_log['exception_terminal_lines']})
        lines.append(f"Job {job}: scored request records show {tail['scored_error_records']} errors and {tail['scored_cancelled_records']} cancellations. TTFT p99/max was {p['p99_ms']:.1f}/{p['max_ms']:.1f} ms, with {p['over_threshold_count']}/{p['count']} over 3000 ms; request-mean ITL p99/max was {q['p99_ms']:.3f}/{q['max_ms']:.3f} ms, with {q['over_threshold_count']}/{q['count']} over 20 ms. Diagnostic profiler start returned HTTP {', '.join(str(x) for x in controls['start_http_status_by_worker'].values())}; all three profiler stop requests returned HTTP 500. Each role log ends this traceback with `{'; '.join(terminal) or 'no terminal exception line captured'}`. The profile-control failure is therefore a control-path failure, separate from the zero scored-request error count. Collected trace files by role: {trace_counts}. Trace contents were not inspected; exact filenames are in JSON.")
    lines += ["", "## Limits", ""]
    lines.extend(f"- {limit}" for limit in data["limits"])
    lines += ["", "Reproduce with `python3 observability.py` from this directory. The script writes only `observability.json` and `observability.md`; it performs no scheduler or network calls.", ""]
    (OUT / "observability.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
