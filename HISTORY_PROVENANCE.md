# Import history provenance

The source directories already contain dated notes, run snapshots, scheduler records, frozen scripts and corrected conclusions. They did not have a Git commit for each research step. This repository imports those existing records now.

Research files are grouped by their retained last-modified UTC day and topic. Their import commit's author timestamp is the latest retained modification time in that group, with a reproducible path list and date basis recorded in `provenance/import-commits.json`. This represents the snapshot's recorded time, **not independently verified original authorship or an exact reconstruction of intermediate file edits**. File copy operations and extracted archives can affect modification times. Explicit run/collection timestamps inside the files take precedence for interpreting experiments.

All committer timestamps use the actual time of import. Imported commit messages identify the records as imports. Bootstrap, archive metadata and final validation commits use current timestamps. No activity is fabricated to fill missing days or extend the work to an invented month. Old vendor/extracted/reference files are imported with a current author timestamp rather than attributed to the user's past work; upstream Git bundles retain their original authors and dates.

Git identity requested by the owner: `trungdangtapcode <tcuong1000@gmail.com>`. This is commit attribution only, not GitHub authentication. The intended remote is a private `trungdangtapcode/apac-hpc-ai-research` repository; no remote is created or pushed during local preparation.

The source checkouts are not rewritten, reset or cleaned. Their untracked research is snapshotted separately; their original `.git` metadata is represented by portable Git bundles. This import does not reproduce versions that no surviving file, archive or source history contains. Source data that changes during capture is reported rather than silently claimed as verified.
