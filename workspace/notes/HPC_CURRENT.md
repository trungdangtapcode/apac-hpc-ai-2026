# Current HPC/OpenFOAM handoff

Updated 2026-10-21T18:56:35.354784+00:00. **This is the HPC chat.** GPU/Qwen is owned by the separate
GPU chat. Read [session ownership](SESSION_OWNERSHIP.md). Preserve its jobs,
payloads, measurements and ledger; do not switch tracks from shared history.
English artifacts, Vietnamese chat, autopilot off. Keep HPC_Task empty until
actual reviewed deliverables support an authorised package update.

## Iris: full practice chain completed

Job **2293754: COMPLETED / exit 0:0**, hierarchical (7 4 2), iris031,
56 MPI ranks/40 steps. Average **21.9653538363 s/step**, p95 **22.541902 s**;
final Cd **0.4405543814** (dimensionless). Cut 2293752 and mandatory init
2293753 pass. All native/source/step/output gates, exact control expansion
and raw seals are reviewed. This is Iris practice, no contest score or matched
speedup. [Result, complete limits and reviewer](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-65m-20261021/STATUS.md).

Iris access requires forced-TTY SSH with no remote command; its gateway jumps
to login01 only for interactive login. Never run the optimized solver on login
CPUs. Helper: hpc-experiments/tools/iris-interactive.sh. Work root:
/global/exafs/users/rdmaworkshop30/apac2026/tripleu-hpc-20261021T1121.
All source scripts/processor trees stay frozen. Do not touch shared-account
other work. Full Iris mesh content hash and billed SU are not collected.

## ASPIRE-2A CPU: access and active baseline preparation

Interactive password SSH succeeds on asp2a-login-nscc02 through the existing
VPN without new DUO. CPU master reuse works. Earlier no-password batch denials
never tested the password and are historical. Local CPU hostname DNS fails;
the verified 10.103.72.110 route uses HostKeyAlias=aspire2a.nscc.sg. Keep all
private SSH/VPN state outside Git. Helper: hpc-experiments/tools/nscc-cpu-ssh.sh.
[Access proof and correction](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-access-20261021/REPORT.md).

CPU project **59000042** is distinct from H100 project **59010042**. The dated
CPU server ledger shows Grant 30000 / Used 222.154 / Balance 29777.846 /
In Doubt 0 SU at 1 SU/core-hour; refresh before spending. Native openfoam/2512,
CPU normal routing and the official shared mesh are verified. The first CPU
wave has a 100-SU planning ceiling and at most one active CPU allocation.

**25905006.pbs101: F / exit0**, 187 s (3 min 7 s), after about 3 min 43 s in
queue. Full official archive MD5/SHA256 and eight unpacked member hashes,
native v2512/DP, exact 128 partitions/65,334,765 cells and initial fields pass.
Batch MaxRSS 30.3228 GiB; estimated base charge 1.662222 SU is not posted billing.
[Review and sealed evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-baseline-headerfix-20261021/STATUS.md).
**25905114.pbs101: F / exit 0**, 728 s (12 min 8 s), x1001c2s5b1n0,
128 MPI, full mandatory initialization and 40 fixed-work solver steps.
Average **14.9219814004 s/step**, p95 **15.074989 s/step**, final Cd
**0.4389323284**. All reviewed native gates pass; one-node baseline only,
not a four-node score. MaxRSS 121.7611 GiB; estimated allocation 25.884444 SU.
No measured optimization gain yet. Placement probe interleaves; no hardware
counter or actual NUMA page-placement telemetry. Next native Scotch N128 and
a same-node method pair. [Review and evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-solve-h128-20261021/STATUS.md).
[Measured versus requested job durations](../reports/hpc-openfoam-20261021/JOB_DURATIONS.md).

Parent CPU lock/ledger: hpc-experiments/nscc-cpu-timing-probe-20261021/
cpu-budget.lock and cpu-budget.json. All five jobs are terminal and the CPU queue is empty at the review checkpoint.
Reported project Used 250.033 / Balance 29749.967 / In Doubt 0 SU. Delta
27.879 SU agrees with terminal allocation estimates 27.880 SU, but the site
report timestamp is inconsistent and individual posted charges are not known.
Conservative consumed planning ceiling is 29 SU, outstanding zero; unchanged
wave cap 100 SU. Schema 2 guards consumed + outstanding + new reservations.
Historical requested maxima are retired, preserved in each job's provenance.
No AI ledger or payload changes.

## Completed gates and preserved failures

- 25904725: F/exit1 after 2 s, module-reset shell boundary before solver; preserved.
- 25904765: F/exit0 after 84 s, native coded timing function compiles and all five
  toy steps pass on EPYC 7713/v2512/DP. Diagnostic only, no contest score.
- 25904959: F/exit1 after 16 s, comparison rejects one generated filename comment
  before mesh work. Exact normalization proves Iris control equivalence;
  derived 25905006 retains all other gates.
- Ten historical October 9–10 CPU run directories were discovered and sealed;
  none is accepted as a completed Basic baseline. Earlier templates alter
  fixedIter; later zero-step compiler-stop cause is not proven. Preserve them.

The [research log](../reports/hpc-openfoam-20261021/LOG.md) records full reasoning,
corrections and decisions. [Plan](../reports/hpc-openfoam-20261021/PLAN.md) and
[rules](../reports/hpc-openfoam-20261021/RULES.md) retain the pinned references.
Target 1/2/4 CPU nodes on ASPIRE-2A (or verified Gadi project), with 40/80/150
steps; final scored performance is the four-node Average, not Iris walltime.
Next compare native Scotch with the accepted hierarchical baseline on the same node.

Session-name verification at 2026-10-21T14:20:23.198933+00:00: read-only threads.name lookup matches
this environment's CODEX_THREAD_ID to the HPC conversation, and the GPU name
to another conversation. The earlier title-column/short-name lookup missed
renamed sessions; that limitation is historical. Shared routing now uses
CURRENT.md -> AI_CURRENT.md or HPC_CURRENT.md, with the explicit AGENTS map.

## Native Scotch followup submitted


25907236.pbs101 accepted at 2026-10-21T18:58:25.195600+00:00. Fresh native default Scotch N128, serial decomposition on 32 allocated CPUs, 96 GB, zero GPUs, maximum 15 minutes / 8 SU. Root: `/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-scotch128-20261021T185820Z`. Read PLAN.md for hypothesis, control, gates and conditional same-node pair. No candidate performance result yet. Submission intent, queue/accounting checks, exact deployment hashes and receipt are retained. No retry or budget increase.

Conservative consumed ceiling 29 SU plus this 8-SU outstanding reservation commits 37 / 100 SU. The conditional 29-minute pair would bring the maximum to 98.866667 SU, only after preparation passes and a fresh locked budget/queue check. Separate GPU queue inspected read-only: one own running job at submission; untouched.
