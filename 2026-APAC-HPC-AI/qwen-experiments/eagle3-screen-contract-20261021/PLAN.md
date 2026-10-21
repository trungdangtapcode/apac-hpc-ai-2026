# Conditional EAGLE3 matched-capacity screen

This prepares the next comparison while all five H200 slots are occupied and
PBS access is unavailable. It is not a submitted bundle, GPU reservation or
permission to bypass the full 222780 integration review. The retained H200 N62
submission and accepted serving peaks remain unchanged.

## Question and controlled change

Can verified lossless native EAGLE3 improve the H100 N54 operating point by at
least 3% over a fresh, equally observed short target-only control? The current
N1 reference and its cached second pass cannot answer this throughput question.
The earlier screen route identified unequal automatic request limits. This
contract makes their intended control concrete before spending more SU.

Use two TP4/EP1 prefill workers and TP8/EP8 decode, the unchanged official FP8
target, BF16 activations/KV, both-phase HPC-Ops, prefill chunk 4096, FlashInfer
decode attention, MNNVL, round-robin routing, identical NIXL patch, native NUMA
policy and resource observation on both runs. Set explicit bfloat16 on both;
the layer probe proves it retains the existing target activation precision.
Declare max-running-requests 64 on each prefill and 256 on decode in both.
64 exceeds global offered concurrency 54, avoiding a lower artificial prefill
request ceiling even if routing is temporarily uneven. This does not claim
that the previous 48 limit was reached or caused a bottleneck.

The candidate additionally loads the unchanged pinned public EAGLE3 draft,
explicit bfloat16/unquant, steps 2, topk 1, three draft-token slots and native
verification. No output approximation, changed target weights or layer/expert
work. Keep requested graph controls common; inspect the actual algorithm-specific
resolved graphs separately. Equal flags do not establish identical graph coverage,
KV capacity or memory use; draft state and verification are part of the treatment.
Do not force unsupported graphs merely to make two log strings look equal.

## Source and historical runtime finding

The exact retained _handle_eagle_family branch assigns 48 only when the
ServerArgs max_running_requests field is None. The isolated native AST branch
keeps explicitly supplied 64, 256 or 4096. This is not the complete ServerArgs
pipeline or proof that any of those sizes fits full draft/target serving.

Actual 222761 prefill ServerArgs log None. Later initialized scheduler receipts
show 4096 per prefill, 256 decode. Actual failed 222763 prefill ServerArgs log
48, decode 256; it has no final scheduler-capacity receipts before failure.
Consequently, do not describe the failed candidate as an initialized 48-slot
scheduler, or treat an early ServerArgs line as the final allocated capacity.
The initial validator incorrectly expected 4096 already in ServerArgs and
failed against the real reference logs. It was corrected to preserve and
inspect both stages. Raw job records and submitted payloads were not changed.

## Before any load traffic

First collect terminal 222780 and review actual graph/state/transport/dtype,
memory and exact real IDs against the sealed reference. If it fails, select a
concrete supported repair or close the branch; this contract is not a retry.
Only a useful passing integration permits preparing separately frozen screen
payloads. Both require fresh lock-protected budget/own queue reconciliation,
unchanged cap/buffer, definite receipts and verified serial allocation.

In each derived screen, run audit-capacity.py against actual owned role logs
before the benchmark. It requires explicit matching ServerArgs plus final
scheduler receipts. No outer empty redirection logs, contradictory restart
settings or missing final capacity can pass. All roles must show expected
TP/EP, declared BF16 dtype, memory fraction 0.9, exact algorithm and prefill
chunk 4096. This limited log gate does not certify actual tensor dtype,
readiness, exact outputs or the complete native runtime; retain those checks.
Record actual KV slots, free/peak memory and graph coverage for both runs.

## Traffic, observation and stopping rule

Use closed-loop N54, fixed 4000/200, seed 2026, cold-prefix cache busting and the
original gateway/streaming/SLA data settings. Only durations change to
20-second warmup, 40-second measurement and 30-second grace. Label every export
short and unranked. Read canonical goodput.avg * 200 in good output tokens/s;
never compare this short score directly with the full 60/120/30 incumbent.

Require zero request errors/cancellations, joint SLA >=0.90, complete raw
requests and all native/corpus/model/transport gates. Inspect TTFT/ITL tails,
effective concurrency, role queues/running/KV, phase-aligned GPU/CPU/memory
samples and runtime errors. Keep heavy profiles outside traffic. Missing or
misaligned telemetry stays unknown. Acceptance length means output tokens per
verification forward including bonus; it is not tokens/s or a speedup estimate.

A valid short gain >=3% permits a fresh full official matched pair and justified
independent confirmation within budget. A lesser/negative result closes the
unchanged screen. If a distinct draft-step/backend hypothesis is supported,
record why and test it separately; do not retry unchanged to fill a queue.
Determine economical walltime from actual full repair startup, not a one-layer
fixture or a failed startup. No new SU is reserved by this plan. A hypothetical
two-job 30-minute ceiling would be 2048 SU, not a current charge or allocation;
fresh ledger and useful information per SU still govern whether it is warranted.
