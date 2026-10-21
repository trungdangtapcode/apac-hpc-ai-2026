# Current HPC/OpenFOAM handoff

Updated 2026-10-21T12:02:15.622475+00:00 after the reviewed 65M decomposition. The owner authorised HPC
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

## Active full-mesh practice

**2293752: COMPLETED / exit 0:0**, 161 seconds, iris031, one node / 56 allocated
CPUs / one serial task. Reviewed exact 56 processors, total 65,334,765 cells,
all six initial fields, immutable dictionaries, clean native logs and sealed
hashes. Batch MaxRSS 30.5284 GiB, TotalCPU 157.720 seconds. Max interface faces
93,343, 1,326,716 unique cut faces; no off-node traffic inference on one node.
[Review and evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-65m-20261021/STATUS.md).
No solver result or Cd exists yet. **2293753: COMPLETED / exit 0:0**, 103
seconds on iris031/56 ranks. All three native initialization logs, flags,
56-processor identity, READY and unchanged dictionaries pass the sealed
review. Batch MaxRSS 85.6927 GiB; mandatory stage clocks 9/71/8 seconds.
**2293754** accepted 13:45:14 UTC and its retained queue shows RUNNING on
iris031: frozen 04-simpleFoam, 56 MPI/40 steps/maximum 40 minutes. Collect
terminal solver log, coefficient.dat, step timing, invariants and accounting
before claiming a result. Keep at most one active
Iris practice allocation. Full mesh content hash and billed Iris SU remain
uncollected; no national CPU/GPU project reservation.

Iris is practice; scored 1/2/4-node runs belong to Gadi or CPU ASPIRE-2A.
Our existing ASPIRE-2A+ AI account does not establish CPU contest access.

## NSCC CPU access: authenticated

At 13:40 UTC an interactive password SSH login succeeds on asp2a-login-nscc02
through the existing VPN, without reauthentication or new DUO. A later reused
CPU SSH command succeeds. Prior password-free batch denials were not tests of
the password and are historical; do not claim the account is blocked.

CPU project **59000042** has a dated server ledger Grant 30000 / Used 222.154 /
Balance 29777.846 / In Doubt 0 SU, at reported 1 SU/core-hour. It is separate
from AI/H100 project 59010042; do not modify the AI ledger or payloads. Own CPU
queue is empty, openfoam/2512 exists and the official shared mesh is readable.
CPU **25904725.pbs101** is accepted at 13:53:14 UTC: native coded-timing
PitzDaily diagnostic, 8 CPUs/4 MPI/24 GB/no GPU/maximum 10 minutes and
1.333333 SU reserved under the separate CPU lock. First query already says
finished; collect historical accounting/logs before calling it a pass.
The first baseline wave planning ceiling is 100 SU; only the probe is reserved.
[Probe and budget](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-timing-probe-20261021/STATUS.md).
Read existing October 9–10 CPU artifacts in
scratch/apac2026/hpc before preparing a new baseline. [Proof and historical
correction](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-access-20261021/REPORT.md).

Helper: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/tools/nscc-cpu-ssh.sh.
It reuses the separate CPU master via the live VPN, using 10.103.72.110 with
HostKeyAlias=aspire2a.nscc.sg while local DNS remains unresolved. Keep all
private SSH/VPN state out of captures. The old gateway/batch/DNS observations
remain retained in the linked access report and raw safe probe JSON.
