# Full-size byte transfer passes; original PBS job fails

**224116.pbs111 is F / exit 1, not a successful job.** Independently replayed actual rank receipts nevertheless pass the stated native full-span byte-transfer gate. Preserve both findings. PBS also reports Stageout_status 1; rank1-task.log reports a task exit 1 while the outer step status is zero. Both task cleanup markers and the final component marker exist. The exact origin of the exit discrepancy remains unresolved; do not infer a transport failure, a harmless stageout-only failure or a healthy teardown.

## What was actually established

On a2ap-dgx036 and a2ap-dgx037, each GPU allocates and registers all 190 KV regions of 76,132,096 bytes, totaling **14,465,098,240 bytes per rank**, plus **933,888 pinned-host bytes in ten auxiliary regions**. Native TP4→TP8 request-plan and send methods preserve the independently expected flat region order. All **380 selected pages / 97,280 bytes** arrive with distinct expected region/page hashes. A GPU reduction scans **14,465,000,960 other destination bytes** for the original sentinel, and an independent source scan and auxiliary byte checks pass. The source-only initialization prevents prefilled expected receiver data from concealing a missing write.

Both rank receipts bind identical pinned runtime source/API hashes and reciprocal peer metadata hashes, distinct physical GPUs and hosts. Rank receipts finish at **100.161 / 99.996 seconds** from batch T0; stdout reaches `NIXL_PRODUCTION_SPAN_COMPLETE elapsed_s=130.146`. PBS allocation walltime is **229 seconds**, estimated **16.284444 SU**. The discrepancy includes unmeasured shell/container/scheduler overhead; it is not model latency.

## Additional inspection

Both rank phase samples retain CPU RSS and PyTorch GPU allocation/reservation/free/total memory. Maximum sampled allocated memory is **14,465,146,880 bytes**, reserved memory **14,822,670,336 bytes**, RSS **8,063,392 KiB**. These are sampled allocator/process quantities, not KV token occupancy. Sender phases report native KV send 0.004 s, auxiliary send 0.001 s, and source scan 0.068 s; these single diagnostic phases are not serving throughput or network-bandwidth measurements. The request-plan phase takes 15.155 s and includes first-use import/initialization work, so it is not steady-state scheduling cost.

PBS telemetry is retained but internally inconsistent: allocated GPUs are two while resources_used.ngpus is zero, utilization fields show zero, and lowUtilizationTime exceeds job duration. Do not treat these fields as a measured idle GPU or zero errors. Continuous hardware sampling and serving latency/concurrency/queue/token occupancy were not collected in this no-model test. Raw transport logs are inspected for phase completion and explicit errors; absence of a matching error does not prove clean teardown.

## Assessment and next experiment

The earlier small-buffer gap is narrowed: the native transfer can deliver selected request pages at the observed full registration sizes on this physical pair. This does not establish full TP/all-peer deployment, actual model tensor provenance, native request auxiliary strides, EAGLE generated-token equality, goodput, speedup or organiser accuracy. Official accuracy and EAGLE performance remain unverified. H200 25682 remains pending resources; preserve its payload and queue position.

The lifetime fixture checks references only inside `rank_run`; it does not prove tensor ownership through native agent destruction. There is no explicit deregistration/agent-close ordering before function return. This is a teardown uncertainty, not an established cause.

Before a full H100 serving repair, separately instrument each container return, node cleanup and parent exit boundary, with durable independent exit receipts. A diagnostic can keep the already passing data gates and reveal whether the failure occurs during teardown or scheduler staging. Do not rerun the old payload unchanged or promote the PBS failure into a pass.

[Independent replay](independent-head-replay.json), [structured review](REVIEW.json), [terminal raw checksums](collected/evidence-sha256.json), [budget snapshot](RECONCILIATION.json). Published credit has not posted the charge yet; keep the full **42.666667 SU** maximum reserved. Fresh locked internal headroom remains **4507.703333 SU**.
