# Current AI / Qwen research handoff

Updated 26 October 2026, 08:19 UTC. This GPU fork 01a166eb-33cb-7ce0-9699-ec65de26689a continues AI parent 01a15dd3-3094-7712-a991-8ce55b15cbfe; it owns AI/Qwen only. The separate worker owns HPC/OpenFOAM. Chat Vietnamese; artifacts English. No background Codex, schedules or automatic chat notifications.

## Latest measured result: legacy full replay is lower today

Job 26313 (S69) COMPLETED 0:0 after 11:12 on g1/g4. Independent full workload/raw denominator/output audit passes at **2830.923547 good output tokens/s**, 98.427850% joint SLA, zero profiling errors/cancellations, smoke 7/8 and retrieval 12/12. Actual 15 legacy operational files are byte-identical to 25487; actual ServerArgs match except internal random seed, and all graph captures complete. This recovers the deployment/local protocol, NOT today's old 3k throughput. Official full-set 99%-reference accuracy remains UNKNOWN.

The frozen historical 25366/25373/25487 mean is 3044.400475 tokens/s. The new same-runtime replay is 7.012117% lower. Descriptive all-four repeat mean is 2991.031243; preserve the lower observation and do not cherry-pick the earlier cluster. Sparse resource samples do not establish why: decode sampled clocks 1980/3201 MHz and activity 100% match; prefill clocks/power differ by role. Post-score profiling stop 500 errors are retained separately from zero scored serving errors. [Full review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-26313-20261026/REVIEW.md), [repeat series](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-26313-20261026/repeat-series.json).

## Actual submitted queue: five jobs at 08:19 UTC

| Job | Purpose | Immediate state |
|---|---|---|
| 26315(S70) | Full modern control: prefill graph disabled/cap 64 | PENDING Priority |
| 26317(S71) | Full graph breakable/cap 64 | PENDING Dependency (afterany 26315) |
| 26319(S72) | Full graph breakable/native admission | PENDING Dependency (afterany 26317) |
| 26347(S73) | Full graph disabled/native admission | PENDING Dependency (afterany 26319) |
| 26337(S68r2) | Source-corrected no-model NIXL fanout | PENDING Priority |

These are dated snapshots; query actual scheduler before another admission. Four serving arms complete a 2x2 graph/admission design at N64/fixed 4000:200/client seed 2026/full 60:120:30. S70/S71 and S73/S72 compare graph at fixed cap; S70/S73 and S71/S72 compare admission at fixed graph. Every local native/runtime/graph/KV/semantic/raw SLA/error/output gate remains. Need >1% useful valid paired gain before proposing independent confirmation. A failed control blocks paired interpretation; afterany is scheduling, not acceptance. No result exists yet for these five. [Full receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-incumbent-recovery-20261026/submission-receipts.json), [S73 admission](../reports/research-journey-20261019/journal/entries/20261026-s73-submitted-26347.md), [fresh snapshot](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-incumbent-recovery-20261026/S73-POST-SUBMIT.json).

Each serving job requests 16 H200/two nodes/at most 17 minutes; component 26337 uses 16 H200/two nodes/at most 5 minutes. Own cap 5. No PBS SU. Preserve positions and frozen payloads; no blind duplicates or promotion from one peak.

## Important corrections and closed branches

Recent short control 26083 used 20/40/30, disabled prefill graphs and cap 64. Retained 3k used 60/120/30, breakable prefill graphs and native cap. Actual log audit confirms legacy graph use and modern non-use; protocol duration alone was an incomplete explanation. These differences do not explain all variability because fresh legacy 26313 is lower despite parity. [Actual graph audit](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/incumbent-graph-evidence-20261026/README.md), [readable learning/presenter supplement](../reports/ai-research-learning-journey-20261023/INCUMBENT_RECOVERY_20261026.md).

