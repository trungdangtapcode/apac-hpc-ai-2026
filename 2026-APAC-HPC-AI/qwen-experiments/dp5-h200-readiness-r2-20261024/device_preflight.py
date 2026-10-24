#!/usr/bin/env python3
"""Validate and identify only CUDA devices exposed through the assigned mask."""

import json
import os
import sys


def main() -> int:
    import torch

    mask = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not mask or len(mask.split(",")) != 5:
        raise SystemExit("FATAL: expected exactly five scheduler-assigned CUDA_VISIBLE_DEVICES entries")
    count = torch.cuda.device_count()
    if count != 5:
        raise SystemExit(f"FATAL: torch sees {count} CUDA devices, expected exactly 5 assigned devices")
    devices = []
    uuids = []
    for index in range(count):
        prop = torch.cuda.get_device_properties(index)
        name = str(prop.name)
        uuid = str(getattr(prop, "uuid", ""))
        major, minor = int(prop.major), int(prop.minor)
        if "H200" not in name or (major, minor) != (9, 0):
            raise SystemExit(f"FATAL: assigned CUDA device {index} is {name} SM{major}{minor}, expected H200/SM90")
        if not uuid or uuid == "None":
            raise SystemExit(f"FATAL: CUDA device {index} UUID is unavailable")
        devices.append({
            "cuda_index": index,
            "name": name,
            "compute_capability": [major, minor],
            "uuid": uuid,
            "memory_bytes": int(prop.total_memory),
        })
        uuids.append(uuid)
    if len(set(uuids)) != 5:
        raise SystemExit("FATAL: assigned CUDA devices do not have five unique UUIDs")
    print(json.dumps({
        "status": "PASS_ASSIGNED_CUDA_DEVICES",
        "cuda_visible_devices": mask,
        "torch_cuda_device_count": count,
        "devices": devices,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
