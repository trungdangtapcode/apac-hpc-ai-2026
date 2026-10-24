# CPU fixture result

The CPU-only fixture passed on 2026-10-24. It verified the retained pinned-source SHA-256, the documented Triton scale/reciprocal-multiply/clamp/cast expression, presence of the public API signature and partial-result preservation checks, and toy byte-pair mismatch counting/fraction formatting.

This is bookkeeping and source-provenance evidence only. The fixture did not execute Triton, emulate FP8 rounding, import CUDA, load the HPC-Ops extension, or establish any GPU behavior.
