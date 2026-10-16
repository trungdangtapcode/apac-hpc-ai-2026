# Engine/speculation research branches — 2026-10-15

Designs and offline CPU preparation only: no engine/draft download, GPU execution, SU reservation or qsub.
Public metadata and source snapshots with commit IDs and SHA256 are stored in
`../inspection/wake-20261015-2007UTC/public-sources/sources.json`.

[EAGLE3 design](eagle3-01/design.json) starts with target-verified greedy decoding
and a matched8GPU nonspeculative control. The [draft model card](https://huggingface.co/lmsys/Qwen3-235B-A22B-EAGLE3/tree/d75f968c7d9d19ebdfb1a2fbdd176d61a032da14)
names Qwen3-235B-A22B; compatibility/acceptance for Instruct-2507-FP8 remains
unverified. Metadata/config were inspected, weights were not fetched.
[SGLang parameter documentation](https://docs.sglang.io/docs/advanced_features/speculative_decoding)
describes EAGLE3 draft/verification flags. Keep acceptance thresholds1.0; first
prove the installed implementation verifies every committed token with the
unchanged target. The small draft proposal deliberately begins3steps/topk1/4tokens;
this is a test choice, not a measured optimum. Preserve raw token IDs and cases;
small checks cannot establish official accuracy. PD comes after monolithic checks.

[vLLM design](vllm-01/design.json) starts with a pinned image/CLI and8GPU control,
then a separate16GPU PD trial. Inspected upstream [Qwen3MoE implementation](https://github.com/vllm-project/vllm/blob/d12ea8e309d71a79d2001255f500e9642cfe87ef/vllm/model_executor/models/qwen3_moe.py)
accepts quantization configuration; exact official checkpoint support still needs
runtime validation. The [NIXL matrix](https://github.com/vllm-project/vllm/blob/d12ea8e309d71a79d2001255f500e9642cfe87ef/docs/features/nixl_connector_compatibility.md)
lists MoE heteroTP support and requires matching model/cache/backend/connector
properties. Keep handshake checks and BF16KV; inspect the selected image rather
than assume current upstream matches it. The [usage guide](https://github.com/vllm-project/vllm/blob/d12ea8e309d71a79d2001255f500e9642cfe87ef/docs/features/nixl_connector_usage.md)
provides producer/consumer roles and proxy handling. Each worker needs a unique
side-channel port. Use native vLLM transport; the SGLang patch is engine-specific.
No vLLM image was present among inspected shared image filenames.

Ready backend pilots04/05 retain priority. Any new GPU job requires current
budget/queue/quality gates, one own PBS GPU job, <=16GPUs and <=45minutes, under
campaign16384SU total and project reserve13000SU. Model assets remain staged.

## Source follow-up16Oct00:55UTC

[Actual-image EAGLE3 review](eagle3-01/SOURCE_REVIEW.md) confirms target forward,
greedy argmax and dispatch to the compiled verifier at source level only.
Simulation can override real acceptance, so future workers must explicitly
record SGLANG_SIMULATE_ACC_LEN=-1. Match max-running-requests48 in the monolithic
control/candidate; initial comparison is all-greedy with neutral penalties.
Twelve static checks pass; no draft download, GPU validation, reservation or job.
Compiled CUDA behavior, Instruct-2507 compatibility and token equivalence remain
unverified; backend04/05 and loader06 priorities are unchanged.


## CPU token review16Oct02:05UTC

[Native-token review preparation](eagle3-01/TOKEN_REVIEW.md) adds an offline
comparator with30syntheticCPUchecks and6actual-image source checks. No real
capture, model/GPU validation or submission. Source normal text output includes
output_ids; preserve IDs/EOS/finish reasons rather than retokenize rendered text.
Draft compatibility, CUDA verifier and organiser accuracy remain unverified.

## CPU input suite —16Oct2026 05:38UTC

EAGLE3 now has 14 sealed native-token input cases in eagle3-01/token-suite-v1,
prepared offline with the pinned tokenizer/chat template. Retrieval inputs are
3788/7885 tokens including template; max input+cap 8085/8192. Consumer preflight
and byte-identical rebuild pass; no real HTTP/model output/EOS/GPU test, draft
download or submission. See eagle3-01/TOKEN_REVIEW.md; runtime/quality gates and
04→05→06 priorities remain unchanged.
