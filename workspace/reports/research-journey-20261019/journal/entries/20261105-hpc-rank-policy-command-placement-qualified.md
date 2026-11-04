# Where memory policy must be applied in this MPI launch

After the copy/hash-only performance branch lost its independent confirmation, the worker tested actual policy propagation with two bounded no-solver probes. 2294801 wrapped mpirun in numactl; all 56 rank policies remained default and each exact 8 MiB mapping occupied one NUMA node. 2294802 put numactl after mpirun in each rank; all 56 policies became interleave and each mapping had resident pages on both nodes (768/1280 or 1280/768 pages). Reported rank CPU affinity matched. Both jobs COMPLETED 0:0 in 2 seconds on 56 CPUs, 112 rank records and frozen hashes per job.

This rejects the assumption that outer-launcher policy reaches these MPI ranks; it does not identify exactly which runtime layer reset it. The in-rank form qualifies an interface and a first-touch mechanism. Python probe evidence is not a solver speed measurement or proof of OpenFOAM's allocations after exec. A distinct native design now needs actual pre-exec policy proofs and all full native work/source/runtime/force gates, with copy/hash policy held inherited.

Local synthetic-rank execution was unavailable because numactl is absent on the current login machine. That failure remains retained; actual Iris evidence supplies the qualification. Guard pages prevent silent mapping merges, and ambiguity fails. Each actual cost 0.031111 CPU-hours is conservatively 1; both maxima retired once, leaving 1,177 consumed /0 reserved /stage 1,210. No billed SU or AI/NSCC debit is invented.

[Actual mechanism and records](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-inprocess-policy-20261104/completed-2294802/RESULTS.md).
