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
Terminal history already shows F/exit1 after 16 s; retain evidence and inspect
before any repair. A definite submit is not a prepared split or CPU score.

## Native control comparison correction — 2026-10-21T14:14:00.577900+00:00

25904959 F/exit 1 after 16 seconds, 32 CPUs, stops before mesh work. Seal 113
text files including both native expanded dictionaries. Their only diff is
one generated header filename comment. Normalize exactly those known header
strings (each appears once); all remaining expanded bytes are identical.
This proves the intended Iris control semantics after startFrom/endTime edits,
while the CPU validator's whole-file diff was overstrict. Do not hide the failed
scheduler state or call it full CPU preparation. Estimated base 0.142222 SU is
not posted billing; retain 8 SU maximum. Derive only header normalization;
retain every other gate. Future conditional init+solve uses 35 minutes at128
cores (74.666667 SU) to keep all conservative maxima under the100-SU plan.

## Corrected CPU preparation receipt — 2026-10-21T14:16:41.461114+00:00

Separately back up the precise metadata comparison repair, deploy fresh root
and verify every payload hash. Under the CPU lock refresh balance/CPU queue
and read-only combined PBS capacity, retain prior maxima and reserve 8 SU.
One qsub returns 25905006.pbs101 at 14:15:25.657039 UTC. Same 32 CPUs, 96 GB,
one serial process, zero GPUs and maximum 900 s; target decomposition remains
128 ranks. Combined retained maxima 18.666667 SU, plus conditional later
128-CPU/35-minute solve 74.666667 SU gives 93.333334 SU below the 100-SU plan.
No AI work or budget changes. Next inspect actual mesh identity and prep
outputs; submission alone is not a CPU baseline. The full initialization
chain is still required after a valid cut.

## First full Iris practice baseline reviewed — 2026-10-21T14:18:22.145997+00:00

2293754 COMPLETED/0:0 in 925 s on iris031, 56 MPI ranks and 40 contiguous
steps, preceded by accepted cut/init 2293752/2293753. Seal 54 text artifacts;
independently verify mean and all 39 timing rows against native logs. Average
21.9653538363 s/step, median 21.965798 s, p95 22.541902 s, final Cd 0.4405543814.
Every step uses 15 iterations for each U component, 12 for p and 8 for omega/k.
Retain seven omega bounding messages; no fatal or sample-size warning. Batch
MaxRSS 133.3636 GiB and TotalCPU 14:11:24 are accounting, not hardware counters.
Iris full mesh content identity and billed SU are uncollected. Iris is practice,
not the scored four-node CPU site and not a measured optimization speedup.

Native CPU dictionary replay proves all expanded control bytes match except
one generated filename comment. All coded bodies and other system files match.
Initially reject nonempty stderr; it is exactly the two native assignment
echoes, so permit only those entries. A first large PTY transfer truncates and
fails base64 decoding before extraction; successful bounded chunks match the
full remote archive SHA256. Preserve these validation corrections without
changing raw solver data. Next prioritize the submitted ASPIRE CPU baseline
25905006 over another Iris timing sweep. No GPU research, AI changes or
submission-package edits. Full reasoning/evidence in iris-65m-20261021.

## Named-session verification corrected — 2026-10-21T14:20:23.198933+00:00

The GPU worker publishes the separate named-session routing map without
changing this worker's results. Recheck only local threads.name metadata:
current CODEX_THREAD_ID matches the HPC name; GPU is a different conversation.
The earlier lookup used database title and exact short names, so its failure
to expose labels was a lookup limitation, now historical. Do not import other
transcripts. CURRENT is a shared routing index and AI_CURRENT is the GPU-owned
handoff. Correct the shared ownership note to assign by role, not declare every
reader HPC; keep all GPU sources/queues/ledger untouched. Selected safe backup
is separate from the already retained HPC run evidence.

## CPU preparation accepted and duration explanation — 2026-10-21T14:33:21.810477+00:00

