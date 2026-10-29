#!/usr/bin/env python3
"""CPU-only fail-closed fixtures for the pre-AIPerf all-rank receipt gate."""

import json
from pathlib import Path
import tempfile

from check_compile_receipts import EXPECTED_NATIVE_SHA256, check

JOB_ID = "12345"
EXPERIMENT_ID = "compile-startup-fixture"
ROLE = "decode-0"


def gated_check(root):
    return check(root, expected_job_id=JOB_ID, expected_experiment_id=EXPERIMENT_ID,
                 expected_role=ROLE)


def receipt(rank):
    shapes = {}
    for n in range(50, 55):
        shapes[str(n)] = {
            "num_tokens": n,
            "compile_enabled_argument_seen": True,
            "compiled_callable_materialized": True,
            "callable_invocations": 1,
            "successful_cuda_graph_captures": 1,
            "dynamo_unique_graphs_positive": n == 50,
            "fxgraph_cache_positive": n == 50,
            "inductor_cache_positive": n == 50,
            "generated_kernel_positive": False,
        }
    return {
        "schema": "native-qwen-torch-compile-startup-observer-v1",
        "state": "COMPLETE",
        "rank": rank,
        "world_size": 8,
        "job_id": JOB_ID,
        "experiment_id": EXPERIMENT_ID,
        "role": ROLE,
        "distributed_initialized_at_hook": True,
        "native_source_sha256": EXPECTED_NATIVE_SHA256,
        "module_source_sha256": EXPECTED_NATIVE_SHA256,
        "shapes": shapes,
    }


def write_set(root, mutate=None):
    for rank in range(8):
        item = receipt(rank)
        if mutate:
            mutate(rank, item)
        (root / f"rank-{rank}-pid-{9000+rank}.json").write_text(json.dumps(item))


def assert_fail(label, mutate, expected):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_set(root, mutate)
        result = gated_check(root)
        assert not result["ready_for_aiperf"], (label, result)
        assert any(expected in error for error in result["errors"]), (label, result)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_set(root)
        result = gated_check(root)
        assert result["ready_for_aiperf"], result
    # Specifically omit rank 7 after constructing the ordinary full set.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_set(root)
        (root / "rank-7-pid-9007.json").unlink()
        assert "missing rank receipts" in " ".join(gated_check(root)["errors"])
    assert_fail("wrong shape", lambda rank, item: item["shapes"].pop("54") if rank == 3 else None,
                "shapes [54]")
    assert_fail("wrapper only", lambda rank, item: item["shapes"]["50"].update(
        callable_invocations=0, successful_cuda_graph_captures=0,
        dynamo_unique_graphs_positive=False, fxgraph_cache_positive=False,
        inductor_cache_positive=False), "shapes [50]")
    assert_fail("unproven counters", lambda rank, item: item["shapes"]["50"].update(
        dynamo_unique_graphs_positive=False, fxgraph_cache_positive=False,
        inductor_cache_positive=False, generated_kernel_positive=False), "compiler activity unproven")
    assert_fail("source mismatch", lambda rank, item: item.update(native_source_sha256="bad") if rank == 2 else None,
                "pinned-source receipt mismatch")
    assert_fail("stale job", lambda rank, item: item.update(job_id="old-job") if rank == 2 else None,
                "stale/missing Slurm job ID")
    assert_fail("wrong experiment", lambda rank, item: item.update(experiment_id="other") if rank == 2 else None,
                "stale/missing experiment ID")
    assert_fail("wrong role", lambda rank, item: item.update(role="prefill-0") if rank == 2 else None,
                "missing/wrong role")
    assert_fail("not distributed", lambda rank, item: item.update(distributed_initialized_at_hook=False) if rank == 2 else None,
                "not initialized")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_set(root)
        duplicate = receipt(0)
        (root / "rank-0-pid-9900.json").write_text(json.dumps(duplicate))
        assert "expected exactly one process receipt" in " ".join(gated_check(root)["errors"])
    print("PASS: gate accepts current complete evidence and rejects missing-rank, duplicate-rank, wrong-shape, wrapper-only, unproven-counter, source-mismatch, stale-job, wrong-experiment, wrong-role and non-distributed fixtures")


if __name__ == "__main__":
    main()
