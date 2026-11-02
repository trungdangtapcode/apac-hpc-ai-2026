# Full MMLU-Pro quality corpus

## What this folder contains

This is a CPU-prepared, complete MMLU-Pro test corpus for a later local model-quality comparison. It contains all **12,032** `test` questions and their rendered prompts, plus the source's **70** `validation` examples. Every test prompt uses the original official five-shot chain-of-thought format: the first five validation rows from the same category, in source order. No question was sampled, no answer choices were removed beyond the official renderer's `N/A` filtering, and no prompt was shortened or reduced to fewer shots.

The test prompt records include the reference answer for local scoring. They are data files only: this builder did not send any prompt, answer, or request to a model service. The files do not establish that the model passes the 99% quality requirement.

## Frozen sources

- Dataset: `TIGER-Lab/MMLU-Pro`, `default` config, revision `b189ec765aa7ed75c8acfea42df31fdae71f97be`, MIT license.
- Official prompt implementation: `TIGER-AI-Lab/MMLU-Pro`, commit `f418b116db00b065c2aea046518d8fcf74d39872`, Apache-2.0 license.
- The source Parquet files remain untouched in `../mmlu-pro-local-quality-20261024/dataset/source/`.
- The original evaluator remains untouched at `../mmlu-pro-local-quality-20261024/upstream/evaluate_from_local.py`. The local `build_corpus.py` implements only its `format_cot_example` and `generate_cot_prompt(..., k=5)` formatting behavior. `initial_prompt.txt` is a byte-for-byte copy of the pinned prompt; its SHA-256 is in `manifest.json`.

`manifest.json` records source and output sizes/hashes, revisions, renderer provenance, counts, and integrity checks. The official renderer's *full evaluation loop* can lower the number of demonstrations when a prompt exceeds its model context. This corpus intentionally freezes five shots and does not do that. Prompt token lengths/context fit still need checking in the actual model runtime; do not silently drop shots to make a request fit.

## Rebuild

The build used the existing Python 3.9.25 CPU environment and the already-present PyArrow 19.0.1 package. No new network download, model-weight access, GPU, scheduler, or inference was used.

```bash
PYTHONPATH=/tmp/mmlu-pro-pyarrow \
  /home/apacsc42/.local/share/tripleu-presentation-venv/bin/python \
  /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/corpus-tools/build_corpus.py
```

The reused wheel, if this existing package must be reconstructed, is
`pyarrow-19.0.1-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`,
42,190,375 bytes, SHA-256 `335d170e050bcc7da867a1ed8ffb8b44c57aaa6e0843b156a501298657b1e972`.
It was already present under `/tmp/mmlu-pro-downloads`; this task did not download it. The extracted package was already present under `/tmp/mmlu-pro-pyarrow`.

The script fails closed if the source Parquet hashes/counts differ, test IDs are duplicated, validation examples are not exactly five per category, test and validation IDs overlap, or any generated prompt differs from the pinned renderer logic.

## Outputs

- `test-prompts-12032.jsonl`: 12,032 prompts with test IDs, source row index, category, question/options, reference answer, exact five validation IDs, prompt text, and prompt SHA-256.
- `validation-70.jsonl`: all 70 validation rows with category shot order and reference answers.
- `initial_prompt.txt`: pinned official task instruction.
- `manifest.json`: provenance, hashes, counts, and completed integrity checks.
- `build_corpus.py`: deterministic, CPU-only rebuild script.

## Verified result and limits

The build passed with 12,032 unique test IDs, 70 unique validation IDs, 14 categories, exactly five validation examples per category, and no test/validation overlap. The 12,032 prompts each contain the five source-ordered same-category examples and exactly match the local implementation of the pinned official renderer. `test-prompts-12032.jsonl` is 70,346,776 bytes with SHA-256 `15f8c40dff772594a91678cf2021d4955bfbd9f137090a0139d33178364ff4ca`.

This is a **corpus-integrity PASS only**. It is not a quality score, a comparison to a reference model, an official evaluation, or evidence that any model has passed the ≥99% threshold. No tokenizer-length preflight or model inference was performed here.
