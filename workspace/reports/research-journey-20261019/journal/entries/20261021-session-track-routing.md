# Resolve shared-context ownership before continuing AI — 21 October 2026

The owner corrected the current worker to AI/Qwen and identified a distinct
HPC chat. Read-only local session-index and database name metadata, compared
with CODEX_THREAD_ID, confirm current GPU 01a15dd3 and separate HPC 01a1508d.
This is direct local routing evidence, not a claim about inheriting another
chat's conversation context. No complete database, transcript or authentication
state is captured.

Shared AGENTS/README had blanket "this chat handles HPC" wording. That was an
actual routing ambiguity because both chats share the same home workspace.
Replace it with explicit session ownership, make CURRENT a neutral router and
retain the former Qwen material in AI_CURRENT with its historical snapshot.
HPC_CURRENT and all HPC experiments are unchanged. A read-only HPC subagent was
interrupted immediately after correction; no HPC mutation or submission occurred.

This ownership checkpoint does not spend SU, mutate queues or promote a result.
The next AI action is to collect/review native TP4 probe 223005, whose fresh
scheduler state is F/exit 0 after 406 seconds. Exit status alone does not pass
its semantic/runtime gate. Preserve the completed-run review and choose the
next justified AI hypothesis within the existing GPU project lock/cap. Keep
HPC CPU project 59000042 separate from AI 59010042. No automation is enabled.
[Verified mapping](../../../../notes/track-ownership-20261021.md).
