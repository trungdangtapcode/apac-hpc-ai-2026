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

## 2026-10-21T19:54:02.939903+00:00: full NUMA solve pair submitted and queue-scope correction


**25907753.pbs101: R** at 2026-10-21T19:54:02.909127+00:00. Accepted 2026-10-21T19:52:53.014595+00:00; one exclusive CPU node / 128 ranks / 440 GB / no GPU, max 29 min / **61.866667 SU**. Native default Scotch control and fresh NUMA tree candidate each run 40 steps after mandatory candidate initialization. Physical-core and NUMA grouping guards run outside solver timing. Keep zero-field/source hashes, all fixed numerical work, native timers, force outputs and resource/phase evidence. See PLAN.md.

Fresh CPU own queue was empty, read-only combined PBS capacity and project balance passed, durable intent/reservation and exactly one qsub retained. Expanded cumulative ceiling **1,000 SU**, conservative consumed **85 SU**, new reservation **61.866667 SU**, total **146.866667 SU**. Old 100-SU first-wave ceiling remains historical. No AI changes or background Codex.

Native graph filter passed in 25907688; still no NUMA solver gain. One ordered pair does not establish a stable win. The wrapper preserves the inherited CPU_HS_PAIR_PASS marker for compatibility; exact role input hashes identify **default Scotch vs NUMA Scotch**, not hierarchical vs Scotch. No frozen payload is changed after submission.

Next prepare validated 256-rank inputs as an afterok follower while this pair runs, if combined cap permits. A failed parent blocks that follower; keep one CPU allocation active at a time.

Queue correction: actual normal routing includes q1–q6; qdev caps each job at 128 CPU as well as 256 aggregate. Larger 256/512-core normal requests can route elsewhere (q5 max 2048). Earlier qdev-only inference did not establish a cluster-wide restriction. Retain snapshot and cpu-continuation-20261021/QUEUE_POLICY.md; inspect actual multi-node routing on submission.

## 21 October: preserve and fix a local deployment size limit

The first three-case N256 deployment exceeded the OS per-argument size limit (errno 7) before SSH started. No remote process, qsub or budget reservation occurred; no cluster job or SU was lost. Replaced embedded base64/hash arguments with a tar stream over SSH stdin, retaining safe-path checks, refusal of existing roots and returned exact hash verification. This is a local transport fix; frozen native case/job payload is unchanged. Exact failure and fix live in nscc-cpu-three-cuts256-20261021/deployment-attempt1.json and deploy-submit.py.

## 2026-10-21T19:59:32.087973+00:00: queue three distinct two-node cuts behind native parent gates


**25907772.pbs101: H**, dependency hold `afterok:25907753.pbs101`, verified from PBS at 2026-10-21T19:58:35.319652+00:00. This is the intentional dependency wait, not a solver hang. Parent **25907753 is R**. PBS also records the matching beforeok relationship on the parent. Only one own CPU allocation can run along this chain. No manual release or duplicate submit.

This serial job prepares **hierarchical (16 8 2), default Scotch, and node-aware Scotch (2 128), synthetic weights 10:1** for 256 ranks / two nodes / official 80-step endpoint. It does not run a solver or claim a score. Native pinned case generation, full mesh identity, exact partition/field/source checks and reciprocal graph evidence are retained. Maximum 45 min on 32 allocated CPUs, serial task, 96 GB, zero GPUs = **24 SU**. See PLAN.md for the full hypothesis and acceptance gates.

The first local deployment failed with errno 7 before any SSH/qsub/reservation. Fixed by streaming the bundle over SSH stdin; returned deployed hashes exactly match all expected inputs. That failed local attempt is preserved. The actual submission occurred once at 2026-10-21T19:57:49.064727+00:00, root `/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-three-cuts256-20261021T195743Z`.

At locked checks, one CPU parent plus one exiting AI job occupied two combined slots. This follower is the third, respecting combined PBS cap three and preserving AI. Conservative consumed ceiling **85 SU**, retained parent maximum **61.866667 SU**, follower **24 SU** = **170.866667 / 1,000 SU** planning commitment. This is not actual charged usage; terminal resource estimates are **83.417778 SU** before running work. Original 100-SU wave remains historical, expanded by the owner's explicit instruction.

