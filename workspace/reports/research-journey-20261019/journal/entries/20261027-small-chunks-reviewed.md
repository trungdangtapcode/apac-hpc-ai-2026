# Close smaller chunks after one slower pass and one actual SLA failure

Question: does smaller prefill work reduce queue latency under full native N64? Chunk6144 passes at2661.889812 good tokens/s but is slower than the earlier8192 reference. Chunk4096 produces677 TTFT breaches in1580 profiling requests and only57.151899% qualify; its raw1437.120127 good tokens/s is not an eligible score. Both local output checks pass, so output sanity is separate from latency acceptance. The original strict failure remains.

[Detailed observations with units, resource inspection, limits and next decision](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-small-chunk-review-20261027/REVIEW.md).

The next larger-chunk interaction retains prior old-auto-decode12288 loss. An immediate ENOSPC startup failure led to a different infrastructure repair, not a performance verdict. Preserve all stages and do not infer a score from scheduler submission.
