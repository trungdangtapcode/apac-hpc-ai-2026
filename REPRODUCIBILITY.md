# Reproduction and recovery

## Recover evidence first

Clone the private Git repository using an authorised GitHub account:

```bash
git clone https://github.com/trungdangtapcode/apac-hpc-ai-research.git
cd apac-hpc-ai-research
git log -5 --oneline
```

A successful clone recovers committed inline files and the complete published Git history. It does not fetch the content-addressed objects referenced by the manifest. Obtain the matching sibling object store from its separately preserved copy before requesting full restoration.

Copy the sibling object store to durable storage. Run deep verification, then restore into a new destination with `tools/restore_snapshot.py`. Restore does not submit jobs, start VPN, authenticate, launch Codex or overwrite a running experiment. Keep `backup/manifest.jsonl`, `backup/scan-results.json`, the object index and upstream Git bundles with the archive.

Original file SHA-256 and modification times are retained. Original run manifests may refer to excluded container homes or dependency caches; an archive can preserve evidence without claiming every cluster path is portable. Refer to the scope/exclusion reports when a historical manifest contains a file outside the retained set.

## Recover the runtime

The exact local `sglang-harbor.sqsh` and `aiperf.sqsh` containers are stored as external objects. Restore them and compare their hashes with the retained `nscc-pbs/asset-contract.json`. Do not assume that pulling today's image tag recreates the tested image. Enroot/Pyxis is used on the H200 Slurm platform; the H100 PBS platform uses the retained Singularity wrappers. Drivers, interconnects, shared filesystem paths and scheduler allocations must be provisioned by the target cluster.

Restore the model metadata and obtain the public `Qwen/Qwen3-235B-A22B-Instruct-2507-FP8` checkpoint under a new configured path. Weight shards are not part of this archive. The metadata inventory records the local shard layout and the available checksum contracts; a full immutable weight-file checksum set may not exist in the original records. Do not claim bit-for-bit model recovery from names/sizes alone.

## Resume research

Read `workspace/notes/CURRENT.md`, `POLICY.md`, the linked latest review and the actual scheduler. An archived handoff is dated, not live state. Verify whether previously submitted jobs still exist before resubmission. Preserve raw failed attempts and all benchmark requests. Codex autopilot was explicitly disabled and must remain disabled unless newly requested.

Select a complete accepted baseline and create a **new derived bundle**. Map old `/home/apacsc42`, `/scratch/models`, `/scratch/enroot-images` and PBS paths to the new environment. Update the new bundle's configuration, exports, mount paths and patch checksums consistently; freeze a new SHA256SUMS before submission. Never rewrite historical submitted bundles merely to make them run elsewhere, as their hashes establish what was measured.

Revalidate topology/TP/EP, native FP8 weights, BF16 cache, NIXL transport variant, kernel backends and each role's resolved server arguments. Keep the full 60/120/30 protocol, 4000/200 workload, errors in the denominator and both per-request latency conditions. Local output checks are not the official full reference-set accuracy evaluation. Small gains require repetitions and fresh controls. Do not compare H100/H200 points as a common ranked score or treat the old frozen calibration as universal.

## Known recovery boundaries

This archive cannot recover deleted intermediate edits, uncollected remote PBS results, private authentication, scheduler reservations, GPU availability or public-model bytes that were never copied. The manifest and verification report identify what was actually captured. The published Git history now has an off-machine copy in the private GitHub repository. External object bytes remain local until copied separately and would still be lost with this temporary machine. Do not describe the GitHub clone as complete runtime or evidence recovery.
