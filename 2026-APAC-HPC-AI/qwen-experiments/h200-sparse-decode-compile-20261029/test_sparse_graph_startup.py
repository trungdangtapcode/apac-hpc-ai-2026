#!/usr/bin/env python3
"""Synthetic CPU-only fixtures for the sparse-graph startup gate."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile

from check_sparse_graph_startup import GRAPH_BUCKETS, COMPILE_BUCKETS, check


JOB = "fixture-27383"
EXPERIMENT = "s108-fixture"
ROLE = "decode-0"


def build_fixture(root: Path, mode: str):
    receipts = root / "receipts"
    receipts.mkdir()
    for rank in range(8):
        shapes = {}
        for shape in GRAPH_BUCKETS:
            compile_on = mode == "compile" and shape in COMPILE_BUCKETS
            shapes[str(shape)] = {
                "num_tokens": shape,
                "compile_enabled_argument_seen": compile_on,
                "compiled_callable_materialized": compile_on,
                "callable_invocations": 1,
                "successful_cuda_graph_captures": 1,
                "dynamo_unique_graphs_positive": compile_on,
                "fxgraph_cache_positive": compile_on,
                "inductor_cache_positive": compile_on,
                "generated_kernel_positive": False,
            }
        path = receipts / f"rank-{rank}-pid-{rank+1000}.json"
        obj = {
            "schema": "native-qwen-torch-compile-startup-observer-v1",
            "state": "RUNNING",
            "receipt_path": str(path.resolve()),
            "job_id": JOB,
            "experiment_id": EXPERIMENT,
            "role": ROLE,
            "rank": rank,
            "world_size": 8,
            "distributed_initialized_at_hook": True,
            "observer_disabled_unix": 2,
            "observer_disabled_after_capture_shapes": list(GRAPH_BUCKETS),
            "native_source_sha256": "77b1e38dba14788800b6b6351af1b5b8a80d9e42b91b57e9484ea4561d33a48c",
            "module_source_sha256": "77b1e38dba14788800b6b6351af1b5b8a80d9e42b91b57e9484ea4561d33a48c",
            "installed_unix": 1,
            "updated_unix": 3,
            "shapes": shapes,
        }
        path.write_text(json.dumps(obj))
    config = {
        "decode_cuda_graph_batch_sizes": list(GRAPH_BUCKETS),
        "decode_torch_compile_max_bs": 56,
        "decode_enable_torch_compile": mode == "compile",
    }
    cfg = root / "config.json"
    cfg.write_text(json.dumps(config))
    bs = ", ".join(map(str, GRAPH_BUCKETS))
    log = root / "decode-0.log"
    log.write_text(
        "SPARSE_GRAPH_SOURCE_VERIFIED\n"
        + "server_args=ServerArgs(enable_torch_compile=" + str(mode == "compile")
        + ", torch_compile_max_bs=56, tp_size=8, ep_size=8, dp_size=1, "
        + "enable_dp_attention=False, disable_attn_tp_gather=False, "
        + "enable_two_batch_overlap=False, disable_cuda_graph_padding=False, "
        + "moe_a2a_backend='none', moe_dense_tp_size=None, max_running_requests=256, "
        + "cuda_graph_config=CudaGraphConfig(decode=PhaseConfig(backend='full', max_bs=64, bs=["
        + bs + "])))\n"
    )
    return receipts, log, cfg


def main():
    with tempfile.TemporaryDirectory(prefix="sparse-graph-fixture-") as td:
        root = Path(td)
        for mode in ("control", "compile"):
            case = root / mode
            case.mkdir()
            receipts, log, cfg = build_fixture(case, mode)
            got = check(receipts, log, mode, cfg, JOB, EXPERIMENT, ROLE)
            assert got["ready_for_aiperf"], (mode, got["errors"])
            # Independently replay from the immutable receipt directory.
            replay = check(receipts, log, mode, cfg, JOB, EXPERIMENT, ROLE)
            assert replay == got, (mode, "independent replay differs")

        candidate = root / "compile-missing"
        candidate.mkdir()
        receipts, log, cfg = build_fixture(candidate, "compile")
        first = next(receipts.glob("rank-0-*.json"))
        obj = json.loads(first.read_text())
        del obj["shapes"]["52"]
        first.write_text(json.dumps(obj))
        got = check(receipts, log, "compile", cfg, JOB, EXPERIMENT, ROLE)
        assert not got["ready_for_aiperf"] and any("bucket 52" in e for e in got["errors"])

        candidate = root / "compile-stale"
        candidate.mkdir()
        receipts, log, cfg = build_fixture(candidate, "compile")
        first = next(receipts.glob("rank-0-*.json"))
        obj = json.loads(first.read_text())
        obj["job_id"] = "old-job"
        first.write_text(json.dumps(obj))
        got = check(receipts, log, "compile", cfg, JOB, EXPERIMENT, ROLE)
        assert not got["ready_for_aiperf"] and any("job ID" in e for e in got["errors"])

    print(json.dumps({"state": "SYNTHETIC_FIXTURES_PASS", "cases": 4,
                      "graph_buckets": list(GRAPH_BUCKETS),
                      "compile_buckets": list(COMPILE_BUCKETS),
                      "gpu_or_torch_runtime_used": False}, indent=2))


if __name__ == "__main__":
    main()