The owner asks progress and minutes per job. Fresh history shows 25905006
F/exit0, 187 seconds, versus 900 seconds requested; queue wait about 223 seconds.
Seal 162 selected text files and independently review hashes, native DP/build,
128 partitions and total 65,334,765 cells, full official archive/member identity,
unchanged dictionaries and field gates. All pass. MaxRSS 30.3228 GiB, CPU time 155 s,
CPUpercent 71 are coarse accounting; no hardware bandwidth/locality inference.
Estimated base 1.662222 SU is not separately posted charging; retain the maximum.
Explain actual runtime, requested cap and queue separately in JOB_DURATIONS.md.
Iris solver took 925 s and the full split chain 1189 s; no direct site speedup is
claimed. Next independently freeze a 128-rank full init+40-step solve capped at
35 minutes within the existing 100-SU envelope. No GPU research or AI mutation.

## Full CPU baseline admission and backup recovery — 2026-10-21T14:38:48.997415+00:00

Accepted preparation justifies a fresh native N128 full initialization and
40-step solver, keeping fixedIter, schemes, precision and function objects.
Freeze the source and validate syntax. Check the CPU ledger/project, empty
own CPU queue and combined PBS cap under the dedicated lock. Reserve maximum
74.666667 SU; retained whole-wave maxima are 93.333334 SU below 100 SU. One
qsub returns 25905114.pbs101 at 14:35:53.856665 UTC. The 14:37:48 UTC snapshot
is Q in qdev: one exclusive node, 128 CPUs/ranks, 440 GB, zero GPU, maximum
2100 seconds. No complete CPU result or site speedup is claimed.

Two concurrent shared Git operations interrupt the earlier review/plan backup:
first an index lock, then the staged-path scope assertion. Captures are safe;
inspect all pending paths and recover the two already verified captures as
separate path-scoped commits, preserving other staged work and existing history.
Both are pushed before closing this checkpoint. Adopt serialized selected-path
HPC checkpoints; never delete another process's Git lock or sweep mixed work.
The definite job receipt and current budget are retained even though the backup
recovery completed after submission. No scheduling retry or data loss occurs.

## Pending solver: actual queue restriction — 2026-10-21T14:48:23.781917+00:00

At the owner's status checkpoint, query actual CPU PBS history/state and the
scheduler comment plus qdev configuration. 25905114 remains Q; no native solver
has started and no new result exists. PBS explicitly reports the queue-wide
ncpus limit. qdev max_run_res is 256 cores across all users; 148 are assigned,
leaving 108 versus the requested 128. At least 20 assigned cores must be
released to fit this particular cap. Five queue jobs are running; do not infer
their completion times or claim an ETA. Approximately 12 min 30 s queue delay
is distinct from the prospective 35-minute execution cap. Preserve position
and reservation; the queue is not empty and the one-active-CPU cap prevents
another independent allocation. No blind retry, spending increase, alternate
queue request or GPU-track mutation. Retain exact safe reason/configuration
JSON and dated handoff; collect native logs when the actual job becomes terminal.

## 2026-10-21T18:56:35.354784+00:00: first accepted ASPIRE CPU baseline and accounting


Job **25905114.pbs101** finished F / exit 0 on x1001c2s5b1n0, with 128 MPI ranks, native OpenFOAM v2512 and double precision. All three mandatory initialization stages and 40 fixed-work simpleFoam steps pass the retained reviewer. This is a one-node baseline, not the four-node/150-step contest score.

| Quantity | Observed value |
|---|---:|
| Native Average, 39 measured steps | 14.9219814004 s/step |
| Median / p95 | 14.920225 / 15.074989 s/step |
| Final Cd | 0.4389323284, dimensionless |
| Whole allocation | 728 s = 12 min 8 s |
| Batch maximum RSS | 121.7611 GiB |
| Estimated base allocation charge | 25.884444 SU |

