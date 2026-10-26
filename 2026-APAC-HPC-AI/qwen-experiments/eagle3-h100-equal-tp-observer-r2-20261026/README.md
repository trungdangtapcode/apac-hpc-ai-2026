# One-node equal-TP H100 EAGLE3 path diagnostic

**Source-only preparation. Not uploaded, submitted, queued, or GPU-tested.** This candidate requests one H100 node with eight GPUs for at most 20 minutes. At 128 SU per GPU-hour, its maximum allocation is **341.333 SU** (`1200 × 8 × 128 / 3600`). Root owns any admission and queue decision.

## Question and prior evidence

R6 job `224554.pbs111` attempted a serial-first P/D diagnostic with P0 TP4, P1 TP4 and D TP8 across two nodes. All metadata/source gates and worker readiness passed, but both serial P-to-D semantic calls failed before the concurrent phase: one returned NIXL remote-disconnect errors; the other also produced NIXL not-found errors. Since the serial phase failed, the concurrent-after-serial hypothesis was not tested and that branch is closed unchanged.

This new diagnostic asks a distinct bounded question: **can any one EAGLE3 semantic P-to-D request pass with equal TP and a single H100 node?** It uses one P worker at TP4 and one D worker at TP4 with EP4, places both on the same eight-GPU node, and sends exactly one semantic request after actual role, source and metadata gates pass.

## Change, controls and confounds

The candidate holds the reviewed Qwen3-235B-A22B-Instruct-2507-FP8 target, EAGLE3 draft, BF16 target/draft execution settings, EAGLE steps 2 / top-k 1 / 3 draft tokens, native NIXL patch SHA `912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f`, worker launcher and router protocol to the R6-derived settings. One P-to-D path is used; no second prefill route, concurrency phase, 1,600-ID comparison or AIPerf score is included.

The role allocation is fixed: P gets assigned GPU offsets 0–3 and D gets offsets 4–7 on the same PBS node. Both roles perform their own four-device H100/SM90 UUID check; the CPU PBS-shim fixture checks the requested offsets. The accepted portable prerequisite is the preserved job 224276 P4 EAGLE3 prefill-readiness receipt, verified by SHA-256 before launch and copied into the run artifact. It gates reuse of the reviewed source/image/draft context; it is not evidence that this new decode role or P/D transfer passed.

This one-run comparison changes **both node locality and decode TP** relative to R6. Any success cannot attribute the improvement to either factor alone. It also adds EP4 to D, while R6 used D TP8/EP8. The purpose is only to establish whether this combined, equal-TP single-node path works at all. A later matched experiment would have to separate locality from decode TP before claiming a cause.

Both target model copies are expected to fit across the four assigned H100s per role, with the small EAGLE draft model. Startup remains fail-closed: missing or wrong H100 assignments, absent source reports, missing actual rank receipts, invalid expert-map geometry, invalid EAGLE draft metadata, server exit, or health timeout stops before the semantic request. This is a capacity hypothesis, not a measured memory result; the actual run may fail while loading either copy.

## Run protocol and acceptance

PBS reserves one exclusive eight-GPU H100 node for at most 20 minutes. The frozen topology has one `prefill-0` TP4 worker followed by one `decode-0` TP4 / EP4 worker; the local PBS adapter consequently assigns offsets 0–3 then 4–7. The P and D server processes each start from their own four-GPU slice. The batch waits for both native health endpoints, then requires eight real metadata receipts and four loaded source-module identity reports with matching ordered names and measured item widths across the two roles. The semantic client starts only after that gate.

The total phase envelope is 850 seconds for model startup and role/router readiness, 240 seconds for one semantic P-to-D request and independent receipt replay, and 80 seconds for bounded teardown: 1,170 seconds, below the 1,200-second PBS limit. All stages use absolute allocation-relative deadlines; later stages cannot borrow time from teardown. The request uses a unique run token, requires HTTP 200, nonempty assistant text and internally consistent token usage, and stores a hashed response receipt. A returned NIXL handle alone is never treated as transfer completion; the end-to-end semantic response is the transfer gate.

## Interpretation limits and next decision

A failed startup or request leaves this new topology unqualified. One successful semantic request would show only that this exact one-node/equal-TP path works once with this model, image, draft, placement and source patch. It would not show that same-node locality or TP4 caused any difference, that concurrent requests work, that all routes work, that 1,600 token IDs match, or that EAGLE3 meets model-quality requirements. No output-ID accuracy, organizer ≥99% quality, score or performance claim is in scope.

The next experiment should first review this actual terminal and receipts. If the semantic path passes, isolate locality and decode-TP effects in separate controlled contrasts before attributing a cause. If it fails, preserve the first failing phase/error and source-backed native send markers, then refine that path without repeating an unchanged losing R6 serial hypothesis.

## CPU-only evidence

`test_metadata_fixture.py` projects four actual P0 and four actual D rank metadata files from failed R6 into a local fixture to check the new eight-rank parser and width comparison. This is historical metadata-parser evidence only: the old D records are TP8 and do not demonstrate that a new TP4/EP4 decode worker will initialize. `test_pbs_offsets.sh` exercises the actual PBS shim in dry-run mode and checks offsets 0–3 and 4–7. `test_worker_args.py` executes the actual worker launcher with local command stubs and checks its emitted server arguments. These CPU fixtures make no GPU, transport or model-success claim.

## Files

- `benchmark.pbs`, `topology-job.sh`, and the PBS container/shim wrappers implement a future one-node run.
- `worker.sh`, `device_preflight.py`, `pd-observer/`, `metadata-gate.py`, and `semantic_probe.py` provide actual role, source, rank and single-request gates.
- `prerequisites/224276/` contains the hash-verified accepted parent receipt.
- `fixtures/r6-observed-projection/` retains only the eight historical metadata records used by the CPU parser fixture.
- `SOURCE_PROVENANCE.json`, `CPU_VALIDATION.json`, and `SHA256SUMS` record source lineage, fixture limits and frozen-file hashes.

No scheduler, GPU, SU ledger, queue, credential or submission operation was used to prepare this candidate.
