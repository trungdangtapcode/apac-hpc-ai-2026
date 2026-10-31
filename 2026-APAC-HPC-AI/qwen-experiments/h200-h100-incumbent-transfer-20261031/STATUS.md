**Final H200 verification — 2026-10-31T13:05:20.255825+07:00, Vietnam time (UTC+7):** **4/4 reviewed local passes, own queue empty.** 27777 fresh control **3038.022907**; 27779 FA3 **2999.245473 (-1.276404%)**; 27781 H100 recipe N54 **2738.940099**; 27783 H100 recipe N64 **2721.815800 (-10.408319%)**, all good output tokens/s. Keep the existing H200 DeepGEMM/chunk 8192 prefill and HPC-Ops/FlashInfer/MNNVL decode at N64; no new winner or promotion. H100-recipe N54->N64 does not improve goodput and increases mean TTFT 896.156 -> 1591.493 ms with larger sampled prefill queues; no direct causal time decomposition. Official quality UNKNOWN. Actual wave 12.671111 GPU-hours, zero PBS SU. [Final review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/FINAL_RESULTS.md). The requested four-job verification is complete; no useful-gain repeat qualifies. Unrelated research remains stopped, no background Codex/schedule, H100 authentication/spending or HPC change. Published slides/ZIP unchanged.

Earlier dated queue/result snapshots below are historical.

**Latest AI review — 2026-10-31T11:24:39.696311+07:00, Vietnam time (UTC+7):** **3/4 reviewed local passes**: 27777 control 3038.022907; 27779 FA3 decode 2999.245473 good tokens/s (**-1.276404%** versus fresh control); 27781 H100 recipe N54=2738.940099. All have zero scored errors/cancellations, smoke 7/8 non-regression, retrieval 12/12. Keep FlashInfer decode and close this FA3 candidate; official quality UNKNOWN. 27783 H100 recipe N64 is running; do not isolate recipe effects from N54 versus N64. [Full review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/RESULTS.md). Preserve its admitted position; no redundant fifth trial.

Earlier dated snapshots below remain historical.

**Latest reviewed progress — 2026-10-31T10:53:26.134276+07:00, Vietnam time (UTC+7):** 27777 COMPLETED 0:0/13:08 and independently passes all local gates at 3038.022907 good output tokens/s, 1872/1898 good (98.630137%), 26 TTFT/0 ITL breaches, zero scored errors/cancellations, smoke 7/8 no regression, retrieval 12/12. It is a fresh control, not an improvement. 27779 is running with actual FA3 decode/runtime gate passed; 27781/27783 remain Resources-pending. [Complete review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-attention-transfer-20261031/CONTROL_RESULTS-27777.md). No additional GPU submission: three admitted candidates remain unfinished; four-job scope is preserved. Official quality remains UNKNOWN.

The admission snapshot below is historical; see this latest review and fresh scheduler evidence for current state.

# Four-job H200 wave: all scheduler acceptances retained

Observed 2026-10-31T10:34:46.460360+07:00, Vietnam time (UTC+7). New Slurm acceptances:

| Job | Configuration | Concurrency | Scope |
|---|---|---:|---|
| 27777 | DeepGEMM prefill/chunk 8192, FlashInfer decode |64| Existing fresh H200 control |
| 27779 | DeepGEMM prefill/chunk 8192, FA3 decode |64| Existing attention candidate |
| **27781** | HPC-Ops prefill/chunk 4096, FlashInfer decode |54| H100 serving recipe at retained H100 load |
| **27783** | HPC-Ops prefill/chunk 4096, FlashInfer decode |64| Same H100 recipe at current H200 load |

All retain HPC-Ops decode and 16 H200 / two nodes, at most 17 minutes per job.
New pair maximum 9.066667 GPU-hours; total wave 18.133334 GPU-hours, zero PBS SU.
The four measurements include one control; no claim of four distinct winning
H100 optimizations. No performance result exists for the newly submitted pair.

Dated actual queue:

```text
27783|ap42-s113-h100n64|PENDING|0:00|2|(Resources)
27781|ap42-s112-h100n54|PENDING|0:00|2|(Resources)
27779|ap42-s111-fa3|PENDING|0:00|2|(Resources)
27777|ap42-s110-flashinfer|RUNNING|4:08|2|g[1,4]
```

Shared Slurm admission lock protected a fresh own cap-five check, site query,
per-bundle manifest hashes, checksum verification, sbatch test and definite
receipts. [Admission records](admission/) bind actual job IDs to reservations
and manifests; source/CPU qualification was captured and pushed in 538bd026
before submission. Twenty synthetic CPU runtime/client-load fixtures passed,
including rejection of an N64 export/summary as N54. Those are not GPU results.
No older payload, queue position, dependency or job was changed.

Use unchanged full workload and all local runtime/source/physical-KV/ two-semantic
route/output/error gates. Review tail latency, queue/batch/KV, actual backend
activation, hardware samples, startup and allocation cost before accepting scores.
Compare 27783 versus 27777 as a coupled runner/chunk recipe; compare 27781 versus
27783 for load sensitivity. Do not infer an isolated runner effect or pure GPU
speed ratio. Official full-set accuracy remains UNKNOWN.

The owner explicitly expands the earlier two-job initial stage to four total.
Further useful-gain confirmation remains conditional and separately reviewed.
No H100 authentication/spending, HPC changes, schedules, background Codex,
slide/submission change or organiser upload. [Plan](PLAN.md), [CPU validation](validation.json).