Renumber, potential, boundary and solver native clocks were 9, 49, 5 and 643 seconds respectively. All 40 steps used fixed iterations U=15, p=12, omega/k=8. Eight omega bounding messages are retained; no timing confidence warning. Review includes every stage's End/exit, source identities, architecture, steps, native timer data, force output and accounting. `review.py` reproduces `review.json`; raw text is sealed under collected/25905114.pbs101.

Aggregate CPU time is 25:01:24, 96.673% of allocated core-seconds. This does not identify a bandwidth, MPI, cache or NUMA bottleneck. GNU time wraps the PALS launcher; its 0% CPU must not be interpreted as solver inactivity. The placement probe saw all ranks and CPU masks 0–127 but interleaved lines prevent reconstructing per-rank mapping. NUMA masks are permissions, not page placement. Hardware counters, bandwidth, power and page locality were not collected. A derived probe should emit one atomic record per rank outside solver timing.

The public one-node hierarchical value is 14.668759 s/step; our single run is about 1.726% slower. This is not a matched comparison or proof of a cause. Native Scotch is the next distinct hypothesis: test graph partitioning while retaining fixed physics and numerical work. A same-node H→S pair reduces host differences, with order/cache/repetition limits reported explicitly.

CPU accounting now reports Used 250.033 SU, an amount delta of 27.879 SU from 222.154. All five terminal allocation estimates sum to 27.880 SU. The site's displayed timestamp is chronologically inconsistent and detailed usage is incomplete: no exact individual posted charge is claimed. Conservative consumed planning ceiling is 29 SU, with no outstanding CPU jobs. This retires historical requested maxima without raising the unchanged 100-SU wave ceiling. Future submission guards must include consumed plus outstanding plus new maximum.

The earlier queue snapshots below are historical. The job started at 14:48:58 UTC, after about 13 minutes 5 seconds queued, and finished after 728 seconds. No queue resubmission occurred.

## 2026-10-21T18:58:51.708284+00:00: controlled native Scotch followup


25907236.pbs101 accepted at 2026-10-21T18:58:25.195600+00:00. Fresh native default Scotch N128, serial decomposition on 32 allocated CPUs, 96 GB, zero GPUs, maximum 15 minutes / 8 SU. Root: `/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-scotch128-20261021T185820Z`. Read PLAN.md for hypothesis, control, gates and conditional same-node pair. No candidate performance result yet. Submission intent, queue/accounting checks, exact deployment hashes and receipt are retained. No retry or budget increase.

Conservative consumed ceiling 29 SU plus this 8-SU outstanding reservation commits 37 / 100 SU. The conditional 29-minute pair would bring the maximum to 98.866667 SU, only after preparation passes and a fresh locked budget/queue check. Separate GPU queue inspected read-only: one own running job at submission; untouched.

Only decompositionMethod changes from the accepted case. The graph-cut hypothesis, observed one-node reference advantage and four-node counterexample are retained in the experiment PLAN. Exact numerical inputs remain byte-checked. Whole-mesh and control-zero-field hashing occurs only on allocated compute CPUs. A terminal prep job alone is not a passing solve or score.

## 2026-10-21T19:05:41.330316+00:00: Scotch preparation reviewed and promoted


Job **25907236.pbs101** passes the full reviewer: F / exit 0, 371 seconds (6 min 11 s), 32 allocated CPUs / one serial task, native v2512 / double precision. Official archive MD5/SHA256 and all eight unpacked members match. Exactly 128 partitions contain 65,334,765 cells and all restored fields. Initial control fields are sealed: 768 files. Sealed collection contains 164 safe text files; processor trees remain on cluster.

| Partition statistic | Hierarchical (16 4 2) | Default Scotch |
|---|---:|---:|
| Maximum cells | 510,431 | 516,440 |
| Maximum cell excess over mean | about 0.000617% | 1.177864% |
| Maximum processor interface faces | 131,252 | 42,141 |
| Unique interface faces | 2,109,346 | 1,549,377 |
| Maximum processor neighbors | 16 | 35 |

