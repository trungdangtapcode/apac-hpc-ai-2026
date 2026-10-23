# Repaired H200 exact reference accepted

Job **25585** is terminal COMPLETED/0:0. Frozen submitted payload and raw bytes match the terminal seal. The actual client captures **8 real responses / 1600 actual token IDs**, including the first token; all four A/B pairs have identical IDs and finish semantics. Both actual P/D warmup receipts replay independently, all 4+4+8 BF16 rank gates pass, runtime and post-run independent head checks pass, and pre-worker/current/result asset identities agree.

Phase times from allocation start: `{'ALL_WORKERS_READY': 328, 'ALL_PAIRS_WARM': 368, 'TOKEN_REFERENCE_PASS': 452}` seconds. Role-specific startup/N1 telemetry coverage, sampled GPU/VRAM/power ranges and exact request timings are retained in REVIEW.json. These are diagnostic samples, not scoring saturation or a startup-speedup comparison. Full KV geometry is not collected.

The missing HOME repair reaches the actual client and establishes the fresh H200 reference that failed 25495 could not provide. No EAGLE3 has run, no performance or official accuracy was measured, and the cached second pass does not establish cold-cache timing. Only now may a separately derived EAGLE3 correctness candidate be prepared, retaining fresh draft identity and actual per-rank geometry/semantic transfer/runtime gates before exact ID comparison and any later matched throughput screen.

[Machine-readable review](REVIEW.json), [actual reference](../runs/25585/target-reference.json), [terminal seal](../runs/25585/artifact-manifest.json).
