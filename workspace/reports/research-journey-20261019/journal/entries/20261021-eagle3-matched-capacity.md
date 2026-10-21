# EAGLE3 screen: match declared and initialized capacity — 21 October 2026

**Question and prior evidence.** Continue improvement without buying a misleading
comparison. The real reference 222761 and failed native candidate 222763 use
unequal implicit prefill limits. Neither the cached N1 reference nor a failed
startup is a throughput control. Full repair 222780 is uncollected while the
local VPN wrapper reports no live session; all five H200 queue positions remain
occupied. No authentication replacement or new DUO was authorised or attempted.

**Hypothesis and control.** After full integration/output equality passes,
compare EAGLE3 against a fresh target-only control at H100 N54. Both explicitly
set max-running-requests 64 on each TP4/EP1 prefill and 256 on TP8/EP8 decode,
with bfloat16 activations, FP8 target, BF16 KV, chunk 4096, HPC-Ops, MNNVL,
FlashInfer decode, round-robin, unchanged transport and common observers.
64 exceeds global offered concurrency 54, so this declared limit cannot itself
cap one prefill below total offered requests. The earlier 48 setting is not
shown to have been saturated. Draft/verification overhead and any native graph
resolution changes remain treatment effects to inspect, not hidden assumptions
of identical memory or graph coverage.

**Inspected evidence and correction.** Executing the exact retained native
_handle_eagle_family capacity AST branch verifies None becomes 48 and explicit
64/256/4096 survive that branch. This is not complete ServerArgs initialization.
The initial validator wrongly expected final 4096 already in the reference's
ServerArgs. Real logs show None there; later scheduler initialization shows
4096/4096/256. Failed 222763 shows 48/48/256 in early ServerArgs, with no final
scheduler-capacity receipts. The validator was corrected, and this failed local
assumption is preserved in ATTEMPTS.md. Never promote early argument values to
proof that a scheduler initialized with those values.

**Implementation and validation.** New audit-capacity.py reads all three roles'
early ServerArgs and final scheduler initialization logs. It rejects missing or
contradictory records, unexpected TP/EP/dtype/chunk/memory settings and differing
final capacities. This limited log gate is intended before future load traffic;
it does not certify actual tensor dtype, full runtime, token equality or quality.
Four native-branch cases and 11 synthetic log-gate cases pass, including missing
role, conflicting restarts, auto dtype, wrong TP/algorithm, native defaults,
missing final scheduler and a different final effective ceiling. Both historical
jobs' task logs are hash-linked and inspected. No GPU inference, new benchmark,
new score or SU reservation is produced by these CPU checks.

**Assessment and next decision.** The contract removes an avoidable experimental
confound and distinguishes requested from initialized state. It does not show a
performance improvement or prove the old request ceiling caused the bottleneck.
First collect/review 222780 actual state/graphs/transport/memory/IDs. Only a useful
passing integration permits frozen short screen payloads. Use fresh equally
observed control/candidate, 20/40/30, zero errors/cancellations, joint fraction
>=0.90 and prospective >=3% goodput gain before a full official matched pair.
Acceptance length is tokens/verification including bonus, never tokens/s.
Refresh queue and published ledger under lock before spending; retain outstanding
maxima, cap 51000 SU and 13000 SU buffer. No blind retries, sixth H200 job or
background automation. The accepted N62 submission stays unchanged because this
is an unmeasured prospective contract, not a promoted serving result.

**Preservation.** [Plan, code and validation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-screen-contract-20261021/PLAN.md),
[source hashes](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-screen-contract-20261021/source-provenance.json)
and dated queue/access observation are captured in a small research checkpoint,
then pushed and verified against live origin. Frozen job payloads and raw logs
are unchanged; no credentials/session material are recorded.
