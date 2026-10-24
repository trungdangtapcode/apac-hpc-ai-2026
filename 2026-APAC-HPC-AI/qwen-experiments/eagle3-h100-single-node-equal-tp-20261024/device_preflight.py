#!/usr/bin/env python3
"""Record and validate the exact four-H100 slice assigned to one role."""
import json
import os
from pathlib import Path
import sys

role = os.environ["QWEN_ROLE_NAME"]
expected = {"prefill-0": [0, 1, 2, 3], "decode-0": [4, 5, 6, 7]}
assigned = [int(x) for x in os.environ.get("QWEN_ASSIGNED_GPU_INDICES", "").split(",") if x]
if role not in expected or assigned != expected[role]:
    raise SystemExit(f"FATAL: PBS GPU slice mismatch for {role}: {assigned}")
import torch
mask = os.environ.get("CUDA_VISIBLE_DEVICES", "")
if len(mask.split(",")) != 4 or torch.cuda.device_count() != 4:
    raise SystemExit(f"FATAL: {role} must see exactly four assigned CUDA devices")
devices = []
for index in range(4):
    prop = torch.cuda.get_device_properties(index)
    uuid = str(getattr(prop, "uuid", ""))
    if "H100" not in str(prop.name) or [int(prop.major), int(prop.minor)] != [9, 0] or not uuid:
        raise SystemExit(f"FATAL: {role} CUDA index {index} is not an identified H100/SM90")
    devices.append({"local_cuda_index": index, "uuid": uuid, "name": str(prop.name),
                    "compute_capability": [int(prop.major), int(prop.minor)],
                    "memory_bytes": int(prop.total_memory)})
if len({x["uuid"] for x in devices}) != 4:
    raise SystemExit(f"FATAL: duplicate H100 UUIDs within {role}")
out = Path(os.environ["QWEN_ARTDIR"]) / f"devices-{role}.json"
out.write_text(json.dumps({"role": role, "assigned_gpu_indices": assigned,
                           "cuda_visible_devices": mask, "devices": devices},
                          sort_keys=True, indent=2) + "\n")
print(f"ASSIGNED_FOUR_H100S_VERIFIED role={role} indices={assigned}", flush=True)
