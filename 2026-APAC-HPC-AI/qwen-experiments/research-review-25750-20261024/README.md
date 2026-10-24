# H200 EAGLE3: draft portability passed; diagnostic metadata gate failed

Job **25750** failed with scheduler exit **1:0**, after **341 seconds**. This is a failed experiment, not a completed correctness result. It produced no target output IDs or performance score.

The previous job 25682 stopped because local filesystem device IDs were incorrectly compared across nodes. S42 replaced that comparison with full per-role byte verification and retained local read-stability checks. This hypothesis is supported: all three actual role receipts pass, including g4. The draft/config/publisher bytes have the pinned hashes and sizes in every role's filesystem view; g4's differing device ID is local metadata, not different draft content.

All sixteen target/draft worker ranks initialize and pass the BF16, NIXL, graph and resolved-runtime checks. The following geometry validator then fails before semantic pair warmup. All **32 real before/after receipts** exist. Both prefill roles report head fields 1/4; decode reports both fields as **not_collected**. All have 190 regions. The old validator applies the prefill head signature to decode and rejects these actual records.

Pinned `disaggregation/decode.py` constructs its KV manager before it conditionally assigns those head fields in the staging branch. Registration observations therefore cannot be required to contain values not yet assigned. The correction must preserve unknown values, rather than fabricate decode heads or remove rank checks. S43 is a separate frozen derivation with a narrow decode-role/TP8/page1/190-VRAM-region/256-byte-stride exception, bound to actual model configuration. All native transfer, semantic warmup, reference and 1600-ID correctness gates remain. CPU replay of the real receipts qualifies the validator only; actual output correctness remains unproved.

`REVIEW.json` records per-role geometry and startup telemetry inspection. Role hardware samples, runtime/transport startup logs and phase markers were collected and inspected. Last sampled VRAM/activity values describe startup only; there is no scoring phase, latency distribution, generated-request queue or kernel profile. No inference about an idle serving bottleneck follows from them. Native speculative acceptance and official accuracy are not measured.

For a presentation: “The model now starts on all sixteen GPUs with identical verified draft bytes. The next failure is in our diagnostic assumption about when decode metadata exists, so we fix that assumption while preserving the actual output checks.”
