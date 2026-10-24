# Current AI / Qwen research handoff

Updated 2026-10-24T08:38:02.289695+00:00. GPU fork `01a166eb-33cb-7ce0-9699-ec65de26689a` continues parent `01a15dd3-3094-7712-a991-8ce55b15cbfe`. This session owns AI/Qwen; the other worker owns HPC/OpenFOAM. English artifacts, Vietnamese chat. Query live schedulers before treating any dated state as current. No background Codex, schedules or automatic chat notifications.

## Five submitted jobs — latest check 24 October 08:34 UTC

| Cluster / job | State then | Experiment |
|---|---|---|
| H200 **25862** | Pending, Resources | S49: EAGLE compared with the accepted deterministic target 25855; 16 GPUs  / 17 min |
| H200 **25863** | Pending, afterany 25862 | S47: fresh BF16-KV control, N64 short 20/40/30 screen; 16 GPUs  / 17 min |
| H200 **25864** | Pending, afterok 25863 | S48: matched FP8-KV candidate; independently replays actual control gates before any worker starts; 16 GPUs  / 17 min |
| H100 **224466.pbs111** | Q  / aiq2 | R6: serial initial P/D requests, then concurrent retest with separate receipts; 16 GPUs  / 20 min  / max 682.666667 SU |
| H100 **224468.pbs111** | H, afterany224466 | R3: one-GPU physical-expert partition test with a source-corrected independent oracle; 1 GPU  / 10 min  / max 21.333333 SU |

Preserve all positions and frozen payloads. Do not resubmit an existing/uncertain receipt. **S49** uses the real 25855 reference/review/seal hashes, all-rank BF16, 190-region EAGLE geometry, both semantic paths, native speculative counters and strict 1600-ID equality. Its deterministic settings match the new target; S45 remains an old unbound template. [Source and receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-h200-deterministic-candidate-20261024/).

**S47/S48** change only KV precision on both P and D: auto→actualBF16 versus `fp8_e4m3`. Common query dtype BF16, P cap 64 / D cap 256, eager prefill, decode graphs 1–64, DeepGEMM 8192/HPC-Ops/FlashInfer/MNNVL, native NIXL, same seed 2026 and fixed 4000/200 client. Both retain exact local smoke-regression/12-retrieval/runtime/SLA/no-error checks. They are unranked short screens, not official accuracy. The real index has no K/V scale keys; default 1.0 is source-inferred, per-layer scales unobserved. Only a valid candidate gain >1% justifies considering full matched confirmation. [Plan, CPU evidence and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-kv-h200-screen-20261024/README.md).

**R6** retains actual accepted 224276 observer proof. R5 passed 16-rank metadata but both first concurrent P/D requests failed. New phases have distinct tokens/directories and windowed native send evidence. A restored locality helper was missing in R5; physical nodes may differ, so even a pass is not causal proof of an initialization race. No 1600-ID or performance stage. [R6](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-serial-init-r6-20261024/README.md).

**R3** preserves 2% native/oracle and 1e-7 copy-map gates. Pinned Tencent/HPC-Ops commit `ab1a402` proves BF16 gate-up store, FP8 block quantization after SiLU product, then BF16 down store. The previous oracle omitted those formats. New independent Torch operations model them; no result is claimed before GPU execution. Five virtual EP partitions execute serially on one H100, not five-GPU communication. [R3](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hpc-ops-replica-r3-20261024/README.md).

## Completed evidence and interpretation