Close power-of-two 26085: 2337.35 tokens/s and 89.12% SLA, a real gate failure. Prefill fusion 26089 and decode fusion 26091 pass but gain only 0.484%/0.273% versus fresh short 2558.14, below prospective 3%; no unchanged confirmation. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-26083-26091-20261026/REVIEW.md).

Close S62 full-topology retries: 26081 passed runtime/32 KV records but only two prefill-1→decode routes returned; both prefill-0 routes failed within 180-second budget, no AIPerf export. Source review does not support a host-only cache-key collision. Separate S68 component 26308 then failed our missing native-source mount before any NIXL agent/VRAM registration/transfer. All 16 GPU starts are proven; no network failure was measured. Exact 912b7e mount and unchanged 27c3ce API pin are repaired only in frozen 26337; one bounded attempt, no model/full-bootstrap/TP-collective proof even if byte transfer passes. [S62 failure](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-26081-20261025/REVIEW.md), [S68 prerequisite failure](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-26308-20261026/REVIEW.md), [26337 receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-s62-bootstrap-diagnosis-20261025/S68R2-SUBMISSION.json).

N66/N68/N70 jobs 26065–26067 independently pass short raw-profile checks but lose to contemporary N64. Slurm still records FAILED because our old checker hardcoded N64. N72 genuinely fails SLA. Derived helpers read configured concurrency; frozen failures remain. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-26064-26068-20261025/REVIEW.md). Decode-only EAGLE 25998 passes but loses 4.74%; all-worker 25948 fails SLA. No official accuracy failure/pass is inferred from exact-token or small-output diagnostics. Older cache/five-rank/EAGLE failures and corrected interpretations are retained in [previous handoff](history/20261026-ai-before-0819-condense.md) and the [journal](../reports/research-journey-20261019/journal/README.md).

## Observability and preservation

Inspect raw tails/errors/concurrency, role-local queues/KV, transport/runtime logs, CPU/GPU/VRAM/cost evidence. GPU active time is not FLOPS; VRAM is not KV token occupancy. Earlier outer benchmark_start/end sampling includes warmup/grace; newer request-admission envelopes exclude those but are still not exact phase clocks, and host skew is uncalibrated. Missing data is not zero. Heavy profiles stay after scoring. Raw 26313 artifacts are terminal-sealed/captured; external objects are hashed in the sibling artifact store, not uploaded by Git push.

Edit active sources once, capture explicit safe milestones, verify/commit/push promptly with actual dates. Preserve failed branches and raw provenance. No independent development in the archive, no blind Git sweeps, no frozen-payload edits. Submission/slides/HPC payloads have not changed in this continuation.

## H100 access restored — 26 October 08:46 UTC

One owner-continued VPN reconnect and one echo-disabled SSH authentication succeeded; independent BatchMode reaches a2ap-login01/PBS. Phone-side DUO delivery/approval is UNKNOWN, not claimed. Earlier no-VPN notes are historical. AI 59010042 queue is empty; fresh site label 26/10/2026-16:40:02 gives used 47552.669/balance 16447.331/In Doubt 0 SU. All 2634.666667 SU unreconciled maxima remain reserved, conservative headroom 13812.664333. No new GPU submission at this checkpoint. [Restoration and evidence](h100-restored-20261026.md).

Existing CPU SSH read-only queue has one job 25999546.pbs101. Preserve other worker's payload/ledger; fresh CPU-before-AI queue/lock checks still required before any qsub, combined cap 3/one running AI. Recovered 224555 readiness and 224561 local output exit 0; 224554 transport fails and 224560 equal-TP semantic returns but inherited marker gate fails. Acceptance/research followups require actual raw review; no official accuracy/goodput claim follows. Private auth/cache/session state is preserved and excluded from Git. H200 five pending positions remain.


H100 retained full N54 best individual is 2433.019859 tokens/s (222048), separate from H200. Packaged AI primary remains N62 pending reviewed authorized promotion; official full-set accuracy remains unverified. Continue the authorized distinct-hypothesis loop when capacity/evidence permit; this never enables background Codex.
