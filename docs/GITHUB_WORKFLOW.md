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
