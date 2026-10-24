# S49 H200 deterministic EAGLE3 candidate

S49 is derived from frozen S45 and bound to the independently accepted S46 target reference from actual job 25855. The exact target bytes and review are retained as `accepted-s46-25855-target-reference.json` and `accepted-s46-25855-review.json`; `target-reference-binding.json` pins their hashes and the review seal.

The CPU/source preparation preserves the inherited EAGLE3 candidate gates: pinned draft bytes and metadata, explicit BF16 target/draft runtime, deterministic sampling, two BF16 KV allocations per EAGLE3 rank, all-rank NIXL coverage, native P/D semantic receipts, 190-region geometry checks, native speculative counters, repeat stability, and exact matching of both 1,600-ID candidate passes to the accepted target reference. Runtime logs accept the native deterministic allreduce disable marker or the source-backed forced-disable marker only when the resolved ServerArgs flag is true.

`validate-cpu.py` passes with the accepted reference binding and demonstrates that an unbound state and altered reference hash fail closed. These checks establish source/CPU readiness only. No S49 GPU allocation, submission, endpoint request, runtime validation, performance score, or official accuracy evaluation occurred. Root review and the root-owned controller/submission decision remain outstanding.

See `FROZEN_PROVENANCE.json`, `target-reference-binding.json`, and `validation.json` for canonical provenance and current state.
