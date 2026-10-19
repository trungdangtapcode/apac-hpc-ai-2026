# What the coverage audit establishes

Audited at **2026-10-19T19:20:50.960324+00:00**, against committed archive HEAD `b009830c4775482a589f6b8c11898dec873e61f1`.

All **247** retained Markdown documents in the selected source trees match their captured SHA-256, archive copy and committed Git blob. All **194** indexed own research IDs occur in at least one of those documents. There are **127** dedicated Slurm job sections, including **127** with explicit purpose/observation/lesson fields.

This verifies that retained written records are in Git, rather than only on the temporary source filesystem. It does not prove every historical chat statement was written down, every deleted edit survived, every job has a complete causal analysis, or every old result passed later quality gates. An ID mentioned in a plan is not a completed review. The job index deliberately preserves this distinction.

The authored journey is a retrospective, source-linked reading guide. Its summaries are written now; they are not fabricated original dated entries or a complete transcript. Read corrections before treating old conclusions as current. No scheduler, credit, accuracy or throughput rerun is performed by this audit.

Scope is the manifest at the stated HEAD. Unselected source changes, remote uncollected jobs and authentication state are outside this claim. Large logs, traces and containers remain external objects: Git includes their manifests and recovery metadata, not all bytes. An off-host copy of that sibling store is still required.

Rebuild with `python3 build-index.py` on the original machine after a completed capture. The script refuses source/archive/Git hash disagreements and excludes this generated journal to avoid self-reference. Later document edits make this a dated audit, not a continuous mirror. See `coverage.json` for every input path and hash.