Next collect/review the parent and then the three cuts. Prepare a full two-node hierarchical/default-Scotch baseline, while retaining one combined slot for active AI work where possible. Node-aware promotion requires actual graph evidence. Multi-node normal requests can route outside qdev; the qdev 128-core per-job cap is not a cluster-wide limit. No background Codex/schedules or AI payload changes.

## 2026-10-22T14:16:12.096147+00:00: access-blocked continuation, qualified gates and corrected provenance


The current HPC session read the persistent handoff and attempted fresh collection of the submitted one-node default/NUMA pair 25907753 and dependent three-cut preparation 25907772. Both checks stopped before SSH/PBS because no live VPN namespace existed. A brief client process was observed during local work, then the VPN terminal was dead with exit code1; the HPC worker did not start/stop it. No exact expiry, server policy, credential error or exit cause is asserted. The dated running/held snapshot is historical; current job states/results remain unknown. Batch jobs do not require this client SSH session to keep running.

While access is unavailable, bounded parallel work completed the three-cut evidence reviewer, two-node submit/review tools and independent static provenance audit. Root review fixed processor-tree evidence assumptions, completed-parent handling and preservation of prior derived reviews. The 80-step semantic gate was qualified on both pinned organizer two-node reference logs and rejected one changed fixed iteration; these are parser checks, not new benchmarks. Local syntax checks pass. The full two-node payload is ready but not deployed/submitted, and its 170.666667-SU maximum is not yet reserved. No native multi-node execution has been verified.

A dated correction explains inherited NUMA PREPARATION metadata: original default decomposeParDict remained falsely marked immutable, while actual frozen payload and pair input hashes correctly pin the changed NUMA dictionary. Other inherited immutable entries match. No frozen payload/measurement changed.

Continue within the owner-requested 1,000-SU cumulative CPU ceiling. Retain conservative consumed85 plus existing requested maxima85.866667 until actual terminal evidence can be collected. Do not interpret the stale project usage display as current spend, release reservations speculatively, or charge the separate AI project. No new compute job, AI change, schedule or background Codex was started in this access-blocked checkpoint.

The owner was asked whether DUO approval is available for restoration. Once access succeeds, collect/seal both jobs, run their reviewers, inspect all warnings/tails/work/forces/graph/resource evidence, reconcile terminal costs and submit the ready H/S256 pair if native prep passes and fresh queue/capacity/budget checks permit. Keep any failed branch and held dependency; do not resubmit unchanged merely because live access was missing.

## 2026-10-22T15:05:50.041275+00:00: recovered losing NUMA run and three valid two-node inputs


Scratch evidence for **25907753.pbs101** was recovered and sealed after VPN/CPU SSH restoration on 22 October. **127 text artifacts** pass the files-only reviewer: all native commands exit zero, 40 fixed-work steps per solve / 39 timed samples, original source/precision/function objects, finite forces, exact timing crosschecks, unchanged zero-time fields, and physical-core/eight-NUMA grouping. The final native wrapper marker exists. **PBS history returns Unknown Job Id**, so final scheduler exit, whole-allocation elapsed time, resource maxima and actual billing are not claimed. Retain the full **61.866667-SU** reservation.

| Metric | Default Scotch | NUMA tree (8 16), synthetic 10:1 |
|---|---:|---:|
| Average, seconds per step | 13.880988254 | 14.358714620 |
| p95, seconds per step | 14.018158 | 14.566025 |
| Maximum, seconds | 14.237294 | 16.614805 (step 10) |
| Final Cd, dimensionless | 0.4359888360 | 0.4345811574 |
| Omega bounding messages | 10 | 8 |

Candidate time per step increases **3.4416%** in this ordered same-node pair. Its graph had 10.6283% fewer logical cross-NUMA faces but 1.3423% more total faces; the graph objective did not translate into a timing gain. The evidence does not establish the cause: no measured MPI wait/traffic, bandwidth/cache counters, power or page residency, and no reverse-order repeat. Do not infer a causal NUMA bottleneck or remove the slow step. Default's 13.880988 is the best observed one-node average so far, but comparisons to earlier hosts/allocations are contextual, not additional controlled speedups. No four-node score.

Decision: close this unchanged NUMA configuration as a performance candidate and prioritize the validated two-node baseline. A source/graph improvement alone is insufficient. Keep the complete losing run and exact samples in review-files-only.json. No quality claim follows from a different Cd or fewer bounding messages. Numerical work remains fixed; no universal Basic ±0.5% gate is invented.


