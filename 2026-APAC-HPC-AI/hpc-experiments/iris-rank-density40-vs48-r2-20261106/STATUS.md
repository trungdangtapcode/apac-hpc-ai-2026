# R2 derived after source-checker TypeError

**2294999 FAILED 1:0** in 61 seconds on iris001, before any solver arm. The accepted-source log identifies one helper interface error: `verify_exact_tree()` returned an integer, but its caller unpacked `(file_count, directory_count)`. The source data and manifests were not rejected as mismatched. Preserve the failed job and its evidence in the preceding package; do not amend its receipt or frozen 100-file payload.

This derived package changes only `source_checks.py` within the frozen operational payload. The fix returns both measured integers: the complete file count and actual directory count. `offline_checks.py` now builds a realistic 40-rank Scotch source fixture from pinned inputs, initialized zero fields, rank-local mesh files, the READY marker, shared mesh symlink and supplementary inventory. It invokes the same `verify()` entry point used before the first solver arm and separately verifies the tuple contract. The test would fail with the old helper API.

The exact earlier 100 hashes are retained in the preceding directory. The derived review re-seals the same payload set with only the corrected source-checker hash changed. Parent controls still require a fresh root review, successful offline checks, a fresh deployment and receipt, locked queue/budget gates, and scheduler acceptance. No new deployment or submission has been performed from this package.

The previous failed allocation cost was 61 × 56 / 3,600 = 0.948889 allocated CPU-hours, rounded up to one for the local ledger. Parent reconciliation is 1,629 consumed, zero reserved, stage 1,768. A prospective 140 CPU-hour retry requires a bounded agent-selected stage of 1,769 (+1); this is not billed SU or a new owner-set allowance.
