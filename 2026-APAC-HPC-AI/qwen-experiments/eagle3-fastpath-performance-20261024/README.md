# Fast-default EAGLE performance comparison

The deterministic N64 control 25930 recorded zero requests meeting both latency limits and mean ITL 29.145 ms. Its helper path also failed after profiling. Correcting that path would not make the unchanged slow configuration competitive, so pending helper-only jobs 25940/25941 were cancelled before allocation.

This new pair restores the native fast path on both arms: FlashInfer sampling, MNNVL decode fusion, P64/D256, chunk 8192, BF16 target/KV, prefill graphs disabled and decode graphs 1–64. The actual 25863 control provides positive same-platform evidence: 95.28% SLA and 2,796.15 good output tokens/s under the same short client protocol. Actual 25797 verifies the candidate fast runtime at its historical P48 setting; P64 still needs new runtime evidence. The only paired model-execution factor is EAGLE3.

All original latency, error, source, geometry, two-route semantic and local response gates remain. Official accuracy stays unknown and the earlier exact-ID failure remains failed. The new pair is unranked performance feasibility, not a qualified improvement or promotion. Invalid dependent Slurm jobs will cancel natively instead of remaining pending forever.
