# Private GitHub workflow

The repository is [trungdangtapcode/apac-hpc-ai-research](https://github.com/trungdangtapcode/apac-hpc-ai-research). Keep it private. Authentication belongs to the local GitHub CLI configuration, outside the research source trees and archive.

## Work once and capture a milestone

Edit research in `/home/apacsc42/2026-APAC-HPC-AI` and notes, tutorials or reports in `/home/apacsc42/workspace`. Do not maintain independent edits in three copies. At a completed milestone, prepare a JSON list of source-relative files or directories that actually changed. Do not select private VPN state, credentials, disposable environments or model weights.

```bash
cd /home/apacsc42/apac-hpc-ai-research
python3 tools/capture_update.py --selection backup/updates/MILESTONE/selection.json --report backup/updates/MILESTONE/capture.json
python3 tools/verify_snapshot.py --report backup/updates/MILESTONE/verification.json
git status --short
```

The selection and report paths in this example must be replaced with the actual milestone paths. Capture scans selected content, verifies new compressed objects and updates the cumulative manifest. It does not commit, upload or run automatically. Review excluded paths and any changed object references before committing.

## Small checkpoints are required

Commit and push each small, coherent checkpoint when it becomes safe and reviewable. Do not collect several experiments, unrelated fixes, code changes and reports into a single large end-of-session commit.

Useful checkpoint boundaries are:

- A researched hypothesis with its reproducible scripts and configuration.
- Actual job receipts with their budget reservation and frozen-payload records.
- A completed run's evidence review, measurements and interpretation.
- A narrowly scoped fix and its relevant validation.
- A documentation or presentation update.

Keep dependent files together so each commit describes a reproducible change. Split by purpose, not an arbitrary file or line count. Do not create empty commits, invent work, backdate ordinary new work or routinely rewrite existing history.

Do not wait for a GPU job to finish or an entire experiment wave to complete before preserving work that is already done. Capture only relevant safe paths and explicitly review staged files so unrelated pending changes do not get swept into the checkpoint. Push after each checkpoint and verify the remote hash. End the work turn with a safe checkpoint, or identify exactly which source changes remain uncaptured or unpushed. Retain raw evidence and keep the external artifact/recovery metadata consistent. This does not install a background sync service or change GPU authorisation.

## Commit and publish

Use a subject that describes the actual change: `feat(bench): ...`, `fix(nixl): ...`, `research(load): ...`, `docs(presentation): ...` or `chore(backup): ...`. New ordinary work uses its actual author and committer timestamps. Historical record dating is separately documented in HISTORY_PROVENANCE.md; do not create empty commits or invent missing experiments.

```bash
git diff --stat
git add -- REVIEWED_PATHS
git commit -m 'research(load): describe the measured change'
git push origin main
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Replace REVIEWED_PATHS and the sample message with the actual reviewed files and subject. The local and remote commit hashes must match before reporting successful upload. Check that the remote remains private. Source files excluded by ignore rules need explicit review before any force-add; do not force-add credentials to satisfy a file count.

After committing, run `python3 tools/refresh_recovery_set.py` to refresh the local bundle, verify actual Git blobs and test restoration. This does not upload the sibling artifact store. See OFF_HOST_RECOVERY.md for the remaining recovery requirements.

## History correction on 19 October 2026

At the owner's explicit request, reconstructed research subjects were changed from generic import categories to conventional subjects based on the retained files. Their committer dates were aligned with the existing metadata-based author dates. Every per-commit file tree remained identical. The first published branch was replaced using an explicit force-with-lease against its verified old hash. The mapping and original dates remain auditable under provenance/ and the retained pre-rewrite local bundle. This one-time correction is not a reason to force-push ordinary future milestones.

There is no automatic mirror, background Codex or notification schedule. Autopilot remains disabled. Repository publication does not authorise additional GPU allocations or authentication attempts.
