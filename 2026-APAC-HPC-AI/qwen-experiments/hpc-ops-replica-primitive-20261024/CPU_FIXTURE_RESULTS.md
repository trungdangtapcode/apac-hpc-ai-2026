# CPU fixture result

**Result: PASS** for deterministic source/shape checks, run locally on 2026-10-24 with `python3 cpu_fixture.py cpu_fixture.json`.

The fixture reads the pinned trivial expert-slot implementation and HPC-Ops wrapper signatures, confirms 130 physical slots split evenly as 26 across each of five virtual ranks, confirms physical IDs 128 and 129 map to logical IDs 0 and 1, and checks route rows that exercise both base and replica IDs without selecting two physical copies of the same logical expert in one row.

This is Python source/shape evidence only. It does not execute the HPC-Ops kernel, CUDA, distributed routing, or a collective. See the exact fixture JSON in `cpu_fixture.json`.
