#!/usr/bin/env python3
"""CPU-only source/shape fixture for 128 logical experts replicated into 130 slots."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "pinned-source/sgl-workspace/sglang/python/sglang/srt"
LOGICAL = 128
PHYSICAL = 130
EP = 5


def main() -> None:
    location = (SOURCE / "eplb/expert_location.py").read_text()
    hpc_wrapper = (SOURCE / "layers/moe/moe_runner/hpc_ops.py").read_text()
    hpc_api = (
        ROOT
        / "hpc-package/usr/local/lib/python3.12/dist-packages/hpc/fuse_moe.py"
    ).read_text()

    # Guard this fixture against drifting away from the retained implementation.
    assert "def append_trivial_expert_slots(" in location
    assert "new_slots % num_logical_experts" in location
    assert "def fuse_moe_blockwise(" in hpc_api
    assert "rank_ep" in hpc_api and "num_expert_total" in hpc_api
    assert "global_num_experts" in hpc_wrapper and "moe_ep_rank" in hpc_wrapper

    physical_to_logical = list(range(LOGICAL)) + [0, 1]
    assert len(physical_to_logical) == PHYSICAL
    assert physical_to_logical[-2:] == [0, 1]
    shards = [physical_to_logical[i * (PHYSICAL // EP) : (i + 1) * (PHYSICAL // EP)] for i in range(EP)]
    assert all(len(shard) == 26 for shard in shards)
    assert [shard[0] for shard in shards] == [0, 26, 52, 78, 104]
    logical_to_physical = {
        logical: [physical for physical, value in enumerate(physical_to_logical) if value == logical]
        for logical in range(LOGICAL)
    }
    assert logical_to_physical[0] == [0, 128]
    assert logical_to_physical[1] == [1, 129]
    assert all(logical_to_physical[i] for i in range(LOGICAL))

    # Fixed rank-invariant route fixture: one physical copy per logical route per row.
    logical_rows = [[0, 1, 127, 64], [0, 1, 127, 64], [0, 1, 127, 64], [0, 1, 127, 64]]
    physical_rows = []
    for row_id, row in enumerate(logical_rows):
        physical = []
        for expert in row:
            if expert == 0 and row_id % 2:
                expert = 128
            elif expert == 1 and row_id % 2 == 0:
                expert = 129
            physical.append(expert)
        assert len(set(physical)) == len(physical)
        assert [physical_to_logical[e] for e in physical] == row
        physical_rows.append(physical)
    assert {128, 129}.issubset({expert for row in physical_rows for expert in row})
    assert {0, 1, 127}.issubset({expert for row in logical_rows for expert in row})

    result = {
        "status": "PASS",
        "scope": "CPU shape/source fixture only; not HPC-Ops execution, CUDA, or a distributed all-reduce.",
        "logical_experts": LOGICAL,
        "physical_experts": PHYSICAL,
        "ep_size": EP,
        "physical_slots_per_virtual_rank": [len(shard) for shard in shards],
        "physical_to_logical_tail": physical_to_logical[-4:],
        "logical_expert_0_copies": logical_to_physical[0],
        "logical_expert_1_copies": logical_to_physical[1],
        "logical_route_rows": logical_rows,
        "global_physical_topk_rows": physical_rows,
    }
    print(json.dumps(result, indent=2))
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
