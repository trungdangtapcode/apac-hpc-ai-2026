# HPC research milestone — 21 October 2026

**Question and prior evidence.** After clarifying that published R2/R5 requires
Basic work for both tasks, the owner requested HPC research and said someone
else supports AI. Earlier Qwen-only scope is superseded for this research.
No team HPC baseline or HPC submission evidence is available. Existing AI
jobs, payloads, spending controls and accepted results are preserved.

**Research and exact sources.** Main resolves to
b4df52907f5bbb9152ef6ae902c925fc79d54417. Freeze 177 selected public files with
Git blob verification and SHA256 provenance. Read the current rules/addendum
and Iris/Gadi/ASPIRE-2A application notes. Independently recompute 21 public
reference runs, including all measured step averages, final Cd and every
available partition's cell/interface consistency. Retain source-owner labels;
none are our jobs. Native OpenFOAM-v2512 tag resolves to
87ed40d256d22ea38fcc648dfc82a22162427b18; inspect pinned Scotch tree-coefficient
handling and its actual coefficient-reader path, with COPYING retained.

**Observations and units.** Four-node Gadi hierarchical/scotch averages are
2.379600/2.126043 seconds per step at 416 MPI ranks. ASPIRE-2A defaults give
3.414517/3.575991 at 512 ranks. Repeated ASPIRE Scotch spans about
3.191–3.576 seconds per step with the same coefficient.dat bytes. This is
observed run variation on different node sets, not a universal noise model.
ASPIRE hierarchical's cell imbalance is about 0.002% but worst-rank interface
faces are 119,912; Scotch has about 1.072% cell imbalance and 22,214 worst-rank
interface faces, with maximum neighbor count increasing 20→66. Global cut
faces do not establish off-node communication or a causal bottleneck.

**Assessment and hypothesis.** Prioritize a valid Basic baseline and native
hierarchical/scotch decomposition over random MPI/compiler sweeps. A first
distinct candidate keeps method scotch but sets domains/domainWeights to reflect
actual node/rank grouping. This is supported by pinned native code and F1's
chosen-method coefficient allowance. It is not method multiLevel, not a code
patch, and has no measured speedup yet. processorWeights takes precedence in
the implementation; verify actual parsing and placement before any benchmark.
Other hypotheses are ranked in PLAN.md, with matched controls and repetition.

**Costs and correctness.** Public split-chain Scotch 1/2/4-node examples total
about 217 SU on Gadi and 167 SU on ASPIRE-2A. These are historical costs, not our
reservations or available credit. Basic keeps double precision, fixed numerical
work, all preparation and function objects; GPUs are forbidden. Basic Cd is
a sanity check, not a universal ±0.5% gate. Apply F3's matched-baseline rule
only where required for Bonus, preserving its method-only exception. Keep
solver Average, total walltime and billed service units separate.

**Failed attempts and corrections.** Original/relocated case URLs could not
provide the full case; a sign-in page is not retained as source. An initial
native source parent-path lookup returned 404; the correct path was found and
retained without erasing that observation. A broad parser fatal-string match
was corrected before acceptance to exclude the ordinary trapFpe startup line.
Published ASPIRE default MPI teardown faults stay visible, not relabelled as
clean jobs; the official runtime remedies require matched site validation.

**Access.** Existing AI SSH reaches ASPIRE-2A+ and does not establish CPU
ASPIRE-2A access. The owner said they have Iris or Gadi, then supplied a key
path and endpoint. First SSH rejects 0644 key permissions; chmod 600 fixes it.
Both non-login and login-shell checks then return instance-20210305-2210,
with no scheduler in PATH and no documented Iris kit. A local relay alias iris
refers to that same endpoint, not proof of another compute service. Other
users' Gadi aliases are not used. Next-hop/real-cluster clarification is pending.
No private key contents, authentication state or host-key cache enters research.

**Next decision.** Obtain the genuine practice kit and our own contest project,
then validate the entire Basic chain on Iris before a bounded CPU campaign.
No HPC job, mesh download, install or reservation occurs here. Candidate JSONs
are explicitly unsubmitted. Keep HPC_Task empty until actual reviewed evidence
can support an authorised package update. Autopilot remains off.

**Preservation.** Initial source/access/scope checkpoint 88765a0 was pushed
before the derived analysis and plan. This milestone retains English readable
reports, native-source provenance, analysis code/results, candidate definitions
and access limitations in a second small checkpoint. Git and live origin are
verified; no sensitive SSH material is captured.

