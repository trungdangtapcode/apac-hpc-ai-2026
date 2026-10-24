# Job 224468 review: HPC-Ops R3 one-GPU virtual EP math

## Question and prior evidence

This run checked whether the source-pinned blockwise FP8 MoE operator and a source-faithful numerical oracle agree when a single H100 executes five virtual expert-parallel (EP) ranks. The preceding R2 run failed its unchanged relative-L2 limit: EP1/oracle was 0.022924 and EP5/oracle was 0.022979 against a limit of 0.02. R2's FP32 oracle omitted native intermediate formats. R3 changed the oracle to model the pinned sequence: BF16 gate-up output, SiLU-product requantization to E4M3 with block scales, BF16 down output, FP32 top-k accumulation and final BF16 cast. The submitted threshold stayed at 0.02; the physical-copy threshold stayed at 1e-7. The oracle consumes the actual SGLang-quantized activations and weights; no output-fitted correction was used.

## Run and provenance

- PBS job: `224468.pbs111`; final state `F`, exit status 0, stage-out status 1.
- PBS wall time: 82 seconds; program-reported elapsed time: 24.2918 seconds.
- Node and device: `a2ap-dgx037`, NVIDIA H100 80GB HBM3, compute capability 9.0, UUID `0bc6bd5f-a156-c028-f9d4-417982bc5b56`.
- Geometry: 16 tokens, hidden size 256, intermediate size 128, 128 logical experts and 130 physical experts, EP size 5, top-k 4, block shape 128x128. Each virtual rank has 26 physical expert slots.
- Runtime: PyTorch `2.11.0+cu130`, HPC-Ops `0.0.1.dev0+gab1a402`, upstream commit `ab1a402724635507037426068f6cddc3d30dc0a8`.
- The result records and matches hashes for the runtime SGLang quantization and runner sources and the installed `hpc/fuse_moe.py`. The submitted tree retains source provenance and checksums for the selected upstream HPC-Ops files. The native extension itself is identified by path and size in the result, but was not separately archived as a binary.
- Terminal accounting and collection evidence are in `collected/pbs-accounting.txt`, `collected/pbs-stdout.txt`, and `collected/evidence-sha256.json`. Full collected files are retained in `collected/`; `raw-evidence.tar.gz` preserves the raw collection.

## Findings

The run reports `PASS`. EP1 versus oracle relative L2 was 0.0059553883 (0.59554%); EP5 versus oracle was 0.0062373071 (0.62373%); EP5 versus EP1 was 0.0023261150 (0.23261%). The physical-map duplicate oracle relative L2 was exactly 0.0. All measured relative-L2 values were below 0.02, and the duplicate-copy value was below 1e-7.

The candidate emitted five BF16 rank outputs, each with shape `[16, 256]`; the baseline and oracle also had shape `[16, 256]` and BF16 dtype. The submitted driver checks output shape, dtype and finiteness. Rank nonzero flags were `[true, false, true, false, true]`. The deterministic route covers logical and copied physical expert IDs, including physical IDs 128 and 129.

An activation diagnostic found 3 byte differences among 4096 values (0.0732422%) compared with each of two independent quantizer calculations. All 4096 values remained inside the source-aware E4M3 rounding bound, with zero bound violations. This remains a diagnostic; it does not motivate changing the gate.

## Interpretation and limits

This is evidence that this synthetic operator case passes its numerical and physical-copy gates using the pinned source-derived oracle. It is not a distributed EP, collective, communication, Qwen model, accuracy, model-memory, or serving-performance result. Five virtual ranks ran serially on one H100 and were combined with a local Torch operation; there was no process group, all-reduce or inter-GPU traffic. The synthetic dimensions and fixed route do not establish production routing, EPLB balance, DP attention, NIXL or MNNVL behavior.

The candidate timing (0.007714 seconds) comprises five sequential native EP calls; the EP1 timing (0.0000806 seconds) is one later call. These counts and ordering are unmatched, so they do not support a speed comparison. The PBS wall-time cost estimate is `82 seconds × 128 GPUs / 3600 = 2.915556 SU`; this is an estimate, not a posted ledger charge. No budget ledger was changed.

GPU evidence consists of sparse before/after memory snapshots, not continuous utilization, peak VRAM, kernel profiling, thermal sampling or hardware-health telemetry. Those measures were not collected in this run and must not be inferred from the PASS status.

## Next useful check

The next numerical step should preserve the pinned native formats and unchanged gates while exercising a second fixed seed or route that includes the physical-copy boundary. That would test whether this pass is tied to this one deterministic fixture. A separate multi-GPU/distributed test is required before making any system-level EP claim; this one-GPU result cannot substitute for it.

## Files

- `collect.py`: bounded terminal collection procedure.
- `collected/`: terminal accounting, raw run files and collection checksum manifest.
- `raw-evidence.tar.gz`: archived raw collection.
- `REVIEW.json`: machine-readable result and scope summary.
- `RAW_ARCHIVE.sha256`, `REVIEW_SHA256SUMS`: integrity records for this review.
