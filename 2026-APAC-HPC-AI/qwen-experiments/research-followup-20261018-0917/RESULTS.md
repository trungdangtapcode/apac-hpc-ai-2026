# Status and repeat reviews — 18 October 2026, 09:18 UTC

## H100 decode gain repeated

Independent HPC-Ops decode job **221274.pbs111** reaches **2,304.083 good output tokens/s** at concurrency 50. The original result 221263 was 2,308.308; their descriptive mean is **2,306.196**. Against the previous matched control 221262 at 2,245.534, the repeat is **2.6073% higher**. Both observations point in the same direction; the newly submitted control 221275 is still running and is needed to assess time drift. This is not a statistical confidence interval or an official accuracy certificate.

The repeat's joint latency success is **98.6815%**, mean time to first token **689.271 ms**, mean inter-token latency **17.779 ms**. Full terminal seal, frozen payload, protocol, runtime, error/latency, short nonregression and all 12 long retrieval checks pass. Decode runtime changes only the main and inherited speculative MoE runner to HPC-Ops; speculative decoding stays disabled. Preserve all raw artifacts. See 221274.pbs111-gates.json and 221274.pbs111-review.json.

At the live check, **221275** is running the fresh auto-runner control and **221276** is held behind it for the bounded concurrency 52 HPC-Ops trial. Keep these positions; no additional credit-consuming experiment is justified before their results.

## H200 chunk gain is small in the independent repeat

Job **24527** finished successfully in **10:54**. Independent DeepGEMM chunk8192 repeat at concurrency 56 scores **2,718.692 good output tokens/s**, compared with fresh chunk4096 control 24526 at 2,715.832: **+0.1053%**. The original chunk8192 observation 24425 was 2,722.281, +0.2022% versus its control. Both differences are positive, but small; no material large improvement is established.

Repeat joint latency success is **98.9362%**, mean first-token latency **770.050 ms**, mean inter-token latency **16.372 ms**. Full terminal, sealed payload, unchanged protocol, intended runtime, short nonregression and 12/12 long checks pass. Its frozen hashes match the registered payload. Only chunk size and its derived prefill graph configuration differ from the matched control, with decode unchanged. See 24527-terminal-review.json. The earlier 24527-review.json is a preserved historical waiting-for-seal observation, superseded by the terminal review.

At 09:18 UTC, jobs **24528** (chunk6144), **24529** (HPC-Ops prefill) and **24538** (HPC-Ops decode with DeepGEMM prefill) remain pending Priority. No evidence of a hung active job: 24527 progressed through warmup and scoring, then completed normally. Preserve pending positions rather than cancelling/resubmitting them.

## Credit and limits

Latest observed ledger, as of 18 October 17:00:01 SGT: Used **21,580.231 SU**, Balance **40,883.769 SU**, In Doubt **1,536 SU**. This balance already excludes the prepayment. Repeat 221274 took **14:26**, estimated **492.658 SU** at 128 SU/GPU-hour for 16 GPUs, but that charge is not yet reflected in Used. Retain its conservative maximum reservation until ledger reconciliation. All three previous reservations total **4,608 SU**; operating headroom under the unchanged 51,000 SU internal limit remains **24,811.769 SU** using grant minus Used minus outstanding reservations. Do not subtract prepayment twice.

The new ledger snapshot is saved in the collected run's own-jobs-and-credit.txt. No new job or GPU reservation was added this turn. No AI scheduling, background Codex, slide/package changes or organiser upload. Full organiser reference-score accuracy remains unverified.