**25907772.pbs101**: **284 sealed safe text artifacts** recovered from scratch. All three pinned native cases pass full source and official archive/member identity, 256 partitions / 65,334,765 cells, restored-field checks represented by frozen native check-cut.py/CUT_READY, native decomposition End/exit and final wrapper marker, plus reciprocal graph-collection assertions. Raw processor mesh/field trees were not downloaded. PBS history returns Unknown Job Id: final PBS state, whole-batch elapsed/resources and actual charge are unverified. Keep the full **24-SU maximum** reservation.

| Quantity | Hierarchical (16 8 2) | Default Scotch | Node-aware Scotch (2 128), synthetic 10:1 |
|---|---:|---:|---:|
| Unique cross-group faces | 717,233 | 99,591 | 127,359 |
| All unique interface faces | 3,054,282 | 2,116,218 | 2,131,904 |
| Worst-rank interface faces | 87,288 | 34,886 | 33,930 |
| Maximum processor neighbors | 19 | 54 | 33 |
| Maximum cell excess over mean | 0.001205% | 1.127319% | 1.206860% |

Logical groups of128 are not proven physical hosts until the two-node launch probe matches them. Default Scotch has much fewer cross-group faces than hierarchical; node-aware Scotch increases them **27.8820%** versus default, with **0.7412%** more total faces, while reducing fan-out and worst-rank faces. It is not a network-cut winner. Postpone this unchanged tuning unless measured small-message/fan-out evidence justifies a distinct test. Graph face counts are not traffic or elapsed-time estimates.

Decision: proceed with the prepared matched H/default-Scotch two-node / 80-step baseline after fresh capacity/budget checks and full runtime source/rank validation. Re-restore original zero fields before mandatory initialization. Native input evidence can be reused while honestly retaining unavailable scheduler accounting; do not manufacture an old afterok success record or release its reservation. Current submission is blocked by other untracked OpenFOAM work discovered on the shared CPU account, not by these native preparation checks.

## 2026-10-22T15:07:29.494177+00:00: restore access and defer launch rather than overlap unknown CPU work


Access is restored. Native default-versus-NUMA evidence shows **13.880988 vs 14.358715 s/step**, a **3.4416% NUMA slowdown** in one ordered pair. Keep the losing branch and all samples; no reverse test or causal bottleneck proof. N256 native preparations also pass: default cross-group faces99,591 versus hierarchical717,233, while the node-aware tree worsens that objective to127,359. Prioritize default-versus-hierarchical full two-node timing, not blind promotion of a graph tuning.

The 256-rank / two-node / 80-step H/S pair is prepared and hash-verified in a fresh remote directory, with original zero-field restoration, physical-core/host guards, complete mandatory initialization, all fixed work and durable wrapper lifecycle. Its **170.666667-SU** maximum is **not reserved** and no new job was submitted. Fresh account queue checks found other untracked OpenFOAM jobs and stopped safely. Existing jobs remain untouched.

Old PBS history is unavailable; scratch native proof is reviewed separately from scheduler/accounting proof. Our ledger retains **85 SU conservative consumed + 85.866667 SU requested maxima =170.866667 /1,000 SU**. Current actual usage is not inferred from stale myprojects output. Other shared-project jobs are not silently added or funded through this ledger; coordinate ownership and total cost before further submissions. The owner's expanded research direction remains active within agreed caps.

Next: clarify shared CPU ownership, inspect/reuse legitimate existing work rather than duplicate it, then refresh real queues/project budget and submit the ready matched baseline when allowed. No AI changes or background Codex. All safe raw evidence, reasoning and orchestration are captured/verified/committed/pushed as separate milestones. External artifact store is not automatically uploaded by Git.

## 2026-10-22T15:28:26.661074+00:00: shared native baseline review and distinct offline placement hypothesis


**Question and control.** Can the completed shared CPU runs supply useful baseline evidence without duplicate allocations? Jobs 25921487.pbs101 and 25921492.pbs101 use the official 40/80-step endpoints on one/two ASPIRE CPU nodes, 128/256 ranks. Their current scripts use default Scotch with SRX disabled. They were submitted from another work root, outside this worker's receipts and budget; identity and frozen script provenance remain unresolved. No queue, payload or ledger was changed on their behalf.