Scotch reduces interface faces but increases cell imbalance and neighbor fan-out. This supports testing, not a proven speedup or a measured bottleneck: all ranks will communicate within one node for the immediate screen. Native decomposition/preparation took longer than hierarchical (371 vs 187 seconds), and that setup cost must remain visible independently of solver seconds/step. Batch MaxRSS 31.906254 GiB; estimated allocation charge 3.297778 SU, not individually posted billing. Hardware bandwidth/cache/MPI counters, power and actual page placement were not collected.

Next decision: promote to the frozen same-node H→S pair, with candidate mandatory initialization, unchanged numerical work, exact zero-field reuse guards and all native output checks. Do not rerun decomposition or modify submitted payloads. Retain the terminal prep maximum 8 SU pending reconciliation, so conservative total planning commitment remains 29 consumed + 8 retained + 61.866667 requested pair = 98.866667 / 100 SU. No budget increase or AI changes.

## 2026-10-21T19:07:46.983112+00:00: same-node pair submitted after accepted Scotch preparation


**25907325.pbs101**, accepted 2026-10-21T19:06:38.629513+00:00, is **Q** in the retained 2026-10-21T19:06:52.767507+00:00 snapshot. One exclusive ASPIRE-2A CPU node, 128 MPI ranks, 440 GB, no GPU; maximum 29 minutes, 61.866667 SU. Queue waiting is additional; no start-time prediction or candidate speedup exists yet.

Fresh CPU queue was empty and the separate GPU queue was inspected read-only under the CPU submission lock. Project 59000042 balance and the unchanged 100-SU first-wave limit pass. Durable intent/reservation precede exactly one qsub. Conservative commitment is 29 SU consumed ceiling + 8 SU terminal prep maximum retained pending reconciliation + 61.866667 SU pair = **98.866667 SU**. No AI ledger, payload, queue or schedule changes.

Scotch preparation 25907236 passes full review before this submission. The candidate runs all mandatory initialization once, then hierarchical and Scotch each run 40 fixed-work steps on the same node. Control initialized fields are immutable and checked against 768 SHA256 records before reuse; both trees are checked after noWrite solves. Exact native inputs, fixed iterations, force outputs, timers and exits are gates. Atomic placement diagnostics occur outside solver timing. The payload, deployment hashes, checks, receipt, raw observations and source reviewer are retained.

This is a first ordered H→S pair. Report cache/order and single-pair limitations, all tails and Cd, including a losing result. No four-node/150-step score or repeated improvement is claimed. See PLAN.md and PRE_SUBMIT_REVIEW.md. Do not modify the submitted payload or resubmit unchanged.

Remote root: `/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-method-pair128-20261021T190634Z`.

## 2026-10-21: derive a NUMA-aware native partition hypothesis while the pair runs

Prior evidence: baseline 25905114 passes at 14.921981 s/step; default Scotch 25907236 has fewer faces but more neighbors/cell imbalance. Pair 25907325 is running and its control is provisionally 14.787224 s/step, with unchanged Cd. No final candidate result yet. Atomic diagnostic ranks map CPU=rank 0–127 to eight NUMA sets in blocks of sixteen. This verifies a logical grouping, not actual memory page residence or a runtime bottleneck.

Pinned native v2512 source selects SCOTCH_archTleaf for domains/domainWeights when processorWeights is absent. Derived fresh candidate adds only scotchCoeffs domains (8 16), domainWeights (1 0.1), normalized integer costs 10:1. These weights are a synthetic contrast, not measured hardware ratios. No socket tier is claimed because the retained summary does not individually map CPUs to sockets. Static syntax/input gates pass; library execution is unmeasured.

Next, only after terminal pair review and locked cost reconciliation, submit an at-most-8-SU serial prep if it fits the unchanged 100-SU wave. Its allocated compute stage will inspect reciprocal processor-neighbor face graphs on hierarchical, default Scotch and candidate trees, preserving boundary hashes and logical cross-group cuts. A smaller graph cut is a cheap filter, not a speedup. Review imbalance/fan-out/setup cost and close a losing branch. A later solver needs its own affordable reservation and matching placement; no active payload or AI job was changed. Exact hypothesis, source reference, mapping and scripts: hpc-experiments/nscc-cpu-numa-scotch128-20261021/PLAN.md.

