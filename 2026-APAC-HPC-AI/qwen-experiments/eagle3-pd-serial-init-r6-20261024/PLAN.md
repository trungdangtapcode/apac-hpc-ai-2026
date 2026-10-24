# R6 experiment plan

## Research question and prior result

R5 `224277.pbs111` reached ready state and passed its 16 actual metadata receipts and six loaded-source checks. Both semantic routes were then submitted concurrently to one TP8 decode worker. Both returned HTTP 500 during P-to-D KV transfer, with NIXL sender/remote-disconnect errors. The remote disconnect's internal cause was not captured. The two simultaneous requests are a plausible confound, not a confirmed cause. R5's exact 1,600-ID gate never ran.

R5 startup took about 490 seconds from its controller T0 to startup end. R6 caps startup at 650 seconds, leaving 160 seconds of headroom versus that single observed allocation. Different scheduler placement and workload variation remain risks; R5 used `a2ap-dgx024` plus `a2ap-dgx028`, while R6 node selection is not fixed. Within R6 both semantic phases share one allocation and worker processes. R5 native agent IDs are UUIDs (`uuid.uuid4()`), not hostname/TP-rank strings, so static agent-name collisions are not supported by the evidence.

## Hypothesis and control

A cold pair of simultaneous P-to-D requests may expose an initialization interaction that is distinguishable from later concurrency after both route pairs have been initialized serially. The control sequence uses the same endpoint inventory, P0/P1 prompts, model, NIXL source, TP4/TP4/TP8 geometry, and running workers in both phases. Only request order/concurrency and receipt namespace differ.

- Serial phase: P0 to D, then P1 to D; two separately replayed receipts.
- Concurrent phase: P0 to D and P1 to D at once; two new receipts under a distinct run token and directory.
- Fail closed if either phase lacks both independently valid receipts. An earlier phase's receipt cannot satisfy a later phase.

## Source changes

The intended experimental change is the serial-then-concurrent semantic initialization protocol. The observer gate independently verifies both phase receipt sets and preserves the R5 metadata/source and native-send gates. Controller deadlines are reduced for a 20-minute allocation: startup 650 seconds, serial 90, concurrent 90, teardown 90; total main envelope 920 seconds. All phase deadlines are absolute from allocation T0 and run-local phase start.

The model, bfloat16 dtype, EAGLE3 arguments, NIXL source, topology, router settings, graph behavior, request body, and native method instrumentation remain unchanged. Additional non-experimental corrections restore the missing R5 locality helper and add an opt-in CPU test seam for InfiniBand discovery so the actual worker argv can be checked without a cluster.

## Acceptance and interpretation

A diagnostic pass requires all 16 metadata receipts and six source reports before the first request; both serial receipts; both concurrent receipts; independent replay of each phase; and per-rank native KV/aux invocation and outcome markers. A returned NIXL handle is not completion evidence. A failed phase is preserved and blocks later phases.

- Serial pass, concurrent fail: evidence that concurrent follow-on traffic can still fail after serial initialization; investigate per-route/session handling.
- Both pass: local evidence that this sequence passed once. It does not establish the R5 root cause or prove general P/D correctness.
- Serial fail: preserve the first phase's per-route responses and logs; do not run the concurrent phase.

This diagnostic stops after semantic receipt checks. It does not run output-ID comparison, full accuracy, AIPerf, performance screening, or official scoring. The 1,600-ID result from the accepted H100 reference remains untested here. A passing warmup is not a correctness or competitive-performance result.

## Resource and evidence limits

The request uses at most 16 H100 GPUs for 20 minutes; the full-walltime conservative maximum is 682.666667 SU. This is a ceiling estimate, not a ledger posting. The run retains PBS output, task logs, metadata and source receipts, transfer events, phase markers, resource samples, and worker-locality diagnostics. It does not enable an unverified NIXL logging environment variable or heavy profiler. Network counters and backend-level traces remain unavailable in this draft.
