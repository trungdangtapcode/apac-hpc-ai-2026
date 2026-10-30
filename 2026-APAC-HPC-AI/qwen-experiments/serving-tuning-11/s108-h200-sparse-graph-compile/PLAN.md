# S108: Blocked Sparse Decode Compile Candidate

This directory is source-only blocked preparation. Job27383 FAILED in native torch.compile at bucket54 because `fused_set_kv_buffer_arg` is unsupported by the native rotary implementation. The proposed sparse list still compiles bucket54. No GPU submission entrypoint is retained.

The hypothetical list and cap values are retained only to document the abandoned hypothesis. Do not interpret `expected_compile_buckets` as executed or successfully compiled shapes. A source/backend remedy and new exact-image startup qualification are required first. Any code/fusion change requires a new matched control.
