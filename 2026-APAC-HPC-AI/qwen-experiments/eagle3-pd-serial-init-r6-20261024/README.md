# R6 serial and concurrent P/D initialization diagnostic

**Prepared only. This candidate has not been uploaded or submitted.** It requests two H100 nodes, 16 GPUs, and at most 20 minutes. The conservative full-walltime cap is **682.666667 SU** (`1200 s × 16 GPUs × 128 SU/GPU-hour ÷ 3600`). Actual cost would depend on scheduler accounting. This draft does not alter the queue or reserve budget. Any future submission needs an explicit PBS `afterok:224276.pbs111` dependency and the in-job accepted-parent receipt gate.

R5 `224277.pbs111` passed the 16-rank metadata and loaded-source gates, then both P-to-D semantic calls failed during concurrently launched warmup. Its two errors surfaced as a NIXL sender exception and remote disconnect; it did not establish their root cause. R6 separates first-session initialization from simultaneous follow-on traffic within one allocation:

1. Require all three roles' 16 actual metadata receipts, matching names, dtypes, and widths, and six loaded `conn.py` / `utils.py` source reports before sending requests.
2. Launch both P-to-D routers and send the same two semantic requests **serially**: P0 to D, then P1 to D. Replay both receipts in a phase-specific directory with a phase-specific run token.
3. Keep the same worker processes, model, topology, request content, and endpoint inventory. Send both routes again **concurrently**, using a different phase-specific receipt directory and token. Replay both receipts independently; the serial receipts cannot satisfy this gate.
4. Retain per-rank native KV and auxiliary send markers, role-specific 5-second GPU telemetry, worker-locality diagnostics, and phase markers. The diagnostic ends after both semantic phases; it does not run the 1,600-ID comparison or claim output correctness, official accuracy, or a score.

A serial pass followed by concurrent failure would show that concurrent follow-on traffic still fails after serial initialization. A pass in both phases would support only a local hypothesis about the observed initialization sequence; it would not prove the transport root cause. If serial fails, the controller stops before the concurrent phase and preserves the failure artifacts.

R6 leaves the native NIXL source (`912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f`), model, precision, EAGLE settings, TP4/TP4/TP8 layout, router policy, graph settings, and worker launch arguments unchanged. The worker receives an opt-in test-only UCX-interface override for the local argv fixture; normal execution still discovers active InfiniBand interfaces. A CPU regression executes the actual worker launcher and checks target/draft dtype, EAGLE, transfer, and graph arguments, including `--dtype bfloat16`.

R5's frozen worker launcher referenced `capture-worker-locality.py`, but the helper was absent from that bundle; its retained locality logs show the file-open failure. R6 includes the matching source-backed helper at SHA-256 `c4d24551e54ebc1ad6a84b2604b9ef6b7ed3bcd2020ae1b3939569ca6cc62ec6`, so role-locality evidence is actually available in a future run. This only restores the configured observation.

See [PLAN.md](PLAN.md), [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json), [CPU_VALIDATION.json](CPU_VALIDATION.json), and [R5 source checksum snapshot](R5_ROOT_SHA256SUMS). `SHA256SUMS` covers the frozen runtime payload. No credential, session cache, receipt, queue mutation, GPU result, or submission approval is included.

## Final root admission contract

Root retains the actual passing224276 parent-receipt gate in the batch. Its PBS afterok condition is already satisfied. To preserve one running AI allocation with the independent kernel probe, the new scheduler dependency is **afterany:224460.pbs111**. This supersedes the draft admission wording above; it does not make kernel success a prerequisite for this independent transport experiment. Root rechecks the actual parent status, combined CPU/AI queues and selected AI credit under the usual locks.
