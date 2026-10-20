# Current APAC handoff — 20 October 2026

## Matched H100 prefill interaction submitted — 2026-10-20T09:30:58.728352+00:00

**222281 (R) → 222282 (H)**, verified afterany chain, compares both-phase HPC-Ops with prefill chunk 4096/8192 at fixed N54, equally observed. Default dense 132-SM DeepGEMM retained; no micro tweak. Two 16-GPU/45-minute maxima, 3072 SU, one running allocation. The previous 8192 loss used auto prefill and does not settle this interaction. [Exact plan, invariant checks, budget, receipts and review steps](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-prefill-hpc-chunk-interaction-20261020/RESULTS.md). Prior 160-case SM80 screen passes numerics but fails consistent benefit; all raw cases preserved. Serving peaks unchanged; official accuracy unverified. H200 all five still Priority-pending. Published pre-submit Used 37439.430; last micro 35.271111 unposted, retain 170.666667 plus 3072: total 3242.666667 bound, internal headroom 10317.903333 under unchanged 51000 cap/13000 buffer. No package, auth or background AI change. Earlier queue/credit snapshots below are historical.

## Accepted local serving results

**H200 highest individual: 24915 = 3022.034919 good output tokens/s, N62**, 98.726% joint SLA (1860/1884), 24 TTFT breaches, zero ITL/errors. Full local protocol/runtime/output gates pass; +4.537% versus fresh same-N auto control 24914. **Exact independent repeat 24962 remains pending**. N60 is independently reproduced by 24738/24913 at 2990.151/2989.175 (−0.033%), with DeepGEMM prefill chunk 8192 plus HPC-Ops decode. [N62 review and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0218/RESULTS.md).

**H100 highest individual: 222048 = 2433.019859**, N54 incumbent, only +0.088% over 221590; not an established new optimisation. Observed interval1/2 pair 222049/222050 passes at 2395.311/2406.802 (+0.480%). Later unobserved 222178/222179 passes 2420.816780/2419.693212 (+0.0464%, below 1% gate): keep default receive interval1 and close that setting. [H100 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-h100-restored/RESULTS.md), [unobserved confirmation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0647/RESULTS.md).

Keep H100/H200 separate. Scheduler exit 0 never means accepted measurement. **Official full-set >=99%-reference model accuracy remains unverified.** No new serving score in this continuation.

## Live queues at this query

- **H200 24928**: observed receive-interval2 N60.
- **H200 24962**: exact independent N62 repeat of 24915.
- **H200 24964/24965**: fresh observed DeepGEMM8192 versus HPC-Ops8192 prefill at fixed N60/HPC-Ops decode.
- **H200 24990**: isolated native FP8 TP8 decode linear screen, same repaired contract as H100 222242.

All five are **Priority-pending**, no model positions cancelled, no sixth job. [Fresh Slurm snapshot](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-prefill-tp4-20261020/live-slurm.txt). Original micro 24983 and cache-only 24988 were replaced only while pending, zero runtime; their frozen payloads and cancellation receipts are retained.

**H100 222281 R → 222282 H**, verified serial afterany: current both-phase HPC-Ops/chunk 4096 versus the missing HPC-Ops-prefill/chunk 8192 interaction at N54. Both observed, same full protocol/output checks. Two 16-GPU/45-minute maxima, one running. Native dense kernels remain default 132 SMs; **all 160 SM80 cases pass but fail benefit gates**, so the tested 80/96/120 budgets and default Triton branch are closed. [Plan, actual receipts, strict reviewer and telemetry steps](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-prefill-hpc-chunk-interaction-20261020/RESULTS.md).

## Newly completed kernel evidence

**222242.pbs111 passes all 256 full cases** (eight ranks×32), plus ten separate unranked provider-preflight cases. Source/config, numerical/input guards, nine finite positive samples, eight distinct GPU UUIDs and four nonempty kernel traces verified. **Keep DeepGEMM for TP8 decode projections on H100**: Triton loses every rank/shape/M; at M54 QKV is about twice as slow, O projection about 26% slower. FlashInfer only gains 2.34% median at QKV M16, inconsistent elsewhere; native M>=32 falls back to DeepGEMM. No useful >=5% signal, so no losing full-model pair. [All comparisons, units and sealed evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-privatehome-20261020/RESULTS.md).

Earlier attempts 222210/222232 failed setup, with zero completed cases. First FlashInfer import cache, then TVM/TensorRT home paths. Explicit known cache variables alone were insufficient; the first CPU fixture covered only FlashInfer. Private empty writable home mount at the existing HOME path fixes real GPU execution without changing HOME or mounting real account credentials. DeepGEMM broad warmup finished within the bounded preflight; its generic 10–20-minute warning was not an observed timeout. Preserve failures and exact payloads. Estimated charges 20.480/21.617778 SU; successful screen 73.955556 SU. Synthetic numerical pass is not official model quality.

## Resource evidence and closed branches

H200 24926/24927 full local pass 2991.709/2971.312, N60. Single observed overhead −0.682% is descriptive, not established statistically. 24927 UUID/phase coverage verified; GPU activity is not FLOPS or bandwidth efficiency. Node counters require deduplication; cross-node clock skew remains uncalibrated. [Complete inspection](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0530/RESULTS.md), [per-run observability](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md).

Keep FA3 decode, forced NCCL Simple, forced one-shot, PDL-off, flat phase inference-mode and unchanged larger chunks closed on retained evidence. FA3 prefill remains. Actual native kernel decisions and successful HTTP control responses supersede old symbol/parser assumptions. Post-score profiles do not count as scored timings.

## Budget and execution policy

Pre-submit publication queried 2026-10-20T09:29:00.721061+00:00: Used **37439.430 SU**, Balance **26560.570 SU**, In Doubt zero. Completed 222279 estimated 35.271111 SU is unposted; retain full 170.666667 maximum plus new pair 3072. Conservative total bound **3242.666667 SU**, internal headroom **10317.903333 SU**, unchanged **51000 cap/13000 buffer**. [Proof](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-prefill-hpc-chunk-interaction-20261020/prior-accounting.json). No duplicate prepayment subtraction; refresh ledger before later spending.

During active authorised work, review outputs and submit distinct supported hypotheses within fresh budget/queue checks. At most five active H200, three active PBS and one running PBS allocation. No blind duplicates, unchanged losses, numerical relaxation or automatic load/interval growth. VPN/SSH currently works; do not restart authentication unnecessarily. [VPN duration](../tutorial/19-vpn-session-lifetime.md).

Vietnamese chat only; all artifacts English. Qwen only, HPC_Task empty. No package edit this continuation. The earlier authorised 32-slide English update remains [delivered](presentation-update-20261020.md); no claim of official quality. Preserve raw failures and reasoning in the [journal](../reports/research-journey-20261019/journal/README.md).

Capture safe source/evidence milestones explicitly, verify, commit and push to the authorised private repo; no automatic mirror. GitHub does not contain external large artifact-store bytes; separate off-host copy remains needed. **Autopilot OFF**, no background Codex/schedules or automatic chat-notification promises.
