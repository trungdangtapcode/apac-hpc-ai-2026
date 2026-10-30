# Sparse decode graph startup and padding control

**Current state:** S107 is prepared for root review as an independent compile-off startup/padding trial. S108 is blocked by a real native compile incompatibility and is not runnable or admitted. No GPU job was submitted from this preparation.

## S107 question

The fresh full-list control 27376 captured decode graph sizes 1–64 on all eight ranks. Rank logs report capture completion in 101.46–101.49 seconds, using 1.15 GB (native log label) per rank. The first capture progress interval was 80.90 seconds after DeepGEMM entered JIT precompile. The cost is front-loaded, so fewer buckets may save only part of startup time; shape count is not a timing model.

S107 tests only whether a sparse list can preserve the required high-concurrency request buckets while lowering startup capture work. Its exact list is `[1, 2, 4, 8, 16, 32, 48, 50, 52, 54, 56, 64]`: 12 captures instead of 64. Pinned source and the actual 27376 D8 runtime flags show batch-size alignment 1, so the 50/52/54/56 buckets survive filtering. Default graph padding selects the next retained bucket: 51→52 and 53→54. Bucket64 keeps the graph maximum unchanged. S107 keeps `torch.compile` disabled and uses a fail-closed all-rank current-job capture receipt gate before the unchanged full N64 workload.

Compare S107 with full-list control 27376 only as a bounded sparse-padding/startup observation; this is not a matched same-day pair and run-to-run variation remains. A material local-score regression closes the sparse list. A passing result does not establish compilation compatibility or qualify a compile-enabled derivative.

## S108 compile branch blocker

S108's planned sparse list cannot fix the source error in job27383. The full-list compile startup attempted compile bucket54 and failed inside Qwen3-MoE's `apply_qk_norm_rope` → native rotary forward with `AssertionError: fused_set_kv_buffer_arg is not supported for native implementation` (`rotary_embedding/base.py:244`). The job ended FAILED after 3:35; eight receipts show compile enabled at54 and zero successful graph captures for that shape. Sparse list includes54, so the same incompatibility remains reachable. Do not submit S108 or treat 27383 as a timeout/capture-count failure.

S108 is retained as source-only blocked preparation, with no submission entrypoint. A native source/fusion fix requires separate source feasibility and startup qualification. If the fix changes runtime code or fusion behavior, it requires a new matched control; S107 is not automatically that control.

## Preserved boundaries

The S107 harness preserves the model and precision, P8-TP4/D8-TP8-EP8, page1 KV, NIXL, DeepGEMM prefill chunk8192/breakable graphs, tokenizer settings, native source bindings, two semantic P/D routes, 600-second startup, global 720-second warmup ceiling, 1020-second hard stop, and full N64 exact requested4000/200 workload, seed2026, full60/120/30, error/output/smoke/retrieval gates. Quality remains unknown. No configuration result or official score is claimed.

CPU-only source, configuration, AST, shell syntax and synthetic receipt tests are recorded in [REPORT.md](REPORT.md). They do not establish a GPU readiness result. Review S107's payload and the current queue/cap before admission. S108 stays blocked until a code-level remedy passes separate qualification.
