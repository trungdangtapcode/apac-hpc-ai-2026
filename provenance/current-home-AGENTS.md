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
