# APAC session routing

Updated 2026-10-21T14:04:04.405544+00:00. This shared file routes each chat to its own handoff.
A shared filesystem does not change track ownership.

| Chat | Session ID | Handoff |
|---|---|---|
| GPU — AI/Qwen | `01a15dd3-3094-7712-a991-8ce55b15cbfe` | [AI_CURRENT.md](AI_CURRENT.md) |
| HPC — OpenFOAM | `01a1508d-26b0-7dd0-9dc1-f217ce0aff40` | [HPC_CURRENT.md](HPC_CURRENT.md) |

Determine the current session using CODEX_THREAD_ID and local session metadata.
The owner explicitly confirmed GPU belongs to the current AI worker and HPC to
a different Codex. Do not substitute a last-edited shared context for this map.
[Verified mapping and correction](track-ownership-20261021.md).

Each worker updates its own handoff and preserves the other track's queues,
payloads, measurements, credentials and separate budget ledger. Keep shared
Git checkpoints explicit and serialized. No schedules or background Codex.
The [previous shared Qwen/HPC snapshot](history/20261021-before-session-track-routing.md)
is historical; no source measurements were deleted by this routing change.
