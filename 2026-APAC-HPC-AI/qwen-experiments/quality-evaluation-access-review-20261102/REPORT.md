# What the public competition repository provides for quality verification

## Answer

The repository **does specify the quality requirement**, who runs it and how its reference is defined. The reviewed public revision **does not provide a runnable full-set quality recipe or numerical reference scores**. Submitting its sample Slurm/PBS jobs runs serving and AIPerf performance measurements; it does not automatically enrol a team in an organiser quality evaluation.

The latest public main observed on 2 November 2026 is `b4df52907f5bbb9152ef6ae902c925fc79d54417`. The recursive tree is complete, with 412 blobs. This review retrieved the two AI application notes, common baselines and all public Firmus/ASPIRE sample scripts/READMEs: 20 files. Their inspected contents contain no `accuracy`, `quality`, `mmlu`, `gpqa`, `lm_eval`, `evalscope` or `opencompass` invocation. The public issues API returned zero issues/PRs. These are statements about the reviewed public material, not private organiser infrastructure or team Slack.

## What Q1 actually says

The [official Qwen Q1 quality section](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/1.%20Qwen3%20AI%20Task%20Rules.md#q1-basic-vanilla) assigns full-set checking to the organisers. The required ratio is `submitted_stack_score / organiser_reference_score >= 0.99`. The reference is their own unchanged official FP8 model run, not BF16 model-card scores. Their checks are not restricted to a team-invented MMLU-Pro/GPQA pair. The text names model-card benchmarks and AIPerf checks non-exhaustively, without publishing a complete task list, revisions, prompts, generation/scoring configuration, aggregation method or reference result artifact.

The official reconstruction procedure is also separate: organisers rebuild the submitted stack under a dedicated account and invoke the fixed client through the team's gateway. No public quality-evaluation registration API, automatic submission mechanism or receipt was located in this review. Do not claim a quality evaluation is running merely because a compute job completed or a ZIP exists.

| Item found | What it establishes | What it does not establish |
|---|---|---|
| Q1 quality wording | Official requirement, evaluator responsibility and reference definition | A runnable team-side evaluator or a measured team quality score |
| Public deployment/AIPerf scripts | How to start services and measure latency-qualified throughput | Full-set answer correctness |
| Common performance baselines | Platform-specific performance context | The FP8 quality denominator |
| Qwen FP8 model card | Model provenance, serving examples and recommended generation practices | The organisers' same-recipe reference scores |
| Job 28197 | A successful complete portable deployment/performance acceptance | A full-set accuracy test or an organiser submission receipt |

Snapshots, URLs and SHA-256 identities are in `source-review.json`, `official-ai-files-manifest.json`, `official-ai-content-review.json` and `additional-sources.json`. `rules.md` retains the exact fetched quality wording. The downloaded model card is supporting primary-source context, not a substitute for the organiser reference.

## What is already available locally

An older, **unsubmitted** [MMLU-Pro protocol](../mmlu-pro-local-quality-20261024/README.md) exists from 24 October. It retains the full 12,032-row test Parquet and 70 validation examples, but its executable prepared screen selects only **128 questions**. This review independently verified both source-file hashes and the 128-question corpus hash and unique IDs. Its local results directory contains no completed response summaries. No inference was performed in this review.

Its comparator would divide candidate correct answers by an independently measured local reference correct count, with all errors retained. It does not use the organiser's reference. Its 0.99 gate is explicitly a small-screen triage rule, **not official certification**. The exact tokenizer/template preflight must pass before any generation. The native login Python currently lacks Transformers/tokenizers; a qualified existing runtime is needed. This is not a claim that the provided serving/client containers lack those packages.

The old protocol uses five-shot CoT, a 2,048-token output allowance, an official-local-evaluator 4,096-token context constraint, and the submitted server's 8,192-token context constraint. All prompt token lengths are still unmeasured here. Do not silently truncate prompts, remove examples, shorten reasoning output or treat the AIPerf 200-token output setting as an accuracy-evaluation recipe. No generation pilot supports an allocation-duration estimate yet.

## Concrete next steps and decision boundary

1. Preserve the current submission and its exact successful payload. Do not modify the 120-second ranked performance command to imitate a quality test.
2. For **internal regression evidence**, derive a separately labelled evaluation against an unchanged official FP8 control. Fix the same questions, dataset revision, prompt/template, generation settings and answer parser before comparing control and candidate. Verify prompt fit and native API behaviour without truncation, then measure a small runtime pilot before admitting a larger sample or full 12,032-question run. The old 128-question screen cannot be relabelled a full-set result.
3. Retain raw responses, errors, answer parsing and score provenance for both sides. Report each benchmark and its ratio independently; do not invent the organiser's aggregation rule or assume equality of output strings is its criterion.
4. An **official >=99% conclusion** needs the organisers' actual evaluation/receipt or their exact published recipe plus corresponding reference. The public sources checked here do not supply that denominator. A team-side matched check can reduce risk but cannot manufacture an official pass.

This turn performs source inspection and local corpus-integrity review only. No GPU/PBS job, authentication, budget reservation, organiser message/upload or submission-material change was made. Broad performance research remains stopped. The owner asked us to find the public information ourselves; no further request for the owner to locate it is needed.
