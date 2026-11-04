# Iris Open MPI tiny-Allreduce qualification

## Question

On one exclusive 56-CPU Iris node under the GCC 11 and HPC-X 2.50 environment,
does forcing Open MPI `coll/tuned` recursive doubling (algorithm 3) reduce
`MPI_Allreduce` latency for 1- and 8-double payloads compared with the default
collective selection? This is an MPI microbenchmark qualification only. It does
not run OpenFOAM and cannot establish solver causality or solver performance.

The candidate is eligible for further consideration only if correctness passes,
`ompi_info` documents algorithm 3 as recursive doubling, the verbose candidate
probe establishes actual `tuned` selection, and every within-process block in
both adjacent ABBA contrasts shows at least 10% lower median and p95 worst-rank
latency for both payload sizes. The driver records a closed/unavailable result
otherwise. A result from this diagnostic does not authorize or imply a native
solver job.

## Measurement design

All four launches use the same compiled C binary, 56 MPI ranks, two payloads
(8 and 64 bytes), 100 warmups per payload, and two measured blocks of 1,000
calls per payload. Each rank times each call locally with `MPI_Wtime`. After
each measured block, ranks reduce their 1,000 per-call durations with `MPI_MAX`;
rank 0 writes per-block median and p95 plus the complete raw worst-rank latency
array. Correctness checks compare every result to the exact sum expected from
all 56 ranks.

Launch order is A1 default, B1 candidate, B2 candidate, A2 default. Each launch
has a 30-second timeout. Before measurement, short control and candidate probes
run a correctness-checked Allreduce with `coll_base_verbose=30`; separate raw
logs retain component-selection output. The probe only identifies the selected
collective component. It does not attribute a solver bottleneck.

The candidate flags are gated on `ompi_info --param coll tuned --level 9`
showing tuned Allreduce algorithm 3 as recursive doubling. Candidate flags:

```text
--mca coll tuned,basic,libnbc,self
--mca coll_tuned_priority 100
--mca coll_tuned_use_dynamic_rules 1
--mca coll_tuned_allreduce_algorithm 3
```

The driver records exact tool output and paths for `mpirun`, `mpicc`, `ompi_info`,
and `ucx_info` when available, plus tool hashes, binary hash, and source hashes
before and after execution. It does not infer the active PML from `ldd`.

## Resources and environment

The Slurm envelope is one exclusive Iris node, 56 CPUs, zero GPUs, low QoS, and
five minutes maximum. Setup follows the rank-memory qualification job: `gcc/11`,
`hpcx/2.50`, and the matching OpenFOAM environment initialization. No OpenFOAM
application is executed. Each of the four benchmark launches and each probe is
time bounded; the runner also has a 240-second outer timeout for cleanup margin.

Official Open MPI v5.0.x references:

- [Collective component selection and tuning](https://docs.open-mpi.org/en/v5.0.x/tuning-apps/coll-tuned.html)
- [Open MPI v5.0.x collective operations](https://docs.open-mpi.org/en/v5.0.x/tuning-apps/collectives/index.html)

## Files and interpretation

`microbench.c` is the common benchmark binary source. `job.sbatch` defines the
bounded runtime environment; `run.py` performs compile, capability gate,
probes, ABBA launch and threshold assessment. Raw launch logs and outputs live
under `runs/A1`, `runs/B1`, `runs/B2`, `runs/A2`, `runs/probe-control`, and
`runs/probe-candidate`. Tool transcripts, `qualifier-metadata.json`,
`probe-selection.json`, `launches.json`, `assessment.json`, and
`qualification.json` retain provenance and outcomes.

An unavailable component, unsupported flag, missing tuned selection evidence,
failed correctness, timeout, incomplete result, or insufficient matched benefit
must remain unavailable/closed; no score promotion is permitted. This prepared
payload has not been deployed or submitted. No scheduler job ID or measurement
is claimed here.
