# H200 EAGLE3 stops at the worker draft identity guard

**25682 is FAILED / 1:0 after 75 s**, 16 H200, no PBS SU. The decode step on g4 reports `draft fingerprint changed: model.safetensors` before demonstrated native model initialization. Prefill steps are cancelled during guarded teardown. No generated output IDs, semantic P/D warmup, live model/graph/geometry proof or score exists.

The earlier batch-node full verifier passes the pinned draft's entire 1,145,943,008 bytes, publisher SHA, tensor header and architecture-only adapter. The worker helper then compares filesystem device/inode/size/time tuples directly with that other-node report. Such stat identity is not a portable content identity. The failing worker's actual tuple/hash was not logged, so do not assert which field changed or that its bytes matched. A genuine different remote file would also need to fail verification.

Supported repair: run the original full byte/header/adapter verifier inside each role worker, retain local before/after stat checks during hashing, compare the three pinned SHA/length identities to the parent report and independently require all three role receipts before warmup. Do not skip verification, change weights, loosen output equality, mutate 25682 or submit an unchanged retry. The real remote byte result remains pending in the derived attempt.

The source/new helper tests verify same content with different node-local metadata, reject changed size/hash/revision, missing roles and tampered receipts, and full-hash the actual staged draft on CPU. Those are CPU tests, not evidence for the original g4 bytes or speculative execution. [Complete raw SHA inventory](RAW_MANIFEST.json), [terminal accounting](sacct-terminal.psv), [structured review](REVIEW.json).
