# Iris Scotch comparator at 56 ranks

## Question and prior evidence

The owner explicitly requested using **both NSCC CPU and Iris CPU** on 25 October. Existing Iris job 2293754 completed the full hierarchical (7 4 2) 65M chain at 56 ranks / 40 steps, mean 21.9653538363 s/step over 39 timings. It is an Iris practice result, not a scored NSCC result or a matched comparison to the newer NSCC 3.364622070 s/step. Different hardware and rank counts remain separate.

The old Iris validity chain is already complete; do not repeat the toy baseline. The next distinct hypothesis is whether a Scotch partition improves this same 56-rank workload. First produce and review a fresh Scotch cut in a unique own root, then initialize all mandatory stages, then make a matched hierarchical/Scotch solver comparison. Do not treat a fresh Scotch mean versus the three-day-old hierarchical mean as a controlled speedup.

## Reviewed first job

Derive the organizer's 13.1-cut script, preserving the Scotch 56-rank algorithm and native modules. Pin all 41 fetched source-case text files locally and in the job payload. Use only the existing group serial mesh; verify all 8 full-member SHA256 values against the retained official NSCC archive extraction before decomposition. Matching file sizes observed on login is not that proof. No mesh download or execution of optimized solver ELFs on a login CPU.

The job requests one exclusive 56-CPU Iris node, account rdmaworkshop / QOS low, 40 minutes: **37.333333 allocated CPU-hours maximum** under whole-node accounting. The new Iris branch has a bounded planning envelope of 224 allocated CPU-hours; charging in SU is not exposed, so no SU rate or balance is claimed. No NSCC SU is debited by this separate Slurm job. Keep one active own allocation per CPU cluster; this implements the owner's explicit two-cluster direction. NSCC's combined PBS cap 3 remains separate. Never cancel or alter other jobs under the shared Iris account.

Only serial decomposePar and restore0Dir run. Decomposition has a 30-minute timeout, mesh hashing 3 minutes, restore 90 seconds and validation 60 seconds within the 40-minute allocation. Refuse every existing artifact instead of deleting or accepting endpoint directories. Require exactly processor0–55, all restored fields, native v2512/scalar64/End/no fatal errors and native per-rank cells summing 65,334,765. Preserve source hashes before/after and ordinary CPU/resource metadata. No READY, parallel initialization, solver time, Cd proof or score is claimed by this cut stage.

## Next decision and evidence limits

If the mesh identity or native cut gate fails, preserve the full logs/artifact and inspect that failure before any retry. If it passes, review native/source/mesh/resource evidence and submit the required renumberMesh, potentialFoam and applyBoundaryLayer stage in a separately frozen derived job. A later solver retains 40 steps / 39 timings, fixed iterations and all numerical work; assess each cluster separately and retain failed branches. Shared-account charging, memory bandwidth, NUMA traffic and network counters are not collected by this cut.
