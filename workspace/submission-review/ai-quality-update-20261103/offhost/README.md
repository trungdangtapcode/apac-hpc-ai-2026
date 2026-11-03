# Verified private off-host copy of the final presentation materials

Release `ai-quality-presentation-20261103-v1` in the existing private repository
`trungdangtapcode/apac-hpc-ai-research` holds the current submission ZIP, PPTX,
full/main presentation PDFs and EN/VI transcript Markdown/PDF files. All eight
files were downloaded again and matched their captured byte lengths and SHA-256.
The source Git capture is `0ce8fed26457d077b779ddd88bde64a50294232e`.

The GitHub asset filename for the ZIP is `VNUHCM.-.TripleU.zip`; its local source
filename is `VNUHCM - TripleU.zip`. [The explicit map](REMOTE_ASSET_MAP.json)
and [verification receipt](DOWNLOAD_VERIFIED.json) identify exact original and
remote names. The first lookup failed only on this name; the retained downloaded
bytes then passed the follow-up verifier. No data file was replaced.

```bash
gh release download ai-quality-presentation-20261103-v1 --repo trungdangtapcode/apac-hpc-ai-research --dir NEW_DOWNLOAD_DIRECTORY
```

This is a private backup, not an organiser upload. It does not contain model
weights or runtime/authentication state. The ZIP contains all full-study answer
records and the scorer needed for the documented CPU-only replay. Earlier
private v4 remains the broader quality-study source/object backup.
