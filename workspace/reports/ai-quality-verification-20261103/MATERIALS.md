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

### Latest verified backup: v3

The private draft release **`quality-evidence-20261103-v3`** contains the quality evidence captured at Git commit `42322e23fde0e0801cefbc9fcaf04549a3a04ffe`. It was uploaded, downloaded from GitHub again, restored in an isolated directory and independently checked. Read [the publication receipt](backup-verification/v3/PUBLICATION_RECEIPT.json) and [the exact executed verification script](backup-verification/v3/verify_restore.py).

| Verified v3 coverage | Value |
|---|---|
| Selected source paths restored |789|
| Unique external objects downloaded/verified |17|
| Bundle size |25148115 bytes|
| Bundle SHA-256 |`4e7ab609433a963d9bd953165d89eb976fd8efd1b2c487c84e57a642ba7c2329`|
| Original frozen files verified |310|
| Additional guarded files/dependencies verified |27|
| Required bytecode files restored |16|
| Scores replayed from restored raw responses |28373:1200;28375:1205;28382:1206;28384:1204;28386:1166|

The source, original dataset, complete prepared prompts, all fixed bundles, pilot failures and the **five completed full-study runs** are covered. The third reference is included as an unmatched result; only the first two shards are paired, covering 3008/12032 questions per role. Later job outputs are outside this dated snapshot. Local retained transport: `apac-hpc-ai-research-artifacts/portable-quality/20261103-v3/quality-object-backup-20261102T191845Z.tar.zst`.

Retrieve the actual data using the existing private repository account:

```bash
gh release download quality-evidence-20261103-v3 --repo trungdangtapcode/apac-hpc-ai-research --pattern quality-object-backup-20261102T191845Z.tar.zst --dir NEW_DOWNLOAD_DIRECTORY
```

Draft assets require appropriate repository access. This is a private research backup, not an organiser submission. No credentials are included.

### Earlier verified versions are retained

| Version | Restored paths / objects | Completed full-study runs covered | Receipt |
|---|---|---|---|
|v1|668 /13|28373,28375,28382|[v1 receipt](backup-verification/v1/PUBLICATION_RECEIPT.json)|
|v2|742 /15|28373,28375,28382,28384|[v2 receipt](backup-verification/v2/PUBLICATION_RECEIPT.json)|

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
