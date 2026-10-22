# Fresh staged EAGLE3 draft identity

Verified 2026-10-22T17:23:30.717374+00:00. This CPU-only continuation checks the actual draft file reachable by a future native H200 bundle. No new Slurm or PBS allocation was made and no submitted payload was changed.

## Question and change

The current H200 full N64 result is independently reproduced near 3044.28 good output tokens/s. The queued full N64/N68 pair tests a distinct load hypothesis. EAGLE3 remains a correctness-first alternative: accepted draft proposals could reduce target decode work, but prior H100 full-model runs failed before a valid speculative output comparison. The freshly queued H200 target reference 25495 must pass before a speculative candidate is frozen or submitted.

The older native H200 port plan only checked draft alias/size information. Run `python3 verify-draft.py --output NEW_RECORD.json` from this directory to stream the current public draft once and compare its complete digest with the retained pinned publisher LFS record. The output is created exclusively; a failed attempt is retained and cannot silently overwrite an earlier result. The verifier also replays the safetensors header and verifies that the draft-only config adaptation changes only the architecture name.

## Observations

- Repository: `nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507`, revision `ff0f0c0999f6c86b21dfd2f5803eebc4ac712224`.
- Actual weight bytes: **1145943008**. Full SHA256: `bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86`; matches retained publisher LFS evidence.
- All **15** tensor-header entries match the retained inventory: **13 BF16** tensors and **2 I32** token-map tensors. No tensor execution is implied.
- Native adapter config SHA256: `fc9573a970a1afd1c78ca29df2837f0d3f9f577721590a2fa132b87f759c9433`. Only `LlamaForCausalLM` → `LlamaForCausalLMEagle3` differs from the retained publisher config.
- File identity (device/inode/size/mtime/ctime) was stable throughout verification. Elapsed streaming/header/metadata check: **2.162368 seconds**; this is a cached local file-read observation, not a GPU-startup forecast.
- No GPU, model execution, AIPerf, output-equivalence measurement, official accuracy evaluation or PBS SU was used. Weight bytes remain outside Git and its external evidence store.

## Assessment and next decision

The staged draft is intact and suitable for the next source/runtime preflight. This does not establish that H200 SGLang loads it correctly with the full target, that NIXL transfers the heterogeneous state, or that greedy output IDs match. Recheck identity at the eventual candidate freeze and retain its manifest in the result. Keep explicit BF16/unquantized draft settings and uniformly eager prefill from the narrow H100 repair evidence; do not interpret the draft's BF16 weights as permission to alter the official FP8 target.

Preserve pending jobs 25487/25488/25495. Review terminal 25495 semantic output and transport evidence before deriving a canonical EAGLE3 candidate. Prepare redacted actual KV registration geometry through a separate reviewed source derivation; full geometry is currently not collected in 25495. A later valid candidate would still need a separately matched load pair, not inference from speculative acceptance length. Official accuracy >=99% of reference remains unverified.

## Retained sources

[Exact current byte record](VERIFICATION.json), [repeatable verifier](verify-draft.py), [pinned publisher metadata](../eagle3-preflight-20261020/draft-file-metadata.json), [inspected header](../eagle3-preflight-20261020/draft-safetensors-header.json), [full target/image audit](../eagle3-h200-reference-assets-20261022/REVIEW.md), [reference receipt](../eagle3-h200-reference-run-20261022/RESULTS.md), [native port design](../eagle3-h200-port-20261022/PLAN.md).
