#!/usr/bin/env python3
"""Offline structural and syntax checks; never launches MPI or Slurm."""
import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
c = (ROOT / "microbench.c").read_text()
py = (ROOT / "run.py").read_text()
sbatch = (ROOT / "job.sbatch").read_text()
readme = (ROOT / "README.md").read_text()
checks = {
    "56_ranks": "size != 56" in c and '"-np", "56"' in py,
    "correctness_checked_allreduce": "MPI_Allreduce" in c and "correctness" in c,
    "payload_counts_1_and_8": "{1, 8}" in c,
    "100_warmups_1000_calls_2_blocks": all(x in c for x in ("WARMUPS 100", "ITERATIONS 1000", "BLOCKS 2")),
    "per_call_worst_rank_raw_array": "MPI_MAX" in c and "raw_worst_rank_seconds" in c,
    "median_and_p95_threshold": "median_reduction_fraction" in py and "p95_reduction_fraction" in py and ">= 0.10" in py,
    "ABBA_order": all(x in py for x in ['("A1", [])', '("B1", CANDIDATE)', '("B2", CANDIDATE)', '("A2", [])']),
    "per_launch_30s_timeout": '], 30)' in py,
    "candidate_capability_and_selection_gates": "candidate_algorithm3_documented" in py and 'selected_component_observed") != "tuned"' in py,
    "resource_limits": all(x in sbatch for x in ("--exclusive", "--ntasks=56", "--gpus=0", "--time=00:05:00", "--qos=low")),
    "no_solver_command": "simpleFoam" not in sbatch and "foamRun" not in sbatch,
    "official_documentation_links": "docs.open-mpi.org/en/v5.0.x" in readme,
}
ast.parse(py)
failed = [name for name, passed in checks.items() if not passed]
for name, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'} {name}")
if failed:
    raise SystemExit(1)