## 2026-10-21T19:33:23.239113+00:00: validate cross-group graph analysis on actual boundaries


Read-only metadata collection retained 256 small ASCII processor-boundary files from the accepted initialized hierarchical and default Scotch trees. No field arrays or binary mesh were copied. Local bounded analysis checked every reciprocal neighbor edge, retained SHA256 for each boundary file and reproduced both native decomposePar totals exactly. See boundary-metadata.tar.gz, collection provenance and graph-parser-validation.json. This validates the real parser before a paid candidate prep allocation.

| Unique interface faces | Hierarchical | Default Scotch |
|---|---:|---:|
| All neighbor edges | 2,109,346 | 1,549,377 |
| Across logical rank groups of 16 | 1,203,493 | 371,658 |
| Within a group | 905,853 | 1,177,719 |
| Maximum processor faces | 131,252 | 42,141 |
| Maximum processor neighbors | 16 | 35 |

The separate current allocation's atomic diagnostic rank map matches these logical groups to eight NUMA CPU sets. These are interface face counts, not actual communication volume, wait time, memory traffic or page locality. A later allocation must recheck placement. Default Scotch already reduces cross-group faces; this may leave less benefit for an explicit tree. That is a reason to use an inexpensive graph screen before spending on another solver.

Decision: retain the native (8 16) tree hypothesis with synthetic weights 10:1, compare all graph quantities and cell imbalance, and only promote a non-dominated result. The active H→S pair is still running; its final result and locked budget reconciliation gate any new submission. No allocation or budget increase is performed by this analysis. No numerical score is claimed.

## 2026-10-21T19:40:11.178495+00:00: same-node H/S review, a weak observed gain and a bounded next hypothesis


Job **25907325.pbs101** passed both native solves on the same exclusive ASPIRE-2A CPU node, x1001c0s1b0n0. Order was hierarchical then Scotch, 128 MPI ranks, OpenFOAM v2512 / double precision, 65,334,765 cells, identical fixed physics, iteration counts and function objects. This is a one-node 40-step method screen, not the four-node 150-step contest score.

| Metric | Hierarchical (16 4 2) | Default Scotch |
|---|---:|---:|
| Average, seconds per step | 14.7872238123 | 14.6402329083 |
| Median, seconds per step | 14.708853 | 14.480458 |
| p95, seconds per step | 15.222146 | 14.848304 |
| Slowest step, seconds | 15.693371 (step 36) | 21.120703 (step 9) |
| Standard deviation, seconds per step | 0.236305 | 1.060469 |
| Measured steps | 39 (steps 2–40) | 39 (steps 2–40) |
| Final Cd, dimensionless | 0.4389323284 | 0.4359888360 |
| Native solver clock, seconds | 621 | 616 |
| Omega bounding messages | 8 | 10 |
| Native timing confidence warning | No; calculated minimum 2 samples | Yes; calculated minimum 50 samples |

Scotch has the lowest observed average in this pair, a **0.9940% reduction in time per step** (1.01004 control/candidate ratio). It is not a confirmed optimization: one ordered pair, a seven-second outlier and the native confidence warning do not establish a stable one-percent gain. Keep step 9 in the average; do not trim it or raise the official 40-step endpoint just to suppress a warning. Median and p95 are useful diagnostics, not replacement contest metrics. The independent hierarchical baseline was 14.921981 s/step on another node and is contextual only.

## Numerical and execution inspection

