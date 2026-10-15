# Public Slurm history: observations and revised research priorities

Snapshot: 2026-10-15 11:39 UTC. Query window starts2026-10-01. These are public
Slurm accounting records and queue settings, not another team's scripts, logs,
model outputs or benchmark results. No other user's workspace was read.

## Submission limits and priority

Both users have account `hpcai` and QoS `normal`. Its `MaxSubmitPU` is5: the
maximum pending plus running jobs per user, not five simultaneous allocations.
The `hpcai` partition contains only g1/g4, and these jobs request both nodes and
all16 GPUs. Thus those five pending jobs do not mean five16-GPU runs at once.
Our earlier cap of4 was an internal controller choice, not a cluster rule.
Active new plans now allow5, and job23780 fills the fifth slot.

At the snapshot, `sprio` showed apacsc01 at754 and apacsc42 at566. Fair-share
accounts for the displayed difference; both use normal QoS. The configuration
has age weight0 and fair-share weight10000. This is not evidence of a special
submission privilege, and increasing pending count does not itself increase
priority. Fair-share changes with accounting and scheduler updates.

| User | Job records | COMPLETED | CANCELLED | FAILED | PENDING | Actually started |
|---|---:|---:|---:|---:|---:|---:|
| apacsc01 | 163 | 87 | 60 | 11 | 5 | 99 |
| apacsc42 | 84 | 58 | 6 | 16 | 4 | 74 |

Our pending count subsequently increased to5 with23780. `COMPLETED` means the
batch script exited successfully; it does not establish a completed benchmark,
passing SLA or accuracy. Version labels are arbitrary and are not experiment
counts. Many submissions were cancelled before starting.

## What names suggest — inference only

| Period / examples | Possible research direction | Confidence and limits |
|---|---|---|
| Oct7, `ref07-8plus8`, `q02-v0520`, `q03-kvfp8`, `q11-p2tp4-eagle` | Early SGLang/version, KV precision, P/D geometry and EAGLE trials | Medium: names, not command lines |
| Oct9 onward, `v1-vllm-12p4-nebius`, `v6-vllm-6xTP2-prefill` | A vLLM branch with12 prefill GPUs,4 decode GPUs; multipleTP2 prefill replicas | Medium/high for engine label; exact deployment unknown |
| `v31-...prefill-deepgemm`, `v32-...pbatch32k` | Prefill GEMM and token-batch limits | Medium; no measured gain visible |
| `v42-decode-EP-hpc-moe`, `v47-5xPP2-push-decode-DP6-EP6-hpc` | Expert/data parallel decode, pipeline-parallel prefill, alternative KV connector direction | Medium; `hpc` is their label and may refer to a connector/kernel, not the contest HPC task |
| `v50-...ACC`, `d1-ACC-...`, `v85-ACC-12to4-DP4-EP4-deepep-ll` | Accuracy checks and DeepEP low-latency DP/EP configurations | Medium; `ACC` does not prove accuracy passed |
| `v82-...draft2-official-N128`, pending `v97-12to4-DP4-deepep-draft3-official-N128` | Speculative decoding plus load search; perhaps two/three draft tokens | Medium for speculation, low for exact token counts; they could be draft revision labels |
| `cold`, `fullseed`, `stagger30`, `async-scheduling` | Startup/reproducibility, worker launch order and scheduling | Medium; exact timing/protocol unknown |

Repeated names and continuation of a branch are weak evidence that it remained
interesting to them, not evidence that it is faster than ours. Their N128/144
labels do not reveal goodput or SLA and are not comparable with our N53 score.

## Consequences for our work

Our17 topology tests varied P/D allocation, TP and EP but did **not** explore
attention DP. The earlier DeepEP pilot also retained tensor-parallel attention.
Rejecting that measured point does not reject DP-attention plus DeepEP as an
architecture. Speculative decoding was deferred in our plan; that left a large
search dimension unexplored while we refined kernels and routing.

1. **Submitted23780:** DP-attention8 / attentionTP1 / EP8 / DeepEP low-latency
   FP8 dispatch on the current8+8 round-robin N52 deployment. Keep the P/D split
   fixed for this first comparison. It combines the dependencies needed for a
   working architecture; it is not a single kernel attribution experiment.
2. **Prepare lossless EAGLE3:** inspect exact-image PD support, stage the matched
   public draft, then compare short linear proposal depths before combining
   speculation with DP attention. Keep greedy target verification and unchanged
   official benchmark settings. Inspect actual acceptance length and verification
   time; a draft can slow serving at high batch size.
3. **Revisit12+4 with the new architecture:** benchmark it against8+8 only after
   deployment/transport validation. Its old tensor-parallel score cannot predict
   performance under DP attention or speculative verification.
4. **Prepare an independent vLLM branch:** inspect the available image/version,
   Qwen3 FP8 loading, PD connector and DP/EP support; then establish a full
   matched baseline before attempting the other team's apparent combination.
   A pending name is insufficient evidence to replace our stable deployment.

The public draft metadata and config are pinned at commit
`7f8040f188bc80e309ddb2a25faf30550b356b72`. The checkpoint is explicitly for
Qwen3-235B-A22B-Instruct-2507, with592,461,824 BF16 floating parameters plus
integer/boolean maps; the model card describes general-purpose perfect-blend
training. We downloaded metadata/config/card only, **not weights**, and have
not run an EAGLE3 benchmark. Its card's example uses an older repository label;
use the pinned actual repository, not that copied path. Tokenizer compatibility,
FP8-target integration and target-only output comparisons still require checking.

Primary technical references:
[SGLang speculative decoding](https://docs.sglang.io/docs/advanced_features/speculative_decoding),
[matched public EAGLE3 draft](https://huggingface.co/lmsys/SGLang-EAGLE3-Qwen3-235B-A22B-Instruct-2507-SpecForge-Meituan),
[SGLang PD disaggregation](https://docs.sglang.io/docs/advanced_features/pd_disaggregation),
[vLLM expert parallel deployment](https://docs.vllm.ai/en/v0.22.1/serving/expert_parallel_deployment/).

Raw accounting exports, QoS/association settings, priority snapshot and draft
metadata are retained beside this note. Our new experiment and decision policy:
[wave8 plan](../serving-tuning-08/PLAN.md).
