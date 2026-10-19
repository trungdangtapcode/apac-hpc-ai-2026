# APAC HPC-AI Qwen research archive

This repository imports the team's existing Qwen-serving research, run evidence, learning notes and presentation work from a temporary cluster account. It preserves the two original directory trees so links, run IDs and frozen execution payloads remain traceable.

- `2026-APAC-HPC-AI/`: organiser reference material and `qwen-experiments/`, containing serving configurations, Slurm/PBS scripts, run artifacts, reviews, transport patches and failed attempts.
- `workspace/`: persistent notes, tutorials, reports, submission materials and reviewed operational source.
- `backup/manifest.jsonl`: every retained original file, SHA-256, size, permissions, modification time and storage location.
- `provenance/`: original upstream Git bundles and the explicit import-history ledger.
- `tools/`: snapshot, verification and restoration programs.

## Private GitHub repository

The owner authorised GitHub publication on 19 October 2026. The private repository is [trungdangtapcode/apac-hpc-ai-research](https://github.com/trungdangtapcode/apac-hpc-ai-research), with `main` tracking `origin/main`. The first 50 local commits were successfully pushed before the publication documentation updates.

GitHub contains the Git history and reviewed inline files. External artifacts remain in the sibling store on the cluster; they have not been uploaded by this Git push. Follow [the GitHub workflow](docs/GITHUB_WORKFLOW.md) for later milestones and [off-host recovery coverage](docs/OFF_HOST_RECOVERY.md) before relying on the remote as a complete backup.

## Read the current research state

Start with [the handoff](workspace/notes/CURRENT.md), [notes index](workspace/notes/README.md), and the latest linked experiment review. These are dated snapshots, not live scheduler state. Failed deployments and incomplete benchmarks remain evidence; they are not accepted performance results. Local synthetic output checks do not establish organiser full-set accuracy.

The existing absolute `/home/apacsc42` links and container/model paths are part of the original records. See [reproduction and portability](REPRODUCIBILITY.md) before running them under another account. Preserve frozen submitted bundles; adapt a new derived experiment instead of editing historical evidence.

## Git is only one part of this backup

Small reviewed files are stored directly in Git. Larger files are stored once by content hash, compressed with Zstandard, in the **sibling directory `../apac-hpc-ai-research-artifacts/`**. Multiple original files with the same bytes refer to one object. This retains repeated inputs, raw requests, logs, profiles, slide assets and exact local container images without putting huge blobs in Git.

**Copy both directories off this machine. A local commit alone is not a remote backup. Cloning this Git repository alone does not recover the external objects.** The object store's manifest is committed; the bytes must be uploaded separately when remote backup is configured. Objects marked `LOCAL_ONLY_REVIEW_REQUIRED` are not approved for automatic upload. The initial local preparation did not authenticate or upload. The later owner-authorised GitHub push covers only Git objects; it does not transfer the sibling artifact store.

```bash
python3 tools/verify_snapshot.py --store ../apac-hpc-ai-research-artifacts
python3 tools/verify_snapshot.py --store ../apac-hpc-ai-research-artifacts --deep
python3 tools/restore_snapshot.py --store ../apac-hpc-ai-research-artifacts --destination ../restored-apac
```

Verification without `--deep` hashes Git files and checks object presence and metadata. Deep verification decompresses each unique object and checks its full hash and length. Restoration verifies every copied file and refuses to replace existing different content by default. Requirements: Python 3.9+, Git and the `zstd` command.

## History and secret handling

The commits are a **transparent retrospective import**, not a claim that the repository existed during the original experiments. Author dates for dated research imports follow retained file metadata and are documented; committer dates record the actual import. No commits are invented for missing days. Original organiser history is retained separately with its original attribution. See [history provenance](HISTORY_PROVENANCE.md).

Credentials, VPN authentication/session state, private logs, environment secrets, machine-private directories, container homes and recreatable environments are excluded. Potential secret matches are excluded from all portable payloads, with paths and reasons recorded in `backup/scan-results.json`; secret values are never written into that report. Pattern scanning is a precaution, not proof against every possible secret. Frozen model/client containers are opaque local runtime objects, not Git blobs or published assets.

See [backup summary](backup/summary.json), [scope and exclusions](BACKUP_SCOPE.md), and [verification report](backup/verification.json) for actual coverage and unresolved limitations.

The archive is a captured copy. Active research still runs from the original source directories; future results are not automatically mirrored here. See [local preservation status](workspace/reports/local-repository-backup-20261018/REPORT.md).

## Later milestone captures

The initial 47-commit import is followed by ordinary commits using actual dates. The 19 October status milestone recovers three PBS runs, captures the five completed H200 runs and records live queue, VPN and credit observations. Read `2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0400/RESULTS.md` and `backup/updates/20261019-status/` for this capture's scope. This is a manual archive, not an automatic mirror of the active source directories.

For an explicit later milestone, supply a JSON list of source-relative paths to `tools/capture_update.py --selection <list.json> --report <capture.json>`. It applies the existing exclusion/scanning policy and hashes selected data, verifies newly compressed objects, updates the cumulative manifest, and retains unselected paths. It does not infer that every source change has been captured. Verify, commit and refresh the recovery set before claiming the milestone is backed up. Never rerun the initial fresh-tree builder over this repository.

The later 19 October continuation milestone submits four H200 trials (24721–24724) and two serial PBS trials (221589–221590), with sealed H100 profile analysis, frozen new bundles, resource reservations and explicit returned receipts. Its scope is `backup/updates/20261019-followups/`; the source-linked report is `2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0412/RESULTS.md`. These new jobs were queued at capture, not measured results.

The next 19 October load-results milestone retains H200 24721/24722 and PBS 221589/221590 raw evidence and passing local reviews, with higher observations of 2839.532 and 2430.891 good tokens/s on their respective platforms. Independent repeats and one further load step were submitted as H200 24732/24733 and PBS 221645/221646. See `backup/updates/20261019-load-results/` and `2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0527/RESULTS.md`; new higher-load points are not independently repeated or officially accuracy-certified yet.
