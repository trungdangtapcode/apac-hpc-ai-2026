# Persistent APAC research notes

Read [CURRENT.md](CURRENT.md) first to identify the current chat's track. GPU/AI
uses [AI_CURRENT.md](AI_CURRENT.md); the separate HPC chat uses
[HPC_CURRENT.md](HPC_CURRENT.md). The owner explicitly confirmed these are two
different sessions on 21 October. Shared files and the latest writer do not
change ownership. Handoffs are dated; query the relevant real scheduler when
needed. Preserve the other track's jobs, payloads, measurements and budget.

Use Vietnamese for chat only. New code, documentation, notes, reports and submission materials are English, except the owner's explicitly requested [Vietnamese slide transcript and bilingual guide data](ai-bilingual-transcripts-20261030.md). This narrow exception does not change submission language. Historical raw records keep their original bytes and may retain Vietnamese text.

| What do you need? | Where to read |
|---|---|
| Understand exactly what TP/EP do on the GPUs | [Under-the-hood walkthrough](../tutorial/22-tensor-expert-parallel-under-the-hood.md) |
| Count every retained AI GPU allocation and explore the research dependencies | [Run timeline and lineage](../reports/ai-run-lineage-20261103/README.md) |
| Separate Codex environments under one Linux account; diagnose launchers, state paths and migrations | [Practical Codex home guide](../tutorial/21-separate-codex-homes-shared-linux-user.md) |
| Recover the session list after moving CODEX_HOME; distinguish the temporary-directory warning | [1 November Codex recovery](codex-home-session-recovery-20261101.md) |
| Study the AI reasoning and practise presentation answers: start here | [Study entry point](../reports/teacher-qa-preparation-20261101/README.md) |
| Understand why each AI idea was worth trying and how the tests changed the decision | [Thinking process and hypothesis development](../reports/teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md) |
| Prepare answers to teacher Thanh’s questions, with actual evidence and limits | [Quick cards and detailed Q&A](ai-teacher-qa-preparation-20261101.md) |
| Current AI slides, bilingual scripts, final nine-run evidence and accepted portable deployment | [Current 12–13 minute narrative edition](ai-narrative-12min-20261103.md) |
| Teacher requirement closure and remaining human rehearsal | [Material-level closure](../submission-review/ai-basic-submission-polish-20261102/REQUIREMENT_CLOSURE.md) |
| Earlier gaps found before the final revision | [Historical requirement assessment](ai-teacher-requirement-audit-20261101.md) |
| Final exact packaged AI entry: accepted job and review route | [2 November accepted run 28197](ai-final-portable-acceptance-20261102.md) |
| Learn exactly how the quality experiment was designed, scored and preserved | [Detailed quality methodology](../reports/ai-quality-verification-20261103/README.md) |
| Actual owner-authorised local accuracy measurement and pilot jobs | [Quality verification stage](ai-quality-verification-20261102.md) |
| What ≥99%-reference quality means, exact known numbers and why Basic can be submitted | [Quality clarification](ai-quality-threshold-clarification-20261102.md) |
| Current final readiness, AI rule checks and remaining pre-upload items | [2 November audit](ai-final-preflight-20261102.md) |
| Historical readiness before the final presentation release | [1 November preflight](ai-final-preflight-20261101.md) |
| Latest AI queue and nine-run source/archive integrity check | [1 November audit](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-integrity-check-20261101/README.md) |
| Current bounded H100-to-H200 verification and job count | [Verification scope](ai-h100-to-h200-verification-20261031.md) |
| Latest actual AI queues, final job coverage and H100/H200 separation | [31 October queue/result reconciliation](ai-final-queue-reconciliation-20261031.md) |
| Current presentation: engineering investigation, visual reasoning and protected HPC handoff | [Current deck, guides and verified-source Q&A](ai-investigation-presentation-20261031.md) |
| Read or print the complete presenter transcripts as PDFs | [Vietnamese PDF](../reports/ai-final-report-20261030/TRANSCRIPT_VI.pdf), [English PDF](../reports/ai-final-report-20261030/TRANSCRIPT_EN.pdf) |
| Understand and rehearse every current slide: purpose, notation, axes, units, colors and tradeoffs | [Vietnamese transcript](../reports/ai-final-report-20261030/TRANSCRIPT_VI.md), [English transcript](../reports/ai-final-report-20261030/TRANSCRIPT_EN.md) |
| Learn the AI journey and explain it in a presentation | [Beginner narrative](../reports/ai-research-learning-journey-20261023/README.md), [speaker notes](../reports/ai-research-learning-journey-20261023/SPEAKER_NOTES.md), [glossary](../reports/ai-research-learning-journey-20261023/GLOSSARY.md) |
| Distinguish our own HPC experiments, borrowed recipes and the next actual owned-candidate job | [Own HPC research status](../reports/hpc-own-research-status-20261102/README.md) |
| Why the historical 22-second observation and recent relative gains differ; current direct best-recipe test | [Retained identity audit](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-absolute-time-audit-20261105/README.md), [reviewed six-arm comparison](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-best-recipes40-r2-20261106/STATUS.md) |
| HPC task explanation, rules, baselines and experiment plan | [HPC research](../reports/hpc-openfoam-20261021/README.md) |
| Visual HPC journey: hypotheses, measurements and decisions on NSCC and Iris | [4 November map](../reports/hpc-run-lineage-20261104/README.md) |
| Learn the HPC track, its complete research story, figures and presenter script | [HPC learning and presentation guide](../reports/hpc-research-journey-20261023/README.md) |
| Current HPC slides: Iris recipe comparisons, screening horizons and updated NSCC reproduction; AI preserved | [3 November HPC presentation](../submission-review/hpc-iris-slides-20261103/README.md) |
| Historical combined presentation: 32 AI slides + 8 HPC slides, portable CPU scripts and native logs | [23 October combined delivery](../submission-review/hpc-update-20261023/README.md) |
| Real portable replay, AI reader correction and current ZIP; HPC/slide bytes preserved | [29 October reader repair](ai-artifact-path-fix-20261029.md) |
| Final AI report, presentation, PDF and current submission; HPC preserved | [30 October journey/panel update](ai-journey-presentation-20261030.md) |
| Current submission, N64 deployment, measured logs and slides | [28 October AI delivery](ai-submission-update-20261028.md) |
| Latest checked public repository update | [Pinned upstream review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/upstream-review-20261020/REPORT.md) |
| Competition points, registration wording and specialist prizes | [Scoring and tracks](contest-scoring-and-tracks-20261020.md) |
| Official workload, ranking formula and units | [Closed-loop workload and Goodput × 200](official-goodput-clarification-20261020.md) |
| Current findings, corrections, queues and next steps | [Current handoff](CURRENT.md) |
| Per-run inspection beyond scores and remaining telemetry gaps | [Observability review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md) |
| Entire retained research reasoning and later entries | [Research journal](../reports/research-journey-20261019/journal/README.md) |
| EAGLE3 source checks, verified draft staging and exact-token diagnostic | [CPU preflight](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-preflight-20261020/REPORT.md), [staging](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-preflight-20261020/STAGING.md), [current token route](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-integration-20261021/TOKEN_ROUTE.md) |
| DeepInfer, what we already tested, and new locality/EAGLE3 leads | [Pinned review and preflight](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepinfer-review-20261020/REPORT.md) |
| Current priorities and immediate experiment | [Research priorities](../reports/research-priorities-20261020/PLAN.md), [completed startup-cost pair](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-20261020/RESULTS.md), [reverse confirmation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-confirm-20261020/RESULTS.md), [static locality probe](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-gpu-locality-20261020/RESULTS.md) |
| VPN duration, why it changed, and future configuration | [VPN session lifetime](../tutorial/19-vpn-session-lifetime.md) |
| Historical questions and explanations | [Conversation handbook](../tutorial/14-so-tay-hoi-dap.md) |
| Tutorials by topic | [Tutorial index](../tutorial/README.md) |
| User requirements and decisions | [Decisions](DECISIONS.md) |
| Mandatory dispatch, fallback and truthful status rules | [Research execution contract](research-execution-contract-20261027.md) |
| Important milestones and corrections | [Timeline](TIMELINE.md) |
| Dated session reports | [Latest reports](../research-autopilot/LATEST.md), [history](../research-autopilot/HISTORY.md) |
| Execution policy and budget rules | [Policy](../research-autopilot/POLICY.md) |
| Experiment ledger | [RUNS.md](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RUNS.md) |
| Serving comparisons | [Results](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/SERVING_TUNING_RESULTS.md) |
| Credit reconciliation and reservations | [Budget](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json) |

