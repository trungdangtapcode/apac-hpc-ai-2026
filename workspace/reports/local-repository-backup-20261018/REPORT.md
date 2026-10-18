# Local research preservation — 18 October 2026

The user requested a local backup before installing GitHub CLI or publishing anything. The intended remote is a private `trungdangtapcode/apac-hpc-ai-research` repository. No remote repository, authentication or upload has occurred.

## Locations

- Git archive: `/home/apacsc42/apac-hpc-ai-research`.
- Required large-object store: `/home/apacsc42/apac-hpc-ai-research-artifacts`.
- Original active research remains in `/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments` and `/home/apacsc42/workspace`; these paths and queued GPU jobs were not moved or rewritten.

The archive is a captured copy, not an automatic mirror of future experiments. New results in the original working directories need an explicit subsequent capture. The task did not resume optimisation, submit jobs, restore VPN or enable Codex autopilot.

## Captured data and coverage

The verified base capture retains 17,570 regular source files: about 93.31 GB of logical data, with 477 unique external objects occupying about 18.83 GB plus about 608 MB of small Git-tree files. Final handoff/report updates are added separately to the final manifest. Repeated inputs and snapshots share SHA-256 objects; logical file identity and exact bytes remain reconstructible. Code, notes, tutorials, all captured successful/failed run evidence, submitted scripts, reviews, profiles and presentation artifacts are covered. Empty submission directories are recorded for restoration without adding files into HPC_Task.

Both exact local Enroot container hashes match the original tested asset contract. Public Qwen model weights (about 220 GiB) are not copied; configuration, tokenizer, shard layout and available checksum contracts are retained. Public checkpoint download and cluster hardware/software are still required. Remote H100-only results uncollected before the VPN disconnect are not part of this local snapshot.

The two old damaged raw collection archives are retained byte-for-byte in owner-only `local-review-objects`, with incomplete member-inspection status. Do not automatically publish them. Authentication state/private logs, private keys, environment secrets, container homes and recreatable caches/environments are excluded with documented reasons. A strict signature scan of the Git tree passed; pattern scanning does not certify absence of every possible secret in opaque binary assets.

## Git history and verification

There are 44 explicitly labelled imported snapshot groups, plus bootstrap and archive metadata commits. Source metadata supports 29 September and 9–18 October; no daily activity is invented for gaps or an artificial month. Author dates follow retained metadata; committer dates show actual import. Original organiser history is stored in two separately verified Git bundles with original attribution. Identity: `trungdangtapcode <tcuong1000@gmail.com>`.

Deep verification decompressed and hashed all 477 unique objects and checked every small captured source file. A recovery test restored a handoff, raw generated input, presentation and damaged archive with matching hashes. Final integrity and commit metadata are recorded in the archive's backup reports. A final current-time commit records this handoff and capture updates.

## Remaining work

This is still on the same temporary machine. A local commit is not a durable remote backup. Keep both directories together, or use the standalone history bundle plus object store. Install/authenticate GitHub CLI and create/push the private repo only in the later requested phase. Large objects require separate off-machine transfer; Git cloning alone cannot restore them. Review local-only/opaque objects before publication. Read the archive README and REPRODUCIBILITY.md for recovery boundaries and commands.
