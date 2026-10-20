# Persistent APAC research context

For work about APAC-HPC-AI2026, Qwen serving, either cluster, Slurm/PBS, VPN,
research progress or the user's tutorial, first read:

1. `/home/apacsc42/workspace/notes/README.md`
2. `/home/apacsc42/workspace/notes/CURRENT.md`
3. The relevant linked tutorial/plan and actual scheduler state when needed.

The user explicitly asked to preserve knowledge from conversations and not make
them repeat instructions. Record new explanations, decisions, measurements,
failed attempts and corrections in the linked notes during the same turn.
When correcting an old claim, update the current answer and mark older accounts
historical. Preserve raw run artifacts. Never present a dated snapshot as live.

Use concise Vietnamese for chat only. Use English for the codebase and all work
artifacts, including code comments, documentation, research plans, reports, notes,
tutorials, and submission materials. This supersedes earlier permission to write
tutorials or learning notes in Vietnamese. Qwen track only; keep HPC_Task folders
empty. Do not change submission materials unless relevant/authorized.

Scheduled Codex runs are fresh sessions using file handoff, not forks of the
user's chat. Keep POLICY.md, CURRENT.md and reports consistent. They cannot send
messages into the original chat. Do not promise automatic chat notification.

Never write passwords, OTPs, recovery codes or authentication/session material
into notes. Existing authentication may be used without exposing its contents.
Respect current user steering and the current research budget; do not infer
additional authorization from historical notes.

Codex autopilot is disabled at the user's explicit request (2026-10-16 13:42:29 UTC).
Do not re-enable it, create replacement schedules, or launch background Codex
without a new explicit user request. Existing GPU jobs, the non-AI Slurm watcher,
and VPN are intentionally left running.

Write user-facing notes and plans in readable prose with normal word spacing.
Explain unfamiliar terms and keep implementation evidence separate from the main
explanation. Do not compress prose into concatenated words or acronym strings.

## Active workspaces and research archive

Edit work once in its active source directory:

- `/home/apacsc42/2026-APAC-HPC-AI`: research code, configurations, job scripts,
  experiment plans, logs and raw results.
- `/home/apacsc42/workspace`: persistent notes, tutorials, reports and submission
  materials. Keep existing submission restrictions in force.

`/home/apacsc42/apac-hpc-ai-research` is the local Git archive of both source
trees. Do not manually develop three independent copies. At each completed work
milestone, capture the relevant source changes and new evidence into the archive,
screen for sensitive material, verify the capture and commit the safe changes.
Preserve failed runs and provenance; use actual dates for new commits.

Large retained artifacts belong in
`/home/apacsc42/apac-hpc-ai-research-artifacts`; keep the archive's manifests,
hashes and recovery metadata consistent with the captured files. A Git commit
alone does not include those external objects. Do not copy authentication state,
private VPN caches, credentials, model weights or disposable runtime caches.

There is currently no automatic synchronization or incremental capture service.
Perform captures explicitly during authorized work; do not enable background
Codex or schedules. Report any uncaptured changes honestly. The initial snapshot
builder refuses an existing Git repository; do not bypass that guard or rebuild
over the archive. Preserve the existing history when adding later captures.

The owner authorised the private GitHub repository
`https://github.com/trungdangtapcode/apac-hpc-ai-research` on 19 October 2026.
GitHub CLI authentication is configured outside the archive. During authorised
work, capture, verify and commit each completed milestone, push safe Git changes
to the existing private origin, and verify that origin/main matches local HEAD.
This is an explicit workflow, not an automatic mirror or background schedule.
The sibling artifact store has not been uploaded by Git and still requires a
separate off-host copy. Never capture GitHub CLI credentials.

Use descriptive conventional commit subjects such as `feat(bench): ...`,
`fix(nixl): ...`, `research(load): ...`, `docs(...): ...` and `chore(...): ...`.
Do not use generic `Import records...` titles for the research history. The
owner-requested reconstruction aligns existing record author/committer dates
with retained metadata; its mapping is in provenance/. Ordinary new work uses
actual dates. Preserve that audit trail and do not routinely rewrite history.

## Continue the authorised research loop

The user reaffirmed on 19 October 2026 that an available research queue must not
be left empty merely because the preceding branch lost. During active authorised
work, review completed runs, research the next distinct hypothesis, check budget
and queue capacity, then submit the justified followup without another reminder.
A status request during this research is also a checkpoint for continuing that
loop, not a reason to do repeated status-only turns while feasible work is idle.
Close unchanged losing branches; do not interpret their stopping rules as a
global research stop. Preserve queue positions, acceptance gates, budget and
active-job caps. Do not submit blind duplicates solely to fill a queue.
This does not re-enable background Codex, autopilot, schedules or automatic
chat notifications.

## Commit small checkpoints and push promptly

The user explicitly requires frequent backup commits. Split work into small,
coherent checkpoints and commit/push each checkpoint as soon as its files are
safe and reviewable. Do not accumulate several experiments, unrelated fixes,
code changes and reports into one large end-of-session commit.

Typical separate checkpoints are a hypothesis with its scripts/configuration,
actual submission receipts with reservation changes, one completed-run review
with its interpretation, a fix, and a documentation update. Keep files needed
for one reproducible change together; do not split mechanically by file count
or create empty commits to inflate history. Do not wait for GPU completion or
an entire experiment wave before backing up already completed work.

Edit active sources once, capture only the checkpoint's relevant safe paths,
verify the capture, use a descriptive conventional subject with actual dates,
push to the existing private origin, and verify origin/main matches local HEAD.
Review staged paths explicitly; do not sweep unrelated pending work into a
commit. End each work turn with a safe checkpoint or identify exactly what is
still uncaptured or unpushed. Preserve frozen evidence and the existing history.
Keep credentials and session state excluded, and preserve external artifact
manifests/recovery metadata. This is an agent workflow, not authorisation for
a background watcher, automatic schedule or extra GPU spending.

## Preserve the complete research reasoning

The owner clarified on 19 October 2026 that records must cover the whole journey,
not just the newest result. Use workspace/reports/research-journey-20261019/journal/README.md
and its entry template as the reading/writing route. For each reviewable research
milestone, retain the question and prior evidence, hypothesis, exact change and
control, job/bundle IDs, observations with metric units, assessment and limits,
next decision and any corrected interpretation. A status line or job-ID mention
alone is not a complete analysis. Preserve failed and losing branches. Label
retrospective summaries honestly; never invent missing original dates, reasoning,
chat statements or measurements. Link new records into the journey/index during
authorised work and capture/verify/commit/push small milestones. The dated
coverage audit verifies retained written material, not every past chat message
or external object byte on GitHub. This does not enable schedules or extra GPU
spending.

## Inspect beyond the contest score

For each completed run, record what was collected, what was inspected, findings,
limitations and the next hypothesis. Review tail latency/errors/concurrency,
role-specific batch/queue/inflight and KV state, runtime/transport logs,
available CPU/GPU diagnostics and cost evidence. Missing hardware telemetry
must be marked not collected or not inspected, never zero or healthy.
Use bounded matched hardware/server sampling and phase markers in future derived
bundles after validating interfaces and monitoring overhead. Keep heavy profiles
outside ranked scoring and preserve frozen submitted payloads. GPU utilization,
KV token occupancy, sampled VRAM and kernel-time sums are different quantities;
do not infer a causal bottleneck from a score or an aggregate alone.
Read the 20 October observability report linked from CURRENT for actual coverage
and its profiler HTTP response correction. The correction and resource collector
are deployed only through later derived bundles; CURRENT records actual rollout
and evidence limits. Never change already submitted payloads in place.
