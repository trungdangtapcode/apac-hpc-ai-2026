# A real quality pilot fails the small-sample point gate

The unchanged-FP8 reference 28367 first failed at stock TP8/EP1 weight construction (192-wide MoE partition versus 128-wide FP8 block). It had no model-accuracy result. A separately frozen native EP8 correction 28371 passed, without altering candidate 28368 or scorer. Full source and failure proof are retained.

Both actual 128-question runs are complete and error-free: reference 104/128=81.25%, candidate 102/128=79.6875%. The candidate/reference correct-count ratio is 98.076923%, below the predeclared 0.99 local point gate. Do not call this pilot PASS or infer quality from unchanged weights. It remains a 128-question balanced sample, not the full 12032-question population or organiser reference.

Raw response replay confirms answer parsing/counts. Fourteen answers differ; five reference-only and three candidate-only correct yield the two-answer net loss. Reference 12 and candidate 14 length endings remain scored under the identical 2048 output cap; parser fallback and one invalid reference output are retained. This does not identify an individual causal kernel or descriptor defect. Whole deployments, numeric paths and batch behavior differ; no ablation was run.

Actual top-level cost for failed 103s, candidate 457s and corrected-reference 388s is 4.213333 GPU-hours, zero PBS SU; all reservations retired. Measured pilots size a separately frozen full 12032-question N64 comparison, not a changed scoring rule. Eight balanced shards per role and 16 max 17 minute allocations have a declared maximum 72.533334 GPU-hours; first full shards will test the CoT-duration forecast. No pilot answers are mixed into full-set results. Keep all incomplete/error branches; never cherry-pick retries. Ranked submission/HPC untouched.

[Measured results and limitations](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/reviews/PILOT_RESULTS.md). Preserve raw responses, provenance and failed layout. Full-set and official quality remain unproven until their own actual evidence.
