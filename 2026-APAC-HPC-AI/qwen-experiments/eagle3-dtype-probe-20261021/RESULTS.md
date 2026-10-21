# Native shared-embedding dtype probe receipt

**222769.pbs111**, submitted 2026-10-21T05:51:56.649144+00:00, initially R; one H100/four minutes/max 8.533334 SU. No full target or attention inference. The fixture reads only the real official target embedding, compares native auto/BF16 configs and native shared-embedding input RMSNorm eager/graph behavior. [Plan and limits](PLAN.md).

Fresh own queue empty; locked Used 44393.346, Balance 18582.654, In Doubt 1024.000 SU. Retain unposted 222763 full maximum plus this maximum; conservative internal headroom 5574.120667 SU, unchanged 51000 cap/13000 buffer. [Reconciliation](reconciliation.json). No dtype hypothesis PASS yet; native full PD requires a separate derived job after actual fixture validation.

## Sealed fixture PASS — 2026-10-21T06:00:15.649406+00:00

157 seconds/estimated 5.582222 SU. Native auto FP16/shared BF16 mismatch reproduces; explicit BF16/unquant keeps target BF16/FP8 and passes native eager/graph norm with exact replay. [Full scope and limits](REVIEW.md).
