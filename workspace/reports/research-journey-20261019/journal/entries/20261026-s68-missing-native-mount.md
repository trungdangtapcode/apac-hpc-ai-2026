# S68 job 26308 failed at source identity, not transport

26 October 2026. Actual Slurm accounting is FAILED 1:0 after 1:54 on g1/g4. All 16 rank logs have distinct actual H200 GPU UUIDs, then reject the same missing-source-mount error before creating NIXL agents, registering VRAM or posting transfers. No rank result exists; goodput/accuracy/transport timing and byte verification were not measured. This is our packaging error, not evidence of bad network, GPU fault or failing S62 communication.

The copied proven peer helper requires the deployed patched conn.py SHA 912b7e…; this container launches with the unmounted image's original conn.py SHA 28da79…. The submitted job forgot the native source mount. The pins correctly rejected this mismatch. They must remain unchanged. Source extraction independently confirms the installed nixl_cu13/_api.py hash 27c3ce… matches the helper's exact pinned API.

An early-stop command was issued only after all 16 raw logs proved the same pre-agent failure and srun teardown was still active; preserve early-stop.json. Final accounting records FAILED 1:0, not cancellation; do not rewrite that state based on the command alone. The allocation is 0.5067 GPU-hours; it has no separate PBS SU charge. Startup logs prove 16 GPU identities but no continuous GPU/CPU telemetry was collected. Ephemeral pointer/metadata exchange files were not produced/retained; no credentials were involved.

Prepare a new S68r2 bundle that mounts the exact already-retained patched 912b7e source and checks the effective mount's hash before launching ranks. Byte-transfer algorithm, all result gates, deadlines and role placements remain identical. This repairs a failed prerequisite; it is not a blind repeat of measured transport. The original one-attempt component rule closed the submitted payload; the reviewed derived prerequisite repair gets one bounded attempt. No full-model topology retry is authorized by a component pass. Four full incumbent-recovery jobs remain queued/running and unchanged.

Raw retained evidence: runs/26308, its submitted-payload and scheduler-accounting.txt; [inspection](inspection.json); [early stop](early-stop.json). The first source-extraction command also failed on an existing destination/incorrect package path; corrected selected-file extraction found nixl_cu13. Both extraction logs remain historical CPU preparation evidence.

Source: qwen-experiments/research-review-26308-20261026/REVIEW.md
