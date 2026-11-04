# In-rank numactl applies policy and changes anonymous placement

2294802 COMPLETED0:0 in2seconds /56 CPUs. All120 collected files verify. Each arm has56 unique ranks with exact8MiB /2,048-page mapping accounting. Inherited ranks all report default policy and a wholly single-node mapping. Candidate ranks all report interleave policy and resident pages on both NUMA nodes. Observed splits are N0=768/N1=1280 or N0=1280/N1=768, not an asserted exact50/50 distribution. Reported affinity matches by rank across arms: True.

The changed form is `mpirun ... -- numactl --interleave=all python3 rank_probe.py`. Outer-launcher 2294801 left every observed rank at default policy. This qualifies placement of the policy-setting command inside the rank, without attributing the reset to a specific runtime component. No solver, model, page-cache preparation or performance score is measured. Python rank evidence is not an observation of OpenFOAM's allocations after exec; any native test must capture its own pre-exec rank policy and preserve exact work/output/runtime checks.

Actual allocated cost 0.031111 CPU-hours, conservatively 1. Retire 4.666667 reserved once under lock: 1,177 consumed /zero reserved /stage 1,210. A native hypothesis may now test in-rank solver policy with preparation held inherited and unchanged. No speedup is claimed by this diagnostic.
