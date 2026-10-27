# Four jobs submitted after correcting native GPU visibility

The actual one-GPU direct Enroot probe 26538 completed 0:0 in 39 seconds and returned the expected CUDA tensor result on one H200. It proves the real supplied image can execute CUDA using node-local rootfs storage. The next full jobs 26545/26547 failed before AIPerf: the second prefill step reports global Slurm GPU IDs 4–7, but NVIDIA CLI in that step rejects device 4 as unknown. The relative CUDA mask is 0–3. Prefill 0 and decode both reached their native worker/HPC-Ops initialization; no new score was measured.

The incorrect assumption was that global SLURM_STEP_GPUS IDs could be given directly to NVIDIA CLI after entering the allocated step. The SchedMD definition of global IDs remains correct; the CLI's actual visible indexing differs. Preserve the failed runs and this correction. R2 uses the step-visible CUDA indices, keeps scheduler cgroups, and gives CPU-only steps void GPU visibility. No privileged plugin setting or external account changes.

| Actual new job | Purpose | Resource bound | Scheduling gate |
|---|---|---|---|
|26574|Two four-GPU CUDA tests; require eight distinct UUIDs|8 H200, one node, 4 minutes|No model inference|
|26579|Full N64 chunk 8192 control|16 H200, two nodes, 17 minutes|afterany 26574 + actual split-proof guard|
|26581|Full N64 chunk 10240 intermediate batch|Same|afterany 26579 + same proof|
|26583|Full N64 chunk 12288 larger batch|Same|afterany 26581 + same proof|

The owner explicitly requested three or four queued experiments. These four are concrete distinct roles: one necessary binding prerequisite and a control plus two bounded chunk treatments. The intermediate chunk tests whether partial packing gives a better queue/dispatch tradeoff than the endpoints, not an unchanged duplicate. All three serving arms retain the original full N64/4000:200/seed2026/cold-prefix/60:120:30, model/image/precision/transport and strict runtime/graph/KV/two-route/raw-denominator/latency/error/output gates. No model starts without actual two-by-four CUDA results and disjoint GPU identities. A failed prerequisite aborts before model steps, rather than leaving an indefinitely unsatisfied dependency. No scheduler success or small tensor pass is called benchmark acceptance.

Official full-set accuracy remains UNKNOWN. Prior small-chunk losses and the older 12288/auto-decode loss remain visible. Require >1% useful valid paired improvement and acceptable tails before proposing an independent confirmation; no automatic repetition or widening. No PBS SU, background Codex, package/slide promotion or HPC worker action.

Reproduction: all full frozen payloads and SHA256SUMS are under serving-tuning-11/s84-h200-native-r2-chunk 8192, s85-h200-native-r2-chunk 10240 and s86-h200-native-r2-chunk 12288. Relative to S82, only launcher GPU visibility/CPU masking, declared worker chunk and corresponding checker expectation, identity and prerequisite receipt change. Original benchmark schema is byte-identical. submission-receipts.json contains every definite ID and dependency. The probe has its own retained script, CUDA program and wrapper; its UUID gate is not simulated.