## Source recovery and preparation checkpoint — 2026-10-21T11:02:23.528287+00:00

The owner asked for progress. Rechecking the supplied endpoint confirms the earlier scheduler/kit limitation. An independent source search finds the correct migrated official namespace openfoam/community/hpc, exact commit 84c262431117f5c921db8335e368a12d0e9fa3f0. Recover 42 text files with Git blob/SHA256/mode provenance; no mesh. A new helper derives only allowed Basic text settings; 12 temporary platform/node/method combinations and overwrite rejection pass, with invariant inputs and Allrun syntax checked. No solver, Cd, CPU job or new performance claim follows. The old full-case access failure is now historical; the real compute-service route remains unresolved. [Details](CASE_RECOVERY.md).

## Access wording and available MCP check — 2026-10-21T11:08:18.606822+00:00

The owner asked whether Iris cannot be accessed, and explicitly requested using an available MCP route before asking again for connection details. Inspect the active tool catalog for Iris/HPC/SSH/remote-shell capabilities and the configured resource/template catalog: none exposes an Iris execution or connection route in this session. The standard local Codex configuration has no mcp_servers section names. This is a bounded observation about this session, not proof that no Iris connector exists elsewhere. No plugin installation, account connection or authentication change is attempted.

The precise answer remains: SSH authentication to the provided endpoint works, but access to the actual Iris scheduler/compute service has not been established. The last retained endpoint query returns instance-20210305-2210 without scheduler/kit. Do not say SSH itself failed, that Iris is down, or that another person cannot access it. No fresh CPU measurement or job submission follows from the catalog check. Earlier requests for next-hop information remain pending; do not repeat them as though the owner supplied no endpoint.

## Interactive gateway correction and practice preparation — 2026-10-21T11:25:54.739129+00:00

The owner supplied the organiser email: interactive login auto-jumps to Iris. Forced-TTY SSH without a remote command now verifies the real login01 hostname, scheduler clients, 32 Iris nodes and current APAC kit. Earlier remote-command SSH stayed on the gateway. The earlier inference that a next-hop credential was missing was premature. Authentication and scheduler submission are separate. Preserve gateway observations but mark their interpretation historical. Copy only the kit into a unique team work root; login binary inspection passes. Plan one unchanged toy job, one whole 56-CPU Iris node/four MPI ranks/maximum five minutes, no national CPU/GPU reservation. The toy is not the 65M score. [Exact route and gates](IRIS_ACCESS.md).

## First Iris submit receipt — 2026-10-21T11:27:45.117130+00:00

After verified kit hashes, successful login-only binary inspection and a fresh empty account queue/31 idle nodes, submit only the unchanged organiser toy gate. Slurm returns 2293751 and confirms RUNNING on iris031 with 56 allocated CPUs, four MPI ranks, maximum 300 seconds. This proves the account can submit and receive compute allocation. It is not completion, 65M equivalence or a contest score. No blind retry, group-tree edit, unrelated account job or national CPU/GPU spending reservation is involved. The next decision waits for the owned terminal result and actual toy logs.

## First native Iris toy review — 2026-10-21T11:30:34.133595+00:00

Job 2293751 is COMPLETED/exit 0:0, 30 seconds, 56 CPUs/one iris031 node, four MPI ranks. Download and seal only 26 text evidence artifacts, not processor meshes or authentication. All ten stage logs, both split identities, native v2512/scalar64 and ten contiguous solver steps pass. Retain timing-confidence warnings; tiny toy averages are not a 65M score, a causal speedup or Cd validation. Hardware telemetry and billed SU are uncollected. This establishes working interactive access, successful Slurm allocation and the native MPI/solver smoke gate. Continue next with actual 65M input/script inspection before a bounded practice chain; no new full case or national/GPU reservation is made in this question checkpoint.

## First full-mesh baseline submission — 2026-10-21T11:39:42.821636+00:00

**Question and evidence.** The owner requested progress. Toy 2293751 passes
native MPI/solver startup for hierarchical and Scotch. Iris has an empty shared
account queue and idle practice nodes. Inspect the actual three N56 kit scripts,
shared text case, binary mesh header, disk/quota and partition before allocating.
All 39 common retained text files exactly match pinned case 84c2624; two redundant
root property copies match constant/. The mesh header declares 65,334,765 cells;
a full content hash is not collected. The filesystem reports 16 TiB free, no
hard user quota and 180000 MB advertised memory/node. Other-platform serial
RSS is an estimate, not measured Iris use.

