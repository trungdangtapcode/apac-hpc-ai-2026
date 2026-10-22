# Native descriptor path passes its small two-GPU gate

Reviewed 2026-10-21T20:01:48.672327+00:00. **223097.pbs111 completes with exit0 in 199 seconds.** All 24
actual native SGLang descriptor WRITE handles complete and destination byte hashes
match the independently rebuilt expected layouts. The three geometries 94/94,
94/95 and 95/95 each pass eight logical TP4-to-TP8 whole-head routes. This totals
9056 descriptor pairs and 2318336 bytes of transferred payload.

## What this establishes

Actual hosts are a2ap-dgx035 and a2ap-dgx039, with distinct recorded GPU UUIDs.
The pinned adapter, common helper, staging helper and installed NIXL API/binding
identities match between ranks. Source/destination pages 1,3 to 0,2 are verified
alongside all untouched sentinel bytes, including unused draft regions. The
allocation-head semantic gate passes and a local replay independently rebuilds
all expected hashes. Submitted nested source paths and the complete evidence
seal verify; the earlier flattened-copy failure in 223091 does not recur here.

Actual joined PBS stdout is inspected (38203 bytes). UCX inter-node RMA log
entries are present and the selected NIXL_ERR/remote-disconnect/metadata-not-found/
Traceback/UCX ERROR/OOM patterns have zero matches. Both per-rank task logs are
empty because pbsdsh output is in joined PBS stdout. Container mount warnings
fall back to extraction and a torchao SyntaxWarning appears; neither is hidden
as an error-free log claim. No assertion proves a specific zero-copy mechanism.

## Accounting and observability limits

Estimated allocation cost is **14.151111 SU**, not the maximum 42.666667-SU
reservation. At the fresh 20:00 UTC locked ledger check the published Used is
still 46367.710 SU; the charge is not uniquely posted, so keep the entire maximum
reserved. Own GPU queue is empty after this terminal job. No cap increase or
full-model allocation follows this review automatically.

Correction to the frozen collector's telemetry scope sentence: raw PBS accounting
also includes automatic coarse GPU counters for node039, including reported
520 MB maximum GPU memory, 2966 J energy and zero sampled SM percentages. Their
mapping/coverage is not verified; reported lowUtilizationTime exceeds the job's
199-second walltime, and resources_used.ngpus is zero despite the two-GPU
allocation and actual GPU proof. These fields cannot establish zero GPU activity
or healthy hardware. The job reports 203 CPU-seconds and peak host memory
8455508 kB, allocation aggregates without phase alignment. No custom matched
GPU/CPU/power sampler, server queues, KV occupancy or kernel profile was collected.
There is no inference request, latency/SLA sample, goodput or contest score.

## Assessment and next decision

Together with 223091, this removes a simple reproducible base-transfer or
small-descriptor arithmetic failure on these selected node pairs. It does not
clear the earlier failed 019/031 pair, native full model startup, large pools,
190 separate layer registrations, CPU auxiliary transfers or actual eight-rank
bootstrap/concurrency. It is not EAGLE3 equivalence or performance proof.

The next distinct cheap hypothesis is to call the actual native registration
method for 190 separate tiny KV regions and the actual DRAM auxiliary send path,
with independent GPU and host byte checks. Prepare and validate that bounded
component before reserving another full model. The separate prospective semantic
warmup gate is CPU-validated; it must be deployed in a fresh integration bundle
before any expensive output-correctness retry. Keep H200/H100 incumbents and
the unverified official accuracy gate unchanged.
