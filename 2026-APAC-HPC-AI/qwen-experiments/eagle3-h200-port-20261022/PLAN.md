# Native H200 EAGLE3 correctness route

## Current continuation — 22 October 2026

The target-only native reference is now frozen and submitted as **25495**; the separate speculative candidate remains unsubmitted. Full target/image byte verification passed 34/34 current files. A fresh full draft verification now passes its 1,145,943,008-byte publisher digest, all 15 tensor-header entries and the architecture-only adapter. [Target/reference receipt](../eagle3-h200-reference-run-20261022/RESULTS.md), [draft audit](../eagle3-h200-candidate-assets-20261022/REVIEW.md). The reference explicitly does not collect full KV geometry; a later derived diagnostic must add and review that instrumentation. No full H200 speculative correctness, performance or official accuracy result exists.

The dated design below is retained. Its statements that no reference is submitted, current byte hashes are unknown, or 25371/25373 are still pending are historical preparation state; AI_CURRENT and the linked definite receipts/reviews take precedence.

## Original unsubmitted design

This was an unsubmitted design recorded earlier on 22 October 2026. No allocation or result was created by writing it.

## Why this branch is still distinct

The current H200 target-only path is locally accepted and reproducible at N62, with a new accepted N64 point awaiting its own repeat. The load frontier is a small gain, not proof of a global plateau. Native EAGLE3 could reduce target decode iterations through accepted draft proposals, but no local full-model EAGLE3 correctness or performance result exists.

H100 failures exposed separate issues: inherited draft dtype/quantization, inconsistent prefill graph capture, shell-function dispatch, and an actual NIXL peer disconnect. The BF16/unquant layer probe and uniform eager prefill probe fix their narrow tested issues. The semantic per-pair warmup checker now rejects masked remote failures. The later no-model base-transfer, actual-descriptor and native-registration/DRAM probes pass, but do not prove production full-pool transfers or repair the original disconnect.

A native H200 port can investigate the full path without spending the limited H100 PBS budget. Its control is the actual working Slurm deployment, rather than a PBS launcher copied onto Slurm. The different hosts/network and known-good target-only path are experimental conditions, not proof that EAGLE3 transport will work. Preserve the original H100 failures.

## Two separate correctness allocations

First derive a target-only H200 exact-token reference from the working native H200 launcher. Then, only after its semantic review passes, derive one EAGLE3 candidate against that fresh H200 reference. Each is a separate 16-H200, two-node allocation with a hard ceiling of 17 minutes. Do not put two full startups into one allocation or borrow the old H100 outputs as an H200 reference. No ranked load test precedes correctness.

Reuse the already validated frozen input corpus and native `/generate` route: four cases with input lengths 22, 21, 22 and 4000, two greedy passes, sampling seed 2026, requested 200 output tokens per case, `ignore_eos`, and complete native output-logprob IDs including the first token. Require all 1600 output IDs, expected finishes, repeat stability and candidate/reference equality. Retokenizing decoded text is not a replacement. Independently replay the full result in the head process, rather than accepting launcher exit alone. These diagnostics are separate from official streaming AIPerf scoring.

Retain H200 target DeepGEMM/chunk8192 prefills, TP4 prefill and TP8/EP8 HPC-Ops decode, native NUMA, FP8 target/BF16 KV, FlashInfer/MNNVL, round-robin routing and the supported NIXL patch. For the speculative candidate, explicit BF16 compute and unquantized draft are required by the retained dtype evidence. Use native EAGLE3 steps 2 / top-k 1 / three draft tokens, with uniform eager prefill to avoid the demonstrated rank-divergent graph path. Decode graphs and other memory/capacity settings require explicit native runtime validation. Changes made for the correctness diagnostic must be recorded; later throughput comparisons need their own matched control.

Use the CPU-validated semantic pair checker after all expected workers/router are ready and before any output client. Preserve raw pair responses and bind receipts to the exact inventory and fresh experiment identifier; no authentication headers are retained. Failed or missing pair semantics stop immediately. Do not print a successful all-pairs marker from a masked child status.

## Asset identity and feasibility gates

The retained public draft is `nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507`, revision `ff0f0c0999f6c86b21dfd2f5803eebc4ac712224`, 1145943008 bytes, SHA256 `bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86`. Reuse the full draft verifier in the new payload. Never capture weights into Git.

Prior read-only local inspection found the H200 draft aliases point to the same 1145943008-byte file and the image has the same 26476240896-byte size as the H100 image. The 33 target files also matched retained names/sizes. This is not a fresh full checksum verification or proof that image/model bytes match between platforms. Revalidate the actual paths, target staging manifest, draft digest and image identity before freeze. The R3 token helper currently hardcodes H100 paths/platform/reference and must be derived explicitly for H200; do not mutate that frozen H100 payload.

Derive from native Slurm. Do not copy PBS `srun` aliases, host dispatch shims or task-status assumptions. CPU checks must exercise actual launch dispatch, expected role inventory, failure propagation, deadline handling, semantic warmup replay and full token-result rejection cases. Retain all payload hashes and exact source provenance.

Use one absolute startup deadline shared across workers, not a fresh deadline for each readiness wait. A prospective budget is startup at most 600 seconds, pair warmup at most 120, the eight-request exact-ID client at most 210, checks 20 and teardown 40, with a hard stop before 1020 seconds. These are proposed limits, not measured H200 startup guarantees. Validate sequencing and overhead against retained startup data before requesting the allocation; fail rather than silently extending walltime.

Collect bounded resource samples and phase markers. Add redacted native KV geometry per role/rank: region counts, layer IDs, dtypes, head counts, strides and byte spans, without raw pointers or peer metadata. Require all 16 expected ranks and consistent actual dtype/KV/graph arguments. This geometry should clarify what the earlier synthetic registration probes did not cover. Do not rewrite the frozen transport merely to make a candidate run.

## Decision after correctness

If fresh reference, semantic warmup, full candidate IDs or runtime gates fail, retain the earliest failing evidence and stop this exact attempt. Only a concrete supported repair justifies another full-model allocation. If correctness passes, prepare a separately matched short load pair, with explicit equal capacities and all quality/protocol gates. No speculative throughput gain is currently established. Official >=99% reference accuracy remains a separate unverified requirement.

The immediate queued work remains N64 replication 25373 and short N64/N68 screen 25371. P12/D4 stays withheld because equal-TP whole-pool descriptor setup is unbounded by actual candidate geometry. Review completed runs before choosing the next full-model allocation; never submit blind duplicates merely to fill capacity.

## Retained source routes

- `eagle3-reference-corpusfix-20261021/REVIEW.md`: real H100 target-only reference and ID route.
- `eagle3-pd-eager-prefill-r3-20261021/REVIEW.md`: actual full-PD disconnect and false warmup marker.
- `nixl-native-registration-probe-20261021/REVIEW.md`: native small-buffer registration/auxiliary pass and limits.
- `pair-warmup-semantic-20261021/PLAN.md`: independent semantic receipt protocol.
- `eagle3-screen-contract-20261021/PLAN.md`: future matched-capacity screen contract.
- `serving-tuning-10/s29-h200-observed-n62-full-control/`: native working Slurm control source.
