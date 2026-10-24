# Pinned SGLang API review

## Scope and source identity

Reviewed the existing image `/scratch/enroot-images/sglang-harbor.sqsh` read-only on 24 October 2026. Selected source files were extracted with `unsquashfs -processors 4`; no image was started and no network request was made. The exact source snapshots inspected are retained under [`pinned-sglang/`](pinned-sglang/) with hashes in [`PINNED_API_SHA256SUMS`](PINNED_API_SHA256SUMS).

The SGLang worker does implement `POST /v1/tokenize` in `http_server.py` (route decorator near line 1737). Its `TokenizeRequest` accepts exactly one of `prompt` or `messages`; its chat branch calls `_tokenize_chat_request`, which passes the chat request through `OpenAIServingChat._process_messages`. The response schema is `tokens`, `count`, and `max_model_len`. This is the worker API shape, not a guaranteed inference-gateway route.

## Gateway finding

The same image includes Rust SGLang Model Gateway source. Its HTTP inference router explicitly forwards `/v1/chat/completions` in `routers/http/router.rs` (`route_chat`), while the reviewed inference `RouterTrait` does not expose a tokenize method. The gateway's separate tokenizer handler accepts `request.prompt.as_strings()`, tokenizes plain text without special tokens, and returns `tokens`, `count`, and `char_count`. It does not accept `messages`, apply the chat template, or return `max_model_len`. That handler is distinct from the inference router interface inspected here. Therefore the previous client assumption that gateway `/v1/tokenize` gave the exact chat-template token count was wrong and has been removed.

## Selected preflight contract

The client now uses one method: offline Hugging Face `AutoTokenizer` loaded only from the explicitly provided local tokenizer directory with `local_files_only=True`. It verifies tokenizer JSON, tokenizer config, and chat-template SHA-256 values against the pinned provenance. It renders the exact user message sent to `/v1/chat/completions` via `apply_chat_template(..., tokenize=True, add_generation_prompt=True)`, with no engine-specific thinking flags or template kwargs. The token count therefore includes the chat template's generation prefix. It reserves the full 2,048 generated tokens.

The official threshold is `prompt_tokens < 4,096 - 2,048`, i.e. strictly fewer than 2,048 prompt tokens. The serving topology threshold is `prompt_tokens + 2,048 <= 8,192` (or the explicitly passed serving context if changed). The 8,192 value is the configured serving context, not a runtime response from the router; no request is made to discover server state. A deployment whose tokenizer files or template hashes differ fails preflight. Any tokenizer loading/rendering error or unfit question prevents all generation requests. No truncation, shot removal, fallback tokenizer, alternate route, or alternate chat template is attempted.

This remains CPU-prepared protocol code. No inference, GPU, scheduler, or live HTTP call was made. The existing latency and 17-minute feasibility question remains open for root review. The offline preflight can confirm exact local tokenization but cannot verify the running server's live context configuration or independently prove server-side chat-template equivalence; model/tokenizer/template identity must be checked in the admitted deployment metadata.
