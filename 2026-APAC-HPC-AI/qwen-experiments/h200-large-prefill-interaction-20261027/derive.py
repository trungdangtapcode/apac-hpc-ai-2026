#!/usr/bin/env python3
"""Create two immutable H200 chunk-size payloads from frozen S72."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "serving-tuning-11/s72-h200-full-pgraph-breakable-capnative"
OUT = Path(__file__).resolve().parent.parent / "serving-tuning-11"
ARMS = {"s78-h200-full-chunk12288": 12288}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def derive(name: str, chunk: int, parent_sums_sha: str) -> dict:
    target = OUT / name
    if target.exists():
        raise SystemExit(f"refusing to overwrite existing output: {target}")
    shutil.copytree(SOURCE, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    cfg_path = target / "config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg.update({
        "experiment": name,
        "label": name,
        "study_arm": "prefill_chunk_size",
        "arm": "control",
        "prefill_chunked_prefill_size": chunk,
        "source_bundle": "serving-tuning-11/s72-h200-full-pgraph-breakable-capnative",
        "matched_pair": "Compare chunk12288 versus full HPC-Ops decode control26319 chunk8192; old24723 used auto decode and is retained as a losing different-backend observation.",
        "official_score_claim": False,
        "quality": "UNKNOWN_NOT_EVALUATED",
        "ranked": False,
        "speedup_claim": False,
    })
    write_json(cfg_path, cfg)

    worker = target / "worker.sh"
    worker_text = worker.read_text()
    old = "--chunked-prefill-size 8192"
    if worker_text.count(old) != 1:
        raise SystemExit(f"{name}: expected one frozen worker chunk argument")
    worker.write_text(worker_text.replace(old, f"--chunked-prefill-size {chunk}", 1))

    checker = target / "check-fast-runtime.py"
    checker_text = checker.read_text()
    old_expected = "common.update(chunked_prefill_size=8192,moe_runner_backend='deep_gemm',flashinfer_allreduce_fusion_backend='auto')"
    new_expected = "common.update(chunked_prefill_size=cfg['prefill_chunked_prefill_size'],moe_runner_backend='deep_gemm',flashinfer_allreduce_fusion_backend='auto')"
    if checker_text.count(old_expected) != 1:
        raise SystemExit(f"{name}: checker source differs from reviewed S72 spelling")
    checker.write_text(checker_text.replace(old_expected, new_expected, 1))

    job = target / "job.sbatch"
    job_text = job.read_text()
    old_path = "/serving-tuning-11/s72-h200-full-pgraph-breakable-capnative"
    if job_text.count(old_path) != 1:
        raise SystemExit(f"{name}: expected one frozen QWEN_BUNDLE identity")
    job_text = job_text.replace(old_path, f"/serving-tuning-11/{name}", 1)
    job_text = job_text.replace("ap42-s72-full-bre", name[:15], 1)
    job_text = job_text.replace("s72-h200-full-pgraph-breakable-capnative-${SLURM_JOB_ID}", f"{name}-${{SLURM_JOB_ID}}", 1)
    job.write_text(job_text)

    (target / "README.md").write_text(
        f"# {name}\n\nPrepared H200 full N64 prefill chunk-size arm ({chunk}). Read the paired plan at `../../h200-large-prefill-interaction-20261027/PLAN.md`. This payload is not yet submitted and has no GPU result.\n"
    )
    (target / "PLAN.md").write_text(
        f"# {name}\n\nThis is one arm of the matched full N64 H200 chunk-size bracket. It uses chunk size {chunk}; all other runtime and workload settings are frozen from S72. See `../../h200-large-prefill-interaction-20261027/PLAN.md` for evidence, gates, limitations, and pair interpretation. No result is claimed.\n"
    )

    derivation = {
        "schema": "h200-prefill-chunk-full-derivation-v1",
        "bundle": f"serving-tuning-11/{name}",
        "parent_bundle": "serving-tuning-11/s72-h200-full-pgraph-breakable-capnative",
        "parent_sha256sums_sha256": parent_sums_sha,
        "changed_serving_factor": {"prefill_chunked_prefill_size": chunk},
        "worker_flag": f"--chunked-prefill-size {chunk}",
        "checker_expectation": "Read expected chunk from config.json; require exact match with each prefill ServerArgs record.",
        "graph_geometry": "Native runtime-generated geometry; checker requires complete breakable graph capture on every prefill rank and does not force another chunk's bucket sizes.",
        "all_other_frozen_payload_files_copied": True,
        "source_payload_config_sha256": sha256(SOURCE / "config.json"),
    }
    write_json(target / "DERIVATION.json", derivation)
    sums = subprocess.run(
        ["bash", "-lc", "find . -maxdepth 1 -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS"],
        cwd=target, check=True,
    )
    subprocess.run(["sha256sum", "--check", "SHA256SUMS"], cwd=target, check=True, stdout=subprocess.DEVNULL)
    return {
        "bundle": str(target.relative_to(ROOT)),
        "chunk": chunk,
        "files": len(list(target.glob("*"))),
        "sha256sums_sha256": sha256(target / "SHA256SUMS"),
    }


def main() -> None:
    subprocess.run(["sha256sum", "--check", "SHA256SUMS"], cwd=SOURCE, check=True, stdout=subprocess.DEVNULL)
    parent_sums_sha = sha256(SOURCE / "SHA256SUMS")
    results = [derive(name, chunk, parent_sums_sha) for name, chunk in ARMS.items()]
    print(json.dumps({"state": "DERIVED_NOT_SUBMITTED", "bundles": results}, indent=2))


if __name__ == "__main__":
    main()
