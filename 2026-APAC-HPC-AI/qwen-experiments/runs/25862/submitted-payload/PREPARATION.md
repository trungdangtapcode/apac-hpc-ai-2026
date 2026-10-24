# S49 preparation record

## Question and prior evidence

Can the pinned EAGLE3 candidate preserve both repeat stability and exact agreement with a separately accepted deterministic H200 target reference, while retaining its draft, runtime, P/D semantic, per-rank geometry, native speculative-counter, and all 1,600 generated-ID checks?

The immediate precursor S45 was waiting for an accepted deterministic target. Earlier target attempt S44 job 25807 failed its strict runtime gate after 309 seconds: all 16 KV ranks had BF16 allocations, but the actual common server command omitted `--dtype`, leaving resolved `ServerArgs.dtype` as automatic. The S46 controlled correction added explicit `--dtype bfloat16` and fixed the parser for the native source-backed forced FlashInfer allreduce-fusion disable marker. Actual job 25855 completed 0:0 in 521 seconds; independent review found the target semantic, deterministic runtime, all-rank BF16/NIXL, 188-region target geometry, and both P/D warmup receipt gates pass. The historical identity comparison with job 25585 remains informational and is not an acceptance gate.

## S49 hypothesis and controlled change

If the S45 EAGLE3 configuration is run under the accepted S46 deterministic target contract, then two EAGLE3 passes should remain stable and match the accepted target IDs, provided every inherited draft/runtime/transport/geometry/semantic/speculative metadata gate also passes.

S49 is a new copy derived from frozen S45. It binds the exact target-reference bytes and accepted review JSON from job 25855, pins both hashes and the artifact-manifest seal, and routes its submission-time bundle path to S49. It ports the S46 runtime parser behavior for the native forced-disable marker while retaining EAGLE3's strict two BF16 KV allocations per rank. S45 files were not modified.

## Validation and limits

CPU/source fixtures pass for the S49 worker's explicit BF16 and deterministic flags, inherited asset and geometry contracts, EAGLE3 deterministic-runtime shape, actual 25855 reference corpus and 1,600 IDs, accepted review binding, and fail-closed unbound/tampered binding cases. Shell syntax checks pass. These validate preparation only.

No S49 GPU allocation, queue submission, endpoint request, runtime result, performance measurement, or official accuracy evaluation occurred. Root review and the root-owned controller/submission decision remain outstanding. A future GPU run must retain all S45 gates, including fresh draft identity, 190-region EAGLE3 geometry, both semantic P/D receipts, native speculative counters, repeat stability, and exact ID agreement with both accepted target passes. The 188-region target-only geometry from S46 does not replace the candidate's 190-region EAGLE3 gate.
