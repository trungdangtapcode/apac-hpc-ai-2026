# Native runtime R3: actual dispatch

Recorded 2026-10-27T17:56:03.194845+00:00 (2026-10-28T00:56:03.194845+07:00, Vietnam time).

Job 26574 passed actual split-four plus split-four CUDA on eight distinct H200 UUIDs. Full control 26579 reached all workers, source/runtime/KV gates and both semantic routes, but the AIPerf image's default command script interpreted the intended `env` argv as an AIPerf subcommand: `Unknown command "env"`. It produced no profile export or valid score. Jobs 26581 and 26583 failed the existing 120 GiB local rootfs capacity guard, at router startup and initial worker startup respectively. They are failures, not completed valid measurements.

R3 explicitly sets Enroot `--rc` to a frozen `exec "$@"` script. It keeps the CUDA visibility repair and all existing source mounts and scheduler cgroups. The installed Enroot 4.2.0 help and `/usr/lib/enroot/runtime.sh` establish that a command is otherwise passed to the image command script; the actual new probe tests the real image. Startup and post-worker cleanup remove only owned `/tmp/apacsc42-native-JOB-STEP` directories belonging to independently verified terminal jobs, or the current job after step clients have terminated. Removal uses Enroot's own rootfs removal operation, within the existing allocation deadline. No other account's files are selected.

Actual prerequisite **26764 completed 0:0 in 5 seconds** on g1/g4. The real AIPerf image accepted `env ... bash -c ...`, asserted the intended environment and empty CPU-step CUDA mask, and reported AIPerf 0.12.0. Both nodes' cleanup scans succeeded. There were **zero matching own native roots** at both scans, so actual stale-root deletion was not exercised. Available local space was approximately 253.9 GiB on g1 and 148.0 GiB on g4. Own leaked rootfs files are not established as the cause of previous capacity failures; transient node occupancy and the conservative per-extraction guard remain limitations. The 120 GiB guard is unchanged. Post-step cleanup is a precaution, not a measured performance optimization.

| Accepted job | Frozen payload | Resources | Dependency |
|---|---|---|---|
|26764|native-runtime-r3-20261027/probe.sbatch|2 nodes, zero GPUs, 5-minute maximum|None; now COMPLETED 0:0|
|26766|s87-h200-native-r3-chunk8192|16 H200, 2 nodes, 17-minute maximum|afterany 26764 plus actual proof guard|
|26768|s88-h200-native-r3-chunk10240|Same|afterany 26766 plus actual proof guard|
|26770|s89-h200-native-r3-chunk12288|Same|afterany 26768 plus actual proof guard|

These three performance arms retain full N64, fixed 4000/200 tokens, seed 2026, cold prefixes, 60-second warmup, 120-second measurement and 30-second grace. They preserve P4+P4/D8 EP8, FP8 weights with BF16 activation/KV, breakable prefill graph and HPC-Ops decode. Only prefill chunk differs across the new arms. Unchanged model worker, benchmark, expected inputs and strict checkers are byte-compared with each arm's parent; Python AST, shell syntax and manifests pass. The generated payloads are frozen. Scheduler acceptance and test-only receipts are retained in submission-receipts.json. The initial local build command used the wrong working directory, created only a nested local preparation directory and did not submit a job; its own new files were moved to the intended directory before the successful checks and actual admission.

The three full jobs remain pending at this snapshot. They must pass actual runtime/source/KV/two-route, raw joint latency at least 90% including errors in the denominator, zero request errors/cancellations and local output non-regression before interpretation. Require a useful gain over 1% against the same-runtime control before independent confirmation. Official full-set 99%-reference accuracy remains UNKNOWN. Neither probe is a throughput score. Historical H200 3044.400475 good tokens/s mean remains historical, not reproduced by these failed jobs.

H100 access was also checked using both existing authorised SSH helpers. Both returned `Expected one live VPN session`; no working session was discovered and no authentication prompt or VPN restart was triggered. Both current PBS queues are unknown. Prepared H100 R2 therefore remains unsubmitted under the required combined queue gate. The H200 jobs continue independently. No HPC payload, ledger, package, slide or schedule changed.