**Preserved evidence.** The read-only collector sealed 135 text members plus local recovery/hash records. PBS sanitized records establish F / exit 0 and actual allocation hosts. The independent reviewer checks every retained hash and archive path, all five native stage End markers/no fatal errors, official source files after only allowed rank/method/endTime substitutions, 65,334,765 cells and the correct partition counts. Every step has Ux/Uy/Uz 15, pressure 12, omega 8 and k 8 iterations. All 39/79 positive finite timestep durations match solver-log and function-object data exactly; the arithmetic means match native Average. Finite force rows cover all 40/80 steps. Root reran the reviewer successfully after reviewing and correcting its interpretation.

| Job | Nodes / ranks | Native mean, seconds/step | p95, seconds | Maximum, seconds (Time) | Final Cd, dimensionless | PBS elapsed | Estimated SU |
|---|---:|---:|---:|---:|---:|---|---:|
| 25921487 | 1 / 128 | 14.450756959 | 14.595540 | 16.145866 (31) | 0.4359888360 | 18 min 1 s | 38.435556 |
| 25921492 | 2 / 256 | 7.462835189 | 8.327817 | 16.397209 (12) | 0.3271298097 | 18 min 25 s | 78.577778 |

The 1.936 per-step ratio describes prescribed-endpoint scaling across separate allocations; it is not a same-work controlled speedup. The one-node result does not improve on the earlier 13.880988254-second observation. The two-node native logger recommends 225 samples for its own 2% / 95% target, versus 79 retained; keep the full official endpoint mean and all slow steps. Any longer confidence diagnostic must be separate from ranked 40/80/150-step endpoints.

**Inspection beyond Average.** Full samples, p95, maxima/time indices, IQR outliers, native work, Cd series, partition balance, runtime tails, warnings and PBS CPU/memory/cost evidence are recorded in review.json. Whole-allocation CPU utilization derived from CPUT/(allocated CPUs × elapsed) is 66.42% / 63.48%; it includes preparation and solve and cannot diagnose a solver bottleneck. PBS raw last cpupercent samples are a different quantity. Resource memory/vmem retains native kb units. Estimated SU uses elapsed × allocated CPU count × reported rate 1 / 3600, not individually posted charges. The scripts warn that SRX-off conflicts with default XRC and disables XRC. Runtime dynamic timing-library compilation is visible. Negative omega bounding also occurs in accepted controls; preserve it as a diagnostic, not an invented failure. Page residency, measured MPI wait/traffic, cache/bandwidth/frequency/power counters and solver-time physical affinity were not collected.

**Acceptance limits.** Actual MPI rank/core mapping, final zero-field seals, immutable mesh identity and frozen submitted source/command provenance are missing. Stage scripts accept End even if an individual native process returned nonzero, so final batch exit zero does not establish every stage return. These are useful native baseline observations, not a fully accepted score. No four-node/150-step measurement is available yet.

**Next decision and cost coordination.** Do not rerun the losing NUMA-decomposition branch or blindly duplicate these default baselines. At 15:21 UTC six shared jobs were queued: Scotch four-node 64/96/128 ranks per node, hierarchical one/two/four-node. Five reported node_pool insufficiency and the one-node hierarchical job reported qdev aggregate CPU capacity. Preserve every queue position. This worker's matched two-node H/S payload remains ready but unsubmitted; fresh queue, ownership and cost coordination are prerequisites. Our conservative commitment remains 170.866667 / 1,000 SU. The project's query still returned Used 250.033 / Balance 29749.967 with a 21 October report-as-of timestamp: this is stale billing, not evidence these new jobs cost zero.

Continue useful offline research while capacity/ownership is unresolved. The distinct placement question is whether keeping exactly the same Scotch partitions and changing only rank-to-NUMA placement can reduce logical cross-group faces without the extra faces introduced by NUMA-aware decomposition. A graph screen is a proxy only; any future same-node paired solve must preserve physics, full init, numerical work, field and placement gates, and fit the budget. A separate reviewed transport proposal holds XRC off and tests SRX explicitly on/off; SRX-off itself is already used, so it is not a newly discovered technique.

**Preservation.** Collector and native evidence were captured in 825bbfe2. This review is a separate checkpoint with English explanations, raw failure boundaries, no authentication material, and no AI changes. [Full results](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/shared-cpu-intake-20261022/RESULTS.md) and [machine-readable review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/shared-cpu-intake-20261022/review.json).

