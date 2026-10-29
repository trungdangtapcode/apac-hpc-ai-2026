# Decode `torch.compile` feasibility for the pinned H200 Qwen runtime

**Reviewed:** 29 October 2026 UTC. **Status: NOT READY for a scored full run.**
**Pinned image:** `/scratch/enroot-images/sglang-harbor.sqsh`, SHA256
`b74ae77446bfedd6c5d72820b45be255cc513cf7c7c039d1bf63679c8178bfe5`.
The image hash comes from existing job/source provenance; it was not rehashed
for this bounded source review. Extracted-file hashes are in
[`evidence/SOURCE_MANIFEST.json`](evidence/SOURCE_MANIFEST.json).

## Candidate and hypothesis

The only plausible new native kernel path found in this pass is SGLang's
experimental full-CUDA-graph `--enable-torch-compile` path. It can wrap the
actual decode model forward in `torch.compile`; the default compile mode is
`max-autotune-no-cudagraphs`. This may fuse pointwise work or reduce launch
overhead inside replayed graphs. No performance gain is established.

Do not use decode backend `tc_piecewise`: the pinned source explicitly says
that decode path is unimplemented and resolves it to the ordinary `full`
backend. The candidate would preserve `full` and target only the decode worker.
The existing worker launches role-specific arguments; its prefill worker has a
separate argument set. The current decode worker captures graph batches 1–64.

## Why the flag alone is not useful

The current workload is fixed N64. Existing decode samples show the active
batch concentrated around approximately 50–54 requests. With the default
`torch_compile_max_bs=32`, SGLang's capture code selects only captured shapes
at or below 32 for compilation. Thus the default compile setting misses the
observed high-concurrency decode shapes and is not a useful candidate as-is.

Raising the cap to 54 would select every captured shape 1–54, including the
observed shapes 50–54. Raising it to 64 would select all 64. The runner creates
a compile wrapper for each selected captured shape and runs capture with that
wrapper. The source does not provide a lower-bound shape filter. With 8 decode
ranks, cap 54 implies up to 54 shape capture/compile attempts per rank (432
rank-shape attempts); cap 64 implies up to 512. This is an upper-bound count of
attempts, not a claim of 432 or 512 unique compiler outputs: Dynamo/Inductor
caching may reuse work. The configured compile mode uses autotuning, and no
matched startup measurement establishes that either cap fits the existing
600-second startup allowance and 1020-second hard stop.

Qwen-specific source shows `Qwen3MoeForCausalLM` does not define
`_can_torch_compile`. The pinned warmup guard uses
`getattr(model, "_can_torch_compile", True)`, so source inspection finds no
Qwen class-level veto. This is stronger than the earlier “unknown” assessment,
but it does not prove the loaded runtime keeps compilation enabled: only a
real role log after model warmup can establish that.

The runner has no explicit per-shape “torch.compile succeeded” receipt in its
normal capture log. A scored run must therefore add a validated lightweight
runtime gate (or equivalent reliable compiler markers) that proves the flag
remains enabled after warmup and that at least the intended high-load shapes
50–54 were actually compiled/captured on every decode rank. Otherwise the
score could be from eager forwards while reporting a misleading compile
configuration.

## Decision and prerequisites

Do not submit a scored compile run yet. The candidate is distinct and
source-supported, but startup and actual compilation are unverified. Before a
full run, establish all of these without altering the incumbent payload:

1. Validate a low-overhead runtime marker that distinguishes compiled from
eager capture and records rank plus graph batch size. A CLI parse or
`ServerArgs`-only check is insufficient.
2. Run a bounded startup-only trial with the exact model, FP8 weights, BF16
activation, 8 decode ranks, full graph sizes, and proposed cap 54. Require the
flag to remain enabled after warmup, successful compiled captures for 50–54
on every decode rank, ordinary full graph captures for remaining sizes, and
startup within the current deadline. Abort without scoring on any failed gate.
3. Only after that passes, compare one N64 run against fresh target-only
interval-1 control 27270 (3039.053386 good output tokens/s); preserve the
standard workload, accuracy/output gates, telemetry and timing. Keep interval-4
job 27274 untouched. Require the existing >1% useful-gain and tail-latency
gates before confirmation.

No job, scheduler state, GPU allocation, submission package, workspace note,
or Git history was changed in this review. No GPU or CUDA import was used.
The paired 27270/27272 telemetry supplied by the parent showed 100% sampled
GPU activity and about 45% memory activity at fixed clocks, but does not
identify a bottleneck; it is not evidence that torch compilation will help.

## Source map

The manifest hashes all selectively retained source files. Key locations:

- `server_args.py:2004–2014`: experimental flag and default cap 32.
- `base_cuda_graph_runner.py:61–99`: compile set is captured sizes no greater
  than `torch_compile_max_bs`.
- `decode_cuda_graph_runner.py:829–833, 909–921`: warmup may disable compile;
  capture selects the compile wrapper per shape.
- `torch_compile_decoration.py:43–61`: `torch.compile` wrapper and default
  compile mode.
- `base_runner.py:415–426`: `_can_torch_compile` guard.
- `qwen3_moe.py:934 onward`: Qwen3 MoE top-level class; no class-level
  `_can_torch_compile` assignment.
- `server_args.py:4377–4418`: listed incompatibilities concern piecewise
  compilation; they do not establish compatibility of this full-graph path.
- `runner_backend_utils.py` and `decode_cuda_graph_runner.py:18–23`:
  decode `tc_piecewise` falls back to `full`.
- `serving-tuning-11/s100-h200-transfer-poll4/worker.sh:34–46`: separate
  role arguments and current full decode graph sizes 1–64.
