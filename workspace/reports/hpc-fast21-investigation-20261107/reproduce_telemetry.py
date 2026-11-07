#!/usr/bin/env python3
"""Summarize retained Iris telemetry without modifying any run artifacts."""

import argparse
import hashlib
import json
import re
import statistics
from pathlib import Path


ARMS = {
    "B1-balanced48": 32.001684127615384,
    "A1-default48": 24.663577539410255,
    "A2-default48": 24.20099855576923,
    "B2-balanced48": 21.08590768471795,
}
VM_KEYS = (
    "numa_hit", "numa_miss", "numa_foreign", "numa_local", "numa_other",
    "numa_pages_migrated", "pgmajfault", "pgscan_kswapd", "pgscan_direct",
    "pgsteal_kswapd", "pgsteal_direct", "pswpin", "pswpout",
)
RESOURCE_KEYS = {
    "user_seconds": r"User time \(seconds\): ([\d.]+)",
    "system_seconds": r"System time \(seconds\): ([\d.]+)",
    "max_rss_kib": r"Maximum resident set size \(kbytes\): (\d+)",
    "major_page_faults": r"Major \(requiring I/O\) page faults: (\d+)",
    "minor_page_faults": r"Minor \(reclaiming a frame\) page faults: (\d+)",
    "voluntary_context_switches": r"Voluntary context switches: (\d+)",
    "involuntary_context_switches": r"Involuntary context switches: (\d+)",
    "filesystem_inputs": r"File system inputs: (\d+)",
    "filesystem_outputs": r"File system outputs: (\d+)",
}


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def proc_text_value(text, key):
    match = re.search(rf"^{re.escape(key)}:\s+(\d+)", text, re.MULTILINE)
    return int(match.group(1)) if match else None


def vmstat_value(vmstat, key):
    if isinstance(vmstat, dict):
        return vmstat.get(key)
    if isinstance(vmstat, str):
        match = re.search(rf"^{re.escape(key)}\s+(\d+)", vmstat, re.MULTILINE)
        return int(match.group(1)) if match else None
    return None


def resource_summary(path):
    text = path.read_text(errors="replace")
    result = {}
    for name, pattern in RESOURCE_KEYS.items():
        match = re.search(pattern, text)
        result[name] = float(match.group(1)) if match and "." in match.group(1) else int(match.group(1)) if match else None
    elapsed = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\S+)", text)
    result["elapsed_wall_clock"] = elapsed.group(1) if elapsed else None
    result["exit_status"] = int(re.search(r"Exit status: (\d+)", text).group(1)) if re.search(r"Exit status: (\d+)", text) else None
    return result


def snapshot_summary(path):
    data = json.loads(path.read_text())
    mem = data.get("meminfo", "")
    vm = data.get("vmstat", {})
    return {
        "utc": data.get("utc"),
        "scope": data.get("scope"),
        "collection_elapsed_ms": data.get("collection_elapsed_ms"),
        "memavailable_gib": round(proc_text_value(mem, "MemAvailable") / 1024 / 1024, 3) if proc_text_value(mem, "MemAvailable") is not None else None,
        "memfree_gib": round(proc_text_value(mem, "MemFree") / 1024 / 1024, 3) if proc_text_value(mem, "MemFree") is not None else None,
        "swap_total_kib": proc_text_value(mem, "SwapTotal"),
        "swap_free_kib": proc_text_value(mem, "SwapFree"),
        "node_cumulative_numa_miss": vmstat_value(vm, "numa_miss"),
        "node_cumulative_numa_foreign": vmstat_value(vm, "numa_foreign"),
        "node_cumulative_major_faults": vmstat_value(vm, "pgmajfault"),
        "node_cumulative_swap_out": vmstat_value(vm, "pswpout"),
        "pressure_memory": data.get("pressure/memory_error", "not collected"),
    }