**Hypothesis/control/change.** Establish whether the full required Basic chain
works on Iris with the unchanged hierarchical (7 4 2), xyz, 56-rank example.
This is a validity baseline, not a performance optimization. Freeze cut/init/
solver payloads and the complete retained shared text before submit. Prioritize
one serial cut, then review before init, then review before 40-step solver.
One active Iris allocation; full planned maximum 75 node-minutes (70 physical
CPU-hours if all stages allocate 56 CPUs), no invented SU conversion and no
national CPU/GPU spending. Keep HPC_Task empty.

**Submission and observations.** Job 2293752 accepted at 11:38:43.233405 UTC;
subsequent retained scheduler read is RUNNING on iris031, one node, 56 allocated
CPUs and one serial task. Maximum 900 seconds for decomposition/restore only.
No completed 65M stage, solver Average (seconds/step) or Cd is claimed. An initial
hash guard used an unset local orchestration value and failed before sbatch;
corrected explicit SHA256 passes and only one successful submission exists.
A mistaken head on binary owner printed bounded binary bytes; metadata capture
uses a bounded binary read instead. Neither observation changes solver inputs.

**Assessment and next decision.** Inspect terminal accounting, decomposePar End,
exact 56 processors, total cells, method/factors and restore output before init.
Then review renumberMesh/potentialFoam/applyBoundaryLayer before the 40-step solve.
Retain all failures. CPU/NUMA/network telemetry and billed Iris SU are uncollected.
Iris timings will remain practice, not Gadi/ASPIRE contest scores. Details and
raw receipt: iris-65m-20261021/PLAN.md, input-review.json, cut-submission.json.

## DUO-connected CPU-cluster feasibility — 2026-10-21T12:01:27.523376+00:00

The owner asked whether the DUO-connected server can also submit the CPU task.
Separate VPN authentication, SSH cluster identity, PBS project permission and
contest hardware eligibility. Read-only existing SSH identifies a2ap-login01;
normal routes to aiq1/aiq2, no listed OpenFOAM module and no readable published
CPU mesh path. The official task names ASPIRE-2A standard EPYC 7713 nodes or
Gadi normalsr. Resolve the separate CPU hostname via the live AI login, then
reach its SSH handshake through the current VPN by IP. BatchMode has no usable
CPU SSH authentication; no password/OTP is attempted and no DUO session is
replaced. An AI-login-to-CPU socket probe times out, while the VPN-client route
works; a local hostname attempt fails DNS. These are different connection paths,
not proof that the CPU cluster or the VPN is down. Next establish CPU SSH and
check its actual project/queue before spending. No benchmark, qsub acceptance
or CPU project balance is claimed. Preserve exact safe probe JSON and official
references in nscc-cpu-access-20261021; no AI budget files or jobs changed.

## Reviewed full-mesh decomposition — 2026-10-21T12:02:15.622475+00:00

Collect and seal 36 safe text artifacts for 2293752, no processor meshes or
session material. Terminal accounting is COMPLETED/0:0, 161 s, 56 allocated
CPUs on iris031, one serial process; MaxRSS 30.528442 GiB, TotalCPU 157.720 s.
Require native v2512/scalar64, End, exact 56 processors, all expected initial
fields, total 65,334,765 cells and frozen dictionary equality. These gates pass.
Cells vary only 1,166,692–1,166,694. Worst partition interface faces 93,343,
max neighbors 14, sum of per-rank interfaces 2,653,432 equals twice the global
1,326,716-cut summary. The initial parser included that summary as a 57th
partition and correctly stopped; fix the parser to distinguish indented rank
records from the global summary, preserving this correction. No solver gain,
Cd or network bottleneck follows. Next use the frozen mandatory init script
on this verified split; one node/56 ranks/maximum 20 minutes. Hardware locality/
bandwidth counters and billed SU remain uncollected. Keep evidence and reviewer
in iris-65m-20261021 before submitting another allocation.

## Promotion to mandatory initialization — 2026-10-21T12:03:14.876130+00:00

