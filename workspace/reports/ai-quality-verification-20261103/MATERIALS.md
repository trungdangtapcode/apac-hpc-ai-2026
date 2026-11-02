# Quality study materials and recovery

This inventory separates source code, measured answers, execution provenance and backup transport. The study root below is `/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102` in the active tree, or the same relative path inside the Git archive.

## What is retained

| Material | Study path | Why it is needed |
|---|---|---|
| Original question identities and public-source pins | `corpus-tools/`, older `../mmlu-pro-local-quality-20261024/dataset/` | Rebuild without choosing a new test set |
| Complete rendered questions and validation examples | `corpus-tools/test-prompts-12032.jsonl`, `validation-70.jsonl` | Audit few-shot rendering and category/source order |
| Actual tokenizer preparation | `prepared-4k/prepare-manifest.json`, `compiled-corpus.jsonl` | Reuse the exact question/prompt/token identities and adaptive-shot choices |
| Generation and scoring code | `client/quality_client.py`, `aggregate_full.py`, fixture tests | Reproduce API settings, parser, fixed denominators and full-set ratio |
| Failed and corrected reference source | `jobs/reference-pilot/`, `jobs/reference-pilot-r2/`, reference repair plans | Preserve the actual FP8 incompatibility rather than erase the failed attempt |
| Pilot candidate and all 16 full bundles | `jobs/candidate-pilot/`, `jobs/full-ref-*`, `jobs/full-cand-*` | Reproduce the actual model workers and derived evaluation drivers |
| Immutable payload identity | `frozen-pilot/`, `frozen-reference-r2/`, `frozen-full8/` | Detect edits after admission |
| Exact bytecode dependencies | `workflow/required-bytecode.tar`, `REQUIRED_BYTECODE.json`, restore helper | Restore the sixteen files explicitly required by the existing candidate checksum lists |
| Definite scheduler receipts and cost reservations | `admission/`, `admission-reference-r2/`, `admission-full8/` | Prove actual submissions and distinguish them from plans |
| Original responses and per-question scoring | Every completed `evaluation/responses.jsonl`, `run.json`, `summary.json` | Inspect what the model returned; reparse and recompute scores |
| Worker/router/readiness/semantic logs | Each run's artifact directory | Verify startup, actual deployment and errors outside/inside the scored set |
| Human result analysis and accounting | `reviews/` | Explain observations, decisions, limits and actual cost |
| Finite continuation and its review | `workflow/finite_event.py`, `CODE_GUARD.json`, independent review/tests | Audit fixed-shard continuation, queue cap and failure stopping |
| Dated monitoring, without a background watcher | `monitoring/` | Distinguish not-submitted, pending, running, terminal and validated states |

Raw artifacts remain immutable. New reviews and dated snapshots are separate files. A terminal failure is retained, not relabelled a valid accuracy result. Authentication state, private runtime homes, model tensors, container scratch space and disposable caches are excluded.

## What GitHub contains

Small safe source files, documentation, receipts, summaries and manifests are committed to the authorised private Git repository. The normal capture policy places files larger than 1 MiB in the sibling content-addressed object store; Git records their source path, original byte length, SHA-256 and compressed object path. **A Git push by itself does not upload those external object bytes.**

For this important quality study, a separate scoped portable evidence bundle is being prepared for an explicitly selected private GitHub draft release. It contains the captured large objects needed by this study and the original local MMLU-Pro dataset, plus manifests identifying their matching Git source. It excludes unrelated research objects and runtime images. The publication/verification receipt will identify the asset and hash only after upload and a successful download/hash check. Until that receipt exists, do not claim those bytes are off-host.

The precise scope is essential: a quality-study bundle is not a backup of the entire multi-week external store, all serving images or model weights. Future job responses generated after the bundle's timestamp need a later explicit capture/bundle update. The finite measurement callback does not commit or upload data automatically.

## Restore the evidence before attempting any GPU replay

1. Clone the existing private Git archive at the commit recorded by the evidence bundle.
2. Obtain the matching private evidence asset and verify its published checksum.
3. Restore its allowlisted object files into a sibling object store and verify decompressed SHA-256 and byte lengths against the included manifest. Keep existing unrelated objects and indexes; do not overwrite a complete store with a scoped subset.
4. Use the archive's documented restore tooling for the selected source paths. If restoring only this study, preserve the same relative paths for its retained dataset inputs.
5. Run `python3 workflow/restore_required_bytecode.py` from the restored study to restore its sixteen checksum-required public files. `--check-only` verifies a tree without writes.
6. Read the latest handoff and frozen/source manifests. Evidence recovery does not authorise new GPU jobs, authentication or modifying old payloads. A replay on another cluster requires a new derived bundle with remapped paths and its own qualification.

GPU hardware, interconnects, drivers, supplied images and the public checkpoint must be provisioned separately. Retaining the dataset, prompts and raw answers permits score auditing without GPUs; it does not reproduce performance on an arbitrary machine.
