# Separate Codex chats: HPC and GPU

Owner assignment reaffirmed on 21 October 2026. Match CODEX_THREAD_ID to the
explicit named-session map in AGENTS.md and CURRENT.md. This shared document
does not assign every reader the same role. Sharing one filesystem and archive
does not make the two conversations' work or current findings interchangeable.

| Owner-designated chat | Own research | Compute/project | Primary source and handoff |
|---|---|---|---|
| HPC | OpenFOAM v2512, CPU case preparation, partitioning, MPI, validity and seconds/step | Iris CPU practice; ASPIRE-2A CPU project 59000042; Gadi only if actual access/project is established | 2026-APAC-HPC-AI/hpc-experiments; workspace/notes/HPC_CURRENT.md |
| GPU | Qwen serving, inference optimization, AIPerf, accuracy and goodput | Firmus H200; ASPIRE-2A+ H100 project 59010042 | 2026-APAC-HPC-AI/qwen-experiments; workspace/notes/AI_CURRENT.md |

HPC must not submit/cancel GPU jobs, change serving payloads, reconcile the
GPU worker's ledger or treat GPU results as CPU evidence. GPU must not mutate
HPC case inputs, jobs, measurements or the dedicated CPU ledger. Read-only
shared-access and queue-capacity checks are coordination, not ownership of
the other track. Preserve the common VPN and existing SSH connections; do
not restart or disconnect them merely to inspect a different cluster.

Read README.md and CURRENT.md for global orientation, then follow the role's
own handoff. CURRENT.md is now the shared routing index; AI_CURRENT.md and
HPC_CURRENT.md are track-specific. The previous shared Qwen context is retained
as history and does not switch an explicitly assigned chat to another track. When shared policy or root
AGENTS.md applies to both, phrase it by role rather than declaring every chat
HPC or every chat GPU. Use selected role-owned capture paths, review the staged
set and preserve others' pending work in the shared Git archive.

Only conversation metadata was inspected for the requested name check; no
other conversation transcript was imported. The first lookup checked exact
short names and the database title column, so it missed the actual named
sessions. That limitation is historical. A corrected read-only query uses the
threads.name column: both names end in commit, HPC or commit, GPU. The current
CODEX_THREAD_ID matches the HPC name and does not match the GPU name. The
shared [verified mapping](track-ownership-20261021.md) retains the IDs and the
GPU worker's independently recorded check. Database title is not the renamed
session name. No session database, transcript, credential or authentication
cache is copied into research or Git; conversation routing IDs are not tokens.

OpenAI's [CLI documentation](https://learn.chatgpt.com/docs/codex/cli) describes
saved conversation/resume behavior; actual role ownership here is the owner's
instruction, not something inferred from that generic documentation.
