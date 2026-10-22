#!/usr/bin/env python3
"""Inspect sealed post-score GPU traces without changing benchmarks or launching jobs."""
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
JOBS = ("25365", "25366", "25373")
ROLES = {"prefill-0": 4, "prefill-1": 4, "decode-0": 8}
MAX_TRACE_BYTES = 128 * 1024 * 1024


def category(name):
    lower = name.lower()
    # Fused MNNVL RMSNorm includes normalization, not communication alone.
    if "nccl" in lower or "mnnvl_allreduce" in lower:
        return "collective_or_fused_collective_norm"
    if ("hpc" in lower and ("group_gemm" in lower or "fuse_moe" in lower or "activation" in lower)
            or "deep_gemm" in lower and re.search(r"\(deep_gemm::GemmType\)[12](?:,|>)", name)
            or "reorder_deepgemm" in lower or "ep_scatter" in lower):
        return "moe_associated"
    if "flashattn" in lower or "flash_attn" in lower or "flashinfer" in lower and (
            "pagedkvcache" in lower or "mergestates" in lower):
        return "attention_associated"
    if "quant" in lower:
        return "other_quantization"
    if "deep_gemm" in lower or "nvjet" in lower or "gemm" in lower:
        return "other_gemm"
    if "norm" in lower:
        return "other_normalization"
    return "other"


def interval_union_us(intervals):
    total = 0.0
    end = None
    for start, stop in sorted(intervals):
        if stop < start or not math.isfinite(start) or not math.isfinite(stop):
            raise ValueError("malformed kernel interval")
        if end is None or start > end:
            total += stop - start
        else:
            total += max(0, stop - end)
        end = stop if end is None else max(end, stop)
    return total


def sealed_bytes(path, manifest):
    row = manifest[str(path.relative_to(ROOT))]
    raw = path.read_bytes()
    if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
        raise ValueError(f"sealed evidence differs: {path}")
    return raw


def trace(path, manifest):
    compressed = sealed_bytes(path, manifest)
    import io
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        raw = stream.read(MAX_TRACE_BYTES + 1)
    if len(raw) > MAX_TRACE_BYTES:
        raise ValueError("trace exceeds 128 MiB decompression bound")
    data = json.loads(raw)
    events = [event for event in data["traceEvents"]
              if event.get("cat") == "kernel" and event.get("ph") == "X"]
    if not events:
        raise ValueError("trace has no complete GPU kernel events")
    devices = {event.get("args", {}).get("device") for event in events}
    if len(devices) != 1 or None in devices:
        raise ValueError("per-rank trace must identify exactly one kernel device")
    sums, names, counts = Counter(), Counter(), Counter()
    intervals = []
    for event in events:
        duration = event["dur"]
        if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration < 0:
            raise ValueError("invalid kernel duration")
        name = event["name"]
        sums[category(name)] += duration
        names[name] += duration
        counts[name] += 1
        intervals.append((event["ts"], event["ts"] + duration))
    total = sum(sums.values())
    span = max(end for _, end in intervals) - min(start for start, _ in intervals)
    union = interval_union_us(intervals)
    rank = int(re.search(r"-TP-(\d+)(?:-EP-|\.trace)", path.name).group(1))
    return {"trace": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(compressed).hexdigest(),
            "role": path.parent.name, "rank": rank, "device": next(iter(devices)),
            "kernel_events": len(events), "uncompressed_trace_bytes": len(raw),
            "summed_kernel_ms": total / 1000,
            "kernel_interval_union_ms": union / 1000, "first_to_last_kernel_span_ms": span / 1000,
            "kernel_union_fraction_of_trace_kernel_span": union / span,
            "category_fraction_of_summed_kernel_time": {key: value / total for key, value in sums.items()},
            "category_kernel_ms": {key: value / 1000 for key, value in sums.items()},
            "top_kernels": [{"name": name, "count": counts[name], "summed_ms": duration / 1000,
                             "category": category(name)} for name, duration in names.most_common(12)]}


def main():
    destination = OUT / "REVIEW.json"
    if destination.exists():
        raise FileExistsError("Preserve the existing offline review; use a new review directory")
    jobs = []
    for job in JOBS:
        run = ROOT / "runs" / job
        seal_path = run / "artifact-manifest.json"
        seal = json.loads(seal_path.read_text())
        if seal["job"] != job or seal["status_at_seal"]["State"] != "COMPLETED":
            raise ValueError("require retained completed-run seal")
        manifest = {row["path"]: row for row in seal["files"]}
        profile = run / "diagnostic-profile"
        protocol = json.loads(sealed_bytes(profile / "protocol.json", manifest))
        if (protocol["kind"] != "diagnostic-only" or protocol["concurrency"] != 48
                or protocol["trace_steps"] != {"prefill": 4, "decode": 32}):
            raise ValueError("unexpected diagnostic trace protocol")
        requests = json.loads(sealed_bytes(profile / "requests.json", manifest))
        control = json.loads(sealed_bytes(profile / "profile-control.json", manifest))
        traces, roles = [], {}
        for role, ranks in ROLES.items():
            paths = sorted((profile / role).glob("*.trace.json.gz"))
            rows = [trace(path, manifest) for path in paths]
            if len(rows) != ranks or {row["rank"] for row in rows} != set(range(ranks)):
                raise ValueError(f"incomplete trace ranks: {job}/{role}")
            categories = sorted({key for row in rows for key in row["category_kernel_ms"]})
            roles[role] = {"ranks": ranks,
                "category_fraction_mean_across_ranks": {key: statistics.mean(
                    row["category_fraction_of_summed_kernel_time"].get(key, 0) for row in rows)
                    for key in categories},
                "mean_trace_kernel_span_ms": statistics.mean(row["first_to_last_kernel_span_ms"] for row in rows),
                "mean_kernel_union_fraction_of_trace_span": statistics.mean(
                    row["kernel_union_fraction_of_trace_kernel_span"] for row in rows)}
            traces.extend(rows)
        jobs.append({"job": job, "seal_sha256": hashlib.sha256(seal_path.read_bytes()).hexdigest(),
                     "protocol": protocol, "diagnostic_requests": len(requests),
                     "successful_diagnostic_requests": sum(row.get("ok") is True for row in requests),
                     "profile_control": control, "roles": roles, "traces": traces})
        print("Inspected", job, len(traces), "sealed GPU traces", flush=True)
    result = {"state": "OFFLINE_DIAGNOSTIC_TRACE_REVIEW", "reviewed_utc": datetime.now(timezone.utc).isoformat(),
              "jobs": jobs, "gpu_allocations_added": 0, "pbs_su_added": 0,
              "classification": "Disjoint kernel-name heuristic; full names, durations and class assignments retained per rank. Fused collective+normalization remains one associated class.",
              "limits": ["N48 post-score diagnostic traffic, not N62/N64 scored workload or a matched batch sequence.",
                         "Kernel-duration sums can overlap; category fractions are not elapsed time or predicted speedup.",
                         "Per-rank first-to-last kernel union/span is diagnostic coverage, not sampled device utilization or full-job GPU busy time.",
                         "Prefill/decode capture 4/32 steps; absolute role totals are not comparable phase costs.",
                         "Names identify associated work; no critical-path, transfer latency, memory-bandwidth or causal bottleneck claim.",
                         "No official accuracy measurement or new serving configuration is established."]}
    destination.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
