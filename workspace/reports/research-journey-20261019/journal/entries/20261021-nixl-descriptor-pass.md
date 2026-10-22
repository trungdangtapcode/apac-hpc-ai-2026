# 21 October: real descriptor gate passes; next inspect native registration and aux

Recorded 2026-10-21T20:01:48.672327+00:00. Prior question/change/control and receipt are retained in
[plan](20261021-nixl-descriptor-plan.md) and
[submission](20261021-nixl-descriptor-receipt.md).

**223097.pbs111: F/exit0, 199 seconds, estimated 14.151111 SU.** All 24 actual
native KV descriptor writes pass, three geometries × eight virtual TP routes,
9056 descriptor pairs, 2318336 bytes. Both GPUs/nodes/source identities
and all whole-allocation destination hashes match. Head and local independent
semantic replay agree; all submitted/evidence checksums verify.

[Complete assessment, logs and corrected observability limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-descriptor-probe-20261021/REVIEW.md).
Joined PBS stdout contains UCX inter-node RMA and no selected transport/error
pattern matches; per-rank task logs are empty, not a separate health proof.
Automatic coarse PBS counters exist but lack matched coverage and have anomalous
durations; the frozen collector's broad no-telemetry sentence is superseded by
the precise review. No inference, score, SLA or official accuracy measurement.

The ledger has not uniquely posted this charge at 20:00 UTC: retain42.666667 SU
maximum, leaving 4589.623333 SU headroom before any new reservation. GPU PBS queue
is empty, and no HPC CPU resource is queried. Actual native source confirms
draft descriptor lists are appended to target lists, while the patched sender
uses scalar strides; [static review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/kv-geometry-review-20261021/REPORT.md) distinguishes inference from
missing actual KVArgs capture.

Decision: do not repeat the unchanged full model. Validate one distinct bounded
component for 190 real tiny KV registrations and DRAM auxiliary transfer, then
reserve/submit only after CPU gates and a fresh locked queue/ledger check. The
new semantic pair receipt gate must be included before a future full integration
retry. H200 full incumbent 3023.072304 and H100 incumbent 2433.019859 good output
tokens/s remain unchanged; five H200 positions are preserved.
