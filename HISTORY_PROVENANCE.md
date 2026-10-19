# Import history provenance

The source directories already contain dated notes, run snapshots, scheduler records, frozen scripts and corrected conclusions. They did not have a Git commit for each research step. This repository imports those existing records now.

Research files are grouped by their retained last-modified UTC day and topic. Their import commit's author timestamp is the latest retained modification time in that group, with a reproducible path list and date basis recorded in `provenance/import-commits.json`. This represents the snapshot's recorded time, **not independently verified original authorship or an exact reconstruction of intermediate file edits**. File copy operations and extracted archives can affect modification times. Explicit run/collection timestamps inside the files take precedence for interpreting experiments.

Before the owner-requested correction on 19 October, all committer timestamps used the actual import time and record subjects used generic import labels. The current reconstructed record commits use conventional subjects and both author/committer dates follow their retained metadata date. Bootstrap, reference snapshots, archive metadata and later ordinary work retain their actual work timestamps. No activity is fabricated to fill missing days or extend the work to an invented month. Old vendor/extracted/reference files are imported with a current author timestamp rather than attributed to the user's past work; upstream Git bundles retain their original authors and dates.

Git identity requested by the owner: `trungdangtapcode <tcuong1000@gmail.com>`. This is commit attribution only, not GitHub authentication. The remote is the private `trungdangtapcode/apac-hpc-ai-research` repository, created and first pushed on 19 October 2026 after the owner completed GitHub authentication. Local preparation preceded that upload.

The source checkouts are not rewritten, reset or cleaned. Their untracked research is snapshotted separately; their original `.git` metadata is represented by portable Git bundles. This import does not reproduce versions that no surviving file, archive or source history contains. Source data that changes during capture is reported rather than silently claimed as verified.

## Why the initial pushed branch had 50 commits

The base local archive had 47 commits: bootstrap, metadata-dated import groups and final archive/handoff records. Three later research milestones added status recovery, a controlled submission batch and the next accepted operating-point results. This produced the first 50 commits pushed to GitHub. A commit is a group of retained changes, not one experiment, one job or one calendar day. Several job runs can be preserved in one milestone.

The owner subsequently requested at least 60 commits. Publication work is split into separate nonempty commits for repository overview, transport scope, clone/recovery instructions, research navigation, provenance, authentication exclusions, agent handoff, the GitHub workflow, off-host recovery and publication records. These are actual documentation/configuration changes at their real work dates. They are not ten additional benchmark runs or reconstructed historical edits. The first published branch was subsequently corrected at the owner's explicit request, using force-with-lease against its verified old head. Per-commit trees are unchanged; the old-to-new mapping is retained.

## Subject and committer-date correction

`provenance/history-rewrite-20261019.json` maps the 57 pre-correction commits to the current hashes, subjects and date policy. Every mapped commit has exactly the same tree object before and after correction. The metadata-based record author dates already existed; their committer dates were aligned so the GitHub history no longer groups all reconstructed research under the capture day. Reference/vendor snapshots and ordinary later work were not assigned invented historical research dates.

Earlier report snapshots describing generic subjects or actual-import committer timestamps describe the previous branch and are superseded by this section. Original import-group ledgers retain their original commit IDs and labels as historical evidence; use the mapping to locate their current commits. Retained modification times do not reconstruct deleted intermediate edits or prove exact historical development chronology.
