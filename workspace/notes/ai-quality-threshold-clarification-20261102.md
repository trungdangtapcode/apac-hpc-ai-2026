# Quality threshold, actual known numbers and submission — 2 November 2026

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