## Preserve the reasoning during the same turn

Record each new question, hypothesis, controlled change, job ID, observation with units, assessment, limits and next decision. Preserve raw failures and corrections. Use the [entry template](../reports/research-journey-20261019/journal/ENTRY_TEMPLATE.md). Correct the current handoff and mark superseded claims historical; do not erase their evidence. Never preserve passwords, OTPs, session material or other credentials.

The initial 19 October retrospective has 32 source-linked stages. Current document/job counts belong to the [dated coverage audit](../reports/research-journey-20261019/journal/AUDIT.md). The audit checks retained source/archive/Git bytes; it does not certify that every old chat statement survived or every job has equally complete reasoning.

Before submitting, review earlier outputs, runtime and output checks, costs and remaining uncertainty. Form a distinct hypothesis and control, check credit and real queues, then submit within the operating caps. Prefer useful information per SU; do not fill queues blindly or repeatedly test unchanged losses. A failed branch is not a global stop during active authorised research.

## Execution and readable handoff

Codex autopilot was disabled at the user's request on 16 October 2026 at 13:42:29 UTC. Do not enable background Codex or schedules. Existing jobs, the non-AI Slurm watcher and VPN may remain running. Fresh scheduled sessions would use file handoff, not this chat's context, and cannot promise automatic messages here.

Keep CURRENT concise, with history in linked records. Read only relevant history, avoid repeating immutable audits, and use normal word spacing. Explain unfamiliar terms and keep technical evidence linked separately.

## Backup and illustrated journey

The authorised private repository is [apac-hpc-ai-research](https://github.com/trungdangtapcode/apac-hpc-ai-research). Edit in the active research/workspace trees, then explicitly capture, screen, verify, commit and push each small coherent milestone. [Publication and recovery coverage](../reports/github-publication-20261019/REPORT.md) explains the archive. GitHub contains the Git portion; external large artifacts still require a separate off-host copy. There is no automatic mirror.

The [illustrated journey](../reports/research-journey-20261019/diagram/README.md) and [earlier 2938.628-good-token/s report](../reports/research-journey-20261019/REPORT.md) are dated records. Consult the current handoff and later journal entries for new peaks; do not present an older chart as live or mix H100 and H200 scores.
