# Matched local accuracy verification — 2 November 2026

## Authority and objective

The owner explicitly requested research and actual measurement to verify quality, after asking whether unchanged weights already established PASS. This authorises a new bounded AI quality-verification stage on the existing H200 Slurm cluster. It does not restart unrelated performance sweeps, H100/PBS spending, HPC work, VPN authentication or Codex automation. The current submission ZIP remains frozen during measurement.

The public Q1 rule uses the organisers' own full-set reference. Their full recipe/reference is not published in the inspected revision. We will measure a separately labelled local fidelity comparison against an unchanged official FP8 model; a local pass does not manufacture an organiser certification.

## Reference, candidate and common protocol

Reference: two independent stock SGLang TP8 colocated replicas, one per H200 node, published Qwen3-235B-A22B-Instruct-2507-FP8, BF16 activation/KV and context 8192. No mounted transport patch, custom MoE/attention/allreduce backend or graph tuning. This is an accuracy reference, not a Basic ranked colocated-performance submission. Colocation avoids conflating failure of the stock heterogeneous KV bootstrap with model accuracy.

Candidate: the accepted 28197 model-worker configuration: two TP4/EP1 DeepGEMM prefills/chunk 8192 and one TP8/EP8 HPC-Ops decode with FlashInfer, MNNVL and request-scoped NIXL metadata, native FP8 model/BF16 KV. Worker/config/environment/placement/transport bytes are copied unchanged from its frozen R2 payload. A derived driver replaces AIPerf with the quality client. This compares complete serving deployments, not a descriptor-only ablation.

Full source corpus: 12032 test questions and 70 validation examples from pinned MMLU-Pro, all 14 categories. The official five-shot CoT renderer and option preprocessing are retained. CPU preparation renders the exact pinned Qwen chat template, then deterministically reduces shots 5→0 until each question fits the original evaluator's strict prompt <2048 token budget with 2048 output allowance. Both stacks receive the exact same compiled prompts. Zero-shot fit failures block generation; no truncation, skipped IDs or denominator changes.

Greedy chat generation: temperature 0, top_p 1, max_tokens 2048, stop `Question:`, no automatic retries. Scoring uses the pinned upstream parser order, but unparsed output is wrong rather than an invented random guess. Service errors count wrong. Preserve raw responses, usage/finish reason, per-question prompt/token hashes, actual shots, parsed answers and provenance. The paired comparator verifies identical questions/prompts/settings, coverage and error counts before the accuracy ratio.

## Bounded admission and continuation

Initial phase: two independent pilot allocations, one reference and one candidate, each 16 H200/two nodes/max 17 minutes, combined maximum 9.066667 GPU-hours, zero PBS SU. Own active/pending cap 5 and shared Slurm admission lock remain. The pilot uses the retained deterministic 128 question IDs, 14 categories, concurrency 16. It qualifies real API, response format, parser validity and elapsed/token rates; it is not full-set proof. No ranked AIPerf score is claimed.

Startup is bounded by 600 seconds. Quality evaluation deadline is job-start+950 seconds with request timeout 120 and 10 seconds safety margin; incomplete execution stays incomplete. Every accepted job has a frozen manifest, test-only check, definite receipt and reservation. Preserve failed/partial runs and cleanup evidence; do not edit queued payloads.

After both pilots are reviewed, use measured completion/output rates to size a bounded set of full 12032-question shards at the same generation protocol and paired load. Freeze shard membership before inference, retain all questions and combine only exact complete coverage. Declare the resulting stage GPU-hour envelope before further admission; do not silently treat this initial pilot envelope as an owner-wide stop or as unlimited spending. Avoid unchanged retries without a distinct diagnosed fix. Full-reference/candidate ratio >=0.99 with no service/coverage failures is a **local benchmark gate**, not the undisclosed official multi-task certificate.

## Known preparation findings

The older 128-question client assumed a list from apply_chat_template. Actual Transformers 5.14.1 returns BatchEncoding by default; explicit return_dict=False restores pinned single-sequence tokens. This was diagnosed with the real supplied AIPerf image runtime and fixed before GPU admission. Seven fixture tests pass. Native CPU preparation uses the extracted provided client image without downloading weights/dependencies. Enroot image start lacked squashfuse and login cgroup mounting failed; the image's own loader/Python runs tokenizer-only preparation. No GPU is used by that preparation.

## Evidence and reporting

Record actual denominator, correct answers, per-category accuracy, candidate/reference ratio, discordant items, response errors and truncation/invalid-output counts. A pilot pass does not become a full-set result. Inspect worker/backend/model/tokenizer identity, request latency, output lengths, available GPU snapshots, transport logs and cost. Missing hardware telemetry is marked missing. Record results in the research journey and small explicit capture/verify/commit/push checkpoints. Model weights, private runtime homes, credentials and disposable container caches stay outside captures.