## 2026-10-22T15:38:40.906272+00:00: refined placement proxy and binding qualification, no allocation


**Question and prior evidence.** The solved NUMA-aware Scotch decomposition reduced logical cross-NUMA faces by 10.63% but increased total partition faces and lost 3.4416% in timing. Can placement alone improve the communication graph while keeping default Scotch partitions, cells and total faces unchanged? This tests a different factor; the unchanged losing decomposition stays closed. Input is the already validated default N128 processor-boundary graph and retained placement probe, not a new mesh or source variant.

**Change and control.** Map the same 128 logical ranks to eight logical groups, exactly 16 ranks each. Baseline is rank // 16. Initial search used seed 2026, 20 balanced random starts and one million rank-pair swaps with annealing; it found 368,634 crossing faces versus 371,658 (0.813651% reduction). That initial output and its close decision are preserved byte-for-byte in screen-initial.json. Root found the missing warm-start/local-descent check and requested a bounded refinement before accepting that closure. Deterministic steepest balanced-swap descent starts from baseline and both initial/current annealing best mappings; 100 arbitrary seeded swaps check incremental deltas against full edge recomputation. No process rank IDs, processor directories, graph edges or case inputs were changed.

**Offline result.** Final candidate cut is **354,658 logical cross-group faces**, **17,000 / 4.5740977% fewer** than baseline. Baseline is a one-swap local optimum; the two best-mapping starts reach the same lower one-swap local optimum in two accepted swaps. All descents complete in the retained run, about 3.49 seconds on this local host. Graph SHA-256 is db4e5c7697a7959433f485c9f51e4126b65cc660f2891afa3a1619c91148f79f. Rank bijection, all group capacities, **1,549,377 total faces**, **42,141 maximum faces/rank** and **35 maximum neighbors** are unchanged. Root independently recomputed both objective values from immutable edges and verified the preserved initial-result hash. Full assignments, inverse map, swaps, trails and delta checks are retained. This is a heuristic local result, not proof of global optimality or solve speedup.

**Implementation readiness and verification.** A read-only CPU login query confirms PALS mpiexec 1.1.6 documents command-level --cpu-bind list:<cpu>:<cpu>:... . No MPI ranks or allocation were launched. render_binding.py derives CPU IDs from a supplied 128-rank topology probe without running a program or changing affinity. It rendered the retained historical probe, and rejected five malformed/inapplicable probes: duplicate CPUs, duplicate physical cores, multiple hosts, ambiguous affinity and changed baseline rank-block/NUMA grouping. The historical output is an example only; never pass those CPU IDs into a new allocation. A real run needs fresh node topology, an independently checked bound probe, and the exact candidate binding on renumberMesh, potentialFoam, applyBoundaryLayer and simpleFoam. If the baseline grouping differs, recompute the graph control before expensive work. Startup affinity is not proof of solve-time page residency, migration or MPI traffic.

**Assessment and next decision.** Correct the initial sub-one-percent close decision: the refined mapping is worth retaining for a conditional runtime comparison, at lower priority than the pending prescribed-endpoint baselines. Its 4.57% graph improvement is **not** 4.57% faster computation. No memory/fabric traffic, kernel, power or solve duration was measured by this screen. A same-node 128-rank / 40-step control/candidate pair must restore original fields and perform full mandatory initialization for both roles, preserve source/work/function objects, retain all timing outliers and force data, and use fresh field/rank and per-stage return checks. Proposed maximum **29 minutes / 61.866667 SU**; practical confirmation threshold **3% lower native Average**, followed by a separately costed reverse pair only if the first pair and budget gates pass. This is a research threshold, not a Basic output tolerance. CPU placement is permitted runtime tuning; processor-folder relabeling/custom decomposition is not part of this proposal.

**Queue and cost boundary.** At 15:35:36 UTC the account had **3 running and 9 queued shared CPU jobs** from another work root, beyond this worker's own receipts/ledger. The owner has been asked who controls them to coordinate costs and prevent duplication. Preserve all of them. This screen and help/renderer checks consumed **zero cluster SU**, created no qsub intent/reservation/receipt, and made no change to either budget. Our commitment stays **170.866667 / 1,000 SU**. Project billing still reports a stale 21 October as-of value. No background Codex or AI work was started.

