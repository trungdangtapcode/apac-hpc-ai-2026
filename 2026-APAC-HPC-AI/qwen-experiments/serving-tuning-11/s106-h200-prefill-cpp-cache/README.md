# S106: experimental C++ radix cache on prefill

**State: PREPARED_BLOCKED_ON_ACTUAL_27387. Do not submit until the CPU prerequisite passes and root reviews this frozen candidate.** This package derives from the exact retained submitted payload for completed job 27376. It is a real-model startup qualification followed by the unchanged local N64 AIPerf protocol in the same allocation, conditional on startup, KV, P/D semantic, and output checks.

## Hypothesis and single treatment

The 27376 H200 control scored **3041.119598 good output tokens/s** (Goodput requests/s × 200) with Python `RadixCache` on both TP4 prefill roles and `ChunkCache` on the TP8 decode role. It passed the local performance protocol at 98.631579% good requests (1874/1900; zero errors/cancellations). This is a fresh native control, not an optimization or organiser reference.

This candidate changes only the prefill cache implementation: set `SGLANG_EXPERIMENTAL_CPP_RADIX_TREE=1` on the two P roles, keep `disable_radix_cache=False`, and expect `RadixCacheCpp` on all eight P ranks. D stays on `ChunkCache` with `disable_radix_cache=True`; decode cap 256, transfer polling 1, decode graphs, MoE backends, weights and workload stay unchanged. Each P role gets a private `TORCH_EXTENSIONS_DIR` and `MAX_JOBS=2` for the cold C++20 JIT build. No model or kernel source is patched.

## Admission and model-start gates

`job.sbatch` checks actual Slurm accounting for job 27387 and `/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/27387/probe.json` before launching the topology script. It requires `COMPLETED 0:0`, CPU-only probe state `PASS_CPU_FIXTURES_ONLY`, terminal container cleanup, both page-size fixture receipts, and exact CPU runtime-source hashes matching this payload. A missing or failed receipt exits before any model worker starts.

After that gate, each worker checks the pinned image source hashes before calling SGLang. The shared 600-second startup deadline is unchanged. Before the N64 client starts, the payload requires all three workers healthy, per-rank resolved arguments, all eight P `RadixCacheCpp` classes plus one C++ selection marker per TP rank, unchanged D `ChunkCache`, BF16 physical KV/NIXL rank records, validated KV geometry, both P/D semantic paths, and output smoke of at least 7/8 with no regression. Any failed check aborts before the performance client. The existing post-client independent raw head check, output smoke and 12/12 retrieval gate remain.

The allocation remains the matched 16-H200, two-node, 17-minute protocol (maximum 4.533334 GPU-hours). Full N64 AIPerf uses the same cold 4000/200, seed 2026, 60-second warmup, 120-second measurement and 30-second grace. JIT time is inside the existing startup budget; no deadline extension is allowed.

## Interpretation limits and decision

No score exists for S106. The pending CPU job is a prerequisite, not a speed result. A CPU fixture pass verifies only the isolated radix tree and toolchain; full P allocator integration, distributed ownership, startup and semantics are qualified here only if the model gates pass. Official full-set accuracy remains unknown. Compare a complete candidate pass to job 27376; require more than 1% useful gain plus acceptable latency tails before spending on a matched confirmation. A startup or semantic failure is a failed candidate, not a scored result.

The full source pin is in `CPP_SOURCE_HASHES.json`, with byte-preserving excerpts in `source-evidence/`. `SHA256SUMS` covers the frozen candidate payload; `CPP_SOURCE_SHA256SUMS` covers the retained C++ source excerpts. `PARENT_PAYLOAD_PROVENANCE.json` binds this derivation to job 27376's actual submitted payload. `check-cpu-prerequisite.py` is a fail-closed admission guard. No job receipt or performance measurement is present.

## Historical ancestor files

The inherited derive.py and ancestor provenance describe older stages and are retained for history. They are not the S106 generator. PLAN.md describes the current trial; DERIVATION_REVIEW.json compares every retained parent file against the exact 27376 submitted payload, and SHA256SUMS binds the current candidate. No original submitted payload was changed.
