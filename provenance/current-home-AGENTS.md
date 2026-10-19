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

GitHub CLI installation, authentication and upload remain deferred until the
user asks to proceed. Local Git and its sibling artifact store are on the same
machine and do not yet provide protection against loss of that machine.
