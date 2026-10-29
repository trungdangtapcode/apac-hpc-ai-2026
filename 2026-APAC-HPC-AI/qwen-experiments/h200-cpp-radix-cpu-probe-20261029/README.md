# C++ RadixTree CPU preflight

**State: prepared for root admission; not submitted.** This is a zero-GPU, single-process diagnostic to test the pinned SGLang C++ radix-tree extension build and a few synthetic tree invariants before considering a full Qwen startup. It does not benchmark serving or validate `RadixCacheCpp` integration.

## Hypothesis

The experimental cache path is usable only if the native C++ extension builds from the exact pinned SGLang image and preserves key-to-KV-index behavior. `radix_tree.py` calls `torch.utils.cpp_extension.load` on first import, so a cold private build cache tests the real JIT prerequisite. The earlier source-only report and its complete source evidence are included here.

## Frozen trial

- One node, one task, two CPU cores, zero requested GPUs, 2-minute scheduler wall limit.
- Reuse the pinned native Enroot runner and `exec.rc` from `h200-kv-page-primitive-r2-20261028`, guarded by their recorded SHA-256 values.
- Set private job-local `HOME`, `TORCH_EXTENSIONS_DIR`, and temporary directories; cap `MAX_JOBS=2` and `OMP_NUM_THREADS=2`.
- Set the absolute process deadline to batch-start + 90 seconds. `timeout` sends TERM at that deadline and allows up to 30 seconds for native-container cleanup. The Slurm allocation itself is capped at 2 minutes.
- The container receives only this probe bundle read-only, this job's result directory, and its private temporary directory. `/scratch` and model weights are not mounted.
- Import `torch` and the exact pinned `RadixTreeCpp` JIT wrapper inside the container. Assert the container sees no CUDA devices; capture Python, PyTorch, C++ compiler, Ninja, loaded extension path/hash, source hashes, timings and the build log.
- Exercise CPU `torch.int64` indices with 32-token keys at `page_size=1` and `page_size=16`: first insert, duplicate, 16-token prefix, overlapping-key split and index reuse, lock-protected eviction, unlock/evict, and reset counters. Both keys and branches are page aligned. Page 16 is metadata-only here; it is not a page-16 KV-cache qualification.

Any missing compiler/Ninja, source/hash mismatch, visible CUDA device, JIT error, invariant failure, or process deadline is a failed diagnostic. The wrapper writes a failure result where possible and preserves stdout/stderr/compiler output and cleanup markers. Temporary build caches are removed; they are not archived.

## Interpretation boundary

A pass only establishes that this image can build and that the isolated CPU data structure satisfies this fixture. It does **not** prove `RadixCacheCpp` construction with the production KV allocator, eight-rank P selection, disaggregated P/D transfer ownership/release, Qwen output behavior, score, or speed. A separate full-model startup/semantic qualification would be required before any scored trial. Keep the current prefill ChunkCache comparison, decode settings, and queued jobs unchanged.

## Files and evidence

- `probe.py`: bounded runtime probe; no model loading or CUDA tensor creation.
- `job.sbatch`: prepared 0-GPU Slurm request; do not submit without root admission and a fresh queue/capacity check.
- `SOURCE_MANIFEST.json` and `evidence/`: exact source excerpts from the pinned image, including all three JIT translation units.
- `RUNNER_PROVENANCE.json`: pinned image and immutable native runner/RC identities.
- `PIN_SHA256SUMS`: prelaunch hash guard for the payload, source excerpts, and reused runner.

No job ID, run output, or measurement exists yet. After an admitted run, store the scheduler receipt and the small raw files under `../runs/<job-id>/`; retain failure evidence as well as a pass.
