# What the coverage audit establishes

Audited at **2026-10-20T01:50:39.770810+00:00**, against committed archive HEAD `95bf732d78a09e02dd36a9fbe72c6fc2d564a7f4`.

All **277** retained Markdown documents in the selected source trees match their captured SHA-256, archive copy and committed Git blob. All **209** indexed own research IDs occur in at least one of those documents. There are **127** dedicated Slurm job sections, including **127** with explicit purpose/observation/lesson fields.

This verifies that retained written records are in Git, rather than only on the temporary source filesystem. It does not prove every historical chat statement was written down, every deleted edit survived, every job has a complete causal analysis, or every old result passed later quality gates. An ID mentioned in a plan is not a completed review. The job index deliberately preserves this distinction.

The authored journey is a retrospective, source-linked reading guide. Its summaries are written now; they are not fabricated original dated entries or a complete transcript. Read corrections before treating old conclusions as current. No scheduler, credit, accuracy or throughput rerun is performed by this audit.

Scope is the manifest at the stated HEAD. Unselected source changes, remote uncollected jobs and authentication state are outside this claim. Large logs, traces and containers remain external objects: Git includes their manifests and recovery metadata, not all bytes. An off-host copy of that sibling store is still required.

Rebuild with `python3 build-index.py` on the original machine after a completed capture. The script refuses source/archive/Git hash disagreements and excludes this generated journal to avoid self-reference. Later document edits make this a dated audit, not a continuous mirror. See `coverage.json` for every input path and hash.
