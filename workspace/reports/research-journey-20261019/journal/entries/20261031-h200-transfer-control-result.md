# Fresh H200 control: reproduce before interpreting transferred candidates

Reviewed 2026-10-31T10:53:26.134276+07:00, Vietnam time (UTC+7). Question: can the original
H200 native incumbent still reproduce its retained approximately 3044-good-token/s
level before comparing H100-derived candidates? Job 27777 completes 0:0 in 13:08
on 16 H200/g1/g4 and passes the full independent frozen raw/source/runtime/KV/
semantic/output gates at 3038.022907 good output tokens/s. 1872/1898 requests meet
both SLA thresholds (98.630137%), 26 TTFT and zero ITL breaches, zero profiling
errors/cancellations; smoke 7/8 without regression and retrieval 12/12.

Mean/p95 TTFT 1120.236/1396.041 ms and request-mean ITL 15.007/15.349 ms are retained
alongside p50/p99/max and all raw requests. The approximately 0.102% lower score
versus earlier 27376 is ordinary same-setting variation in this one observation,
not evidence of a new optimization. Use 27777 as the prospective comparator for
27779 and the N64 H100 recipe 27783, preserving unlike-load comparison limits.

Inspect beyond the score: 24 samples per role cover 16 distinct GPU UUIDs; decode
GPU activity 100%, prefill 95.698%/97.323%, per-GPU VRAM means 131.268 GiB decode
and 130.207/130.209 GiB prefill. Decode running mean/max 50/54, sampled queue 0,
KV token usage 0.12. All 72 metric polls HTTP 200. No selected transport/OOM marker
or Python traceback in the three role logs. Two setup HTTP 503 responses before
scoring were retried and both semantic paths subsequently passed; distinguish
setup retries from profiling errors. Power/clocks/temperature/memory activity
distributions and host CPU estimates were inspected. Sparse time envelopes,
uncalibrated clocks, missing per-thread/hardware-throttle/kernel traces and
actual token IDs prevent a causal bottleneck claim. Official full-set accuracy
is UNKNOWN. Actual allocation 3.502222 GPU-hours, zero PBS SU.

Decision: retain a qualified fresh control, await the three already admitted
candidates and do not promote a recipe or add a redundant fifth job. 27779 is
running with actual FA3 runtime configuration proven; 27781/27783 Resources-pending
in the scheduler snapshot. All terminal raw/control files and payloads are
sealed; source manifests and selected evidence are captured separately from
large external objects. Git alone does not upload the latter.

[Complete control review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-attention-transfer-20261031/CONTROL_RESULTS-27777.md),
[raw/run seal](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/27777/artifact-manifest.json).
