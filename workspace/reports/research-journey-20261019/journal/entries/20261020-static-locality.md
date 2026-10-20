# Static CPU/GPU locality discovery before a binding experiment

The current PBS wrapper binds worker CPUs by an ordinal offset (eight CPUs per preceding GPU), not measured GPU/NUMA locality. Existing scored samples provide node-wide CPU busy state, not per-worker thread placement or a hardware affinity map. Low node-average CPU activity does not rule out a saturated or remote-memory thread. There is not yet evidence that the binding is wrong or that changing it improves goodput.

Collect one bounded static hardware report before designing an expensive full-model affinity trial. One H100 GPU / 14 CPUs / three minutes maximum costs at most 6.4 SU. No model, benchmark or GPU computation is run. Query static identity only for the PBS-allocated UUID; record CPU hardware layout, the process allowed-CPU mask, NUMA node cpulists, that GPU PCI sysfs locality and the static nvidia-smi topo matrix. Missing or denied topology fields remain NOT_COLLECTED, not healthy. No other team files, processes or activity are inspected.

NVIDIA documents that topo -m reports NVML GPU/NIC connection and CPU/memory affinity information: https://docs.nvidia.com/deploy/nvidia-smi/index.html#topology . NVML enumeration is distinct from a container CUDA ordinal. One sampled allocation does not establish masks for the sixteen-GPU serving job or causality; a later derived serving bundle must record its actual affinity/rank/UUID mapping before a binding comparison. No model flag is changed based on assumptions alone.

Submit serially after the current H100 prefetch candidate 222408, within the existing three-active/one-running allocation cap. Refresh credit/queue and reserve the entire 6.4 SU under the budget lock, preserving both existing unposted/running prefetch reservations and the 51000 SU cap/13000 SU buffer. No retry of uncertain qsub. Collect only our terminal run and declared outputs, verify frozen payload hashes and seal the static report; this is not a model score or official accuracy result.

## Definite execution checkpoint — 2026-10-20T13:55:03.119475+00:00

# Static locality probe submitted

Job 222412.pbs111 is dependency-held after running model candidate 222408.pbs111. It requests one H100 GPU, 14 CPUs and three minutes, maximum 6.4 SU, and loads no model. The static report will support or reject the need for a later CPU/NUMA binding hypothesis; it is not a performance run or an assertion that the current binding is wrong. [Question, missing evidence, read scope and bounds](PLAN.md), [CPU fixture](validation.json), [definite receipt](pbs-receipt.json), [actual held state and serial dependency](post-submit.txt).

The submission succeeded before a local continuous-plan timestamp TypeError. Its definite receipt and budget reservation were already saved; the plan writer was fixed and the existing ID inserted and verified without repeating qsub. [Exact correction and preserved provenance](LOCAL_BOOKKEEPING_CORRECTION.md). There is no duplicate allocation or uncertain job ID.

Fresh pre-submit ledger: Used 40272.495 SU, Balance 22703.505 SU, In Doubt 1024 SU. The completed control's estimated 531.342222 SU remains unposted. Preserve both prior 1024 SU maximum reservations plus this 6.4 SU maximum until exact cost reconciliation. Conservative campaign headroom 8673.105 SU within the unchanged 51000 cap/13000 buffer. Reported Balance already excludes In Doubt; do not deduct it again as a separate charge. [Raw ledger and owned jobs](pre-submit.txt), [reconciliation check](reconciliation.json).

After terminal state, collect only this owned job directory and declared stdout, verify SHA256SUMS and seal its JSON. Check allocation UUID, host, NVML versus CUDA numbering, static topology, NUMA lists and process allowed-CPU mask. Missing topology is NOT_COLLECTED; one-GPU masks do not establish sixteen-GPU serving masks or CPU contention. Inspect before proposing any full-model affinity pair. Frozen current model payloads, four H200 queue positions, images, official benchmark, credentials, submission package and background AI settings are unchanged.

## Terminal review — 2026-10-20T14:44:36.465181+00:00

[Sealed static findings and next decision](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-gpu-locality-20261020/REVIEW.md): 222412 exit 0, verified frozen payload and topology PASS; 28 logical CPUs on NUMA 0 have no overlap with allocated GPU NUMA 1 locality. This supersedes the earlier lack-of-evidence snapshot, but does not establish full-serving misbinding, memory placement or a CPU bottleneck. No model/score/CPU-load test was collected. Reported 78 s costs 2.773333 SU, already reconciled. Next collect actual full-serving rank/UUID/mask mapping before a separately controlled intervention. No extra job submitted.
