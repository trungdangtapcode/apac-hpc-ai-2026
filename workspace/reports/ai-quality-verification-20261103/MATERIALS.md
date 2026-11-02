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

### Latest verified backup: v2

The private draft release **`quality-evidence-20261103-v2`** contains all quality evidence captured at Git commit `056719537144ba07b8311d68c45bbdc9c665e784`. Its download was restored into an isolated directory and independently verified; see [the v2 publication receipt](backup-verification/v2/PUBLICATION_RECEIPT.json) and [the exact verification script](backup-verification/v2/verify_restore.py).

| Verified v2 coverage | Value |
|---|---|
| Source paths restored |742|
| Unique external objects |15|
| Bundle bytes |23286988|
| Bundle SHA-256 |`0859bedf9973c16da95d8015f61c72587ac8cf748001e91ae7659f5d825c2f77`|
| Original frozen files / additional guarded files / restored bytecode |310 /27 /16|
| Scores replayed from restored raw answers |28373:1200;28375:1205;28382:1206;28384:1204|
| Paired measured coverage |3008 /12032 questions per role|

The original dataset, complete prepared prompts, all frozen job bundles and the four completed full-study runs are covered. Later job outputs are outside this dated snapshot. Local retained transport: `apac-hpc-ai-research-artifacts/portable-quality/20261103-v2/quality-object-backup-20261102T191253Z.tar.zst`.

Download the latest covered snapshot with:

```bash
gh release download quality-evidence-20261103-v2 --repo trungdangtapcode/apac-hpc-ai-research --pattern quality-object-backup-20261102T191253Z.tar.zst --dir NEW_DOWNLOAD_DIRECTORY
```

### Earlier verified backup: v1

The first scoped evidence bundle is now preserved in the **private draft release `quality-evidence-20261103-v1`** of `trungdangtapcode/apac-hpc-ai-research`. It was uploaded, downloaded again through GitHub CLI, verified by SHA-256, restored in an isolated directory and used to recompute the retained answer scores. [Publication and restore receipt](backup-verification/v1/PUBLICATION_RECEIPT.json) and [the exact executed verification script](backup-verification/v1/verify_restore.py) are committed with this report.

| Verified v1 coverage | Value |
|---|---|
| Captured source commit | `551f044990cd59947ec7cf0639557616a1665905` |
| Scoped manifest paths restored | 668 |
| Unique external objects downloaded and verified | 13 |
| Bundle size | 21,494,014 bytes |
| Bundle SHA-256 | `ab15a872ee425758e4b1b8c090a2d8499aa1cabedf44ada6fd9d4909dded6537` |
| Original full-study science files verified after restore | 310 |
| Additional guarded code/dependencies verified | 27 |
| Required bytecode files restored | 16 |
| Raw-answer scores reproduced without GPUs | 28373:1200, 28375:1205, 28382:1206 correct |

This v1 snapshot includes all captured quality source and original local dataset metadata/objects at its commit, including the frozen full prompts and the three completed full-study runs above. Candidate 28384 finished later and is **not covered by v1**; it is covered by v2 above. The retained local transport is under the sibling store's `portable-quality/20261103-v1/` directory. Original content-addressed objects remain unchanged.

To retrieve the actual data, authenticate to the existing private repository and use:

```bash
gh release download quality-evidence-20261103-v1   --repo trungdangtapcode/apac-hpc-ai-research   --pattern quality-object-backup-20261102T190240Z.tar.zst   --dir NEW_DOWNLOAD_DIRECTORY
```

A draft asset needs appropriate repository access. This is a private research backup, not an upload to the competition or public release. No credentials are part of the asset.

The precise scope is essential: a quality-study bundle is not a backup of the entire multi-week external store, all serving images or model weights. Future job responses generated after the bundle's timestamp need a later explicit capture/bundle update. The finite measurement callback does not commit or upload data automatically.

## Restore the evidence before attempting any GPU replay

1. Clone the existing private Git archive at the commit recorded by the evidence bundle.
2. Obtain the matching private evidence asset and verify its published checksum.
3. Extract its allowlisted object files into a new scoped store directory and verify decompressed SHA-256 and byte lengths against the included manifest. Pass that directory as `--store` to the existing archive restore tool. Do not replace an unrelated full object store or its index with this subset.
4. Use the archive's documented restore tooling at the captured commit, selecting each exact path in the bundle manifest with repeated `--path` arguments. If restoring only this study, preserve the same relative paths for its retained dataset inputs.
5. Run `python3 workflow/restore_required_bytecode.py` from the restored study to restore its sixteen checksum-required public files. `--check-only` verifies a tree without writes.
6. Read the latest handoff and frozen/source manifests. Evidence recovery does not authorise new GPU jobs, authentication or modifying old payloads. A replay on another cluster requires a new derived bundle with remapped paths and its own qualification.

GPU hardware, interconnects, drivers, supplied images and the public checkpoint must be provisioned separately. Retaining the dataset, prompts and raw answers permits score auditing without GPUs; it does not reproduce performance on an arbitrary machine.
