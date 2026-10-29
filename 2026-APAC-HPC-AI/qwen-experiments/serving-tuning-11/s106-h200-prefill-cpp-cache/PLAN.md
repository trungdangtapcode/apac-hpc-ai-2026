# S106 C++ prefill-cache experiment plan

This is a prepared AI/Qwen experiment, blocked on actual zero-GPU prerequisite 27387 and root admission. It has no full-model submission receipt yet.

Question: does the native experimental C++ radix tree reduce prefill bookkeeping while preserving prefix caching? Compare against completed native control 27376, 3041.119598 good output tokens/s. The single serving treatment enables SGLANG_EXPERIMENTAL_CPP_RADIX_TREE=1 only on the two TP4 prefill roles. Decode TP8, ChunkCache, cap 256, polling interval 1 and all other model/precision/topology settings remain unchanged. Role-private build caches and MAX_JOBS=2 constrain cold C++ JIT startup.

Before admission, actual 27387 must complete 0:0 and pass its source-pinned CPU tree fixtures, hidden GPU checks and cleanup evidence. Metadata-only page16 is not page16 KV acceptance. The full candidate must then pass actual all-rank C++ cache selection, physical BF16 KV, source/geometry, both semantic routes and local output smoke before its performance client. The source manifest and each worker are checked before import.

Use the unchanged requested N64 cold 4000/200 workload, seed 2026 and full 60/120/30 timing. Reserve 16 H200 on two nodes, at most 17 minutes (4.533334 GPU-hours); startup 600 seconds and absolute job deadline 1020 seconds are unchanged. Do not add dependency chains or modify old jobs. Missing evidence or a terminal error is not a measurement.

Independently review raw score, good fraction, errors, tail latencies, actual runtime, queue/KV state, sampled hardware and cleanup after completion. Require greater than 1% useful gain and acceptable tails before matched confirmation; otherwise close the exact setting. Official full-set accuracy remains UNKNOWN; local smoke and retrieval do not certify it.

The candidate README and study README explain the current experiment. Inherited SOURCE/PARENT provenance and derive.py document historical ancestor stages; do not run that inherited derivation script to recreate S106. The exact 27376 submitted payload, current configuration/files, DERIVATION_REVIEW.json and checksums identify this candidate. No original parent payload was changed.
