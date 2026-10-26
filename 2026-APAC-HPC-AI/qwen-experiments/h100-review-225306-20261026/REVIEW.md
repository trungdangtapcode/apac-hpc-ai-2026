# H100 EAGLE N24 attempt 225306: semantic setup passed, scoring never ran

PBS records `225306.pbs111` as F/exit 127 after 6:41 on one H100 node with eight GPUs. The PBS stdout names the failure exactly: `timeout: failed to run command 'srun': No such file or directory`. The scored-client stage entered and then the shell went straight to teardown 27 milliseconds later. This is a local launcher integration bug; it is not a failed model benchmark or an SLA result.

The worker launched both roles and the router. All eight H100 devices and native module pins passed the pre-warmup gate. Equal TP4/D4 EAGLE produced an independently validated one-pair semantic response of eight tokens. During that request, all four prefill ranks recorded start and returned-handle markers for both native `send_kvcache` and `send_aux`, with zero observer exceptions. This repeats the bounded functional evidence from 225228 under the scored bundle's exact sources, but it does not measure full-workload quality or speed.

The outer command added by root was `timeout ... srun`. The PBS shim supplies `srun` as a shell function, not as an executable on PATH. External `timeout` tries to `exec` a PATH binary and therefore cannot see that function. GNU timeout returns 127 before invoking any `srun`; thus no AIPerf warmup, profiling request, raw export, smoke or retrieval check ran. The correct repair is to invoke a shell explicitly under `timeout`, source the frozen PBS shim inside that shell, then call its function with an argument-safe wrapper. Derive and test a new R2; never edit the frozen 225306 submission in place. Add a fixture using a temporary shim function, because checking `command -v srun` would miss the same problem.

| Scoring evidence | State |
|---|---|
|PBS terminal record|F, exit 127, walltime 00:06:41; one node, 8 GPUs|
|Pre-warmup metadata/source/device gate|PASS; 8 rank receipts, 8 disjoint H100 UUIDs|
|Native equal-TP observer|Both methods on ranks 0–3, 4 starts/4 returns each, zero exceptions|
|Semantic response|One P/D pair passed, eight output tokens|
|AIPerf scored requests/Goodput|NOT RUN / NOT MEASURED|
|Output smoke and retrieval|NOT RUN|
|Official full-set accuracy|UNKNOWN|

Startup resource samples cover 65 five-second observations across the allocation, not the absent scoring interval: mean sampled GPU activity 17.47% for decode and 13.59% for prefill, with transient maxima 100%; sampled max VRAM was 76.38 and 73.45 GiB/GPU. These startup-inclusive numbers describe model load and one semantic request only. They are not benchmark utilization, idle-capacity proof, or a reason to change concurrency. The role logs show no traceback, CUDA OOM or NIXL transport error. The observed HTTP/2 preface warnings are health-poll noise adjacent to successful health and semantic HTTP 200 responses.

No reference score, Goodput, SLA fraction, output smoke, retrieval score or EAGLE speedup can be calculated for this job. The cost authority retains its 512 SU maximum until the account posts the actual charge; terminal walltime alone does not reconcile the ledger.

Evidence: `PBS-JOB-RECEIPT.json` contains the filtered terminal scheduler fields, `pbs-stdout-selected.log` contains the selected PBS output lines, and `COLLECTION.json` hashes the curated run files. Phase markers, native observer receipts and logs, the independently validated semantic response and allocation telemetry are preserved under `curated-runs/`. The full AIPerf input dump, authentication/session state, weights and runtime caches were not collected. No qsub retry or credit change was made by this review.
