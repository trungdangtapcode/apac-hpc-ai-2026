# Off-host recovery coverage

## What the private GitHub copy contains

A clone contains the published Git history, reviewed inline files, research notes, frozen small payloads, manifests, restoration tools and original upstream Git bundles. It does not contain the sibling artifact directory. A successful push therefore preserves the Git portion off this temporary machine while larger evidence still depends on the separate object store.

## What must accompany the clone

Keep `backup/manifest.jsonl`, `backup/scan-results.json`, the external `objects-index.json`, compressed objects and their SHA256SUMS together. The normal object store contains exact benchmark inputs, request records, profiles, larger archives, presentation assets and the retained runtime containers. Two damaged collection archives are separate local-only review objects with incomplete member inspection; their presence in a manifest is not permission to publish their bytes automatically.

A separately preserved copy of normal objects must use private storage under the owner's control. No external object destination or transfer was configured by creating this GitHub repository. Do not write destination credentials into notes or Git. The public model weights are not in either Git or the retained object set; recover and validate that checkpoint separately as described in REPRODUCIBILITY.md.

## Recover and verify

```bash
git clone https://github.com/trungdangtapcode/apac-hpc-ai-research.git
cd apac-hpc-ai-research
python3 tools/verify_snapshot.py --store ../apac-hpc-ai-research-artifacts --deep
python3 tools/restore_snapshot.py --store ../apac-hpc-ai-research-artifacts --destination ../restored-apac
```

Place the independently preserved artifact directory at the shown sibling path first, or supply its actual path. Verification checks each captured inline file and decompressed object against the manifest. Restore refuses to overwrite different existing content by default. A failure caused by a missing object is a real recovery gap, not a reason to remove that file from the evidence manifest.

The artifact directory also holds a `research-history.bundle`, which can recover the Git portion without GitHub access. `tools/refresh_recovery_set.py` regenerates it after a local commit and tests restoration from a fresh clone without using the original workspace. Transport checksums detect changed compressed files; deep verification checks original decompressed bytes. These checks do not create an off-host object copy.

## Resume carefully from the recovered evidence

Read the current dated handoff and query actual schedulers before resubmitting any job. Recreate machine-private authentication outside the clone. Preserve frozen submitted bundles and create derived configurations for changed cluster paths. Restoring notes does not restart VPN, jobs or Codex autopilot. Keep H100/H200 results and official accuracy limits distinct.
