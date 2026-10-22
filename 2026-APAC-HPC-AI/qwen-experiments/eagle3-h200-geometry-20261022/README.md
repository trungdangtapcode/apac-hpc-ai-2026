# H200 KV geometry proposal

See [PLAN.md](PLAN.md) for scope, source provenance, the receipt schema, limits and proposed runtime integration.

This is an unintegrated, CPU-tested proposal. It has not run on H200 and does not establish dtype, tensor strides, transport correctness, performance or startup overhead. The source payload is generated from the pinned `s37-h200-target-reference/nixl-conn.py`; `derive.py` refuses any source hash other than the reviewed NIXL patch. `kv_geometry.py` writes redacted rank receipts, and `validate_kv_geometry.py` enforces complete coverage for the current TP4/TP4/TP8 placement.

Run the local checks with:

```bash
python3 -m unittest -v test_kv_geometry.py
```

To reproduce into a fresh output directory:

```bash
python3 derive.py /path/to/pinned/nixl-conn.py /path/to/new-output
```

The generator refuses to overwrite an existing derived module or derivation record.
