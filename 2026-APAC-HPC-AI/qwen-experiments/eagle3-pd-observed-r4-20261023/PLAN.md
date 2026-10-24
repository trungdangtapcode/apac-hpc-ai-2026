# R4 prospective H100 EAGLE3 correctness candidate

**Status: PREPARED_NOT_SUBMITTED.** This folder is a derived review draft. It has not been uploaded to the cluster, queued, reserved, or run on a GPU. Root owns independent review, final packaging/freezing, and any later submission decision.

## Prior result and question

The source payload is frozen `eagle3-pd-eager-prefill-r3-20261021`, receipt **223055.pbs111**, which failed F/exit 1 after 734 seconds with zero completed diagnostic responses. Its review records an HTTP 500 `NIXL_ERR_REMOTE_DISCONNECT` during pair warmup followed by missing remote-agent metadata and `NIXL_ERR_NOT_FOUND`. That chronology does not identify whether the first failing remote operation was KV or auxiliary transfer. The head printed `ALL_PAIRS_WARM` despite the remote task failure; that marker cannot be treated as a pass. The original payload, receipts, collection, and raw failure remain untouched.

The prospective observation is whether the first remote failure follows `send_kvcache_slice` or `send_aux`, alongside actual P/D metadata row names, widths, dtypes, and counts. Both native methods remain byte-identical to the original `912b7edb...` implementation; the wrapper records call start and method return/exception only. It does not report asynchronous transfer completion and is not a transport fix.

## Controlled candidate

R4 retains the R3 accepted H100 target-only reference (`target-reference.json`, identity `61b899e3acfb6570e93049dfeca03cf66ae5cb3a2bdf89c03938f3d98da44aeb`) and prepared 4-case corpus. The client still requires 200 actual output IDs per case for both repeated speculative stages, for 1600 actual IDs total, exact output/finish equality to the target reference, and independent response checks. No AIPerf run, ranked score, speedup claim, or official accuracy claim is part of this candidate.

The inference settings remain target FP8, BF16 EAGLE3 draft requested as unquantized, two draft steps, top-k 1, three draft tokens, TP4 + TP4 prefill with HPC-Ops and 4096 chunking, and TP8/EP8 decode with HPC-Ops, MNNVL and FlashInfer. Prefill graph capture is explicitly disabled on both worker types; decode retains native graph captures 1 through 64. The NIXL patched source remains exactly SHA-256 `912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f`.

## New evidence gates

1. Each server Python process adds `pd-observer/` to `PYTHONPATH` only after the worker's existing preflight imports and immediately before `launch_server`.
2. Before semantic warmup, `observer-gate.py pre-warmup` requires exactly 16 actual per-rank metadata receipts (P0 TP4, P1 TP4, D0 TP8), all six actual loaded-source reports (the three roles × `utils.py` and patched `conn.py`), and matching actual names and item widths across roles. P/D row counts may differ and are measured, not guessed.
3. Pair warmup uses the retained H200 `warm-topology.py` and `warmup_semantic.py` helper unchanged. It must create two replayable semantic P/D receipts. After the helper returns, the controller independently reruns its semantic checker and requires per-prefill-role `send_kvcache_slice` and `send_aux` start plus returned-handle or exception observations. No successful transport completion is inferred from a handle.
4. Only after those gates pass does the client run the existing two-stage, four-case exact target-reference check. `check-token-result.py` remains the independent final head gate; warmup stdout is not a gate.

The observer writes no pointer values, raw tensors, request contents, notification strings, or peer names. Each peer name is SHA-256 hashed. Transfer evidence is capped at 128 marker records per process. The module source hashes are checked at import and recorded as actual loaded paths and hashes.

## Runtime and budget bounds

The batch requests PBS project 59010042, two scattered exclusive nodes × eight H100, queue `normal`, and 30 minutes (1024 SU maximum). No reservation is made here. Runtime shells use non-login Bash; the node shim sources `/cm/local/apps/environment-modules/4.5.3/init/bash` only when `module` is unavailable, loads Singularity 4.1.5, and invokes `/opt/pbs/bin/pbsdsh` explicitly. The existing legacy CPU envelope, native NUMA behavior, and PBS GPU-mask calculation are retained. User profiles are not changed.

One batch T0 anchors absolute per-phase deadlines and the cumulative ceiling: startup 900 seconds; warmup 180; client 300; head 60; teardown 90. Each phase deadline is computed from its actual start and clipped by the corresponding cumulative T0 boundary; the full main envelope is 1530 seconds, below the 1800-second PBS walltime. Resource sampling is bounded to the same 1530-second ceiling; no heavy profiler is launched.

## CPU validation and limits

`test-launcher.py` exercises the actual R4 warmup dispatch block and PBS shim with an isolated mocked pbsdsh, including argument preservation, path spaces, returned exit status, timeout termination, child-Bash function inheritance, non-login shell checks, and absolute pbsdsh selection. `test-phase-controller.py` checks absolute deadlines and the 1530/1800-second bounds. `test-semantic-head.py` replays the exact accepted H100 reference through the existing head validator and proves a one-ID mutation fails. The observer suite has six fake-tensor/mock-transfer tests covering the 16-rank source gate, tuple identity, missing/contradictory receipts, transfer outcomes, and the event cap.

These checks use CPU fixtures only. They do not prove that the pinned image loads these exact modules on H100, that either transfer path is invoked successfully, that PBS propagates remote exit status, or that the new candidate passes actual-output equivalence. A source report, 16-rank layout, both observed method paths, two semantic receipts, and all 1600 matching real IDs remain required before any pass claim.