**Preservation.** Archive the original and refined offline attempts, runnable code, input hashes, historical example, PALS help/version, negative checks and conditional plan in a separate safe checkpoint. [Plan and result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/rank-placement-screen-20261022/PLAN.md), [screen details](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/rank-placement-screen-20261022/screen.json), [qualification](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/rank-placement-screen-20261022/qualification.json). No authentication material or remote payload modification is included.

## 2026-10-22T17:34:03.804275+00:00: native rank-density results and corrected setup/confidence interpretation


**Question and prior evidence.** Do fewer Scotch ranks per node improve either prescribed endpoint, and is the default-Scotch graph lead also a solve-time lead? Previous shared S128 results were 14.450756959 seconds/step on one node and 7.462835189 on two. Native graph counts favored default Scotch over hierarchical, but graph faces are not measured traffic or a solver-time predictor.

**Access and evidence.** The healthy VPN reached the CPU SSH port, but commands through the old CPU multiplexing master hung. A separate authenticated master on asp2a-login-nscc02 restored functional hostname/PBS access without resetting VPN or disturbing existing jobs/AI access. Local master-process existence was not remote liveness proof. Connection failure cause remains unknown; private authentication material was excluded. Six four-node jobs were queued and zero CPU allocations active at 17:23 UTC. Their ownership and costs remain outside this worker's receipts and unresolved.

**Control and changes.** Six new shared jobs compare hierarchical 128 ranks/node and Scotch 64/96 ranks/node at one/two nodes, full 40/80 steps. One-node allocations reserve 128 CPUs; two-node allocations reserve 256 CPUs, even with fewer MPI ranks. All full original physics, solver iteration controls, precision, function objects and allowed source parameters were checked. These are separate allocations, not randomized same-allocation controls. Two prior sealed default-Scotch 128-rank/node runs provide context only.

**Native review.** All 399 new archive members, 400 local evidence entries and 398 remote hashes verify. All six new PBS records are F/exit 0. Each run has complete five-stage End/no fatal evidence; expected version/double precision, exact rank/partition count and 65,334,765 cells; every fixed-work iteration for Ux/Uy/Uz=15, p=12, omega=8, k=8; full endpoint Time/force rows; exact solver-log/function-object timing sample agreement and arithmetic mean; finite Cd. Official source case and original inputs match after only allowed rank/method/shape/endTime substitutions. The earlier two sealed controls are hash-verified again, not resealed or altered. Root inspected and reran the derived reviewer; no per-run native gate failure exists.

| Job | Nodes | Method | MPI ranks/node | Allocated CPUs | Mean seconds/step | p95 seconds | PBS elapsed seconds | Estimated SU |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 25921831.pbs101 | 1 | hierarchical | 128 | 128 | 14.366262733 | 14.446429 | 925 | 32.888889 |
| 25921832.pbs101 | 1 | scotch | 64 | 128 | 16.018573416 | 16.478274 | 1045 | 37.155556 |
| 25921833.pbs101 | 1 | scotch | 96 | 128 | 14.374956921 | 14.484753 | 1015 | 36.088889 |
| 25921809.pbs101 | 2 | hierarchical | 128 | 256 | 7.169996913 | 8.009692 | 908 | 64.568889 |
| 25921820.pbs101 | 2 | scotch | 64 | 256 | 7.902555212 | 8.028983 | 1072 | 76.231111 |
| 25921822.pbs101 | 2 | scotch | 96 | 256 | 7.701742313 | 7.887058 | 1071 | 76.160000 |
| 25921487.pbs101 | 1 | scotch | 128 | 128 | 14.450756959 | 14.595540 | 1081 | 38.435556 |
| 25921492.pbs101 | 2 | scotch | 128 | 256 | 7.462835189 | 8.327817 | 1105 | 78.577778 |

**Assessment.** At two nodes the hierarchical N256 observation **7.169996913 seconds/step** is **3.92% lower** than the earlier separate-allocation Scotch N256 observation, while its p95 is 8.009692 seconds and maximum 10.075875 seconds at Time 27. This is a new observed two-node lead, not a matched causal or stable improvement. H1 is the cheapest full allocation in this table at **32.888889 SU estimated**, not a universal solver winner. Across all retained one-node runs the earlier default-Scotch 13.880988254-second observation remains the lowest, so this wave sets no new one-node record. Scotch 64 ranks/node loses mean timing at both endpoints; 96 ranks/node offers no compelling mean/cost advantage in these cross-allocation samples. Retain these losing runs and do not repeat their unchanged configurations blindly. Four-node method rankings remain unmeasured in our collected results; do not extrapolate the two-node choice.

