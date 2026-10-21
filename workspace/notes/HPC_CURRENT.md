# Current HPC/OpenFOAM handoff

Updated 2026-10-21 after the verified Iris toy run. The owner authorised HPC
research and said another person supports AI. Preserve their serving payloads,
jobs and budget controls. English artifacts, Vietnamese chat; autopilot off.

## Actual access: resolved

Use an **interactive** SSH login to the supplied Iris gateway, with no remote
command. Its login shell automatically jumps into the cluster. Earlier remote
SSH commands ran on the gateway VM and missed that jump; the inference of a
missing next-hop account was premature. The organiser email supplied by the
owner resolved this. Do not ask again for a replacement endpoint merely because
a one-command SSH call has no scheduler. [Access and correction](../reports/hpc-openfoam-20261021/IRIS_ACCESS.md).

The verified cluster is login01.hpcadvisorycouncil.com, account rdmaworkshop30.
It has sbatch/srun/sinfo and the documented APAC kit. At 11:21:05 UTC Iris was
up with 32 nodes, 56 CPUs and 180000 MB advertised per node; 31 were idle in the
following allocation-state read. These are dated snapshots. Keep shared keys,
SSH caches and authentication material outside research/Git. Other relay
accounts are not used; existing AI VPN/SSH remain untouched.

Helper: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/tools/iris-interactive.sh.
Work root: /global/exafs/users/rdmaworkshop30/apac2026/tripleu-hpc-20261021T1121.
Kit copied only into that unique work root, not edited in the shared group tree.
Login-only native binary inspection passes. Never execute the Iris-optimized
solver ELFs on login CPUs: the kit documents SIGILL there; use Slurm compute.

## Actual first practice result

**2293751: COMPLETED / exit 0:0**, 30 seconds on iris031. One whole 56-CPU node,
four MPI ranks, requested maximum five minutes. The unchanged organiser
02-toy-stages.sbatch passes hierarchical and scotch in separate directories.
The reviewed ten stage logs, split identities, native v2512/scalar64, contiguous
10-step solver logs and sealed payload/evidence hashes pass. Both timing
confidence warnings remain retained. This is **toy motorBike**, not 65M DrivAer,
not Cd proof and not a contest score. Hardware telemetry was not collected.
[Review and sealed evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-practice-20261021/review.json).

Iris allocation is separate from NSCC/Gadi CPU/GPU accounts. No national project
reservation or GPU job was made. The prior statement that no HPC job existed
is historical: this first toy allocation is now complete. HPC_Task submission
folders remain empty because there is no scored 65M result yet.

## Retained research and next decision

[Research report](../reports/hpc-openfoam-20261021/README.md),
[plan](../reports/hpc-openfoam-20261021/PLAN.md),
[rules](../reports/hpc-openfoam-20261021/RULES.md),
[SSH/scheduler tutorial](../tutorial/hpc-openfoam-and-schedulers.md).

Official contest revision b4df52907f5bbb9152ef6ae902c925fc79d54417 is retained
with 177 public reference files; 21 independently parsed runs remain organiser
measurements, not ours. Exact case 84c262431117f5c921db8335e368a12d0e9fa3f0
is recovered from openfoam/community/hpc: 42 text files with Git blob and SHA256
provenance; 12 Basic text preparations pass static checks, not solver runs.

Next inspect the actual Iris 65M prep/solver scripts, input identity and memory/
scratch needs before one bounded complete Basic practice chain. Preserve each
new decomposition in its own directory and all mandatory initialization. Iris
is practice; scored 1/2/4-node runs belong to Gadi or CPU ASPIRE-2A. Our existing
ASPIRE-2A+ AI account does not establish access to either CPU contest project.
No full 65M job has been submitted at this checkpoint.
