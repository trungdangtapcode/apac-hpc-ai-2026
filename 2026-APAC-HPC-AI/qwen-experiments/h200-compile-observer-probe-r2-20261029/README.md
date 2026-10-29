# Native compile observer interface probe, R2

**Prepared:** 29 October 2026. **State:** derived and staged for parent review;
not submitted. This is a 1-H200, 4-CPU, 4-minute native compute prerequisite.

## R2 correction

R1 job 27338 exited with code 1 after 76 seconds, before compilation or graph
capture. Its raw observer result reports `inspect.getfile(patch_model)` hash
`8b7a477f…e11eb6`. Selective extraction confirms this is the pinned Python
3.12 `contextlib.py` hash. The pinned SGLang function is decorated with
`@contextmanager`; the standard-library decorator returns a `@wraps(func)`
helper. `inspect.getfile` therefore identifies the decorator helper's source.
R2 uses `inspect.unwrap(patch_model)` and hashes both the unwrapped SGLang
module and function source against the expected pinned module hash
`77b1e38d…33a48c`. The standard-library wrapper hash is checked and recorded
separately. R1, including its failed run output, is preserved unchanged.

## Question

Can a small external observer wrap the pinned SGLang
`torch_compile_decoration.patch_model` without changing its source, record when
`torch.compile` is called and returns a callable wrapper, observe calls through
that wrapper, and confirm the same callable can run under PyTorch CUDA graph
capture?
Returning a wrapper alone is not evidence that compiled code was generated.

## Probe behavior

The job imports the pinned runtime inside its native image, checks the exact
`torch_compile_decoration.py` SHA256, sets the same compile-enable environment
value as `ServerArgs`, and calls the native `set_torch_compile_config()` hook
before using `patch_model`. It verifies one visible H200 with no distributed
process group. It uses only a tiny synthetic BF16 MLP. For batch
shapes 1, 52 and 64, it records the native compile wrapper call, returned
callable wrapper type and available fields, wrapper invocation, Dynamo
counters before and after warmup/capture, and numeric Inductor metrics exposed
by the installed runtime. The compile-activity claim remains `UNPROVEN` unless
the run observes a positive Dynamo unique-graph delta and a positive relevant
Inductor cache/kernel metric after warmup. Missing version-specific counters
are reported as unsupported rather than assumed.

For each shape the probe warms up on a side stream, captures and replays twice
with PyTorch `CUDAGraph`, and compares replay output with eager BF16 output.
The pinned SGLang `parallel_state.graph_capture()` is deliberately not called:
source inspection shows it obtains initialized TP and PP groups. The fixture
uses no fake process groups and makes no distributed graph-capture claim. The
synthetic acceptance
limits are max absolute error ≤ 0.02 and relative L2 error ≤ 0.01. These are
observer-fixture limits only, not Qwen output-quality criteria. The process has
an absolute deadline at job start plus 205 seconds, leaving 35 seconds for
cleanup before the 4-minute Slurm wall limit. Python uses the lower of 195
seconds or the time remaining at startup. An outer 205-second timeout covers
native image creation and cleanup as well as the probe. The job requires no
model weights or tokenizer.

## Limits

A pass validates only that the lightweight observer and the compile/capture
interfaces work on a tiny single-GPU model. It says nothing about Qwen3-MoE,
HPC-Ops, eight decode ranks, compile time for the production graph set, startup
within the serving deadline, useful accuracy or throughput. In particular,
this does not authorize a scored run. A later production candidate needs
per-rank receipts for actual Qwen warmup, target graph shapes 50–54, and the
remaining CUDA graph captures, with fail-fast startup timing.

## Files and provenance

- `probe.py`: isolated observer fixture.
- `job.sbatch`: bounded one-GPU native image job; output stays under this
  directory's `runtime/` subdirectory.
- `SHA256SUMS`: checksums of the staged report, script, job file and
  provenance record.
- `provenance.json`: pinned image/source and immutable native wrapper hashes.
- `R2_REPORT.md`: raw failure diagnosis and exact correction.

The pinned image hash is taken from existing job provenance and is not
recomputed here. No broad SGLang, Torch or runtime tree is copied into this
bundle. The shared native container launcher and `exec.rc` are referenced by
path and hash; neither is modified.
