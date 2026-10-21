# Native KV geometry: source-backed limits of the synthetic gate

Reviewed 2026-10-21T20:01:48.672327+00:00. This is static CPU/source evidence, not native runtime KV
argument capture. Two exact public source members are extracted with
unsquashfs using two processors from /scratch/enroot-images/sglang-harbor.sqsh;
original headers are preserved. Their hashes are in source-sha256.json.

The actual prefill `_init_kv_manager` at prefill.py:208 obtains target buffer
pointers, registration spans and per-page item lengths from the target pool.
When a draft pool is present and transferable, it appends the draft pointer,
span and item-length lists at lines217-225. Native decode does the same at
decode.py:434-461 and records VRAM memory kinds. Both separately register metadata
buffer information as auxiliary data. Thus the native speculative layout is a
concatenation of target K/V and draft K/V descriptors, not necessarily a single
all-K then all-V pool.

The retained common helper explicitly handles decode-only draft as target K,
target V, then draft entries. Equal pointer-list lengths split at half but the
current patched function concatenates the selected halves back in original
order; this alone does not establish an ordering bug. The inherited patched
heterogeneous sender uses only the first source and scalar destination item
length for every region. Uniform synthetic strides therefore test arithmetic
but cannot prove actual native stride uniformity.

The retained draft config has four KV heads and head dimension128. Explicit
BF16 KV and one local head make 256 bytes/token plausible for this dense layout;
this is an inference, not a measured actual KVArgs receipt. Native pool descriptor
construction, padding, dtype and allocation spans must be recorded before using
that assumption to clear a real model. Never infer large-pool registration or
auxiliary correctness from the 24 tiny aggregate-buffer transfers in 223097.

The next bounded no-model probe tests actual registration and DRAM auxiliary
methods with tiny distinct buffers. A later real-model derived bundle still
needs redacted actual KVArgs counts/strides/spans plus semantic warmup receipts.
No pointer values or raw agent metadata are recorded in this static report.
