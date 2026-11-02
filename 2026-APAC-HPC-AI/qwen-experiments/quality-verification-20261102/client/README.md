# Local Qwen Quality Verification Client

This client performs a paired local MMLU-Pro quality comparison between the exact FP8 reference deployment and the exact submitted candidate. It does **not** reproduce the organizer's private evaluation suite or certify an official contest pass. A local result can show whether the candidate retained at least 99% of this pinned reference's accuracy on this pinned local test set.

## Protocol and safeguards

- Dataset: pinned TIGER-Lab/MMLU-Pro test split, 12,032 questions; five same-category validation demonstrations in source order.
- Prompt: source-compatible MMLU-Pro CoT text, one user message, rendered with the pinned Qwen tokenizer chat template and generation prefix. The full target question/options are preserved. The number of demonstrations decreases only from five to zero when required by the configured context budget. No question is truncated or removed. An item that does not fit at zero shots makes preparation fail and blocks inference.
- Default preparation context: 4,096 tokens with 2,048 reserved for generation. To reproduce the pinned upstream evaluator's strict `prompt_tokens < 2048` test, pass `--strict-prompt-lt 2048`.
- If both deployments are configured for 8,192 tokens and the selected local comparison protocol reserves 2,048 for output, prepare **one shared corpus** with `--max-context 8192` (prompt budget 6,144), then use that identical compiled file for both runs. This is a declared local protocol; it is not a claim that BTC's private evaluator uses 8,192.
- Sampling: temperature 0, top-p 1, max 2,048 generated tokens, stop `Question:`; no 200-token cap.
- Parser: exact pinned upstream regex order (`answer is`, `Answer:`, final standalone A–J) from MMLU-Pro commit `f418b116db00b065c2aea046518d8fcf74d39872`. The upstream evaluator randomly guesses when parsing fails; this local scorer deliberately counts invalid output as wrong so the denominator is deterministic. A stricter parser is retained only as a diagnostic and does not affect the score.
- Every selected question gets one terminal record. Errors, deadline-not-started records, malformed answers, and missing outputs are wrong in the fixed denominator. There are no retries. Raw response bodies, completion text, usage, finish reason, parse path, hashes and errors are retained.
- `compare` requires paired, complete, identical ID lists and matching prepared corpus/configuration. The local engineering gate is candidate accuracy / reference accuracy >= 0.99 and zero service errors in both runs. These conditions are not an official BTC certification.

## CPU preparation

Run in a CPU environment that has Transformers and the exact local tokenizer files; preparation does not load model weights or use a GPU. The tokenizer files are validated against `../mmlu-pro-local-quality-20261024/source-provenance.json` pins.

```bash
python3 quality_client.py prepare \
  --corpus ../corpus-tools/test-prompts-12032.jsonl \
  --validation ../corpus-tools/validation-70.jsonl \
  --screen-corpus ../mmlu-pro-local-quality-20261024/dataset/screen-128.jsonl \
  --tokenizer-path /path/to/local/pinned/tokenizer \
  --out prepared-8192-2048 \
  --max-context 8192 --max-output-tokens 2048
```

For the original local evaluator's effective input budget, use `--max-context 4096 --max-output-tokens 2048 --strict-prompt-lt 2048`. Preparation writes `compiled-corpus.jsonl`, `prepare-manifest.json`, and the exact historic pilot IDs in `pilot-ids.json`. Output directories are immutable: the command refuses an existing path. The compiled corpus includes expected labels for offline scoring, but those labels are never included in API request messages.

The default full dataset must have all 12,032 rows fit. `--allow-unfit` exists only to preserve an inspection artifact; it does not allow the run command to generate from that artifact.

## Runs

Use a non-loopback gateway URL when the allocated inference server is reachable through one. Keep reference and candidate runs separate, but use the **same compiled corpus**, prompt hashes, sampling settings and concurrency. The precise served model string is recorded in `run.json`.

Pilot on the historic 128 IDs:

```bash
python3 quality_client.py run \
  --corpus prepared-8192-2048/compiled-corpus.jsonl \
  --prepare-manifest prepared-8192-2048/prepare-manifest.json \
  --ids-file prepared-8192-2048/pilot-ids.json \
  --base-url http://NODE_OR_GATEWAY:PORT/v1 --model qwen \
  --out runs/reference-pilot --concurrency 16 --timeout 120
```

Repeat with the candidate and a new `--out` directory. For the full set, omit `--ids-file`, or split into stable disjoint shards using `--shard-count K --shard-index I` for each `I` from 0 through K−1. Shard by the frozen corpus order. Do not reuse or merge output directories. For a wall-clock deadline, provide Unix seconds via `--deadline-epoch`; a request is not started inside `timeout + deadline-margin` seconds of that deadline. Unstarted IDs still receive records and remain denominator failures.

An optional API key is read from an environment variable named by `--api-key-env`; its value is never written to run metadata. A run with any deadline-not-started rows is marked `INCOMPLETE` and exits nonzero; its partial records remain available for diagnosis but cannot pass `compare`.

## Paired comparison

```bash
python3 quality_client.py compare runs/reference-pilot runs/candidate-pilot \
  --out reports/pilot-comparison.json
```

The report shows each accuracy as `correct / denominator`, candidate/reference ratio, category accuracy, service errors, coverage, and paired correctness discordances. The final full-set report is the relevant local engineering result; a 128-question pilot has much wider uncertainty and only estimates whether a full evaluation is worth the runtime.

## Tests

```bash
python3 -m unittest -v test_quality_client.py
```

Tests use an ephemeral loopback HTTP fixture only. They cover parser behavior, concurrency, error/no-retry accounting, fixed denominators, deadline handling, exact coverage, and the ratio gate; they do not claim model quality.
