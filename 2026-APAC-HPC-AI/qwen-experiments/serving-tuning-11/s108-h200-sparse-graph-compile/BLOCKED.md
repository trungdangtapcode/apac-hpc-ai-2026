# S108 Blocked: Native Qwen3 Compile Failure

Do not submit or run this bundle. Its compile-enabled path is blocked by job27383, which failed at compiled bucket54 with `AssertionError: fused_set_kv_buffer_arg is not supported for native implementation` in Qwen3-MoE `apply_qk_norm_rope` through `rotary_embedding/base.py:244`. Sparse graph capture still includes bucket54 and does not remove this code path.

A separate source/backend fix and exact-image startup qualification are required before rebuilding a compile candidate. If the fix changes fusion or runtime code, create a new matched control; S107 is not automatically valid for that comparison. See `h200-sparse-decode-compile-20261029/blocked-compile-evidence.json`.
