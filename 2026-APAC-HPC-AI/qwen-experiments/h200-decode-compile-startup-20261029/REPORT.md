# Qwen decode compile startup observer and gate

## Decision

This stages a source-guarded observer and a fail-closed readiness gate for a
future Qwen3-235B-A22B FP8-weight/BF16-activation TP8 startup trial using the pinned SGLang image.
It does not launch the server or claim this optimization is ready or faster.
The gate must pass before the controller starts AIPerf. Native model math,
weights, precision, graph mode and score workload remain unchanged.

## Evidence motivating the next bounded step

The corrected one-H200 tiny fixture, Slurm job 27340, completed successfully in
97 seconds. For 1, 52 and 64 token fixture shapes, the native SGLang compile
callable was invoked, CUDA graph capture plus two replays passed, and all three
shapes showed positive Dynamo graph counts and generated Inductor kernels
(24, 35 and 35 respectively). This establishes that the observer can detect
real compiler activity in a tiny BF16 module. It says nothing about Qwen or
production startup cost. Receipt source: the immutable
`../h200-compile-observer-probe-r2-20261029/runtime/observer-27340.json`.

The production startup observer wraps (without editing) the pinned native
`torch_compile_decoration.patch_model`, watches PyTorch CUDA graph context
success, and atomically writes rank-local receipts. It records the requested
`num_tokens`, enable argument, callable wrapper markers, first-call counter
deltas, and capture success. It emits no per-request log lines. Rank identity
is refreshed after distributed initialization because `sitecustomize` can run
before rank assignment.

Pinned source inspection confirms the intended decode path calls native
`patch_model` for each decode capture shape, then the full backend captures
inside `self._device_module.graph`. The runner initializes that module with
`torch.get_device_module(self.device)`; for the target CUDA device the observer
wraps `torch.cuda.graph`. The image also has an existing
`/etc/python3.12/sitecustomize.py`; the staged shim verifies its SHA and runs it
first so its optional apport exception hook is preserved. Source copies and
hashes are in `pinned-source/` and `provenance.json`.

The backend has a conditional memory-saver branch that delegates to
`TorchMemorySaverAdapter.cuda_graph` when both the server option and
`SGLANG_MEMORY_SAVER_CUDA_GRAPH` enable it. This stage proves and observes the
ordinary CUDA graph context only. If that adapter branch is enabled and does
not call the wrapped `torch.cuda.graph`, the per-shape capture receipt will be
missing and the gate will block AIPerf; do not treat that as a compile result.

## Fail-closed admission gate

`check_compile_receipts.py` requires eight unique rank IDs and exactly one
process receipt per rank, current Slurm job ID, frozen experiment ID,
`decode-0` role, initialized distributed state at the model hook, matching
pinned native source hashes, and for every rank each shape 50–54 must have compile enabled,
a callable with Dynamo wrapper markers, at least one invocation and a
successful CUDA graph context. Each rank must also show positive Dynamo unique
graphs, FX graph cache activity, and Inductor cache or generated-kernel
activity. A returned wrapper alone cannot pass. The output is a machine-readable
`ready_for_aiperf` boolean; any missing receipt, shape or counter evidence
returns nonzero, so the serving controller must not enter AIPerf.

Positive compile activity is rank-level rather than asserted independently for
every shape: an Inductor cache may legitimately reuse a prior shape. This
qualifies shape-specific proof and is reported as a gate warning. The gate does
not prove all ranks ran the exact same role or that each capture encloses the
same graph implementation; those require review of the eventual full receipts.

## Remaining validation before a scored trial

- Parent must wire the observer directory only into every decode worker's
  `PYTHONPATH`, set `QWEN_TORCH_COMPILE_OBSERVER=1`, `QWEN_EXPERIMENT_ID`,
  `QWEN_ROLE_NAME=decode-0` and a shared receipt path,
  and run the gate after native startup but before AIPerf.
- Verify the active server actually requests shapes 50–54 and captures them;
  the tiny fixture does not prove that.
- Verify each rank receipt is present before startup timeout and that observer
  overhead is negligible. If the shape set or interface differs, fail before
  scoring and preserve receipts.
- Python may log and ignore a failing `sitecustomize` import, so the strict
  pre-AIPerf receipt gate must block a worker that did not install the hook.
- Only after real startup passes should a conditional full score proceed under
  the existing 600-second startup, 720-second warmup and 1020-second hard job
  limits. Full compilation may exceed these limits; no claim is made here.

## Local checks

The CPU-only fixtures exercise the passing schema and reject a missing or
duplicate rank, wrong shape, wrapper-only receipt, unsupported/non-positive
counters, source mismatch, stale job, wrong experiment/role and uninitialized
distributed state. They do not import Torch or access a GPU.
