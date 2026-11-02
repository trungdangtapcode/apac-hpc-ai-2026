# Portable quality evidence backup

`build_portable.py` creates a bounded portable bundle of selected quality-study
evidence that includes external object-store payloads. It does not make a full
runtime backup and does not modify the source archive, its manifest, or the
external object store.

## Scope

The builder selects rows from the archive's captured `backup/manifest.jsonl`
under these prefixes:

- `2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/`
- `2026-APAC-HPC-AI/qwen-experiments/mmlu-pro-local-quality-20261024/dataset/`
- `workspace/reports/ai-quality-verification-20261103/`

It excludes `evidence/builds/` to prevent including its own previous output.
The bundle includes the selected manifest rows, a subset external-object index,
scope metadata, and only the unique `.zst` objects referenced by those rows.
Inline files remain recoverable from the exact Git commit recorded in
`SCOPE.json`; they are not copied into the bundle. Runtime images, model tensor
weights, private runtime homes/caches, authentication/session state and unrelated
sibling-store objects are excluded. Public tokenizer metadata needed by the
frozen experiment is retained.

## Build

Choose a new output directory. Existing output directories are refused.

```sh
python3 /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/evidence/build_portable.py \
  --out-dir /home/apacsc42/quality-study-portable-backup-20261102
```

Optional `--archive` and `--store` arguments override the defaults
`/home/apacsc42/apac-hpc-ai-research` and
`/home/apacsc42/apac-hpc-ai-research-artifacts`. The builder takes a shared
`research-checkpoint.lock`, records the archive `HEAD`, and reads the captured
manifest and external object index as one snapshot.

For every selected external object, it verifies the recorded uncompressed
SHA-256 and byte length by streaming `zstd -d -c`. It also checks the compressed
SHA-256 against `SHA256SUMS` when that older global list contains the object,
and compressed size against `objects-index.json`. A recent incremental capture
can precede a global checksum refresh. For such objects, the builder computes
and records a fresh compressed transport hash after independently verifying
the original bytes against the captured manifest. An existing checksum mismatch
is always an error; the missing older checksum does not weaken the original
content-hash verification.
Compression uses one worker thread. `BUILD.json`, outside the tar archive,
records the resulting bundle SHA-256 and size. No upload is performed.

The bundle is a portable copy of selected evidence, not proof of a complete
study environment. Retain the captured Git commit and upload this bundle
separately when an off-host artifact copy is required.
