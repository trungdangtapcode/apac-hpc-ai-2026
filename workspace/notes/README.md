# Persistent APAC research notes

Read [CURRENT.md](CURRENT.md) first to identify the current chat's track. GPU/AI
uses [AI_CURRENT.md](AI_CURRENT.md); the separate HPC chat uses
[HPC_CURRENT.md](HPC_CURRENT.md). The owner explicitly confirmed these are two
different sessions on 21 October. Shared files and the latest writer do not
change ownership. Handoffs are dated; query the relevant real scheduler when
needed. Preserve the other track's jobs, payloads, measurements and budget.

Use Vietnamese for chat only. All new code, documentation, notes, reports and submission materials are English. Historical raw records keep their original bytes and may retain Vietnamese text.

| What do you need? | Where to read |
|---|---|
| Learn the AI journey and explain it in a presentation | [Beginner narrative](../reports/ai-research-learning-journey-20261023/README.md), [speaker notes](../reports/ai-research-learning-journey-20261023/SPEAKER_NOTES.md), [glossary](../reports/ai-research-learning-journey-20261023/GLOSSARY.md) |
| HPC task explanation, rules, baselines and experiment plan | [HPC research](../reports/hpc-openfoam-20261021/README.md) |
| Learn the HPC track, its complete research story, figures and presenter script | [HPC learning and presentation guide](../reports/hpc-research-journey-20261023/README.md) |
| Combined presentation: 32 AI slides + 8 HPC slides, portable CPU scripts and native logs | [23 October combined delivery](../submission-review/hpc-update-20261023/README.md) |
| Latest AI research presentation, PDF and speaker notes | [22 October presentation](presentation-update-20261022.md) |
| Complete submission, deployment, measured logs, slides and PDF | [21 October full delivery](submission-update-20261021.md) |
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