- **25855 accepted**, COMPLETED 0:0, 521 s. All 16 rank/runtime gates, 32 target-only 188-region receipts, both semantic P/D paths and 1600 stable target IDs independently replay. Historical 25585 mismatch is informational. Teardown cancellation/wait-timeout and sampler URLError records are retained; do not describe every process as healthy. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25855-20261024/).
- **25807 failed** after 309 s before output: the launch command omitted explicit dtype, despite actual BF16 KV. S46 corrects that and the source-backed forced-allreduce-disable marker. Real old logs replay with only the temporary dtype field changed; actual worker argv is now tested. Frozen failure remains. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25807-20261024/).
- **224277 failed**, 566 s: all 16 metadata records/six sources pass; both concurrently initialized P/D requests return 500 with NIXL sender/remote-disconnect. No output IDs. Agents have UUID names, so no static-name-collision evidence. Send-handle return is not completion. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-224277-20261024/README.md).
- **224460 failed**, 81 s: native MoE runs; EP5/EP1 relative-L2=0.232612%, while both fail the original 2% oracle gate (~2.29%). Input quantization differs in 3/4096 bytes (0.073242%) but all spacing bounds pass. Preserve failure; this is not an EP5 correctness pass. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-224460-20261024/README.md).
- Earlier **25796** passes one-H200 native FP8 attention (four cases, max 0.315902% same-rounded-cache error), while **25797** reaches 1600 speculative IDs but fails exact-token checks. **224276** passes narrow real prefill metadata (96 rows; BF16 hidden states [96, 4096]), not full transfer. **25712/25713** close unchanged disabled-graph performance at −0.580368%. [Previous detailed handoff](history/20261024-ai-before-five-job-wave.md).

The organiser's ≥99% requirement compares full benchmark scores, not token identity. Different floating-point ordering is allowed. Our exact-token diagnostics are stricter local investigations; a failure is not official disqualification, and a small pass is not an official accuracy certificate. No new speculative speedup or global SOTA is established.

## Owner-approved H100 allowance

On 24 October the owner explicitly authorised using remaining H100 SU freely before their stated 30 October usable deadline. AI project 59010042 may use its actual 64000 SU grant with **zero discretionary buffer**. Old 51000/13000 bounds are historical; do not reuse old frozen controllers asserting them. Account metadata lists 15 November, so use the earlier owner date for planning without claiming verified account expiration. CPU project/budget unchanged.

Latest locked ledger: **used 46906.945 SU**, published balance 17093.055 SU, In Doubt 0.000 SU. All three older terminal charges sum to 376 SU and reconcile exactly; 224460's 2.88 SU charge also reconciles. Retain maxima 682.666667 +21.333333 = 704 SU for the two new jobs. Conservative allowance after maxima =**16389.055 SU**. Prepayment is already excluded from balance; do not subtract it twice. [Ledger](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json), [owner decision](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-budget-owner-update-20261024/README.md).

Before spending, refresh both PBS queues and selected AI credit under CPU-before-AI locks. Preserve combined PBS cap 3, one running AI allocation, max 16 GPUs / 45 min. Slurm cap 5 and 17 min/job. No blind duplicate queue filling, no cap increase, no interference with HPC work. Existing shared VPN/AI SSH work; no new DUO or authentication-state capture occurred.

## Frontier, next decisions and preservation

Reproduced H200 N64 remains **3044.400475 good output tokens/s** (25366/25373/25487). H100 N54 **2433.019859** (222048) is separate. No official full-set accuracy pass. Packaged primary stays N62 pending a separately reviewed promotion; no HPC/submission/presentation payload changed.

Review S49's actual equality/counters before any speculative speed claim. Review paired S47/S48 raw tails/errors/concurrency, semantic checks, runtime/cache precision and role hardware/server samples; do not infer a bandwidth bottleneck from score alone. Review R6 phase receipts and first transport error. Only an actual R3 oracle pass qualifies consideration of the paused D5 readiness branch: source confirms attention TP1 with TP5/DP5, EP5/130 slots, dynamic dispatch and logical-to-physical loader mapping; no runnable D5 payload or GPU proof yet. [Paused source findings](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/dp5-h200-readiness-20261024/).

[Learning journey](../reports/ai-research-learning-journey-20261023/README.md), [journal](../reports/research-journey-20261019/journal/README.md). Keep every pass/failure and prospective decision, inspect beyond scores, capture explicit safe milestones, verify and push small actual-date commits. Git has safe sources/reports and external-object manifests; large retained corpus bytes still need a separate off-host copy. Preserve existing history and the other worker's payloads.
