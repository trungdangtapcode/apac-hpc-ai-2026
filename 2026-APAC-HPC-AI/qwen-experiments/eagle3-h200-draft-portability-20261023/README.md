# EAGLE3 H200 worker draft portability gate

The prior worker gate compared filesystem device and inode values with a parent
node report. Those values can differ for identical bytes on separate nodes or
mounts. This gate imports and runs the pinned sibling `verify-draft.py` on each
worker, then compares only the pinned repository revision and the three files'
byte lengths and SHA-256 values with the parent full-verification report. The
original verifier retains its local before/after stat checks while hashing,
checks the safetensors header and adapter, and requires the pinned publisher
metadata. No hash or verification check is skipped.

The derived worker bundle must include this `draft-fingerprint.py`, the original
`verify-draft.py` unchanged, and its `draft-evidence/` directory. Each worker
calls the existing two-argument interface:

```sh
python3 "$QWEN_BUNDLE/draft-fingerprint.py" "$draft" "$QWEN_DRAFT_FULL_VERIFICATION"
```

The caller supplies `QWEN_ROLE_NAME` (`prefill-0`, `prefill-1`, or `decode-0`),
`QWEN_ARTDIR`, and `QWEN_JOB_START_EPOCH`. Verification is bounded by the
existing ten-minute startup deadline. One atomic, exclusive, redacted JSON
receipt is written to `QWEN_ARTDIR/draft-worker-verifications/<role>.json`.
After all three role workers finish this gate, run:

```sh
python3 "$QWEN_BUNDLE/headcheck-worker-drafts.py" "$QWEN_ARTDIR" "$QWEN_DRAFT_FULL_VERIFICATION"
```

The headcheck requires exactly the three role receipts, `PASS` flags, the exact
parent report SHA-256, identical portable identities and complete role-local
fingerprints. The receipt records host and local stat fingerprints for
provenance; those fingerprints are not compared across nodes. Full byte
verification proves draft identity only. It does not load a native model,
verify speculative output correctness, or establish official accuracy.

Run CPU tests with:

```sh
python3 -B -m unittest -v test_portable_identity.py
```

The actual staged 1,145,943,008-byte draft is also passed through the original
full verifier by that test; no model bytes are copied into this directory.
