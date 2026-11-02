# Quality threshold, actual known numbers and submission — 2 November 2026

**Submission-status correction — 2026-11-02T14:50:38.446275+07:00, Vietnam time (UTC+7):** The owner reasonably interpreted “submitted” and “waiting for organiser quality evaluation” as an actual submitted quality test. That is not what occurred. Jobs 28194/28197 were cluster deployment/performance acceptance attempts; 28197 passed. Neither invokes a full-set model-accuracy harness. No competition ZIP or quality-evaluation request has been sent to the organisers by this worker, and no organiser receipt or active quality review is evidenced. UNKNOWN means not evaluated in the retained record, not an organiser evaluation already initiated and awaiting its result. Earlier wording about waiting described the intended official procedure too loosely and must not be read as an actual submission status. The local performance/deployment work is complete; official quality certification is not.

The owner asked for the exact quality number after the readiness report listed the organiser's ≥99%-reference evaluation as UNKNOWN. This distinction must be made clearly before giving more readiness advice.

## What is known and what is not

| Quantity | Exact retained value | Meaning |
|---|---:|---|
| Historical selected H200 N64 mean | 3044.400475 good output tokens/s | Performance from three historical full runs; not model quality |
| Separate native job 26766 | 3045.501509 good output tokens/s | One later native full performance observation |
| Joint request-latency fraction in 26766 | 1875/1902 = 98.58044164037855% | Requests meeting both TTFT/ITL limits; not an accuracy score |
| Recent local smoke screen | 7/8, without a new regression versus its local baseline | A small hand-written regression screen, not the official full-set test |
| Recent local retrieval screen | 12/12 | Another small diagnostic, not official model quality |
| Team's official full-set quality score | Not measured/reported | No exact score can honestly be supplied |
| Organiser's corresponding FP8 reference score | Not available to this team in the retained evidence | This is not the BF16 model-card score |
| Quality ratio versus that reference | Not calculable from available results | UNKNOWN means neither measured pass nor measured failure |

## What 99% means

For a corresponding evaluated score, the condition is `team_score / organiser_reference_score >= 0.99`. The exact official handling across their full set is not specified as a team-defined aggregation in the published text; do not invent an average across tasks.

Illustration only: if the reference is 80.0 points, retaining 99% means at least 79.2 points on that same score. It does not mean answering 99% of all questions correctly. It is also unrelated to the separate requirement that at least 90% of all performance requests jointly meet TTFT ≤3000 ms and request-mean ITL ≤20 ms.

## Why a Basic submission can still be sent

The official Q1 states that the organisers run the full-set accuracy check and rebuild the submitted stack under a dedicated account. Required deliverables are reconstruction instructions, the single-job deployment/official benchmark script, and presentation slides; profiling data are optional. The published Basic requirements do not make possession of the organiser's unpublished reference score a pre-upload prerequisite.

Therefore the team can submit its prepared Basic stack and measured performance while stating that official quality validation is pending. This does not guarantee that the submitted stack will pass. Fixed official weights, source/geometry checks and local output screens support the engineering argument but do not substitute for the organiser's quality result.

If experimental Bonus work is claimed, Q2 places a separate self-proof obligation on the team. Do not turn the Basic organiser-run procedure into permission to claim an unverified Bonus quality result.

## Separate final-entry acceptance

The owner separately authorised one final full run of the exact repaired packaged AI entry. That run checks deployment, real P/D semantic paths, the locked AIPerf client, repaired result reading, performance gate and cleanup. It remains a performance/deployment acceptance run, not the official full-set model-quality evaluation. Job 28197 has now passed the complete deployment/performance path at 3051.518173 good output tokens/s and 1881/1907 joint SLA success. That result does not fill in the missing official quality ratio. Only two startup semantic checks were performed in this acceptance; historical smoke/retrieval scores are separate.

[Official Qwen Q1: output quality and re-run](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/1.%20Qwen3%20AI%20Task%20Rules.md#q1-basic-vanilla), [retained exact rule snapshot](../reports/submission-readiness-20261102/official-rules/1.%20Qwen3%20AI%20Task%20Rules.md), [current readiness evidence](../reports/submission-readiness-20261102/README.md).

Correction to the earlier checklist wording: official quality pending is an acceptance limitation, not an assertion that the team is forbidden to upload its Basic package until it obtains the organiser's score. No score is fabricated, and no quality pass/failure is inferred from the absence of that evaluation.

## Independent public-source search — 2026-11-02T21:14:29.481792+07:00 (Vietnam time, UTC+7)

The owner asked us to find the recipe ourselves. [Source review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-evaluation-access-review-20261102/REPORT.md) checks current public main b4df5290, its complete 412-blob tree, 20 AI application/sample files and zero public issues. Q1 defines the threshold and organiser reference, but no runnable public full-set quality harness or numerical reference was located. Common baselines are performance, not quality denominators. The retained local MMLU-Pro corpus hashes pass; its prepared client covers 128 questions, not the full 12,032 test rows. No completed local response summaries exist. Prompt fitting and GPU inference were not performed. Internal matched FP8-control testing remains a separately labelled option; it cannot certify the unpublished official suite/reference. No new job, spending, auth, upload or message was performed.

## Why unchanged weights support an expectation, not a measured pass — 2026-11-02T22:07:32.939717+07:00 (Vietnam time, UTC+7)

The owner asked whether quality should pass because the weights were not changed. The appropriate engineering assessment is that the retained Basic approach gives grounds to expect a pass: it uses the published FP8 checkpoint without intentional requantisation, pruning or layer/expert skipping; BF16 KV is permitted; the submitted transport patch changes request-descriptor preparation rather than intending to change model mathematics. Backend/kernel/parallelism choices are allowed subject to correct computation. Source/geometry checks, working P/D routes and local output screens support that expectation.

Unchanged weight files alone do not prove correct inference. Runtime kernels, KV transfer/cache handling, tokenisation or generation settings can affect answers even with identical weights. Do not infer a numerical accuracy ratio from the performance pass, the 98.6366% latency fraction or two semantic warmups. No matched full-set accuracy/reference result exists in retained evidence. State “expected to pass based on the unchanged-model approach; not yet measured or organiser-certified”, not “quality >=99% PASS”. This is not a diagnosis of an observed runtime correctness failure, and does not mean the team has evidence that quality failed. No new job, spending, auth, upload or submission-payload change.

## Submission-facing wording correction — 2026-11-02T22:25:35.912318+07:00 (Vietnam time, UTC+7)

The owner objected to a main-slide “quality UNKNOWN/unverified” warning being presented as the submission conclusion. The [current Basic edition](ai-basic-submission-framing-20261102.md) leads with unchanged official FP8 model/precision and verified serving contributions. Evaluation workflow and honest measurement provenance remain in methodology/Q&A. This correction changes communication, not the evidence: no full-set quality score or organiser pass is manufactured, no unknown state is relabelled failed, and no raw quality/provenance record is rewritten. Two genuinely stale README replay-gap statements were also corrected to completed job 28197. No executable runtime change or GPU rerun.
