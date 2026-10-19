# Private GitHub publication and commit history

The owner authorised creation of [https://github.com/trungdangtapcode/apac-hpc-ai-research](https://github.com/trungdangtapcode/apac-hpc-ai-research) after completing GitHub CLI login as `trungdangtapcode`. The repository is private and the initial 50-commit branch was successfully pushed. No authentication contents were copied into notes or the archive.

## Commit grouping and the requested correction

The initial count was 47 base archive commits plus three later research milestones. Each milestone groups multiple files and sometimes several GPU runs; one commit is not one job. The owner requested at least 60 commits and subjects such as feat, fix, research and docs, rather than generic import labels.

The first 57 commits were rewritten with descriptive conventional subjects based on their retained file groups. For reconstructed dated research records, committer dates now match their existing metadata-based author dates. Every rewritten commit keeps the exact same tree object. A verified pre-rewrite bundle remains under research-backup-preparation/ and the old-to-new mapping is committed under provenance/history-rewrite-20261019.json. Original capture dates and old IDs remain auditable; the dates do not reconstruct missing intermediate edits. Publication workflow, recovery documentation and this handoff add actual current changes to complete the requested minimum.

## What is and is not off this machine

GitHub stores the published Git history, inline source, documentation, manifests and provenance bundles. Larger benchmark evidence, inputs, traces, presentation assets and exact runtime containers are referenced by the manifest but remain in the sibling `apac-hpc-ai-research-artifacts` directory. This task does not upload those bytes or the model checkpoint. Keep the external store with the archive and preserve it separately off-host before relying on full recovery.

## Verify the current publication

```bash
cd /home/apacsc42/apac-hpc-ai-research
git rev-list --count HEAD
git log -8 --format='%h %cs %s'
git rev-parse HEAD
git ls-remote origin refs/heads/main
gh repo view trungdangtapcode/apac-hpc-ai-research --json visibility,url
```

The local and remote hashes must match, the commit count must meet the requested minimum and visibility must remain PRIVATE. The one-time history correction uses force-with-lease against the verified initial remote hash. Future ordinary milestones use regular commits and pushes; no automated mirror or background Codex was enabled. Research scheduler and credit snapshots were not refreshed during publication.

Checked preparation UTC: 2026-10-19T05:48:14.782568+00:00. The final push verification receipt is stored separately under research-backup-preparation/ so it can contain the exact resulting commit hash without a self-referential commit.
