# Current HPC/OpenFOAM handoff

Updated 2026-10-21T10:28:44.088265+00:00. The owner explicitly requested research into the HPC task
and said another person supports AI. Earlier Qwen-only research scope is
superseded for this work. Existing AI jobs, payloads, submission and spending
rules are preserved; do not operate that worker's queue on their behalf.

The official public repository resolves to
b4df52907f5bbb9152ef6ae902c925fc79d54417. Rules and 177 selected public reference
files are retained under 2026-APAC-HPC-AI/hpc-experiments/upstream-20261021 with
Git blob identities and SHA256 provenance. These are organiser results, not
our own runs. Read the [research report](../reports/hpc-openfoam-20261021/README.md), [plan](../reports/hpc-openfoam-20261021/PLAN.md) and [technical evidence](../reports/hpc-openfoam-20261021/EVIDENCE.md). The derived analysis verifies 21 reference runs; these remain organiser measurements.

Read-only access confirms our existing helper reaches aspire2p.nscc.sg,
a2ap-login01, PBS pbs111 (ASPIRE-2A+ AI). It shows no matching openfoam/2512
module, no simpleFoam executable and no readable mesh at the documented CPU
path. This does not establish whether the separate ASPIRE-2A CPU service is
available to the same user/project. The owner confirmed having Iris or Gadi and supplied an SSH endpoint. Key permissions were corrected to 0600; login succeeds as rdmaworkshop30 on djau.10042008.xyz. Both ordinary and login shells return instance-20210305-2210, with no scheduler in PATH or expected Iris kit. Its local relay alias iris refers to itself. The actual next hop/compute service is still unconfirmed; clarification was requested. Do not use other users' relay account entries. No AI reauthentication, credential capture or DUO was triggered. The separately supplied key was used for the owner-authorised endpoint only; no key bytes are read or retained. Existing VPN/SSH remain running.

No HPC job, mesh download, large install, spending reservation or organiser
submission has occurred. HPC_Task remains empty pending actual evidence.
Autopilot remains off. Keep English artifacts and Vietnamese chat. Capture,
verify, commit and push small safe milestones to the existing archive.
