# Reversed forty-step confirmation reproduces the rank-density signal

Job **2294918 COMPLETED 0:0** on iris001 in **5,250 seconds**, 56 allocated CPUs. Root and independent read-only replay pass all 228 transferred hashes, native 40-step /39-interval outputs, fixed iterations, source/fields/payload checks before/after, runtime/library identities and correct 48/56-rank probes. This is a Basic practice result, not an official full-simulation score.

| Execution order | MPI ranks | Mean (s/step) | p95 nearest-rank (s/step) | Maximum (s/step) |
|---|---:|---:|---:|---:|
| B1 |48|27.534988582|28.342420324|28.503129112|
| A1 |56|32.528428090|41.251678169|41.424238026|
| A2 |56|32.232659866|40.368373174|40.454106741|
| B2 |48|24.783364839|25.598602671|26.808427478|

Pooled 48-rank mean is **26.159176710 s/step**, versus **32.380543978** for 56 ranks: **19.213288300% lower time**. Both label-matched adjacent contrasts favor 48 (15.3510% and 23.1110% lower). Reversing the execution order therefore preserves the direction. Within this job, candidate repeats change −9.9932% and controls −0.9093%; all slow timings remain included.

## What is now supported

| Allocation | Order | 56-rank pooled (s/step) | 48-rank pooled (s/step) | 48-rank time reduction |
|---|---|---:|---:|---:|
|2294916|56/48/48/56|32.322052535|26.703647651|17.382574569%|
|2294918|48/56/56/48|32.380543978|26.159176710|19.213288300%|

The 48-rank pooled mean changes only about −2.04% between allocations; 56-rank control changes +0.18%. This supports a repeatable **same-Iris, forty-step configuration improvement** for these Scotch partitions under opposite orders. Both allocations use the same physical node iris001. It is not a universal 18–19% gain, a longer-horizon result, a matched comparison against the teammate recipe, or an NSCC/Gadi forecast. Rank count and partition change together; no isolated communication or memory bottleneck is established.

## Correctness and telemetry

Same-partition force trajectories repeat exactly through all 40 rows. Cross-partition maximum Cd delta remains 0.004363602, recorded without an invented Basic equality gate. Source48 retains 896 core+13 ancillary hashes and 288 initialized fields; source56 has 1040+13 and 336. Native physical inputs and fixed work remain pinned; full convergence/official acceptance is not claimed by a forty-step practice run.

All 229/270/268/208 phase samples in execution order contain required memory, vmstat and frequency data. Median reported frequency is about 3,300 MHz for every arm. Minimum node available memory is 39.61/39.16/40.98/42.12 GiB respectively. Pressure files are unavailable; per-rank bandwidth, communication profiles, energy and solver-thread residency are not collected. GNU time RSS is a process peak, not summed MPI memory. Initial dynamic-code library lookup misses precede compilation and successful native End, not an established runtime failure. The independent reviewer finds no blocker.

## Cost and next hypothesis

Actual allocation cost is **81.666667 CPU-hours**, conservatively 82. Its 140-hour maximum retires once: **1,392 consumed /zero reserved /unchanged 1,450 internal stage**. Site-billed SU is unknown; NSCC/AI accounting is separate.

A distinct next candidate tests 40 ranks against the current 48-rank configuration, with the same original physical problem. Fewer ranks may reduce some overhead while increasing local work; the two 48-versus-56 successes do not predict a further win. First produce and validate a new Scotch40 cut, then mandatory initialization, then an equal-horizon matched solver comparison. Those stages need their own actual receipts and reviews. No blind repeats or automatic Codex schedules are enabled.

[Exact raw evidence and replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-reverse-20261105/completed-2294918).
