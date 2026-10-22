#!/usr/bin/env python3
"""Seal and replay completed short-screen evidence for H200 job 25371."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import collections
import csv
import hashlib
import importlib.util
import inspect
import json
import math
import os
import re
import sys
import subprocess

os.environ.setdefault("OMP_NUM_THREADS", "4")
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "runs/25371"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def seal_terminal_run():
    """First write to the raw run tree: immutable manifest after terminal state."""
    seal_path = RUN / "artifact-manifest.json"
    if seal_path.exists():
        return json.loads(seal_path.read_text())
    rows = list(csv.DictReader(subprocess.check_output(
        ["sacct", "-X", "-j", "25371", "-P", "--format=JobID,State%30,ExitCode,Elapsed,Start,End"],
        text=True).splitlines(), delimiter="|"))
    status = next((r for r in rows if r.get("JobID") == "25371"), None)
    if not status or status["State"] != "COMPLETED" or status["ExitCode"] != "0:0":
        raise RuntimeError(f"Job is not terminal-successful: {status}")
    files = [p for p in RUN.rglob("*") if p.is_file()
             and p.name not in {"summary.json", "artifact-manifest.json"}
             and "__pycache__" not in p.parts]
    files += [p for p in (ROOT / "runs/25371.out", ROOT / "runs/25371.err") if p.is_file()]
    payload = {
        "job": "25371", "sealed_utc": datetime.now(timezone.utc).isoformat(),
        "status_at_seal": {"state": status["State"], "exit": status["ExitCode"],
                            "elapsed": status["Elapsed"], "start": status["Start"], "end": status["End"]},
        "scope": "All terminal raw run evidence inventoried after successful completion; derived summary excluded",
        "files": [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha(p)}
                  for p in sorted(files)],
    }
    seal_path.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


def sealed_point(core, n):
    """Use the established strict validator, adapting only screen timing and path."""
    if not getattr(core, "_screen_validate_installed", False):
        source = inspect.getsource(core.validate_metrics)
        assert "[('warmup', 60, n), ('profiling', 120, n)]" in source
        source = source.replace("[('warmup', 60, n), ('profiling', 120, n)]",
                                "[('warmup', 20, n), ('profiling', 40, n)]")
        source = source.replace("zip(rows, (60, 120))", "zip(rows, (20, 40))")
        exec(compile(source, "<derived-25371-short-metric-review>", "exec"), core.__dict__)
        core._screen_validate_installed = True
    if not getattr(core, "_screen_point_installed", False):
        source = inspect.getsource(core.point)
        assert "f'confirm/n{n}/artifacts'" in source
        source = source.replace("f'confirm/n{n}/artifacts'", "f'screen/n{n}/artifacts'")
        exec(compile(source, "<derived-25371-screen-path-review>", "exec"), core.__dict__)
        core._screen_point_installed = True
    return core.point(ROOT, "25371", n)


def percentile(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    p = (len(xs) - 1) * q
    lo, hi = math.floor(p), math.ceil(p)
    return xs[lo] + (xs[hi] - xs[lo]) * (p - lo)


def summary(values):
    return {"count": len(values), "mean": sum(values) / len(values) if values else None,
            "min": min(values) if values else None, "max": max(values) if values else None}


KEEP = {"sglang:num_running_reqs", "sglang:num_queue_reqs", "sglang:token_usage",
        "sglang:num_used_tokens", "sglang:cache_hit_rate"}
GAUGE = re.compile(r"^(sglang:[^\{ ]+)(?:\{([^}]*)\})?\s+([-+0-9.eE]+)$")


def aligned_role(role, host, phase):
    path = RUN / f"resource-telemetry/{role}-{host}.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    meta = next(r for r in rows if r.get("kind") == "metadata")
    samples = [r for r in rows if r.get("kind") == "sample"]
    interval = int(float(meta["interval_s"]) * 1e9)
    inside = [r for r in samples if r.get("utc_ns") is not None
              and int(r["utc_ns"]) - interval >= phase["start_ns"]
              and int(r["utc_ns"]) <= phase["end_ns"]]
    outside = [r for r in samples if r not in inside]
    gpu_fields = {"utilization.gpu": "gpu_activity_percent", "utilization.memory": "memory_activity_percent",
                  "memory.used": "sampled_vram_mib", "power.draw": "sampled_power_w"}
    devices = {}
    for row in inside:
        if row.get("gpu_status") != "ok":
            continue
        for gpu in row.get("gpus", []):
            rec = devices.setdefault(gpu.get("uuid", "MISSING_UUID"), {k: [] for k in gpu_fields})
            for raw, values in rec.items():
                try:
                    values.append(float(gpu[raw]))
                except (KeyError, ValueError, TypeError):
                    pass
    per_gpu = {uuid: {label: summary(values) for raw, label in gpu_fields.items()
                      for values in [metrics[raw]]} for uuid, metrics in sorted(devices.items())}
    series = collections.defaultdict(lambda: collections.defaultdict(list))
    for row in inside:
        if row.get("server_http_status") != 200:
            continue
        for line in row.get("server_metrics", []):
            match = GAUGE.match(line.strip())
            if match and match.group(1) in KEEP:
                try:
                    series[match.group(1)][match.group(2) or ""].append(float(match.group(3)))
                except ValueError:
                    pass
    gauges = {name: {"unit_and_scope": ("fraction per labeled series" if name == "sglang:token_usage"
                                         else "raw gauge; do not sum across TP ranks"),
                     "series": {label: summary(values) for label, values in sorted(groups.items())}}
              for name, groups in sorted(series.items())}
    return {
        "state": "COLLECTED", "host": meta.get("host"), "nominal_interval_s": meta.get("interval_s"),
        "sample_count_all_phases": len(samples), "sample_count_inside_scored_phase": len(inside),
        "sample_count_outside_scored_phase": len(outside),
        "gpu_status_inside": dict(collections.Counter(str(r.get("gpu_status", "MISSING")) for r in inside)),
        "server_status_inside": dict(collections.Counter(str(r.get("server_http_status", r.get("server_metrics_status", "MISSING"))) for r in inside)),
        "observed_gpu_uuids_inside": sorted(devices), "per_gpu_sampled_metrics": per_gpu,
        "role_server_gauges_inside": gauges,
        "limits": "UUIDs were not independently mapped to role processes; host CPU and network counters are shared; missing values are not zero; no explicit inflight metric was found in retained telemetry.",
    }


def host_cpu_memory(phase):
    """Deduplicate shared host counters across role samplers before summarizing."""
    by_host = collections.defaultdict(dict)
    for path in (RUN / "resource-telemetry").glob("*.jsonl"):
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        meta = next((r for r in rows if r.get("kind") == "metadata"), {})
        interval = int(float(meta.get("interval_s", 0)) * 1e9)
        for row in rows:
            if row.get("kind") != "sample" or row.get("utc_ns") is None:
                continue
            if int(row["utc_ns"]) - interval >= phase["start_ns"] and int(row["utc_ns"]) <= phase["end_ns"]:
                by_host[meta.get("host", "UNKNOWN")][int(row["utc_ns"])] = row
    result = {}
    for host, indexed in sorted(by_host.items()):
        rows = [indexed[t] for t in sorted(indexed)]
        busy_percent = []
        for before, after in zip(rows, rows[1:]):
            a, b = before.get("node_cpu_jiffies"), after.get("node_cpu_jiffies")
            if not a or not b:
                continue
            delta = [int(y) - int(x) for x, y in zip(a, b)]
            total = sum(delta)
            idle = delta[3] + (delta[4] if len(delta) > 4 else 0)
            if total > 0:
                busy_percent.append(100 * (total - idle) / total)
        available_gib = [float(r["node_memory"]["MemAvailable_KiB"]) / (1024 ** 2)
                         for r in rows if r.get("node_memory", {}).get("MemAvailable_KiB") is not None]
        result[host] = {"unique_host_samples": len(rows),
                        "approx_system_cpu_busy_percent": summary(busy_percent),
                        "available_memory_gib": summary(available_gib),
                        "cpu_method": "Adjacent /proc/stat jiffy deltas; busy excludes idle and iowait; system-wide, approximate.",
                        "network_counters": "Collected in raw samples; per-interface traffic rates not derived."}
    return result


def observability(points):
    markers = [json.loads(line) for line in (RUN / "phase-markers.jsonl").read_text().splitlines() if line.strip()]
    by_n = {}
    for n in (64, 68):
        start = next(m for m in markers if m["event"] == "benchmark_start" and m["detail"] == ["screen", str(n)])
        end = next(m for m in markers if m["event"] == "benchmark_end" and m["detail"] == ["screen", str(n)])
        manifest = json.loads((RUN / f"screen/n{n}/artifacts/phase_manifest.json").read_text())
        phase = next(p for p in manifest["phases"] if p["phase_kind"] == "profiling")
        phase_batches = []
        for line in (RUN / "decode-0.log").read_text(errors="replace").splitlines():
            if "Decode batch," not in line:
                continue
            stamp = re.match(r"\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", line)
            batch = re.search(r"#running-req:\s*(\d+)", line)
            if not stamp or not batch:
                continue
            log_ns = int(datetime.strptime(stamp.group(1), "%Y-%m-%d %H:%M:%S")
                         .replace(tzinfo=timezone(timedelta(hours=8))).timestamp() * 1e9)
            if phase["start_ns"] <= log_ns <= phase["end_ns"]:
                phase_batches.append(int(batch.group(1)))
        raw = []
        lengths = collections.Counter()
        for line in (RUN / f"screen/n{n}/artifacts/profile_export.jsonl").read_text().splitlines():
            row = json.loads(line)
            if row.get("metadata", {}).get("phase_kind") != "profiling":
                continue
            raw.append(row)
            value = row.get("metrics", {}).get("output_sequence_length", {}).get("value")
            if value is not None:
                lengths[str(value)] += 1
        ttft = [float(r["metrics"]["time_to_first_token"]["value"]) for r in raw]
        itl = [float(r["metrics"]["inter_token_latency"]["value"]) for r in raw]
        errors = [r for r in raw if r.get("error") or r.get("errors")]
        roles = {role: aligned_role(role, host, phase) for role, host in
                 (("prefill-0", "g1"), ("prefill-1", "g1"), ("decode-0", "g4"))}
        by_n[str(n)] = {
            "profiling_phase": {"start_ns": phase["start_ns"], "end_ns": phase["end_ns"],
                                "duration_s": (phase["end_ns"] - phase["start_ns"]) / 1e9,
                                "requests": phase["total_request_count"], "errors": phase["error_request_count"],
                                "enclosed_by_run_markers": start["utc_ns"] <= phase["start_ns"] <= phase["end_ns"] <= end["utc_ns"]},
            "decode_batches_during_profiling": {"line_count": len(phase_batches),
                "min_running_requests": min(phase_batches) if phase_batches else None,
                "max_running_requests": max(phase_batches) if phase_batches else None,
                "unique_running_requests": sorted(set(phase_batches))},
            "request_tail": {"raw_records_by_phase": dict(collections.Counter(
                    json.loads(line).get("metadata", {}).get("phase_kind", "unknown")
                    for line in (RUN / f"screen/n{n}/artifacts/profile_export.jsonl").read_text().splitlines())),
                "scored_error_records": len(errors),
                "cancelled_records": sum(bool(r.get("metadata", {}).get("was_cancelled")) for r in raw),
                "ttft_ms": {**summary(ttft), "p95": percentile(ttft, .95), "p99": percentile(ttft, .99),
                            "over_3000_ms": sum(x > 3000 for x in ttft)},
                "request_mean_itl_ms": {**summary(itl), "p95": percentile(itl, .95), "p99": percentile(itl, .99),
                                         "over_20_ms": sum(x > 20 for x in itl)},
                "exported_output_sequence_length_counts": dict(sorted(lengths.items())),
                "limitation": "Exported lengths do not prove generated token IDs."},
            "roles": roles,
            "deduplicated_host_cpu_memory": host_cpu_memory(phase),
        }
    # Bounded log scan: decode batch and explicit graph/eager settings from decode role only.
    decode = (RUN / "decode-0.log").read_text(errors="replace")
    batch_lines = [line for line in decode.splitlines() if "Decode batch," in line]
    batches = [int(x) for line in batch_lines for x in re.findall(r"#running-req:\s*(\d+)", line)]
    explicit = [line.strip()[:500] for line in decode.splitlines()
                if re.search(r"max_running_requests|cuda graph|cuda_graph|Capturing batches", line, re.I)]
    logs = {}
    for role in ("decode-0", "prefill-0", "prefill-1", "router"):
        path = RUN / f"{role}.log"
        lines = path.read_text(errors="replace").splitlines()
        markers = [line.strip()[:500] for line in lines
                   if any(term in line for term in ("ERROR", "Traceback", "NIXL_ERR_", "CUDA out of memory", "RuntimeError:"))]
        logs[role] = {"line_count": len(lines), "traceback_marker_count": sum("Traceback" in l for l in lines),
                      "error_marker_count": sum("ERROR" in l for l in lines),
                      "nixl_error_marker_count": sum("NIXL_ERR_" in l for l in lines),
                      "cuda_oom_marker_count": sum("CUDA out of memory" in l for l in lines),
                      "examples": markers[:5]}
    control = json.loads((RUN / "diagnostic-profile/profile-control.json").read_text())
    starts = [r for r in control if "response" in r]
    stops = [r for r in control if "stop_error" in r or "stop_response" in r]
    traces = {role: sorted(p.name for p in (RUN / f"diagnostic-profile/{role}").glob("*.trace.json.gz"))
              for role in ("prefill-0", "prefill-1", "decode-0")}
    return {"method": "Two-screen phase alignment uses each AIPerf profiling manifest and the submitted sampler's 5-second interval; sample retained only when sample time minus interval is at/after phase start and sample time is at/before phase end.",
            "screens": by_n,
            "decode_runtime": {"batch_line_count": len(batch_lines), "observed_running_request_batch_min": min(batches) if batches else None,
                               "observed_running_request_batch_max": max(batches) if batches else None,
                               "unique_batch_sizes": sorted(set(batches)), "explicit_runtime_lines": explicit[:30],
                               "client_concurrency_is_not_actual_batch": True},
            "role_log_review": logs,
            "profile_control": {"start_http_status_by_worker": {r.get("worker"): r["response"].get("http_status") for r in starts},
                               "stop_error_by_worker": {r.get("worker"): r.get("stop_error", r.get("stop_response")) for r in stops},
                               "diagnostic_profile_outside_scored_interval": True,
                               "trace_contents_inspected": False},
            "diagnostic_trace_inventory": {role: {"file_count": len(files), "filenames": files} for role, files in traces.items()},
            "profile_limits": "Trace files were inventoried only. Profile start responses are checked independently from stop responses; HTTP 500 stop errors do not alter separately validated scored request results."}


def main():
    seal = seal_terminal_run()
    wave_spec = importlib.util.spec_from_file_location("wave10_review", ROOT / "serving-tuning-10/review-wave10.py")
    wave = importlib.util.module_from_spec(wave_spec)
    wave_spec.loader.exec_module(wave)
    base_spec = importlib.util.spec_from_file_location("base_n54_review", ROOT / "serving-tuning/review-n54.py")
    base_core = importlib.util.module_from_spec(base_spec)
    sys.modules[base_spec.name] = base_core
    base_spec.loader.exec_module(base_core)
    points = {str(n): sealed_point(base_core, n) for n in (64, 68)}
    long = wave.long_check(RUN)
    assert points['64']['normalized_protocol'] == points['68']['normalized_protocol']
    assert all(p['metrics']['sla_pass'] and p['short_output_comparison']['research_eligible']
               and not p['short_output_comparison']['new_failed_cases'] for p in points.values())
    assert long['state'] == 'PASSED', 'Long-context gate failed'
    gain = 100 * (points["68"]["metrics"]["good_tokens_s"] / points["64"]["metrics"]["good_tokens_s"] - 1)
    result = {
        "job": "25371", "reviewed_utc": datetime.now(timezone.utc).isoformat(),
        "state": "SHORT_LOCAL_PROTOCOL_SLA_OUTPUT_PASS", "terminal_state": seal["status_at_seal"],
        "sealed_files": len(seal["files"]), "manifest_sha256": sha(RUN / "artifact-manifest.json"),
        "points": points, "long_context": long,
        "within_job_gain_percent": gain, "one_percent_screen_gate": gain >= 1.0,
        "practical_one_percent_screen_gate": gain >= 1.0,
        "full_scored": False, "ranking_promotion_allowed": False, "accuracy_verified": False,
        "observability_file": "observability.json",
        "assessment": "Both short points pass local gates. " + ("Gain meets the 1% screen gate and justifies fresh full matched confirmation." if gain >= 1.0 else "Gain misses the 1% gate; withhold full followup.") + " Short fixed-order results are unranked.",
        "next_decision": "Prepare fresh full N64 control and N68 candidate after safe freeze and queue checks" if gain >= 1.0 else "Close this unchanged load step; no full followup",
    }
    (OUT / "REVIEW.json").write_text(json.dumps(result, indent=2) + "\n")
    obs = observability(points)
    (OUT / "observability.json").write_text(json.dumps(obs, indent=2) + "\n")
    print(json.dumps({"state": result["state"], "gain_percent": gain,
                      "scores": {n: p["metrics"] for n, p in points.items()},
                      "long_context": long.get("state"), "decode_batch": obs["decode_runtime"],
                      "files_sealed": len(seal["files"])}, indent=2))


if __name__ == "__main__":
    main()
