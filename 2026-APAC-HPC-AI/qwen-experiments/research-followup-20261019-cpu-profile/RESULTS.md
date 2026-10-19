# CPU and GPU diagnostic submission

Job **221886.pbs111** was submitted at **2026-10-19T14:40:52 UTC**, with a verified `afterany:221885.pbs111` dependency. This extended the existing serial protocol pair without overlapping 16-GPU allocations. Frozen payload hashes and the scheduler receipt are retained alongside this report.

The ranked N54 benchmark repeats the accepted both-HPC-Ops baseline. Only the separate post-score diagnostic requests CPU and GPU profiler activities instead of GPU alone; ranked traffic and worker settings are unchanged. This is evidence collection, with no predicted throughput gain. Pinned runtime schema support and byte-identical ranked files were checked before submission.

At submission, published Used was 30729.102 SU, Balance 33270.898 SU and In Doubt zero. The 1536-SU maximum reservation brought outstanding conservative reservations to 6144 SU, including finished job 221880 whose charge was not yet published. Internal headroom was 14126.898 SU under the unchanged 51000-SU operating cap and 13000-SU buffer. These are submission-time figures, not current charges.

A later check at 17:20 UTC found 221884, 221885 and 221886 terminal with exit status zero. That alone does not establish valid measurements: their raw evidence is being collected for separate protocol, runtime, latency and output reviews. The latest published credit and terminal-charge reconciliation belong to the subsequent review checkpoint.
