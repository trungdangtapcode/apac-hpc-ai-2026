# Prospective unranked performance pair: S55 control and S56 EAGLE3

## Research question

Under matched deterministic H200 P/D deployment settings, does enabling the already validated EAGLE3 configuration change N=64 short-serving throughput and latency? This is a distinct performance-feasibility question after the S49 exact-reference failure. It does not establish benchmark quality or resolve the S49 failed gate.

## Prior evidence and interpretation

Actual S46 target-reference job 25855 is accepted by its independent review. Actual S49 candidate job 25862 ended FAILED (Slurm exit 1:0, 557 seconds). Startup, all-rank deterministic BF16/NIXL runtime, 190-region geometry, both P/D semantic receipts, and candidate repeat stability passed. All four repeated candidate outputs differ from the accepted 25855 target across 1,600 IDs; first zero-based divergences are arithmetic 138, code 12, Unicode 11, and long4000 61. Keep that strict exact-reference result recorded as FAILED. The review states it is not an official quality verdict; the prospective pair therefore records quality UNKNOWN and omits the exact-ID stage from this separate performance-stage completion protocol. No prior performance score exists for S49.

## Controlled pair

- S55: S46-derived target-only control, no speculative decoding.
- S56: S49-derived EAGLE3 candidate, steps 2, top-k 1, three draft tokens, FlashInfer draft attention.
- Match all other server settings: H200 x16, P8/TP4 and D8/TP8/EP8, BF16 target and KV, deterministic inference, native NIXL base SHA-256 `912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f`, loaded through the instrumented connection wrapper SHA-256 `45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8` (the wrapper hash is the actual `QWEN_NIXL_PATCH_SHA256` checked inside each worker), prefill CUDA graphs disabled, decode graphs for batch sizes 1..64, prefill max-running-requests 48, decode max-running-requests 256, and chunked prefill size 8192.
- One N=64 point per arm, with 20 seconds warmup, 40 seconds measured, and 30 seconds grace. Generate fixed 4000 input and 200 output tokens, seed 2026, temperature 0, ignore EOS. Require the same 7-of-8 smoke floor and 12 retrieval requests on both arms.
- Keep fresh runtime checks, native per-rank geometry checks, and both P/D semantic paths. Expect target-only 188-region and EAGLE 190-region geometry, respectively; these are role-specific invariants, not mismatches. The inherited geometry checker validates native registration receipts and source-derived region counts; layer IDs are not collected and layer ordering remains unproven.

Each arm is a separate 16-GPU deployment and must stay within its own 17-minute allocation. Root review must select a matched execution order and confirm how scheduler placement/time variation will be reported. If conditions differ materially, report the two measurements as descriptive feasibility observations, not a causal speedup. No GPU or scheduler action is part of this preparation.

## Gates and reporting

Preparation gate: source hashes bind to S46/S49 provenance, actual S49 review, model/client images, and native NIXL source. The runnable bundles use identical worker/topology source; their single runtime branch adds EAGLE flags only for S56. CPU fixtures verify the paired settings and fail-closed head-check behavior. A separate cross-job replay reruns actual 25862 runtime/draft/geometry/semantic gates and actual 25920 raw AIPerf inputs/SLA/smoke/retrieval gates; the receipts are hash-bound, explicitly remain separate runs, and establish no performance result. The fixtures also confirm the exact-reference failure and quality-unknown state remain preserved. Allocation gate: root review and a root-owned controller are required. Runtime gate: fresh deterministic runtime and BF16 checks pass on all ranks, native role geometry is correct, and both semantic paths pass. Measurement gate: valid single N=64 interval, no request errors/cancellations, smoke floor and retrieval completion. Report latency percentiles, throughput, errors/cancellations and resource-observability coverage. Keep quality field UNKNOWN. Do not promote the candidate, claim a quality pass, or claim qualified speedup from one pair. MMLU remains optional, not run, and uncertified.

## Preparation status

Complete prospective runnable source bundles and CPU contract fixtures are prepared. They are not frozen or submitted. No GPU allocation, queue operation, endpoint request, model import, or performance measurement occurred. Root review and root-owned submission handling are required before allocation; the controller must submit from the bundle directory and pre-create `runs/` for Slurm stdout.