Every native stage exited zero and has End, v2512, scalar64 and 128-rank markers. Candidate mandatory initialization completed once. All 40 steps keep Ux/Uy/Uz=15, pressure=12, omega/k=8 iterations. All force rows are finite, the timer file and log agree, and both initial zero-time field trees have identical before/after hashes. Control Cd exactly reproduces the prior baseline; Scotch Cd reproduces the public method-specific reference to printed precision. A change in decomposition can change floating-point operation order and GAMG behavior. Do not impose the Bonus accuracy comparison as a universal Basic ±0.5% gate. Lower continuity error alone is not proof of better physical accuracy.

Atomic diagnostic rank records verify unique cores 0–127 and groups of sixteen within each of eight NUMA CPU sets. These are pre-solve diagnostic bindings, not solver migration or actual memory-page residency. Whole allocation: **1373 seconds / 22 min 53 s**, estimated **48.817778 SU**, batch MaxRSS **121.3995 GiB**, aggregate CPU time **45:49:28**. GNU time wraps the launcher; its reported 0% CPU is not solver inactivity. Hardware bandwidth/cache/MPI counters and power were not collected. Read-only status/log snapshots and small boundary metadata collection overlapped the timed allocation; their overhead was not independently measured and no outlier cause is assigned.

## Assessment and next decision

The graph inspection reproduces native totals: Scotch has 1,549,377 total unique interface faces versus 2,109,346, and 371,658 faces across logical groups of sixteen versus 1,203,493. This structure supports a NUMA-aware partition hypothesis, not a measured MPI/NUMA bottleneck. Default Scotch is a provisional candidate; keep hierarchical as an accepted stable control. A reverse-order full repeat would be useful, but the remaining first-wave budget cannot cover its maximum; do not increase the ceiling silently.

Promote only the prepared low-cost native NUMA partition screen: domains (8 16), synthetic integer costs 10:1. It changes only scotchCoeffs. Its preregistered graph/balance filter, exact source reference and native payload live in ../nscc-cpu-numa-scotch128-20261021. Only submit after the locked reconciliation and queue/balance checks, maximum 8 SU, no solver claim. A promising graph still needs an independently budgeted solve and repeat.

## Cost and reproducibility

All seven recorded CPU allocations are terminal. Their requested-core × elapsed-time estimates sum to **79.995556 SU**. Project report still shows a stale amount delta of **27.879 SU**, with In Doubt zero; do not call this exact posted billing. Use conservative **81 SU consumed** = ceil(max(reported delta, terminal estimate) + 1 SU). Unchanged wave ceiling 100 SU leaves **19 SU**, sufficient for the full next 8-SU prep maximum. Original requested maxima remain in the ledger history. Retain refresh/timestamp limitations and never deduct prepaid In Doubt twice.

`review.py` reproduces review.json from **127 sealed text artifacts**, including fixed inputs, both native logs/timers/force outputs, init logs, phase markers, rank records and zero-field seals. detailed-inspection.json retains outlier indices and final diagnostics. Processor fields/meshes remain on the cluster and can be rebuilt from the verified official archive and pinned native preparation. No AI jobs, ledger, payload or submission package changed.

## 2026-10-21T19:41:37.780529+00:00: submit the justified native NUMA partition filter


**25907688.pbs101: R** at 2026-10-21T19:40:48.044548+00:00, qdev, x1001c0s3b0n0. Fresh native default Scotch tree with domains (8 16), domainWeights (1 0.1), normalized synthetic weights 10:1. One allocated CPU node, 32 CPUs, one serial task, 96 GB, zero GPUs; maximum 15 minutes / **8 SU**. No candidate solver speed or physical latency ratio is claimed.

The preceding same-node pair **25907325** passes all numerical/work gates: H 14.787224 vs S 14.640233 s/step, observed 0.994% saving, not stable proof because S has a 21.120703-second outlier and native confidence warning. Current candidate is a distinct graph-locality hypothesis justified by verified groups of sixteen diagnostic ranks per NUMA CPU set and actual processor-neighbor graphs.

