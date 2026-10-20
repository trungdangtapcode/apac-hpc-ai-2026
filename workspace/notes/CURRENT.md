## Public upstream checked — 2026-10-20T12:53:15.752590+00:00

Fetched main is 3d05096 (10 October), seven commits beyond retained checkout 5a67229 (26 September). Qwen rules are byte-unchanged; new PBS/Enroot notes, scripts and raw H100 reference results are useful for deployment/rebuild/startup cost. Recomputed best qualifying published H100 point: N32, 1173.718122 good output tokens/s. This is contextual, not a matched speedup against our different stack. [Complete comparison, pinned snapshot, source hashes and decisions](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/upstream-review-20261020/REPORT.md). Active checkout and submitted payloads unchanged. No new GPU spending, package edit or scheduler/credit refresh for this repository-only question.

## Workload clarification recorded — 2026-10-20T12:48:56.069388+00:00

The supplied organiser reply specifies team-chosen closed-loop concurrency (no target request rate), fixed 4000/200 lengths, no prefix reuse, workload seed 2026, TTFT 3000 ms plus ITL 20 ms, and good_request_fraction >= 0.90. The current H100 benchmark script and completed sealed export 222302 match the checked settings; no frozen payload changed. The reply defines ITL, not an independent end-to-end latency threshold. [Explanation and targeted evidence](official-goodput-clarification-20261020.md#workload-and-latency-clarification-supplied-later-in-this-chat). Queue/credit snapshots below remain dated; none were refreshed in this explanation-only turn.

## Ranking formula clarified — 2026-10-20T12:46:40.317494+00:00

The user supplied a reply attributed to the organiser: read AIPerf Goodput (requests/s) from profile_export_aiperf.json and multiply by fixed 200 for good output tokens/s. Current checked summary/reviewer formulas already agree. This changes no measurement or ranking; latency eligibility and official model quality remain separate. [Source provenance, example and implementation check](official-goodput-clarification-20261020.md). Scheduler and credit snapshots below were not refreshed in this explanation-only turn.

## Smaller H100 prefill chunks submitted — 2026-10-20T12:06:14.504964+00:00

**H100 222382 R → 222383 H**, verified afterany pair: fresh chunk 4096 control versus chunk 2048 at fixed both-phase HPC-Ops, round-robin routing and N54. All other execution/observation/output/transport paths match accepted 222302. Exact pinned graph generator and negative fixtures validate the expected smaller prefill graph range; actual runtime and performance remain unmeasured. [Plan, receipts, gates and next review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-hpc-smallchunk-20261020/PLAN.md).

Prior routing pair full local PASS but power-of-two loses 4.865% (2396.201520 → 2279.626751 good output tokens/s); retain round-robin. Both charges reconcile. Pre-submit Used 39307.091 SU, Balance 24692.909, In Doubt zero; reserve 3072 SU maximum, internal headroom 8620.909 under unchanged 51000 cap/13000 buffer. H200 four model jobs plus repaired micro 25020 are pending, total five; no model position cancelled. Peaks unchanged, official accuracy unverified. No package, auth or background AI change. Earlier scheduler and credit snapshots below are historical.

## Routing pair reviewed and H200 launcher repaired — 2026-10-20T12:03:19.523895+00:00

H100 222302/222303 full local PASS at 2396.201520/2279.626751 good output tokens/s: power-of-two loses 4.865%; keep round-robin. TTFT rises 315.947 ms despite lower ITL; raw tails, exact native policy, all 16 traces and matched scored hardware/server samples inspected. [Full review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/router-queue-research-20261020/PAIR_REVIEW.md). Reviewer corrected the exact struct-like native enum; policy interval is five seconds, separate from earlier monitoring logs. Published Used 39307.091 SU, Balance 24692.909, In Doubt zero; charges reconcile, internal headroom 11692.909 before next spending.

H200 micro 24990 failed exit 127 in 34 seconds because private HOME hid the script path; no kernel cases. Derived /work bind passes actual scheduler-shell path fixture; replacement **25020 submitted**, one node/eight GPUs/ten minutes. Four model queue positions retained. [Fix and preserved failure](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-homebind-fix-20261020/PLAN.md). Model peaks unchanged; official accuracy unverified. Next prepare the distinct H100 HPC-Ops/chunk2048 interaction, not a repeat of losing routing/8192 settings. No package, auth or background AI changes. Older queue/credit snapshots are historical.

# Current APAC handoff — 20 October 2026

## Native prefill routing pair submitted — 2026-10-20T10:13:13.049729+00:00

H100 **222302 R → 222303 H**, verified serial round_robin/power_of_two at fixed HPC-Ops chunk 4096/N54 with matched observation, all worker/scoring/output/transport paths retained. Native CPU parser/Rust mapping validation and common runtime source/policy guards pass locally; no model result yet. [Full question, source evidence, bounded jobs, gates and review route](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/router-queue-research-20261020/RESULTS.md). Prior chunk pair fully accepted 2401.577649/2382.811874, -0.7814%; retain 4096 and corrected native prefill-graph interpretation. All previous costs reconcile; pre-submit Used 38396.869 SU, pair max 3072 reserved, internal headroom 9531.131 under unchanged 51000 cap/13000 buffer. H200 five jobs still Priority-pending, positions preserved. Model peaks unchanged, official accuracy unverified. No package, auth or background AI change. Earlier scheduler/credit snapshots below are historical.

## Accepted local serving results

**H200 highest individual: 24915 = 3022.034919 good output tokens/s, N62**, 98.726% joint SLA (1860/1884), 24 TTFT breaches, zero ITL/errors. Full local protocol/runtime/output gates pass; +4.537% versus fresh same-N auto control 24914. **Exact independent repeat 24962 remains pending**. N60 is independently reproduced by 24738/24913 at 2990.151/2989.175 (−0.033%), with DeepGEMM prefill chunk 8192 plus HPC-Ops decode. [N62 review and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0218/RESULTS.md).

**H100 highest individual: 222048 = 2433.019859**, N54 incumbent, only +0.088% over 221590; not an established new optimisation. Observed interval1/2 pair 222049/222050 passes at 2395.311/2406.802 (+0.480%). Later unobserved 222178/222179 passes 2420.816780/2419.693212 (+0.0464%, below 1% gate): keep default receive interval1 and close that setting. [H100 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-h100-restored/RESULTS.md), [unobserved confirmation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0647/RESULTS.md).

Keep H100/H200 separate. Scheduler exit 0 never means accepted measurement. **Official full-set >=99%-reference model accuracy remains unverified.** New accepted fresh pair measurements are described above; no new serving peak.

## Live queues at this query

- **H200 24928**: observed receive-interval2 N60.
- **H200 24962**: exact independent N62 repeat of 24915.
- **H200 24964/24965**: fresh observed DeepGEMM8192 versus HPC-Ops8192 prefill at fixed N60/HPC-Ops decode.
- **H200 24990**: isolated native FP8 TP8 decode linear screen, same repaired contract as H100 222242.

All five are **Priority-pending**, no model positions cancelled, no sixth job. [Fresh Slurm snapshot](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-prefill-tp4-20261020/live-slurm.txt). Original micro 24983 and cache-only 24988 were replaced only while pending, zero runtime; their frozen payloads and cancellation receipts are retained.

**H100 222302 R → 222303 H**, actual serial afterany pair: native prefill routing round_robin versus power_of_two, fixed chunk 4096/N54, common source/enum preflight and matched sampler. Worker/precision/topology/scoring/quality bytes retained. Prior chunk 8192 pair is fully accepted but -0.7814%, keep 4096; native prefill capture range derives from chunk while decode graphs remain fixed. [Evidence and next review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/router-queue-research-20261020/RESULTS.md).

## Newly completed kernel evidence

**222242.pbs111 passes all 256 full cases** (eight ranks×32), plus ten separate unranked provider-preflight cases. Source/config, numerical/input guards, nine finite positive samples, eight distinct GPU UUIDs and four nonempty kernel traces verified. **Keep DeepGEMM for TP8 decode projections on H100**: Triton loses every rank/shape/M; at M54 QKV is about twice as slow, O projection about 26% slower. FlashInfer only gains 2.34% median at QKV M16, inconsistent elsewhere; native M>=32 falls back to DeepGEMM. No useful >=5% signal, so no losing full-model pair. [All comparisons, units and sealed evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-privatehome-20261020/RESULTS.md).

Earlier attempts 222210/222232 failed setup, with zero completed cases. First FlashInfer import cache, then TVM/TensorRT home paths. Explicit known cache variables alone were insufficient; the first CPU fixture covered only FlashInfer. Private empty writable home mount at the existing HOME path fixes real GPU execution without changing HOME or mounting real account credentials. DeepGEMM broad warmup finished within the bounded preflight; its generic 10–20-minute warning was not an observed timeout. Preserve failures and exact payloads. Estimated charges 20.480/21.617778 SU; successful screen 73.955556 SU. Synthetic numerical pass is not official model quality.

## Resource evidence and closed branches

H200 24926/24927 full local pass 2991.709/2971.312, N60. Single observed overhead −0.682% is descriptive, not established statistically. 24927 UUID/phase coverage verified; GPU activity is not FLOPS or bandwidth efficiency. Node counters require deduplication; cross-node clock skew remains uncalibrated. [Complete inspection](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0530/RESULTS.md), [per-run observability](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md).

Keep FA3 decode, forced NCCL Simple, forced one-shot, PDL-off, flat phase inference-mode and unchanged larger chunks closed on retained evidence. FA3 prefill remains. Actual native kernel decisions and successful HTTP control responses supersede old symbol/parser assumptions. Post-score profiles do not count as scored timings.

## Budget and execution policy

Pre-submit ledger queried 2026-10-20T10:10:36.854514+00:00: Used **38396.869 SU**, Balance **25603.131 SU**, In Doubt zero; all older charges reconciled. Reserve new routing pair **3072 SU** max, internal headroom **9531.131 SU** under **51000 cap/13000 buffer**. [Fresh source](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/router-queue-research-20261020/pbs-pre-submit.txt). Refresh before later spending; no duplicate prepaid deduction.

During active authorised work, review outputs and submit distinct supported hypotheses within fresh budget/queue checks. At most five active H200, three active PBS and one running PBS allocation. No blind duplicates, unchanged losses, numerical relaxation or automatic load/interval growth. VPN/SSH currently works; do not restart authentication unnecessarily. [VPN duration](../tutorial/19-vpn-session-lifetime.md).

Vietnamese chat only; all artifacts English. Qwen only, HPC_Task empty. No package edit this continuation. The earlier authorised 32-slide English update remains [delivered](presentation-update-20261020.md); no claim of official quality. Preserve raw failures and reasoning in the [journal](../reports/research-journey-20261019/journal/README.md).

Capture safe source/evidence milestones explicitly, verify, commit and push to the authorised private repo; no automatic mirror. GitHub does not contain external large artifact-store bytes; separate off-host copy remains needed. **Autopilot OFF**, no background Codex/schedules or automatic chat-notification promises.
