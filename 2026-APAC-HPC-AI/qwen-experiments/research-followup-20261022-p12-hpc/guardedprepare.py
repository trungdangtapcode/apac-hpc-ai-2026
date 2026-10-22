#!/usr/bin/env python3
"""Create mutable P8/D8 and P12/D4 short-screen drafts after read-only gates."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
QWEN = HERE.parent
TUNING = QWEN / "serving-tuning-10"
SOURCE = TUNING / "s21-dg8192-hpc-n60-control"
REVIEW = QWEN / "research-review-25365-20261022" / "REVIEW.json"
RUN_CONFIG = QWEN / "runs" / "25365" / "config.json"
DESTS = {
    "s32-h200-p8d8-current-n60-screen": {
        "p": 8, "d": 8, "pt": 4, "dt": 8, "ep": 8, "pw": 2,
        "placement": "prefill-0\t0\t4\t30100\t9000\nprefill-1\t0\t4\t30101\t9001\ndecode-0\t1\t8\t30200\t0\n",
    },
    "s33-h200-p12d4-hpc-n60-screen": {
        "p": 12, "d": 4, "pt": 4, "dt": 4, "ep": 4, "pw": 3,
        "placement": "prefill-0\t0\t4\t30100\t9000\nprefill-1\t0\t4\t30101\t9001\nprefill-2\t1\t4\t30102\t9002\ndecode-0\t1\t4\t30200\t0\n",
    },
}


def parse_placement(text: str) -> list[tuple[str, int, int, int, int]]:
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        cols = line.split()
        if len(cols) != 5:
            raise ValueError(f"placement row must have five columns: {line!r}")
        rows.append((cols[0], int(cols[1]), int(cols[2]), int(cols[3]), int(cols[4])))
    return rows


def validate_placement(text: str, expected_prefills: int, expected_decode_tp: int) -> None:
    rows = parse_placement(text)
    prefills = [r for r in rows if r[0].startswith("prefill-")]
    decodes = [r for r in rows if r[0].startswith("decode-")]
    if len(prefills) != expected_prefills or len(decodes) != 1:
        raise ValueError("role counts do not match the topology")
    if sum(r[2] for r in rows) != 16:
        raise ValueError("topology must use exactly 16 GPUs")
    if decodes[0][2] != expected_decode_tp:
        raise ValueError("decode TP does not match topology")
    if any(r[2] != 4 for r in prefills):
        raise ValueError("all prefill workers must use TP4")
    gpu_by_node: dict[int, int] = {}
    cpu_by_node: dict[int, int] = {}
    for _name, node, tp, _port, _bootstrap in rows:
        if node not in (0, 1):
            raise ValueError("placement node index must be 0 or 1")
        gpu_by_node[node] = gpu_by_node.get(node, 0) + tp
        cpu_by_node[node] = cpu_by_node.get(node, 0) + tp * 8
    if any(gpu_by_node.get(node, 0) > 8 for node in (0, 1)):
        raise ValueError("placement exceeds eight GPUs on a node")
    if any(cpu_by_node.get(node, 0) > 64 for node in (0, 1)):
        raise ValueError("placement exceeds 64 CPUs on a node")


def verify_source_manifest() -> None:
    manifest = SOURCE / "SHA256SUMS"
    if not manifest.is_file():
        raise RuntimeError("immutable source SHA256SUMS is missing")
    for line in manifest.read_text().splitlines():
        digest, rel = line.split(None, 1)
        path = SOURCE / rel.strip()
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            raise RuntimeError(f"immutable source checksum mismatch: {rel}")


def verify_review_gate() -> None:
    review = json.loads(REVIEW.read_text())
    actual = json.loads(RUN_CONFIG.read_text())
    if review.get("job") != "25365" or review.get("state") != "LOCAL_PROTOCOL_SLA_OUTPUT_PASS":
        raise RuntimeError("job 25365 does not have the required local review state")
    if review.get("full_scored_protocol_equal") is not True:
        raise RuntimeError("job 25365 scored protocol did not pass review")
    metrics = review.get("summary", {})
    if (metrics.get("sla_pass") is not True or metrics.get("errors") != 0
            or metrics.get("cancelled_requests") != 0):
        raise RuntimeError("job 25365 is missing an SLA/error gate")
    if review.get("long_context", {}).get("state") != "PASSED":
        raise RuntimeError("job 25365 long-context check did not pass")
    output = review.get("point", {}).get("short_output_comparison", {})
    if output.get("new_failed_cases"):
        raise RuntimeError("job 25365 has new short-output regressions")
    if (actual.get("id") != "P8-TP4_D8-TP8-EP8"
            or actual.get("prefill_workers") != 2
            or actual.get("decode_tp") != 8
            or actual.get("prefill_extra_flags") != ["--chunked-prefill-size", "8192", "--moe-runner-backend", "deep_gemm"]
            or actual.get("decode_extra_flags") != ["--flashinfer-allreduce-fusion-backend", "mnnvl", "--decode-attention-backend", "flashinfer", "--moe-runner-backend", "hpc_ops"]):
        raise RuntimeError("reviewed job 25365 is not the actual P8/D8 native DeepGEMM/HPC-Ops control")
    deltas = review.get("runtime_delta", {})
    if set(deltas) != {"prefill-0", "prefill-1", "decode-0"}:
        raise RuntimeError("job 25365 resolved role set is incomplete")
    if any(set(delta) != {"random_seed"} for delta in deltas.values()):
        raise RuntimeError("job 25365 runtime changed beyond the reviewed P8/D8 control")


def prepare() -> list[Path]:
    verify_source_manifest()
    verify_review_gate()
    for name, spec in DESTS.items():
        validate_placement(spec["placement"], spec["pw"], spec["dt"])
        if (TUNING / name).exists():
            raise RuntimeError(f"proposal ID already exists: {name}")
    proposals = HERE / "proposals"
    if proposals.exists() and any(proposals.iterdir()):
        raise RuntimeError("proposal output directory is non-empty; refusing overwrite")
    proposals.mkdir(exist_ok=True)
    made = []
    for name, spec in DESTS.items():
        out = proposals / name
        shutil.copytree(SOURCE, out)
        # Preserve the source digest inventory as provenance, not as a draft seal.
        (out / "SHA256SUMS").rename(out / "SOURCE_SHA256SUMS")
        config_path = out / "config.json"
        config = json.loads(config_path.read_text())
        config.update({
            "id": f"P{spec['p']}-TP4_D{spec['d']}-TP{spec['dt']}-EP{spec['ep']}",
            "prefill_gpus": spec["p"], "decode_gpus": spec["d"],
            "prefill_tp": 4, "decode_tp": spec["dt"], "decode_ep": spec["ep"],
            "prefill_workers": spec["pw"], "decode_workers": 1,
            "concurrency": [60], "phase": "screen",
            "screen_warmup_s": 20, "screen_measure_s": 40, "grace_s": 30,
            "confirm_warmup_s": 20, "confirm_measure_s": 40,
            "diagnostic_profile": False, "purpose": "Matched unranked current-stack N60 topology screen",
            "protocol": "Unranked short screen; closed-loop 4000/200; 20s warmup / 40s scored / 30s grace",
            "experiment": name, "screen_unranked": True, "walltime_minutes": 17,
            "control_job": "25365", "source_experiment": "s21-dg8192-hpc-n60-control",
            "changed_factor": ({"resource_split": "P8/D8 to P12/D4"} if spec["p"] == 12
                               else {"fresh_matched_screen_control": True}),
            "resource_monitor": True,
        })
        config_path.write_text(json.dumps(config, indent=2) + "\n")
        (out / "placement.tsv").write_text(spec["placement"])
        job_path = out / "job.sbatch"
        job = job_path.read_text()
        job = job.replace("#SBATCH -J ap42-s21-dg8192-hpc-n60-control", f"#SBATCH -J ap42-{name}")
        job = job.replace(f"export QWEN_BUNDLE={SOURCE}", f"export QWEN_BUNDLE={out}")
        job = job.replace("export QWEN_DIAGNOSTIC_PROFILE=1", "export QWEN_DIAGNOSTIC_PROFILE=0")
        job_path.write_text(job)
        bench_path = out / "benchmark.sh"
        bench = bench_path.read_text()
        bench = bench.replace('run_benchmark "$N" confirm 60 120', 'run_benchmark "$N" screen 20 40')
        bench = bench.replace("r['phase']=='confirm'", "r['phase']=='screen'")
        bench_path.write_text(bench)
        made.append(out)
    return made


if __name__ == "__main__":
    for path in prepare():
        print(f"DRAFT_PREPARED {path}")
