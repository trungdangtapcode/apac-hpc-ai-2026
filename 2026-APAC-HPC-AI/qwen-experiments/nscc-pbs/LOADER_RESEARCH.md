# NSCC startup investigation — 2026-10-15 20:10 UTC

Observed job220562: prefill TP4/EP1 weight load851.14/851.64s; decode
TP8/EP8 98.57s. These configurations differ in expert partitioning and CPU
placement as well as storage access. The timings alone do not identify an I/O
bottleneck. Raw server timing: `inspection/wake-20261015-1930UTC/startup-review.json`.

Inspected the actual `sglang-harbor.sqsh` source, extracted with2CPU workers to
`inspection/wake-20261015-2007UTC/image-source/`. The image size26476240896B
matches the verified transferred asset contract; source file hashes are retained.
No model was loaded on login.

- `model_loader/loader.py:368,565–649`: default loader uses8threads/rank,
  safetensors mmap, and a buffered iterator. Existing server extra config is{};
  mmap is enabled and prefetch disabled. Raising thread count is not an obvious fix.
- `weight_utils.py:1104–1168`: the buffered loader holds a bounded sliding window
  and consumes tensors in file order. Eight TP ranks in two independent TP4
  replicas on the prefill node can compete for memory/page-cache/CPU resources.
  Task CPU masks are32CPUs per replica, disjoint by GPU offset; NUMA locality and
  actual page-fault/I/O rates have not been measured.
- `qwen3_moe.py:1102–1201` and fusedMoE `layer.py:889–938`: expert ownership can
  skip nonlocal expert weights on the EP path. EP1 versusEP8 is a confounder;
  changing prefill EP would also change runtime communication.
- Built-in checkpoint prefetch distributes shards over each local TP group and
  warms OS page cache. Its default policy also selects a single-thread iterator
  instead of the8thread buffered iterator. Two prefill replicas have separate
  groups; this is not demonstrated node-wide deduplication. Source comments are
  an implementation explanation, not proof of reduced I/O in this workload.

Prepared **h100-loader-prefetch-06**, local only, source load-sweep-03. One
prefill flag `--weight-loader-prefetch-checkpoints`; decode unchanged. Same
45min/16GPU/grid32–42/full60/120/30, stop after failed load gate. Separate long
retrieval diagnostic matches prepared backend trials. Syntax/AST/checksums and
workload identity passed; GPU behavior is untested. First preparation failed on
inherited0555 directory permissions; the partial attempt and explanation are
retained. Neither attempt was uploaded, reserved or submitted.

Run only after the already-prepared MNNVL04 and FlashInfer05, passing matching
baseline N32/short checks and budget/empty-queue refresh. Reserve at most1536SU
at actual submission. Compare startup timing from all three workers, readiness,
full N32 exports and raw outputs. Repeat on comparable nodes/cache state before
attributing a startup improvement. Keep prefetch off on decode to isolate the
prefill loader policy. Do not claim general I/O speedup or better model accuracy.
If prefetch gives no clear repeatable benefit, next isolate iterator thread count
or NUMA affinity, one policy at a time; do not copy/retransfer checkpoint assets.

## Follow-up20:20UTC: observability prepared, NSCC access unavailable

Actual source control flow passes mmap tensor views through Qwen load_weights before FusedMoE.weight_loader maps expert ownership and returns for nonlocal experts. Skipping the later copy does not prove that all earlier pages were avoided; retain TP/EP/cache confounders. Added local-only `startup-sampler.py` and `STARTUP_SAMPLING.md` for own worker-tree CPU ticks/faults/I/O/NUMA counters within a future allocation. Controlled CPU child/grandchild validation passed, including logical4MiB write counters; tmpfs physical-write counter was0. No NSCC runtime validation, upload, frozen-pilot mutation or new SU reservation. Evidence: `inspection/wake-20261015-2020UTC/`.

## Follow-up20:57UTC: offline rates and coverage

Added `analyze-startup.py` for sampler journals. Rates use monotonic time and
matchingPID/start-time identities; missing counters remain null. It explicitly
flags PID churn, counter resets, long sample gaps and incomplete live tails,
does not sum RSS or infer causality, and refuses to overwrite evidence. Offline
fixtures and preserved local CPU child samples passed. Local only, not uploaded
or integrated; no new allocation/reservation or changes to frozen04/05/06.
See `inspection/wake-20261015-2055UTC/analyzer-validation.json`.