Before qsub, the CPU lock protects fresh own-queue/project checks, read-only combined PBS capacity, the 100-SU ceiling, durable intent and full reservation. All seven preceding CPU jobs are terminal; **79.995556 SU** estimated terminal usage is conservatively rounded plus buffer to **81 SU consumed**. New 8-SU maximum brings commitment to **89 / 100 SU**, leaving 11 SU unreserved. Project report refresh remains stale; do not equate its 27.879-SU delta with actual wave spending or claim per-job posted charges. No cap increase, AI changes or schedules.

Next collect sealed terminal text with tools/collect_cpu_probe.py, then run review.py. Inspect native archive/member identities, all 128 partitions/65,334,765 cells, restored fields, reciprocal neighbor graphs and preregistered filter. Read PLAN.md and GRAPH_REVIEW.md. A passing native prep can still fail the graph filter; neither is a solver result. Do not automatically promote or submit an underfunded solve. Preserve this payload/root and failures. Root: `/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-numa-scotch128-20261021T194034Z`.

## 2026-10-21T19:46:15.896523+00:00: clarify separate HPC and AI budgets

The owner asked whether HPC SU are shared with AI. CPU OpenFOAM uses project 59000042 (30,000-SU grant); Qwen/H100 uses separate project 59010042. The 100-SU HPC first-wave planning ceiling is a bounded experiment allowance, not the grant or remaining balance. A generic request to continue does not silently increase that ceiling. CPU queue rate is 1 SU per allocated core-hour. Timestamp/refresh limits prevent treating the stale displayed balance as live usage. See notes/hpc-ai-service-units.md; no AI ledger was changed.

## 2026-10-21T19:51:40.782003+00:00: NUMA graph filter passes; owner expands HPC research


Job **25907688.pbs101**: F / exit 0, **385 seconds / 6 min 25 s**, native v2512 / double precision, 32 allocated CPUs / serial task, estimated **3.422222 SU**, batch MaxRSS **32.0174 GiB**. Full mesh identity, 128 partitions / 65,334,765 cells, restored fields, native tree request and reciprocal graph checks pass. All **168 safe text artifacts** are sealed.

| Quantity | Default Scotch | NUMA tree (8 × 16) |
|---|---:|---:|
| Unique cross-group interface faces | 371,658 | 332,157 |
| All unique interface faces | 1,549,377 | 1,570,175 |
| Worst-rank interface faces | 42,141 | 43,115 |
| Maximum processor neighbors | 35 | 32 |
| Maximum cell excess over mean | 1.177864% | 1.005460% |
| Synthetic 10:1 objective | 4,894,299 | 4,559,588 |

Cross-group faces fall **10.6283%**, while total faces rise **1.3423%**. All five preregistered filters pass. This is a promising partition, not a measured solver gain. Logical groups of sixteen correspond to the earlier diagnostic NUMA CPU sets only if the next allocation's placement also matches. Weights 10:1 are synthetic, not measured latency. Tree execution is inferred from matching pinned source/build and requested native dictionary, not direct tracing. No bandwidth, cache, MPI wait/traffic, page residency or power measurements were collected.

Decision: proceed to a same-node 40-step default-Scotch versus NUMA-Scotch pair, complete mandatory candidate initialization, verified physical placement, unchanged numerical work and sealed zero fields. Preserve the native Average including outliers. The preceding H→S pair's observed 0.994% saving remains unconfirmed. A partition benefit must survive a solve and a reverse-order repeat before promotion.

All eight recorded allocations are terminal; core-hour estimates total **83.417778 SU**. Conservative consumed ceiling is **85 SU**, no reservations. The stale project amount delta is not actual current wave spending. The original 100-SU wave could not afford a full pair. The owner then explicitly requested much more research/submission based on the separate large HPC grant. A new bounded continuation raises the **cumulative CPU research ceiling to 1,000 SU**, still far below the 30,000-SU project grant. Keep actual spending/reservations under the CPU lock, one active CPU allocation, combined own PBS cap three, no AI changes or background Codex. This is a new owner-directed phase; preserve original 100-SU provenance.