After the sealed 2293752 review and its separate safe backup, recheck the
native cut log, exact processor set/cells, terminal predecessor, frozen init
hash, absent READY/receipt and empty account queue. Submit 03.2-init exactly
once: 2293753 accepted 12:02:36.204357 UTC; subsequent response is RUNNING on
iris031, one node/56 MPI/maximum 1200 seconds. This runs renumberMesh,
potentialFoam and applyBoundaryLayer with the official flags. No numerical
controls or shared source change. Preserve receipt before waiting for GPU-free
CPU work. Next inspect all mandatory logs, terminal exit and split READY stamp;
no solver performance/Cd or completed initialization is established yet.

## Mandatory initialization accepted — 2026-10-21T13:44:35.070969+00:00

On continue, reconnect through the documented interactive Iris jump; the prior
local PTY no longer exists. 2293753 is COMPLETED/0:0, 103 s, 56 CPUs/MPI on
iris031. Seal 40 safe text artifacts. Review native build/double precision,
all official command flags, clean End/no fatal, predecessor identity, exact
READY and invariant dictionaries. All pass. Stage clocks: renumber 9 s,
potential 71 s, boundary-layer 8 s. Batch MaxRSS 85.692703 GiB and TotalCPU
01:29:32 are accounting observations, not per-rank memory bandwidth/locality.
Default CuthillMcKee band/profile reductions and potential initialization
errors remain diagnostics, not performance gain or final Cd. Full binary
fields/mesh hashes, hardware counters and billed SU remain uncollected.
Next submit the frozen one-node/56-rank/40-step solver, maximum 40 minutes,
using the unchanged prepared tree and fresh solver job directory. No change to
AI work, source math, mesh, function objects or national allocation follows
from Iris practice. Preserve separate reviewed-init and submission checkpoints.

## First full Iris solver allocation — 2026-10-21T13:46:39.429175+00:00

After separately backing up accepted init evidence, confirm frozen 04 hash,
READY, clean terminal predecessor 2293753 and all three logs, plus empty shared
account queue. Submit exactly once: 2293754 accepted 13:45:14.589077 UTC, then
RUNNING on iris031, one node/56 MPI/40 steps, maximum 2400 seconds. This keeps
mandatory preparation intact and stores solve controls/logs in a fresh job
folder. No new split, mathematical change or national project expenditure.
Next inspect output/Cd/step timing and resource accounting; no completed result
or comparison is claimed at this definite receipt checkpoint.

## CPU password authentication resolves access — 2026-10-21T13:48:43.788755+00:00

The owner says continue. Use the existing VPN, offer the previously supplied
credential only to the interactive CPU SSH password prompt, and reach
asp2a-login-nscc02. No VPN restart/DUO trigger or credential capture. This
corrects the unresolved batch-authentication account: no password had been
tried there. A separate CPU master also passes hostname/date. Read-only CPU
checks verify project 59000042 (dated 30000/222.154/29777.846/0 SU ledger),
1 SU/core-hour, empty own queue, normal routing, v2512 module and readable
shared mesh. CPU scratch contains October 9–10 research; preserve its safe
text before more credit. Initial collector uses unsupported capture_output
on Python 3.6; correct to PIPE/universal_newlines, no solver affected. Future
CPU reservations use their own lock/ledger and remain separate from AI project
59010042. No qsub acceptance or CPU result follows from this access checkpoint.

## Recovered historical CPU failures — 2026-10-21T13:50:37.728604+00:00

Before new CPU spending, discover the account's existing October 9–10 work
under scratch/apac2026/hpc. Seal 500 safe text files and compare numerical
settings against the pinned case. Ten run directories are not accepted Basic
measurements: no retained completed simpleFoam Average/End, and earlier
fixedIter files contain unsupported twoStageGaussSeidel. Later official run
25740797 reaches all prep stages but its zero-step solver log ends at native
timing-function compilation. No terminal accounting/compiler stderr proves
why; do not invent timeout/OOM or compiler failure. Original author and
reasoning are unknown. Preserve every branch. The old wrapper also ignores
nonzero native exits after End, so do not reuse it. Next test the unchanged
mandatory coded timing function on a tiny native tutorial within a small CPU
reservation, then prepare a fresh Basic case only if valid. Full raw text and
machine-readable per-run assessment: nscc-cpu-history-20261021.

## First CPU submission receipt — 2026-10-21T13:55:08.870052+00:00