def summarize_arm(root, arm, mean_s_step):
    p = root / "arms" / arm
    samples = jsonl(p / "telemetry-samples.jsonl")
    status = json.loads((p / "telemetry-status.json").read_text())
    n = len(samples)
    width = max(1, n // 5)

    def sample_block(rows):
        med_freq = [x["cpuinfo_frequency"]["median_mhz"] for x in rows if x.get("cpuinfo_frequency", {}).get("median_mhz") is not None]
        min_freq = [x["cpuinfo_frequency"]["minimum_mhz"] for x in rows if x.get("cpuinfo_frequency", {}).get("minimum_mhz") is not None]
        max_freq = [x["cpuinfo_frequency"]["maximum_mhz"] for x in rows if x.get("cpuinfo_frequency", {}).get("maximum_mhz") is not None]
        avail = [x["meminfo_kb"]["MemAvailable"] / 1024 / 1024 for x in rows if x.get("meminfo_kb", {}).get("MemAvailable") is not None]
        first_available = rows[0].get("meminfo_kb", {}).get("MemAvailable")
        last_available = rows[-1].get("meminfo_kb", {}).get("MemAvailable")
        return {
            "sample_count": len(rows),
            "sampled_cpuinfo_median_frequency_mhz_median": round(statistics.median(med_freq), 2) if med_freq else None,
            "per_sample_cpuinfo_median_frequency_mhz_min_max": [round(min(med_freq), 2), round(max(med_freq), 2)] if med_freq else None,
            "per_sample_cpuinfo_minimum_frequency_mhz_median": round(statistics.median(min_freq), 2) if min_freq else None,
            "per_sample_cpuinfo_maximum_frequency_mhz_median": round(statistics.median(max_freq), 2) if max_freq else None,
            "samples_below_2700_mhz_by_sample_median": sum(x < 2700 for x in med_freq),
            "node_memavailable_gib_median_minimum": [round(statistics.median(avail), 3), round(min(avail), 3)] if avail else None,
            "node_memavailable_gib_first_minimum_last": [round(first_available / 1024 / 1024, 3), round(min(avail), 3), round(last_available / 1024 / 1024, 3)] if avail and first_available is not None and last_available is not None else None,
        }

    first, last = samples[0], samples[-1]
    duration = last["timestamp_monotonic_seconds"] - first["timestamp_monotonic_seconds"]
    vm0, vm1 = first.get("vmstat_pages_or_events", {}), last.get("vmstat_pages_or_events", {})
    vm_delta = {}
    for key in VM_KEYS:
        if key in vm0 and key in vm1:
            delta = vm1[key] - vm0[key]
            vm_delta[key] = {"delta_node_counter": delta, "rate_per_second": round(delta / duration, 3) if duration > 0 else None}
        else:
            vm_delta[key] = {"state": "missing from one or more samples"}
    snapshots = {label: snapshot_summary(p / f"solver-{label}-node-snapshot.json") for label in ("before", "after")}
    proof = json.loads((p / "rank-proofs.json").read_text())
    rank_map = {str(x["rank"]): x.get("affinity_cpu_ids", []) for x in proof.get("proofs", [])}
    canonical_map = json.dumps(rank_map, sort_keys=True, separators=(",", ":")).encode()
    return {
        "mean_solver_time_s_per_step": mean_s_step,
        "telemetry": {
            "interval_seconds": status.get("interval_seconds"), "sample_count": n,
            "reported_scope": status.get("scope"), "sampler_returncode": status.get("stop", {}).get("returncode"),
            "first_sample_utc": first.get("timestamp_utc"), "last_sample_utc": last.get("timestamp_utc"),
            "sampled_duration_seconds": round(duration, 3),
            "all": sample_block(samples), "first_fifth": sample_block(samples[:width]), "last_fifth": sample_block(samples[-width:]),
            "whole_node_vmstat_delta_and_rate": vm_delta,
            "whole_node_snapshots": snapshots,
            "cpu_psi": "unavailable: /proc/pressure/cpu absent",
            "memory_psi": "unavailable: /proc/pressure/memory absent",
            "io_psi": "unavailable: /proc/pressure/io absent",
        },
        "resource_time": resource_summary(p / "resource-time.log"),
        "rank_proof": {
            "passed": proof.get("passed"), "hostnames": proof.get("hostnames"),
            "world_size": len(rank_map), "cpu_ids_by_rank": rank_map,
            "cpu_map_sha256": hashlib.sha256(canonical_map).hexdigest(),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-dir", type=Path, default=Path("/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-balanced48-only-20261107/completed-2295090/collected/runs/2295090"))
    parser.add_argument("--output", type=Path, help="Write JSON here; stdout if omitted.")
    args = parser.parse_args()
    arms = {arm: summarize_arm(args.result_dir, arm, mean) for arm, mean in ARMS.items()}
    output = {
        "schema": "hpc-fast21-telemetry-summary/v1",
        "source_job": 2295090,
        "run_directory": str(args.result_dir),
        "notes": [
            "CPU frequency, meminfo, vmstat and resource-time values are node/process aggregate observations as documented in each source; do not infer a process-level cause.",
            "Rates use first-to-last sampled node-global cumulative-counter deltas divided by monotonic sample span.",
            "The initial process rank proofs contain CPU affinity only, not NUMA memory residency.",
        ],
        "same_cpu_map_checks": {
            "B1_equals_B2": arms["B1-balanced48"]["rank_proof"]["cpu_map_sha256"] == arms["B2-balanced48"]["rank_proof"]["cpu_map_sha256"],
            "B1_cpu_ids_are_0_through_47": sorted(set(cpu for ids in arms["B1-balanced48"]["rank_proof"]["cpu_ids_by_rank"].values() for cpu in ids)) == list(range(48)),
            "B2_cpu_ids_are_0_through_47": sorted(set(cpu for ids in arms["B2-balanced48"]["rank_proof"]["cpu_ids_by_rank"].values() for cpu in ids)) == list(range(48)),
        },
        "arms": arms,
    }
    rendered = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
