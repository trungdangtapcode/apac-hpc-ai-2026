# AIPerf token-count provenance audit

Date: 29 October 2026. Scope: read-only inspection of the pinned AIPerf 0.12 source used by the Qwen runs and the retained exported run configurations. No GPU, scheduler, submission, or frozen payload was touched.

## Finding

For runs 27270 and 27272, the exported command and configuration do not set `endpoint.use_server_token_count`. The pinned AIPerf 0.12 model declares its default as `false` (`evidence/source/.../aiperf/config/endpoint.py`, around line 235). Therefore the configured count path is client-side tokenization, not response `usage` counts from the server. The parser branches on this setting (`records/inference_result_parser.py`, lines 309–313): with the default, it tokenizes parsed response text and input text extracted from the exact serialized request payload. With `true`, it reads the last non-empty server usage object and uses `prompt_tokens` and `completion_tokens` (lines 506–515); for streamed OpenAI-compatible requests the endpoint requests `stream_options.include_usage` (openai_chat.py, lines 74–79, 148–159).

The local count path is material to interpreting the rows: synthetic prompt creation samples the configured number of token IDs and decodes them to text (`dataset/generator/prompt.py`, lines 313–322). The parser later tokenizes extracted request text, joined with a space, and tokenizes parsed response text (inference_result_parser.py, lines 365–425 and 589–644). Those metrics therefore describe AIPerf's local tokenization of text, not a retained record of the server's actual input/output token IDs. The exported configurations set tokenizer `Qwen/Qwen3-235B-A22B-Instruct-2507`, synthetic ISL mean 4000/stddev 0 and OSL mean 200/stddev 0; endpoint extras are `min_tokens=200`, `max_tokens=200`, `ignore_eos=true`, `temperature=0.0`. `apply_chat_template` is not set in the export; its pinned source default is false (`config/tokenizer.py`, lines 71–83). The chat endpoint puts per-turn max tokens in `max_completion_tokens` by default and then merges endpoint extras (`endpoints/openai_chat.py`, lines 62–70).

The retained observations are consistent with the discrepancy being in the reported text-tokenization metric: 27270 has output counts 200 for 1898 rows and 199 for 4; 27272 has 200 for 1887 rows and 199 for 5; 26949 has 200 for 1893 rows and 199 for 2. Reported inputs are 3986 or 3987 tokens for 27270/27272, despite the configured synthetic mean of 4000 and zero standard deviation. These values are not evidence that the model physically stopped one token early, nor do they establish a specific tokenizer, prompt-format, or server behavior as the cause. The exact per-row cause remains **unknown** because actual generated token IDs and authoritative per-request server usage are not retained alongside these rows.

## Scoring interpretation

The organizer clarified that official good output tokens per second is `Goodput (requests/s) × 200`; 200 is the fixed workload output length. This audit does not redefine the score, the 90% good-request gate, or any other acceptance gate. Do not replace the official fixed multiplier with a per-run mean of locally re-tokenized output text. Do not mutate frozen submissions or previously recorded results.

## Evidence and provenance

The source image was `/scratch/enroot-images/aiperf.sqsh`, SHA-256 `58fc1cbc2aec897fe39bf74d8f38f055b63c3690429162134f818d9597d22c0a`. Only ten relevant Python source files were selectively extracted; no corpus, image, model weight, runtime home, or authentication material is included. Their hashes are listed in [evidence/SHA256SUMS](evidence/SHA256SUMS).

Retained exported profile configurations:

- Run 27270: `runs/27270/confirm/n64/artifacts/profile_export_aiperf.json`, SHA-256 `6eda0a46c3645ac3a82cdf259c925bc0ff07cd5e3d0cd086ec134d3cd5995609`.
- Run 27272: `runs/27272/confirm/n64/artifacts/profile_export_aiperf.json`, SHA-256 `9e89a90bb472c3d32de8a60220349d9aaf3a34719d437e0cb692dc8d70276d9b`.
- Matched control 26949: `runs/26949/confirm/n64/artifacts/profile_export_aiperf.json`, SHA-256 `3b2d86388adb7168141684fffaa34300ba1a4c61e3bf584e1a47072903ba2a22`.

These exports include redacted API credentials. They are cited by path and hash; this report does not reproduce their full contents or request/response text.