Freeze the native timing probe and hash-verify deployment in a new CPU scratch
root. Under the distinct CPU budget lock, refresh project report, verify empty
CPU queue and count the existing AI queue read-only against the combined cap.
Reserve maximum 1.333333 SU within the first 100-SU CPU planning envelope and
retain a pre-submit intent before qsub. Exactly one submission returns
25904725.pbs101 at 13:53:14.713064 UTC. Eight CPUs/four MPI/24 GB/zero GPU,
maximum 600 seconds. The first later qstat says already finished; collect -x
history and logs. This is actual CPU submission acceptance, not runtime success
or a contest score. No AI spend/job changes, guessed billing or blind retries.

## CPU environment gate failure reviewed — 2026-10-21T13:56:39.579439+00:00

25904725.pbs101 is F/exit 1, 2 s, 8 CPUs/zero GPUs. Seal submitted source,
output and selected history; no native solver or compiled timing library was
executed. Actual site resetmodule uses loadedmods=$(module list | grep -vi
Modulefiles) after purge. Under strict errexit/pipefail, the expected empty
grep result exits the sourced script before defaults reload. Output matches
that boundary. This is a reproducible shell setup mechanism, not proof of a
compiler or model failure. Derive guarded conditional sourcing and validate
modules/runtime; keep native case/timing/flags fixed. Estimated base charge
0.004444 SU is not individually posted billing; retain the 1.333333-SU maximum
until ledger reconciliation. No new full-case allocation or AI change.

## Guarded-reset probe receipt — 2026-10-21T13:59:19.042495+00:00

Back up the source-supported reset repair separately; hash-verify new root.
Under the existing CPU budget lock, refresh project/CPU queue, verify combined
own PBS cap via a read-only AI queue query and retain the old maximum. Reserve
another 1.333333 SU (combined 2.666667) before qsub. Exactly one submission
returns 25904765.pbs101 at 13:58:21.582798 UTC: same eight CPUs/four MPI/24 GB/
zero GPU/max600s, changed reset guard and job label only. A definite receipt
is not native compilation or solver success. Next collect the terminal gate;
no full-case submission, AI budget mutation or uncertain retry.

## Explicit conversation ownership — 2026-10-21T14:03:36.403934+00:00

The owner reaffirms two chats, GPU and HPC; this conversation owns HPC. Inspect
only local title/metadata, without importing another transcript. Exact GPU/HPC
labels are not exposed by the inspected local index, so do not claim a verified
UI mapping. Record owner-assigned roles, source/handoff routes and distinct
CPU/GPU project ledgers in SESSION_OWNERSHIP.md and shared AGENTS.md. Preserve
other-track work; a read-only queue/access check is not an instruction to run
GPU research. No Codex restart, fork, background schedule or auth-state capture.

## Native CPU timing gate accepted — 2026-10-21T14:05:47.616213+00:00

25904765.pbs101 F/exit0 in 84 s, 8 CPUs/4 MPI/no GPU. Seal 28 selected text
artifacts and the native compiled timing-library hash/size; no runtime binary
copied. Verify frozen payload/official function hashes, actual compile/load,
v2512/DP on EPYC 7713, five contiguous steps, End, Average and semantic PASS.
All pass. Retain toy 0.01407 s/step and sample-size warning as diagnostic only.
PBS mem800844KiB/cput117s/CPUpercent45 are coarse accounting, no hardware locality/
bandwidth proof. Estimated cost0.186667SU is not individually posted billing;
retain maxima under the CPU lock. Supported reset repair passes; historical
compile-stop cause is still unknown. Next fresh official N128 full-case prep,
separate from old unverified processor trees and within the 100-SU CPU plan.

## CPU full-case preparation receipt — 2026-10-21T14:13:03.137368+00:00

After the accepted native timing gate, freeze official hierarchical N128 (16 4 2)
case text and a bounded identity/preparation job. It also replays native Iris
control expansion before mesh I/O. Hash-verify a fresh root, check CPU project,
empty own CPU queue and combined PBS cap under the CPU lock, reserve8SU before
qsub. Exactly one receipt25904959.pbs101 at14:10:12.031377UTC:32CPUs/96GB/
serial1/zeroGPU/max900s. Total conservative maxima10.666667SU. No AI mutation.
Terminal history already shows F/exit1 after16s; retain evidence and inspect
before any repair. A definite submit is not a prepared split or CPU score.
