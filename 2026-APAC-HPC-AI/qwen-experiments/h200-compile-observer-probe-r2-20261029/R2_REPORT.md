# R2 derivation: inspect the unwrapped compile context manager

**Date:** 29 October 2026. **State:** prepared for root review; not submitted.

## R1 failure preserved

R1 job **27338** terminated with scheduler state `FAILED`, exit code `1:0`,
after 76 seconds. Its raw observer JSON and Slurm stdout/stderr remain in
`../h200-compile-observer-probe-20261029/`. The JSON records a source-hash
assertion failure before the observer events, compile warmup, or graph capture:

- `inspect.getfile(decoration.patch_model)` produced SHA256
  `8b7a477f978a8532852fd81e241c78182516bc4975d672d580a5848a76e11eb6`.
- The exact same SHA belongs to the pinned image's
  `/usr/lib/python3.12/contextlib.py`.
- The pinned SGLang `torch_compile_decoration.py` itself hashes to the expected
  `77b1e38dba14788800b6b6351af1b5b8a80d9e42b91b57e9484ea4561d33a48c`.

The pinned SGLang source decorates `patch_model` with `@contextmanager`. The
pinned Python 3.12 implementation returns a helper decorated with `@wraps(func)`.
Thus `inspect.getfile` on the decorated helper identifies the standard-library
wrapper source; it does not identify the wrapped SGLang generator function.
A separate host-only `contextlib` reproduction showed `inspect.getfile` changes
from the wrapper file to the original function's file after `inspect.unwrap`.
The source mismatch is therefore an observer introspection bug, not evidence of
a compile, model, or graph-capture failure.

## R2-only change

R2 calls `inspect.unwrap(decoration.patch_model)`, verifies the unwrapped
function belongs to the `torch_compile_decoration` module, and resolves its
source with `inspect.getsourcefile`. It separately hashes and records the
decorator helper's `contextlib.py` file, the unwrapped function source, and the
SGLang module file. Both SGLang hashes must equal the pinned module digest;
the contextlib hash must equal the independently inspected pinned standard
library digest. The probe logic otherwise derives from R1. R1's files, receipt,
raw output, and hashes were not changed.

## Scope and interpretation

R2 is only prepared. It has no scheduler receipt and no runtime result. If its
corrected source guard passes, that will establish the observer loaded the
expected pinned source; only subsequent actual tiny-model calls, numeric
compiler counters, CUDA graph replays, and synthetic tolerances can establish
those fixture interfaces. Even a full fixture pass says nothing about Qwen,
HPC-Ops, multi-rank capture, production startup, accuracy, or performance.
