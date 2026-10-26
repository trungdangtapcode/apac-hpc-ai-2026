# Current AI / Qwen research handoff

Updated 2026-10-26T12:33:36.727174+00:00. This GPU fork 01a166eb-33cb-7ce0-9699-ec65de26689a continues AI parent 01a15dd3-3094-7712-a991-8ce55b15cbfe; it owns AI/Qwen only. The separate worker owns HPC/OpenFOAM. Chat Vietnamese; artifacts English. No background Codex, schedules or automatic chat notifications.

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

## H100 followups actually submitted — 2026-10-26T12:33:36.727174+00:00

225227.pbs111 is Q/aiq2: full accepted N54 reference refresh, 16 H100/two nodes/30 minutes, 1024 SU maximum. 225228.pbs111 is H/afterany 225227: corrected native equal-TP EAGLE observer, 8 H100/one node/20 minutes, 341.333333 SU maximum. Fresh separate CPU queue is empty; combined count is two. Earlier empty AI/one CPU snapshot is historical. Fresh project balance 16447.331 SU; retained old maxima 2634.666667 plus new maxima 1365.333333 leave conservative headroom 12447.331 SU. Neither job has a result. [Reviewed admission](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-followups-20261026/REVIEW.md).

The separate CPU read-only SSH channel required one echo-disabled authentication before queue verification; healthy AI SSH/VPN was preserved. No phone-side DUO approval or exact lifetime is claimed. First upload-only attempt stopped before reservation/qsub; resumed admission reverified manifests and obtained unambiguous receipts. No HPC payload/ledger or schedule was changed.

## H200 full modern control reviewed — 2026-10-26T12:35:14.452190+00:00

26315 COMPLETED 0:0/10:10: 2807.325653 good tokens/s, 98.248588% joint SLA, 1770 profiling requests, zero errors/cancellations, smoke 7/8 and retrieval 12/12. Independent full raw/runtime gates pass; official accuracy remains UNKNOWN. This is 0.8336% below recent legacy 26313, with multiple runtime changes; not an isolated graph effect or improvement. Four jobs remain pending: 26317/26319/26347 serving arms and 26337 component. Keep these positions and await valid matched comparisons before confirmation. [Detailed review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-26315-20261026/REVIEW.md).

Observability unit correction: inherited offline helper divided host KiB by 1024 squared but used TiB labels. Values are GiB (about 2014.874 GiB total/host), corrected in current reviewer/report; earlier snapshots retain the historical mislabel. Raw data, score and decisions unchanged.

## Full graph/admission review and actual next jobs — 2026-10-26T14:33:12.134495+00:00

All four arms pass full local gates: 26315 disabled/cap64=2807.325653; 26317 breakable/cap64=2829.604300; 26319 breakable/native=2827.996286; 26347 disabled/native=2802.498990 good tokens/s. Graph gains 0.79–0.91% remain below prospective 1% gate; native admission has negligible gain. No new-best or official accuracy claim. Close this tuning branch. Earlier pending snapshots are historical.

Actual new Slurm jobs 26436 N62 and 26438 N66 (afterany 26436) bracket full breakable/native N64 with only client load changed; both 16 H200/two nodes/17-minute bounds. Previous short graph-disabled/cap64 sweep is a different runtime. Full local gates and >1% useful-gain condition remain; do not widen before actual review. [Plans and receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-full-load-followups-20261026/REVIEW.md).

## Reviewed full study and bounded transport result

[Four full-arm review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-factorial-review-20261026/REVIEW.md): all pass local gates, graph gains +0.793590% / +0.909806%, native admission changes -0.171931% / -0.056828%. One ordered run per cell limits causality; close this subthreshold treatment without unchanged confirmation. Raw evidence is terminal-sealed.

[26337 component review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-26337-20261026/REVIEW.md): 16 distinct H200 UUIDs, native source/API pins, 32 small synthetic writes and all receiver buffers/sentinels pass. Total 6,160,384 bytes across three phases. No model, SGLang bootstrap, production KV or throughput evidence. Do not infer the earlier full-route failure is fixed or launch it unchanged.

## H100 completed runs independently reviewed — 2026-10-26T14:38:08.713215+00:00

225227 F/0 in 15:38: 2399.186728 good tokens/s, 98.015873% joint SLA, 1512 profiling requests, zero errors/cancellations, smoke 7/8 without regression and retrieval 12/12. Valid current control, 0.347131% below 222551; no gain or unchanged repeat. 225228 F/0 in 6:39: actual eight-H100 equal-TP EAGLE source/device/metadata and one semantic response pass; send_kvcache and send_aux observed on all four prefill ranks without exception. This is a functional prerequisite, not throughput or official accuracy. Earlier Q/H receipts are historical. [Independent review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-review-225227-225228-20261026/REVIEW.md).

Preparing a one-node eight-H100 EAGLE N24 full-workload feasibility job, bounded to 30 minutes/512 SU because the earlier 20-minute envelope cannot safely include the full benchmark and output checks. This uses existing <=45-minute authorization; no budget increase. Not yet submitted at this checkpoint. A one-unit score cannot prove 16-GPU replica scaling. Fresh CPU/AI queue and credit admission still required, all old unreconciled maxima retained.
