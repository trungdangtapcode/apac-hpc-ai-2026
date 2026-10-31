# Fresh H200 control 27777: full local pass, no optimization claim

Reviewed 2026-10-31T10:52:36.841813+07:00, Vietnam time (UTC+7). Slurm COMPLETED 0:0 in 13:08 on g1/g4,
16 H200. Frozen manifest, raw full N64 protocol, actual runtime/physical KV/both
semantic paths and output checks replay successfully. Actual decode backend is
FlashInfer; no draft is loaded. The stdout label UNRANKED_EAGLE_PERFORMANCE_PROTOCOL_PASS
is inherited harness wording, not evidence that this control uses EAGLE.

| Quantity | Result |
|---|---:|
| Good output throughput |3038.022907 tokens/s|
| Exported Goodput |15.190114534 requests/s|
| Joint qualifying requests |1872/1898 (98.630137%)|
| Profiling errors/cancellations |0/0|
| TTFT/mean-request ITL breaches |26/0|
| TTFT mean/p95 |1120.236/1396.041 ms|
| Request-mean ITL mean/p95 |15.007/15.349 ms|
| Small output non-regression / retrieval |7/8 and 12/12|
| Actual allocated GPU-hours |3.502222|

Official score formula remains exported Goodput times 200. Full 60/120/30,
requested 4000/200, client seed 2026 and cold-prefix workload remain. Official
full-set accuracy remains UNKNOWN; these small output checks do not certify 99%
of reference. The score is -0.101827% versus prior 27376;
this is same-setting variation, not a new gain. Use this fresh control for 27779
and the N64 recipe comparison 27783. Do not substitute a historical peak.

## What was collected and inspected

Raw profiling requests and export retain all 1898 requests, 26 TTFT breaches and no
ITL breaches. Tail distributions including p50/p95/p99/max are in the extended
review. Three raw runtime logs show zero Python tracebacks or selected transport/
OOM errors. There were two setup HTTP 503 retries before scoring because pair
routers initially saw no available prefill worker. Both semantic paths later
passed; distinguish those setup retries from zero scored errors. Native terminal
cleanup receipts are retained.

Five-second samples inside the first-to-last profiling-request-start envelope
cover 24 observations per role: four/four/eight distinct GPU UUIDs. Decode activity
averages 100%, prefill 95.698%/97.323%; sampled per-GPU VRAM means 131.268 GiB decode
and 130.207/130.209 GiB prefill. Decode mean/max running requests 50/54, sampled
queue 0 and mean KV token usage 0.12; these are different from VRAM occupancy.
Prefill sampled queue maxima 3/3. All 72 server metric polls return HTTP 200.
Host CPU busy estimates 13.86% on g4 and 12.57% on g1 do not establish scheduler
hot-thread headroom. Available raw power/clocks/temperature/memory-activity
samples were inspected and summarised in control-review-27777.json; no causal
kernel or bandwidth bottleneck is inferred. Heavy traces, Xid/throttle reasons,
authoritative generated token IDs and per-thread demand were not collected.
Uncalibrated host clocks and sparse sampling exclude exact phase/drain coverage.

## Decision and preservation

Keep this as the current matched control, await 27779 and 27781/27783, and do not
promote another recipe until its complete acceptance and comparison pass. The
four-job wave is already admitted; no blind fifth or redundant control is added.
Terminal raw files, frozen payload, client inputs, request records, resources and
scheduler proof are sealed in runs/27777/artifact-manifest.json. Git captures
retain recovery manifests; large external objects require a separate off-host
copy and are not uploaded by Git alone.
