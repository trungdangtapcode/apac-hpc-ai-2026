# S107: Sparse Decode Graph Control

S107 is a prepared compile-off H200 N64 experiment. It reduces decode graph capture buckets from all64 to12, while retaining 50/52/54/56 and max graph size64. It is intended to measure startup and padding cost against full-list control27376; it is not a compile experiment.

The pre-client CPU gate requires all eight current decode-rank receipts and successful captures for every configured bucket. It fails closed on source/config drift. Synthetic receipts are validation fixtures, never benchmark results.

No job has been submitted. Root review and a fresh queue/cap check are required before admission.

Root validation includes the actual fast runtime and complete independent head-check path, with synthetic sparse flags/receipts over read-only control data. Original cache, KV, semantic and output checks are preserved. Ancestor derive.py and compile54 checker are retained history, not S107 entrypoints. Actual graph/source/rank proof remains required on GPU. See the study PIPELINE_VALIDATION.json and DERIVATION_REVIEW.json.
