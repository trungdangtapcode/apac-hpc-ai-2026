# Four-H100 observer preflight fails before model loading

Job **224275.pbs111** is **F / exit 1**, elapsed **66 seconds**. Four actual H100 devices, the pinned graph source and native NIXL source pass their checks. The next embedded HPC preflight calls the nonexistent `torch.cuda.get_device_count()` instead of `torch.cuda.device_count()`. This is our launcher error, not evidence that EAGLE, NIXL or the observer is incompatible. No model loading, metadata receipt, user request, score or quality result occurs.

Root collected all 25 terminal artifacts and verified their SHA-256 hashes. PBS also reports Stageout_status1; the retained on-disk logs permit this review despite stage-out failure. Requested four GPUs over 66 seconds gives a **9.386667 SU** allocated-time estimate; the ledger reconciliation separately determines whether a unique actual charge has posted. A reported resources_used.ngpus0 does not make the four-GPU allocation free.

The attempted full R4 admission correctly stopped at the failed-parent gate before a reservation or qsub. Its payload was uploaded, but it has no PBS job. Preserve that source and failed-admission outputs. R2 is a separate directory changing only the public CUDA API spelling. A strict CPU stub executes the actual embedded snippet: the parent fails and the corrected snippet passes. This regression check does not substitute for a real four-H100 runtime attempt. The new attempt retains all source/observer/BF16/graph/runtime/health and actual four-rank metadata gates.

Available inspection covers startup stdout/stderr, health errors, the zero-receipt validator result, scheduler resources and exact submitted source. Model-time CPU/GPU activity, KV queues, transfer observations, generated-token latency and heavy profiles were not collected because the model never started.

For a presentation: “The small qualification run caught a launcher typo before the expensive model test. We preserve the failed result and correct the call without weakening any runtime acceptance check.”