**Diagnostics and corrected interpretations.** New H2 has 79 timed samples, with native recommended minimum 42 and no short-sample warning. S64-2 recommends 2 and has no warning. The prior S128-2 recommends 225 and actually warns; the warning is not universal to two-node jobs. These logger diagnostics are not formal independent confidence intervals. All samples, IQR outliers, p95, maxima/Time, Cd, negative omega diagnostics, source flags, CPU/memory and native stage tails are retained. Negative bounding is also in accepted controls and is not a Basic failure by itself. No page residency, actual rank/core affinity, MPI-wait/traffic, hardware cache/bandwidth/frequency/power or solver-time migration telemetry was collected.

The earlier draft summed decomposePar's algorithm-only 'Finished decomposition' timer with three init ClockTimes. That is a **partial preparation timer sum**, excluding decomposePar mesh/field transfer/write and unmeasured read/I/O/overhead, not whole setup duration or a setup winner. Derived prose/JSON were corrected before backup. Do not label unmeasured elapsed remainder as I/O. Allocated CPUs determine SU estimates; MPI ranks determine work partitions. PBS cpupercent and CPUT-derived whole-allocation utilization remain distinct.

**Cost and validity limits.** New six-job allocated-CPU estimates total **323.093333 SU**, not posted charges and not reservations funded through this worker's ledger. Missing frozen submitted scripts, individual stage return status, mesh/final-field seals and per-rank affinity prevent full result acceptance. The shared script can mask nonzero stage returns after End even with batch exit 0. A read-only detailed myprojects query for 21–23 October still returns a stale 21 October balance (Used 250.033, Balance 29749.967) and incomplete 27.88-SU detailed usage. Its own output warns of incomplete/inaccurate estimates; do not reconcile our ledger or infer new jobs cost zero. Own conservative commitment stays **170.866667 / 1,000 SU**.

**Next decision.** Prioritize a same-allocation hierarchical/default-Scotch two-node confirmation when coordinated queue/budget gates allow: the validated H/S256 bundle is already staged, max 170.666667 SU, still unsubmitted. A graph-only lead cannot promote default Scotch above the measured hierarchical observation. Prepare the distinct same-partition rank-binding pair offline, max 61.866667 SU, without adding jobs to the six existing shared queue positions or changing caps. All six four-node branches remain untouched. No source, precision or solver-work changes, background Codex, AI work or submission material edits.

**Preservation.** Access fix ec63df39 and six-run raw intake be34c744 are separate pushed checkpoints. This review/interpretation is another small checkpoint. Extracted safe text evidence is in Git. The exact 1,176,823-byte raw gzip is retained as external object f4830287f6a9077c0054784bc84ce76bcbba7d16a7d4f9742e76cc663d0164ed; Git contains its manifest/hash/recovery metadata, not that object byte stream. The sibling artifact store still requires separate off-host preservation. [Full eight-run table and limits](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/shared-cpu-density-review-20261022/RESULTS.md), [review data](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/shared-cpu-density-review-20261022/review.json), [billing attempt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/shared-cpu-density-review-20261022/billing-detail-20261022.txt).

## 2026-10-22T17:43:32.087632+00:00: concrete binding bundle, root runtime-blocker fixes and offline replay


**Question and prior evidence.** The offline default-Scotch N128 mapping reduces logical cross-NUMA-group faces 371,658 to 354,658 (4.5741%) while preserving all partitions and total faces. The solved NUMA-aware decomposition was slower, and new shared density tests did not establish a mean advantage for fewer ranks. The distinct question is whether CPU binding alone improves the same Scotch partition on the same allocated node. A face reduction is not a runtime result or bottleneck diagnosis.

**Change and control.** Prepared a fresh, unsubmitted bundle nscc-cpu-rank-placement-pair128-20261022. Both arms copy the exact same accepted default-Scotch N128 artifact into independent per-job cases. Both restore original fields, perform complete native renumberMesh, potentialFoam, applyBoundaryLayer, and 40-step simpleFoam with unchanged numerical work and function objects. Default binding is the control; the candidate maps existing rank IDs to CPU cores using the frozen group assignment and fresh allocation topology. Both use identical explicit XRC=0, SRX=1, OMP=1; transport is not the treatment. No processor-folder relabeling or mesh/physics/source change is proposed.

