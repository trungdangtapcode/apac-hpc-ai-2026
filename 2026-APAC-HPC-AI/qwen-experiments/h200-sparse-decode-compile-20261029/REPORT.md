# Sparse Decode Graph Review

## Disposition

**S107 is a compile-off sparse-graph startup and padding trial prepared for root review. S108 is blocked and has no submission entrypoint.** No job was submitted here. The source findings support the S107 graph list, but the S108 compile hypothesis is invalidated by job27383's actual source-level runtime failure.

## Pinned source and actual compatibility

The active image is `/scratch/enroot-images/sglang-harbor.sqsh`, SHA-256 `b74ae77446bfedd6c5d72820b45be255cc513cf7c7c039d1bf63679c8178bfe5`. [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) records hashes of selected source files copied from that image.

On GPU, explicit `--cuda-graph-bs-decode` sizes become the phase graph list; server-argument resolution takes its maximum as graph `max_bs`. The runner filters that list by request-pool size and attention/TP alignment. With graph padding enabled, `_pad_to_bucket` uses `bisect_left` to select the next retained size. The compile shape list is the retained capture list filtered by `torch_compile_max_bs` when compile is on.

Job27376's actual decode `ServerArgs` give TP8/EP8, DP1, DP attention off, no attention gather, no MLP gather (`moe_a2a_backend='none'`, `moe_dense_tp_size=None`), no two-batch overlap, and `disable_cuda_graph_padding=False`. These settings make the pinned graph-batch alignment function resolve to 1; none of 50/52/54/56 is removed. The AST-based parser in the new startup checker reads the full logged `ServerArgs` constructor representation and tests this exact runtime configuration without importing PyTorch.

The proposed S107 list has 12 capture buckets. With cap56, a hypothetical compile-enabled path would select 11 of those buckets; this is source-derived eligibility only, not a claim that 11 shapes compiled successfully or that the current model supports this. Job27383 proves the latter is false for current source.

## Startup evidence and invalidated compile branch

The raw 27376 decode log at `../runs/27376/decode-0.log` (SHA-256 `1ce43f2b5b22defe7410f357329f524a419c3f3cbc3008f0f9baabc0c2e2e14a`) records all64/64 CUDA graph captures. TP0–TP7 report 101.46–101.49 seconds and 1.15 GB (native log label) capture memory per rank. The first capture progress interval is 80.90 seconds/iteration after entering DeepGEMM JIT precompile. The bounded facts and limits are in [baseline-capture-facts.json](baseline-capture-facts.json).

Job27383 completed **FAILED, 1:0 after 3:35**. Its retained decode log (`../runs/27383/decode-0.log`, SHA-256 `e68083c0306d57b1936c71ff5d20265f048d670334f7ffec3bedbcabbfd8fe94`) shows the failure in `qwen3_moe.apply_qk_norm_rope` through `torch_dynamo_resume...` into `sglang/srt/layers/rotary_embedding/base.py:244`: `AssertionError: fused_set_kv_buffer_arg is not supported for native implementation`. This is a native Qwen3 compile incompatibility, not an overlarge graph list or compile timeout. All eight retained rank receipts record compile enabled for bucket54, but zero successful graph captures for54; the other graph captures 55–64 do not imply a completed startup. Their SHA-256 values and the config hash are in [blocked-compile-evidence.json](blocked-compile-evidence.json).

Because S108 still includes compile bucket54, sparse graph selection alone does not avoid the failing native call. S108 is **source-only blocked** pending a separate code-level remedy and qualification. It has no `job.sbatch`, `worker.sh`, or `topology-job.sh` admission path. Do not spend GPU on it or use its synthetic compile fixtures as evidence of compatibility.

## S107 guard and limits

S107 uses `[1,2,4,8,16,32,48,50,52,54,56,64]` with compile disabled. It compares the sparse list against the existing full-list control27376 as a bounded startup/padding observation; the comparison has normal run-to-run variation. It does not act as a future compile-fix control unless the code/runtime and remaining settings are shown to match exactly.

Before the N64 client, S107 validates the effective server arguments, source hashes, current Slurm job ID, unique experiment ID, role, distributed world-size8 and exact receipts from ranks0–7. Every sparse graph bucket must have a successful capture on every rank; graph bucket56 is included among required hot buckets. A new observer runs identically on the S107 decode ranks, records graph capture, then restores the global hooks and takes a direct-call fast path before benchmarking. A small Python branch remains in the proxy; this is an instrumentation caveat. S108-only compile-counter requirements remain dormant and blocked.

CPU-only synthetic fixtures test the checker with fake receipts, including deterministic raw-receipt replay, an absent bucket52, and stale job identity. They are not measurements. No GPU/PyTorch runtime imports were used for preparation. The frozen full N64/4000/200/seed2026 workload, deadlines, model/KV/transport/semantic checks, output/error and local acceptance gates remain in S107. No accuracy or official-score claim is made.
