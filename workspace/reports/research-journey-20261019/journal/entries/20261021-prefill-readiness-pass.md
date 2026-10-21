# Uniform eager TP4 prefill reaches native readiness — 21 October 2026

The GPU/AI session resumes after the explicit ownership correction. Probe 223005
is terminal F/exit 0 after 406 seconds, four H100, estimated 57.742222 SU pending
posted reconciliation. Payload subset and raw seals pass. Replaying the actual
artifact guard confirms four NIXL ranks, both graph-disable paths per rank,
eight BF16 KV entries and HTTP/native readiness. This clears the previous
observed rank-divergent graph initialization at the isolated-prefill level.
It does not certify a specific deadlock cause, full PD transfer, actual token
equality, quality or speedup; the successful probe uses a different node.

The full [run review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-prefill-graph-gate-20261021/REVIEW.md)
retains 66 startup samples, actual GPU coverage, missing later thread-locality
capture, unconverted node counters and controlled teardown messages. Health
may execute internal one-token work; no user benchmark requests were sent.
No TTFT/ITL or throughput score exists. Missing fields are not zero or healthy.

Next derive a distinct full 16-GPU correctness repair from frozen 222780. Add
only native prefill graph disable to both prefills; retain decode, BF16/unquant,
FP8 target, NIXL/source/corpus and exact 1600-ID gate. Fix orchestration deadlines
to reserve a useful token-check/cleanup window within the original 30-minute cap.
Fresh locked GPU budget/queue and definite submission receipts are still needed.
A short/load screen remains conditional on complete native/runtime/output gates.
Capture this completed-run review separately before a preparation/submission
checkpoint. HPC payloads, queues, handoff and CPU budget remain unchanged.
