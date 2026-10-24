# R6 source review

The R6 experimental distinction is the initialization protocol: serial P0→D then P1→D, followed by both routes concurrently with independent receipts and phase-bounded native transfer observations. Both phases use the same request text and same worker processes.

Source comparisons against frozen R5:

- `nixl-conn.py` is byte-identical at SHA-256 `912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f`.
- All 11 files in `pd-observer/` are byte-identical to R5, preserving metadata and native-send instrumentation.
- `worker.sh` changes only the optional `QWEN_TEST_UCX_IB` branch used by the CPU fixture. Without that variable, the original InfiniBand discovery block runs unchanged. The fixture executes the full launcher and checks emitted SGLang args for both prefill and decode roles, including explicit `--dtype bfloat16`.
- `capture-worker-locality.py` is restored from the source used by the R3 lineage (SHA-256 `c4d24551e54ebc1ad6a84b2604b9ef6b7ed3bcd2020ae1b3939569ca6cc62ec6`). R5 worker logs show this intended diagnostic failed because its file was absent.
- `config.json`, `benchmark.pbs`, `phase-controller.py`, `topology-job.sh`, `warm-topology.py`, and `observer-gate.py` carry the new candidate identity, 20-minute cap, serial/concurrent phases, and separate receipt checks. Model paths, dtype, EAGLE settings, TP4/TP4/TP8 placement, router policy, NIXL backend, and graph settings remain the R5 values.

R5 logs show NIXL agent IDs and peers as UUIDs (`uuid.uuid4()` in the native connector), with distinct agent IDs in the retained logs. There is no evidence of a static hostname/TP-rank name collision. R5 used nodes `a2ap-dgx024` and `a2ap-dgx028`; a future R6 allocation is not pinned to that pair, so only its within-allocation serial/concurrent contrast is controlled against node placement.

R6 deliberately stops after the semantic and native-send phase gates. The exact 1,600-ID comparison is not run, and no correctness or score claim is made.
