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
| Reviewed result analysis and accounting | `reviews/` | Explain observations, decisions, limits and actual cost |
| Finite continuation and its review | `workflow/finite_event.py`, `CODE_GUARD.json`, independent review/tests | Audit fixed-shard continuation, queue cap and failure stopping |
| Dated monitoring, without a background watcher | `monitoring/` | Distinguish not-submitted, pending, running, terminal and validated states |

Raw artifacts remain immutable. New reviews and dated snapshots are separate files. A terminal failure is retained, not relabelled a valid accuracy result. Authentication state, private runtime homes, model tensors, container scratch space and disposable caches are excluded.

## What GitHub contains

Small safe source files, documentation, receipts, summaries and manifests are committed to the authorised private Git repository. The normal capture policy places files larger than 1 MiB in the sibling content-addressed object store; Git records their source path, original byte length, SHA-256 and compressed object path. **A Git push by itself does not upload those external object bytes.**

### Latest verified backup: v4 — the complete quality study

The private draft release **`quality-evidence-20261103-v4`** contains the quality evidence captured at Git commit `4b7a1d4a2b9e45ae8bc82ab841435cfb0d21d71e`. It was uploaded, downloaded from GitHub again and restored in an isolated directory. The restored frozen scorer reproduced the complete **9460 reference / 9452 candidate** result and all paired outcomes. Read [the publication receipt](backup-verification/v4/PUBLICATION_RECEIPT.json), [the exact executed recovery script](backup-verification/v4/verify_restore.py) and [the restored full comparison](backup-verification/v4/RESTORED_FULL_COMPARISON.json).

| Verified v4 coverage | Value |
|---|---|
| Source paths restored | **1339** |
| Unique external objects downloaded and verified | **39** |
| Bundle size | 45,280,026 bytes |
| Bundle SHA-256 | `1e837442e0df348d00bbecaf2d977b2f66b624a2fc3fc80d968c0fef4e6064c7` |
| Original frozen files verified | 310 |
| Additional guarded files verified | 27 |
| Required bytecode dependencies restored | 16 |
| Full-study runs replayed from restored raw answers | **16/16** |
| Full-set accuracy retention reproduced | **99.915433%** |

Coverage includes the pinned dataset, complete prepared prompts, all fixed bundles, retained pilot failures, every completed full-study response, admission receipts, final accounting, independent replay and run diagnostics at the captured commit. Later small publication receipts and prose corrections are separate Git commits. The builder's `remote_uploaded: false` records its pre-publication state; the publication receipt and successful download/restore establish the later completed upload.

The retained local transport is `apac-hpc-ai-research-artifacts/portable-quality/20261103-v4/quality-object-backup-20261103T042922Z.tar.zst`. Retrieve the actual off-host data with the authorised private repository account:

```bash
gh release download quality-evidence-20261103-v4 --repo trungdangtapcode/apac-hpc-ai-research --pattern quality-object-backup-20261103T042922Z.tar.zst --dir NEW_DOWNLOAD_DIRECTORY
```

Draft assets require repository access. This is a private research backup, not an organiser submission. No credentials, model weights or runtime images are included.

### Earlier verified versions are retained

| Version | Restored paths / objects | Completed full-study runs covered | Receipt |
|---|---|---|---|
|v1|668 /13|28373,28375,28382|[v1 receipt](backup-verification/v1/PUBLICATION_RECEIPT.json)|
|v2|742 /15|28373,28375,28382,28384|[v2 receipt](backup-verification/v2/PUBLICATION_RECEIPT.json)|
|v3|789 /17|28373,28375,28382,28384,28386|[v3 receipt](backup-verification/v3/PUBLICATION_RECEIPT.json)|

Each version has its own source commit, immutable asset hash and actual download/restore proof. Later versions add evidence; earlier versions are historical snapshots rather than silently replaced files.

The precise scope is essential: a quality-study bundle is not a backup of the entire multi-week external store, all serving images or model weights. Future job responses generated after the bundle's timestamp need a later explicit capture/bundle update. The finite measurement callback does not commit or upload data automatically.

## Restore the evidence before attempting any GPU replay

1. Clone the existing private Git archive at the commit recorded by the evidence bundle.
2. Obtain the matching private evidence asset and verify its published checksum.
3. Extract its allowlisted object files into a new scoped store directory and verify decompressed SHA-256 and byte lengths against the included manifest. Pass that directory as `--store` to the existing archive restore tool. Do not replace an unrelated full object store or its index with this subset.
4. Use the archive's documented restore tooling at the captured commit, selecting each exact path in the bundle manifest with repeated `--path` arguments. If restoring only this study, preserve the same relative paths for its retained dataset inputs.
5. Run `python3 workflow/restore_required_bytecode.py` from the restored study to restore its sixteen checksum-required public files. `--check-only` verifies a tree without writes.
6. Read the latest handoff and frozen/source manifests. Evidence recovery does not authorise new GPU jobs, authentication or modifying old payloads. A replay on another cluster requires a new derived bundle with remapped paths and its own qualification.

GPU hardware, interconnects, drivers, supplied images and the public checkpoint must be provisioned separately. Retaining the dataset, prompts and raw answers permits score auditing without GPUs; it does not reproduce performance on an arbitrary machine.
