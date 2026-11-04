# Equal-TP recovery and preserved losses

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Would a separately scoped equal-TP8 descriptor route make the transfer path reliable at larger request loads?

## Why investigate this?

After the first patch enabled a real request path, this branch tested another parallel layout and descriptor route. The rationale is retrospective from the sequence of topology recovery experiments: a path that works at a small load may still fail eligibility as concurrency rises. The evidence should be used to understand the tested option, not as proof that equal TP itself is intrinsically unsuitable.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Parallel layout/transfer route | Heterogeneous prefill and decode TP widths. | A separately scoped equal-TP8 descriptor route; related partial and timeout attempts were retained. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 job 22809 | 1,507.96 good output tokens/s at N32; 95.38% joint SLA fraction. |
| Larger loads | N40 and N48 attempts did not meet eligibility. |

## What did we learn?

- A scored N32 run was possible, but it did not meet the joint request-quality gate.
- Higher-load failures made this branch unsuitable for promotion under the tested setup.

## Decision

Do not select this branch; retain the failures and continue from the denser split baseline.

## Limits and remaining questions

- The score is not comparable with other runs at different layouts or loads.
- No evidence isolates TP equality as the cause of SLA failure.

## Sources

- [journal/JOURNEY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/research-journey-20261019/journal/JOURNEY.md)
- [nixl-equal-ondemand/README.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/nixl-equal-ondemand/README.md)
