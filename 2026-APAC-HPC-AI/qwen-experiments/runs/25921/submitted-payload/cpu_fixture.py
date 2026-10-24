#!/usr/bin/env python3
"""CPU-only structural checks; they do not emulate serving or GPU evidence."""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_mapping() -> dict:
    logical = 128
    physical = 130
    ep = 5
    per_rank = physical // ep
    mapping = list(range(logical)) + [i % logical for i in range(physical - logical)]
    require(len(mapping) == physical, "physical map length")
    require(mapping[-2:] == [0, 1], "duplicate IDs map to logical experts 0 and 1")
    local = [mapping[rank * per_rank : (rank + 1) * per_rank] for rank in range(ep)]
    require(all(len(items) == 26 for items in local), "each EP rank owns 26 slots")
    require(local[0][0:2] == [0, 1], "rank 0 replica source slots")
    require(local[4][24:26] == [0, 1], "rank 4 replica destination slots")
    return {
        "logical_experts": logical,
        "physical_experts": physical,
        "ep_size": ep,
        "local_slots_per_rank": [len(items) for items in local],
        "replica_physical_to_logical": {"128": mapping[128], "129": mapping[129]},
        "rank0_source_local_slots": [0, 1],
        "rank4_replica_local_slots": [24, 25],
    }


def check_worker_contract() -> dict:
    source = (HERE / "worker.sh").read_text()
    required = [
        "--dtype bfloat16", "--kv-cache-dtype bfloat16", "--tp-size 5",
        "--dp-size 5", "--enable-dp-attention", "--ep-size 5",
        "--moe-dp-size 1", "--ep-num-redundant-experts 2",
        "--ep-dispatch-algorithm dynamic", "--moe-a2a-backend none",
        "--moe-runner-backend hpc_ops", "--page-size 64", "--disaggregation-mode decode",
        "--disaggregation-transfer-backend nixl", "--cuda-graph-max-bs-decode 4",
        "http://127.0.0.1:$PORT/health",
    ]
    missing = [flag for flag in required if flag not in source]
    require(not missing, f"worker contract missing arguments: {missing}")
    require("/generate" not in source and "--prompt" not in source,
            "worker must not make user-output/generation requests")
    require("D5_OBSERVER_DIR" in source, "read-only observer is not wired into worker")
    require("device_preflight.py" in source and "headcheck.py" in source,
            "worker must run assigned-device preflight and independent readiness headcheck")
    require("nvidia-smi" not in source and "rg " not in source,
            "worker must not depend on external inventory/search binaries")
    require("--max-running-requests" not in source,
            "startup-only worker should not set an unneeded DP request cap")
    return {"required_worker_arguments_present": required, "generation_request_present": False}


def check_fail_closed_binding() -> dict:
    spec = importlib.util.spec_from_file_location("d5_prepare_check", HERE / "prepare_check.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    prerequisite_problems = module.check_root_binding()
    require(not prerequisite_problems, f"actual R3 prerequisite binding should verify: {prerequisite_problems}")
    original_here = module.HERE
    with tempfile.TemporaryDirectory(prefix="d5-unreviewed-binding-") as temp_dir:
        module.HERE = Path(temp_dir)
        (module.HERE / "ROOT_CANDIDATE_REVIEW_BINDING.json").write_text(json.dumps({"state": "WAITING_FOR_ROOT_CANDIDATE_REVIEW"}))
        review_problems = module.check_candidate_review_binding()
    module.HERE = original_here
    require(any("not accepted" in item for item in review_problems),
            "unreviewed D5 candidate must reject missing candidate/controller root review")
    result = subprocess.run([sys.executable, str(HERE / "prepare_check.py")], capture_output=True, text=True)
    expected_rc = 2 if module.check_candidate_review_binding() else 0
    require(result.returncode == expected_rc, "pre-submit guard must match actual candidate review state")
    return {
        "actual_r3_artifact_binding_verified": True,
        "unreviewed_candidate_binding_rejected": True,
        "guard_exit_code": result.returncode,
    }


def check_health_is_not_readiness() -> dict:
    spec = importlib.util.spec_from_file_location("d5_headcheck", HERE / "headcheck.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="d5-headcheck-cpu-") as temp_dir:
        out = Path(temp_dir)
        (out / "observer").mkdir()
        (out / "health.json").write_text('{"status":"ok"}\n')
        (out / "health-status.txt").write_text("HEALTH_HTTP=200\nHEALTH_READY_UTC=CPU_FIXTURE\n")
        (out / "devices.json").write_text(json.dumps({
            "status": "PASS_ASSIGNED_CUDA_DEVICES",
            "torch_cuda_device_count": 5,
            "devices": [{"uuid": f"CPU_FIXTURE_{i}"} for i in range(5)],
        }))
        (out / "model-header-preflight.json").write_text(json.dumps({
            "status": "PASS_HEADER_ONLY",
            "tensor_payload_read": False,
        }))
        try:
            module.validate(out)
        except ValueError as exc:
            require("no observer" in str(exc), f"unexpected headcheck refusal: {exc}")
        else:
            raise AssertionError("health-only input must never pass startup readiness")
    return {"health_only_readiness_rejected": True, "gpu_evidence": False}


def main() -> int:
    report = {
        "schema": "dp5-h200-readiness-cpu-fixture-v1",
        "scope": "CPU structural/source contract only; no SGLang import, CUDA, model load, health request, or scheduler action",
        "expert_map": check_mapping(),
        "worker_contract": check_worker_contract(),
        "fail_closed_binding": check_fail_closed_binding(),
        "headcheck": check_health_is_not_readiness(),
        "gpu_evidence": False,
        "serving_evidence": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
