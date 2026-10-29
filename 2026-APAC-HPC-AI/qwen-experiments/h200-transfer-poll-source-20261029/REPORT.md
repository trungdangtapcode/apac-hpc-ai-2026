# Decode-side transfer polling: source review and bounded trial proposal

**Reviewed:** 29 October 2026 UTC. **Image:** `/scratch/enroot-images/sglang-harbor.sqsh`, SHA-256 `b74ae77446bfedd6c5d72820b45be255cc513cf7c7c039d1bf63679c8178bfe5`.

## What the measured runs show

Full native control **26949** passed the local N64 performance protocol at **3034.761 good output tokens/s** (1895 requests, 98.628% jointly good, zero errors/cancellations). EAGLE candidate **27238** passed its local protocol at **2971.628 tokens/s** (1851 requests, 98.595%, zero errors/cancellations), but its configuration changed speculation and is not a matched control for transfer polling. Both runs sampled decode with about 50 running requests, zero decode queue, and transfer-request count around a dozen during the scored phase. Parsing the one-second decode log rows within the marker-bounded client interval gives:

| Job | Mean / median / p95 `#transfer-req` | Mean `#running-req` | Max sampled `#queue-req` |
|---|---:|---:|---:|
| 26949 | 13.01 / 12 / 19 | 49.21 | 0 |
| 27238 | 11.67 / 11 / 17 | 50.64 | 0 |

These are log counts, not direct network transfer bandwidth or a causal bottleneck measure. Sparse telemetry over the same request-start envelope reports decode GPU activity **100.0%** for 26949 and **93.76%** for 27238; estimated host CPU busy is **13.14%** and **13.48%**, respectively. The runs therefore do not show obvious host saturation. Raising a polling interval may lower scheduler polling work but could delay completed KV admissions and worsen TTFT.

The earlier receive-poll experiment is not this setting: H200 jobs **24927** and **24928** changed `scheduler_recv_interval` from 1 to 2, while the actual decode logs show `disaggregation_decode_polling_interval=1` in both. At N60, 24928 measured **2983.507 tokens/s**, versus **2971.312** for 24927 (**+0.410%**); that small single-run difference did not clear the >1% useful-gain gate and has no independent confirmation. Do not repeat that unchanged receive-poll arm or confuse it with the KV transfer queue below.

## Pinned source path

`server_args.py:3026-3030` defines `disaggregation_decode_polling_interval`, default 1, with help text saying values above 1 reduce polling overhead. The full source copy is in `evidence/sglang/srt/` and its hashes are in `evidence/SOURCE_MANIFEST.json`.

The actual consumer is `disaggregation/decode.py:2312-2342`, `process_decode_queue()`. On each decode scheduler pass it advances a counter and only, at the configured interval, drains preallocated requests, polls the decode transfer queue for completed KV using `pop_transferred()` (lines 1980-1997), and adds transferred requests to the waiting queue. The active decode loop calls `process_decode_queue()` each iteration; scheduler dispatch for decode mode is at `managers/scheduler.py:4805-4811`. The current 26949 and 27238 `ServerArgs` both resolve `disaggregation_decode_polling_interval=1`.

This knob does **not** reduce the number of in-transfer requests or change the incoming P/D receiver polling cadence. At interval 2 it halves these transfer-queue completion/admission checks from every decode scheduler iteration to every second iteration. Thus the plausible benefit is less repeated transfer-poll / metadata coordination work for the roughly 12 queued transfers, with an explicit risk of delaying their admission by a decode iteration.

## Decision and one bounded candidate

A source-qualified trial is feasible, but has low expected upside because current CPU sampling is modest and decode GPUs are busy. If selected, derive one candidate from the native target-only full control 26949: change **only the decode worker** to `--disaggregation-decode-polling-interval 2`; keep prefills, model, topology, transport, N64 cold workload (4000/200, seed 2026), timing, and all gates unchanged. Compare against 26949 and accept the branch only for a valid full local pass with >1% good-output-token/s gain, no material TTFT/ITL tail regression, zero errors/cancellations, smoke 7/8 without regression, and retrieval 12/12. A smaller or losing change closes interval 2 here; do not automatically try larger intervals. This is a proposal only; no GPU job was prepared or submitted in this review.

Limits: current performance telemetry uses five-second sampling over the request-start envelope, not exact phase boundaries; the transfer-request counts come from periodic server logs. Official 99%-of-reference accuracy remains unknown.
