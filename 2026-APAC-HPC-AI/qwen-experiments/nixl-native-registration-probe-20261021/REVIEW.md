# Native multi-region and DRAM auxiliary gate passes

Reviewed 2026-10-22T00:11:49.638230+00:00. **223132.pbs111 completes F/exit0**, 315 seconds, estimated
**22.400000 SU**. The native register_buffer_to_engine call receives190 distinct
advertised GPU ranges and three pinned DRAM auxiliary ranges on each real rank.
Both physical-rank receipts, reciprocal peer metadata hashes and installed
source/API/binding/PyTorch identities match. All independent byte gates pass.

The actual native init/send methods perform three KV WRITE handles (94/94,
94/95 and95/95) and one send_aux WRITE from host slot1 to slot2. The receiver
compares all GPU/host destination bytes and untouched sentinels. The independent
allocation-head checker and local replay both require the two complete rank
receipts and rebuild expected hashes. Actual KV payload is289792 bytes; host
aux payload112 bytes. All submitted/evidence hashes verify. Raw NIXL metadata
and pointer tables were not collected.

Actual hosts are a2ap-dgx039 and a2ap-dgx037, different from the full-model failure
pair019/031. Joined PBS stdout36861 bytes is inspected and contains no selected
NIXL/remote-disconnect/metadata/Traceback/UCX-error/OOM pattern matches. Empty
per-rank task logs are not a separate health signal because pbsdsh forwards to
PBS stdout. Container fallback-to-extraction warnings remain visible.

## Observability and credit limits

Automatic PBS counters are retained for both nodes, with sampled maximum GPU
memory612MB and coarse zero SM percentages. Their lowUtilizationTime fields
exceed315 seconds and their sample coverage is not established. They cannot
prove zero GPU activity or production health: actual CUDA buffer writes and
hashes are verified separately. No custom phase-aligned sampler, production KV
occupancy, request latency or kernel profile exists in this no-model fixture.
Reported186 CPU-seconds and12499024kB host memory are allocation aggregates,
not scored process demand. There is no goodput or official accuracy result.

The published ledger at the terminal review still contains prepaid In Doubt
42.667 SU rather than a uniquely posted22.4-SU charge. Retain the full42.666667-SU
local reservation and4575.472333-SU internal headroom. Do not subtract In Doubt
a second time from balance. Reconcile the actual charge only after a unique
published delta. The 51000 cap and13000 project reserve stay unchanged.

## Assessment and next decision

This closes the small native multi-region registration and DRAM auxiliary
component, in addition to the preceding base and descriptor gates. It does not
prove production-size registrations, an actual TP4/TP8 collective, native model
bootstrap/concurrent peer lifecycle, EAGLE3 hidden-state exchange, or the failed
019/031 physical pair. Distinct advertised ranges may share CUDA allocator slabs;
no claim counts190 independent physical memory registrations.

Before another full-model retry, require a fresh native KV geometry receipt and
the new independent semantic pair warmup gate. Assess a fresh target-only H200
reference followed by a bounded H200 EAGLE3 correctness diagnostic to preserve
H100 SU; the earlier H100 reference alone is not within-H200 paired proof.
No such port or full-model result is claimed by this component review.