The new bundle gates original source hashes/CUT_READY/ranks/cell count and all stage return codes, full fixed-work/timer/force outputs, restored-field equality and before/after noWrite field seals. Fresh default rank probes must prove one host/128 unique physical cores/eight NUMA groups with contiguous 16-rank blocks. The rendered candidate binding must pass a separate exact rank/CPU/NUMA probe before initialization. Binding applies to all candidate initialization and solver launches. Startup probes do not establish page residency, solver-time migration or measured MPI waits/traffic. Physical cores are not inferred from logical CPU count alone.

**Root review and fixes.** Static syntax checks alone missed concrete runtime failures: lexicographically sorted processor directories compared with a numeric-order expected list; a validator looking in CASE/logFiles while the batch script wrote elsewhere; the FI environment regex dropping actual variable names; and a deadline starting after setup. All were fixed before deployment/submission. Both directory lists are now sorted identically, the real log/validator path is shared, explicit transport settings are recorded, and the deadline starts before modules/probes/copies. The documented PALS command-level --cpu-bind follows -np. Restore sources RunFunctions in a checked bash -ec child. Every timestep must be positive and finite; all 39 logged samples match time-function samples, cumulative times and mean. Cd bounds are diagnostic only, not an invented Basic acceptance tolerance. The stop rule retains the predeclared 3% practical mean gain threshold for considering reverse confirmation.

**Actual qualification.** Root's runnable qualify.py validates all eleven payload hashes, bash/Python syntax, retained historical control/candidate native cases at their production log paths, topology guards and processor names. The two historical 25907325 cases replay 39 samples each with maximum log/time-function difference zero, means **14.78722381225641 / 14.64023290833333 seconds/step**, and preserved 21.120703363-second Time-9 candidate outlier. These are historical validator replays, not a new placement run. The historical default topology passes; a synthetic candidate arrangement tests validator logic only. Duplicate CPU, duplicate rank, mixed host and a distinct-CPU but wrong expected binding all fail. A processor0..processor127 directory fixture tests actual directory-list helpers and detects a missing processor; it is not a mesh or input-acceptance fixture. The qualification records local Python 3.9.25, exact payload hashes, sources and limits. Actual compute-node source/binding/copy performance remains unverified.

**Cost, order and stopping rule.** One exclusive node/128 allocated CPUs/440 GB/no GPU/29 minutes, maximum **61.866667 SU**, normal routing with fresh policy checks required before launch. A 28:30 remaining-time deadline bounds expensive commands and leaves nominal cleanup time; PBS walltime is the hard stop. EXIT diagnostics cannot be guaranteed after SIGKILL/node loss, and wrapper resources are not final PBS billing. File-copy duration/space is not measured; do not assume the full pair fits from older unpaired runtimes. Control then candidate is the explicit first order. Close this mapping if gain is below 3% or a validity gate fails; only consider a separately budgeted reverse pair after a valid qualifying result. No four-node score or established speedup is claimed.

**Submission decision.** At **17:40:31 UTC**, six shared four-node jobs remain queued and zero CPU allocations are active. They are outside this worker's ledger and controller/ceiling coordination is unresolved; preserve them. A bounded depth-two search in the shared work root found no controller/ledger document beyond template README files. This static preparation, replay and probing logic consume **zero cluster SU**. No remote payload deployment, qsub intent, reservation or receipt was made; our commitment remains **170.866667 / 1,000 SU**. Eventual submission must use fresh capacity/project checks, existing ledger lock, complete durable reservation/intent and one qsub with ambiguity handling; it must not bypass combined caps. No automatic schedule, AI change or submission-material update was made.

**Preservation and next step.** Safe payload, offline qualification, failure corrections, source lineage, queue snapshot and unsubmitted plan are a separate small checkpoint. [Plan](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-rank-placement-pair128-20261022/PLAN.md), [pre-submit review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-rank-placement-pair128-20261022/PRE_SUBMIT_REVIEW.md), [qualification](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-rank-placement-pair128-20261022/qualification.json). The causal two-node H/S256 comparison remains a separate, higher-priority endpoint confirmation when controller/cost gates allow; do not blindly duplicate shared sweeps. Existing raw collections and submitted payloads remain unchanged.
