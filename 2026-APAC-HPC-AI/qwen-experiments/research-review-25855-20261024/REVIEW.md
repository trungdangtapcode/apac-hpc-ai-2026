# S46 H200 deterministic target reference review

Job **25855** completed with exit code 0:0 in 8 minutes 41 seconds (521 seconds), independently verified from the retained Slurm accounting receipt. Independent CPU replays against retained actual artifacts passed the strict target token gate (two passes, four cases, 1,600 actual generated IDs), deterministic runtime parsing, all 16 BF16/NIXL rank checks, 32 native geometry receipts across 188 regions, and both P/D semantic warmup receipts. The candidate reference is sealed at `21a604a4b728cb19d595e3f024f9a73384adfc52b572cfaa691dfbd3237e08f6` and its exact bytes hash to `8161487ef7876603f507be1772e53fb3e58aea99d646c260fb7d1042ab3ef3b9`.

The runtime log records explicit BF16, deterministic inference, PyTorch sampling, FA3 global attention, disabled prefill graphs and decode graphs 1–64. The native source-backed forced FlashInfer allreduce-fusion disable marker is present on decode. Target-only KV has one BF16 allocation per rank. The historical 25585 identity comparison is informational and explicitly not an acceptance gate; this review accepts actual job 25855 from its own artifacts.

The validated geometry contains 188 regions and 32 receipts. Decode KV-head count and semantic layer IDs were not collected. Bounded startup/sequential N=1 telemetry exists across the role devices; its sampled ranges and request timings are retained in [REVIEW.json](REVIEW.json), with no saturation or causal claim. There is no scored performance result, official accuracy result, or EAGLE3 evidence.

Next, the accepted reference can anchor an independently gated EAGLE3 correctness candidate.


Operational review: role samplers logged HTTP 200 polls and transient `URLError` polls during startup/shutdown; these are collection gaps, not serving request outcomes. The decode, router, and both prefill worker logs record Slurm step cancellation during teardown after the token pass, plus a decode-side wait timeout. The retained terminal scheduler result is COMPLETED 0:0, and all independently replayed semantic/runtime/geometry gates pass. Startup/shutdown samples include zero VRAM readings, which are retained as observations and not treated as stable occupancy or health evidence.


Operational review: role samplers logged HTTP 200 polls and transient `URLError` polls during startup/shutdown; these are collection gaps, not serving request outcomes. The decode, router, and both prefill worker logs record Slurm step cancellation during teardown after the token pass, plus a decode-side wait timeout. The retained terminal scheduler result is COMPLETED 0:0, and all independently replayed semantic/runtime/geometry gates pass. Startup/shutdown samples include zero VRAM readings, which are retained as observations and not treated as stable occupancy or health evidence.


The independently queried terminal Slurm receipt is retained in [accounting.psv](accounting.psv).
