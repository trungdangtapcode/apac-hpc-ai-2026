#!/usr/bin/env python3
"""Sequential OpenAI-compatible local MMLU-Pro screen client; no retries or credentials on disk."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "dataset/screen-128.jsonl"
CORPUS_MANIFEST = ROOT / "dataset/manifest.json"
PROVENANCE = json.loads((ROOT / "source-provenance.json").read_text())
OFFICIAL_CONTEXT = 4096
SERVING_CONTEXT_EXPECTED = 8192
MAX_OUTPUT_TOKENS = 2048
TEMPERATURE = 0.0
TOP_P = 1.0
ANSWER_MARKER = re.compile(r"(?i)\bthe answer is\s*\(([A-J])\)")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_answer(text: str | None) -> str | None:
    """Accept one final official-format letter only; invalid output stays incorrect."""
    if not text:
        return None
    matches = list(ANSWER_MARKER.finditer(text))
    if len(matches) != 1:
        return None
    match = matches[0]
    if text[match.end() :].strip(" *\t\r\n.!`"):
        return None
    return match.group(1).upper()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def require_loopback(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "http" or not parsed.hostname:
        raise ValueError("Only local cleartext HTTP endpoints are allowed for this screen")
    if not parsed.path.rstrip("/").endswith("/v1"):
        raise ValueError("Base URL must end in /v1 so chat and tokenize paths are explicit")
    try:
        is_loopback = parsed.hostname.lower() == "localhost" or __import__("ipaddress").ip_address(parsed.hostname).is_loopback
    except ValueError:
        is_loopback = False
    if not is_loopback:
        raise ValueError("Endpoint must resolve to localhost / loopback; no external API calls are allowed")
    return url.rstrip("/")


def endpoint(base: str, path: str) -> str:
    return base + "/" + path.lstrip("/")


def load_pinned_tokenizer(path: Path, expected_tokenizer_sha: str, expected_config_sha: str,
                          expected_template_sha: str):
    """Load only the local pinned tokenizer; do not contact a hub or model endpoint."""
    tokenizer_json = path / "tokenizer.json"
    config_json = path / "tokenizer_config.json"
    if not tokenizer_json.is_file() or sha256_bytes(tokenizer_json.read_bytes()) != expected_tokenizer_sha:
        raise ValueError("local tokenizer.json is missing or does not match the pinned SHA-256")
    if not config_json.is_file() or sha256_bytes(config_json.read_bytes()) != expected_config_sha:
        raise ValueError("local tokenizer_config.json is missing or does not match the pinned SHA-256")
    config = json.loads(config_json.read_text(encoding="utf-8"))
    template = config.get("chat_template")
    if not isinstance(template, str) or sha256_bytes(template.encode("utf-8")) != expected_template_sha:
        raise ValueError("local chat template is missing or does not match the pinned SHA-256")
    try:
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise RuntimeError("transformers is required for offline pinned-tokenizer preflight") from exc
    tokenizer = AutoTokenizer.from_pretrained(str(path), local_files_only=True, trust_remote_code=False)
    if tokenizer.chat_template != template:
        raise ValueError("AutoTokenizer chat template differs from the pinned tokenizer_config.json")
    return tokenizer


def tokenize_wire_messages(tokenizer: Any, messages: list[dict[str, str]]) -> list[int]:
    """Render the exact chat wire messages with the pinned template and generation prefix."""
    ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
    if hasattr(ids, "tolist"):
        ids = ids.tolist()
    if not isinstance(ids, list) or any(isinstance(token, bool) or not isinstance(token, int) for token in ids):
        raise ValueError("AutoTokenizer returned an invalid token ID sequence")
    return ids


def post_json(url: str, body: dict, timeout: int, api_key: str | None = None) -> dict:
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    req = urllib.request.Request(url, data=raw, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body_bytes = response.read()
        return {
            "http_status": response.status,
            "http_request_id": response.headers.get("x-request-id") or response.headers.get("x-amzn-requestid"),
            "body_bytes": body_bytes,
            "json": json.loads(body_bytes.decode("utf-8")),
        }


def get_json(url: str, timeout: int, api_key: str | None = None) -> dict:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body_bytes = response.read()
        return {
            "http_status": response.status,
            "http_request_id": response.headers.get("x-request-id") or response.headers.get("x-amzn-requestid"),
            "body_bytes": body_bytes,
            "json": json.loads(body_bytes.decode("utf-8")),
        }


def atomic_json(path: Path, value: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, value: dict) -> None:
    with path.open("a", encoding="utf-8") as out:
        out.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        out.flush()
        os.fsync(out.fileno())


def make_run(base: str, model_id: str, tokenizer_id: str, tokenizer_path: str, tokenizer_sha: str,
             chat_template_sha: str, served_context: int, run_name: str) -> tuple[Path, dict]:
    corpus = load_jsonl(CORPUS)
    manifest = json.loads(CORPUS_MANIFEST.read_text())
    if len(corpus) != 128 or len({r["question_id"] for r in corpus}) != 128:
        raise ValueError("Frozen corpus must contain exactly 128 unique questions")
    if tokenizer_id != PROVENANCE["target_model_tokenizer"]["model_id"]:
        raise ValueError("Tokenizer ID does not match the pinned model revision")
    if tokenizer_sha != PROVENANCE["target_model_tokenizer"]["tokenizer_json_sha256"]:
        raise ValueError("Tokenizer hash does not match the pinned model revision")
    if chat_template_sha != PROVENANCE["target_model_tokenizer"]["chat_template_sha256_utf8"]:
        raise ValueError("Chat template hash does not match the pinned model revision")
    outdir = ROOT / "results" / run_name
    outdir.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    run = {
        "status": "PREFLIGHT",
        "started_utc": started,
        "base_url": base,
        "model_id": model_id,
        "model_variant": PROVENANCE["target_model_tokenizer"]["model_variant"],
        "tokenizer_id": tokenizer_id,
        "tokenizer_local_path": tokenizer_path,
        "tokenizer_json_sha256": tokenizer_sha,
        "tokenizer_config_json_sha256": PROVENANCE["target_model_tokenizer"]["tokenizer_config_json_sha256"],
        "chat_template_sha256_utf8": chat_template_sha,
        "engine_specific_thinking_flag": "unset",
        "prompt_protocol": "Official TIGER-AI-Lab/MMLU-Pro local CoT prompt, exact frozen prompt text per question, one user message, no prompt mutation",
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "official_evaluator_context_length": OFFICIAL_CONTEXT,
        "serving_context_length_expected": SERVING_CONTEXT_EXPECTED,
        "serving_context_length_cli": served_context,
        "context_difference": "Official local evaluator uses max_model_length=4096 and max_new_tokens=2048; serving topology is configured for 8192. Offline AutoTokenizer preflight renders the exact one-user-message chat request with add_generation_prompt=true. The template prefix is included in prompt token count and 2048 generated tokens are reserved; no truncation or shot removal is allowed.",
        "preflight_method": "offline pinned Hugging Face AutoTokenizer from local files; no tokenize HTTP route",
        "dataset_manifest_sha256": sha256_bytes(CORPUS_MANIFEST.read_bytes()),
        "screen_corpus_sha256": manifest["screen_jsonl_sha256"],
        "question_count": len(corpus),
        "request_retries": 0,
        "engine_concurrency": 1,
        "auth_mode": "none" if not os.environ.get("MMLU_LOCAL_API_KEY") else "bearer from environment; secret is never saved",
        "requests": [],
    }
    atomic_json(outdir / "run.json", run)
    return outdir, run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Loopback base URL, e.g. http://127.0.0.1:30000/v1")
    parser.add_argument("--model-id", required=True, help="Exact served model identifier")
    parser.add_argument("--tokenizer-id", required=True, help="Exact model tokenizer identifier")
    parser.add_argument("--tokenizer-path", required=True, help="Local directory with the exact pinned tokenizer files; no hub lookup")
    parser.add_argument("--tokenizer-json-sha256", default=PROVENANCE["target_model_tokenizer"]["tokenizer_json_sha256"])
    parser.add_argument("--chat-template-sha256", default=PROVENANCE["target_model_tokenizer"]["chat_template_sha256_utf8"])
    parser.add_argument("--served-context-length", type=int, default=SERVING_CONTEXT_EXPECTED)
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    base = require_loopback(args.base_url)
    api_key = os.environ.get("MMLU_LOCAL_API_KEY")
    tokenizer_path = Path(args.tokenizer_path).expanduser().resolve()
    tokenizer = load_pinned_tokenizer(tokenizer_path, args.tokenizer_json_sha256,
                                      PROVENANCE["target_model_tokenizer"]["tokenizer_config_json_sha256"],
                                      args.chat_template_sha256)
    outdir, run = make_run(base, args.model_id, args.tokenizer_id, str(tokenizer_path), args.tokenizer_json_sha256,
                           args.chat_template_sha256, args.served_context_length, args.run_name)
    responses_path = outdir / "responses.jsonl"
    preflight_path = outdir / "preflight.jsonl"
    prompts = load_jsonl(CORPUS)
    preflight_errors = 0
    unfit_ids = []
    print(f"Run {args.run_name}: preflighting {len(prompts)} prompts; no generation starts until all pass.", flush=True)

    # The pinned Rust gateway's /v1/tokenize is not a chat-template preflight;
    # use the exact local tokenizer and exact chat messages instead.
    for item in prompts:
        messages = [{"role": "user", "content": item["prompt"]}]
        request_body = {"model": args.model_id, "messages": messages}
        row = {"question_id": item["question_id"], "category": item["category"],
               "prompt_sha256": item["prompt_sha256"], "request": request_body,
               "status": "ERROR", "request_id": None}
        try:
            tokens = tokenize_wire_messages(tokenizer, messages)
            count = len(tokens)
            fits_official = count < (OFFICIAL_CONTEXT - MAX_OUTPUT_TOKENS)
            fits_serving = count + MAX_OUTPUT_TOKENS <= args.served_context_length
            row.update({"status": "OK", "preflight_method": "offline AutoTokenizer",
                        "prompt_tokens_including_chat_template": count,
                        "token_ids_sha256": sha256_bytes(json.dumps(tokens, separators=(",", ":")).encode()),
                        "fits_official_local_4096_context": fits_official,
                        "fits_expected_serving_context_with_2048_output": fits_serving})
            if not fits_official or not fits_serving:
                row["status"] = "UNFIT"
                unfit_ids.append(item["question_id"])
        except Exception as exc:
            preflight_errors += 1
            row.update({"status": "ERROR", "error_type": type(exc).__name__, "error": str(exc)[:2000]})
        append_jsonl(preflight_path, row)
        run["requests"].append({"question_id": item["question_id"], "preflight_status": row["status"],
                                "prompt_sha256": item["prompt_sha256"],
                                "prompt_tokens": row.get("prompt_tokens_including_chat_template"),
                                "token_ids_sha256": row.get("token_ids_sha256")})
        atomic_json(outdir / "run.json", run)

    run["preflight_request_errors"] = preflight_errors
    run["unfit_question_ids"] = unfit_ids
    run["preflight_passed"] = preflight_errors == 0 and not unfit_ids and len(run["requests"]) == 128
    if not run["preflight_passed"]:
        run["status"] = "INCOMPLETE_PREFLIGHT"
        run["generation_started"] = False
        run["finished_utc"] = datetime.now(timezone.utc).isoformat()
        run["decision"] = "No generation requests were sent. Tokenization errors or context limits make this screen ineligible; no prompts or shots were truncated or changed."
        atomic_json(outdir / "run.json", run)
        print(json.dumps({"status": run["status"], "preflight_errors": preflight_errors, "unfit_question_ids": unfit_ids}, indent=2))
        return 2

    run["status"] = "RUNNING"
    run["generation_started"] = True
    run["preflight_passed"] = True
    atomic_json(outdir / "run.json", run)
    counts = {"correct": 0, "incorrect": 0, "invalid": 0, "request_errors": 0, "truncated": 0}
    print("Preflight passed. Starting sequential generation; no automatic retries.", flush=True)
    for index, item in enumerate(prompts, start=1):
        body = {
            "model": args.model_id,
            "messages": [{"role": "user", "content": item["prompt"]}],
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "max_tokens": MAX_OUTPUT_TOKENS,
            "stream": False,
        }
        started = time.monotonic()
        record = {"question_id": item["question_id"], "category": item["category"],
                  "prompt_sha256": item["prompt_sha256"], "answer_key": item["answer"],
                  "status": "ERROR", "request_id": None, "response_text": None, "parsed_letter": None,
                  "correct": False, "finish_reason": None, "usage": None}
        try:
            response = post_json(endpoint(base, "/chat/completions"), body, args.timeout, api_key)
            result = response["json"]
            choices = result.get("choices")
            if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
                raise ValueError("completion response must contain exactly one choice")
            text = choices[0].get("message", {}).get("content")
            if not isinstance(text, str):
                raise ValueError("completion response has no string message.content")
            parsed = strict_answer(text)
            finish = choices[0].get("finish_reason")
            is_correct = parsed is not None and parsed == item["answer"]
            record.update({"status": "OK", "request_id": response["http_request_id"] or result.get("id"),
                           "http_request_id": response["http_request_id"],
                           "completion_id": result.get("id"),
                           "raw_response_json": response["body_bytes"].decode("utf-8", "replace"),
                           "request_payload_sha256": sha256_bytes(json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")),
                           "response_text": text, "parsed_letter": parsed, "correct": is_correct,
                           "finish_reason": finish, "usage": result.get("usage"),
                           "latency_seconds": time.monotonic() - started,
                           "invalid_response": parsed is None,
                           "truncated": finish == "length"})
            counts["correct" if is_correct else "incorrect"] += 1
            counts["invalid"] += int(parsed is None)
            counts["truncated"] += int(finish == "length")
        except urllib.error.HTTPError as exc:
            body_bytes = exc.read()
            record.update({"http_request_id": exc.headers.get("x-request-id"), "status": "HTTP_ERROR",
                           "http_status": exc.code, "error_body": body_bytes.decode("utf-8", "replace")[:4000],
                           "latency_seconds": time.monotonic() - started})
            counts["request_errors"] += 1
            counts["incorrect"] += 1
        except Exception as exc:
            record.update({"status": "REQUEST_ERROR", "error_type": type(exc).__name__,
                           "error": str(exc)[:2000], "latency_seconds": time.monotonic() - started})
            counts["request_errors"] += 1
            counts["incorrect"] += 1
        append_jsonl(responses_path, record)
        run["completed_requests"] = index
        run["counts_so_far"] = counts.copy()
        run["last_http_request_id"] = record.get("http_request_id")
        run["last_completion_id"] = record.get("completion_id")
        atomic_json(outdir / "run.json", run)
        print(f"{index}/128 qid={item['question_id']} status={record['status']} parsed={record['parsed_letter']} correct={record['correct']}", flush=True)

    all_responses = load_jsonl(responses_path)
    counts["denominator"] = 128
    counts["accuracy"] = counts["correct"] / 128
    summary = {
        "status": "COMPLETE",
        "run_name": args.run_name,
        "model_id": args.model_id,
        "tokenizer_id": args.tokenizer_id,
        "tokenizer_json_sha256": args.tokenizer_json_sha256,
        "chat_template_sha256_utf8": args.chat_template_sha256,
        "screen_corpus_sha256": run["screen_corpus_sha256"],
        "dataset_manifest_sha256": run["dataset_manifest_sha256"],
        "question_ids": [r["question_id"] for r in all_responses],
        "counts": counts,
        "all_128_responses_present_once": len(all_responses) == 128 and len({r["question_id"] for r in all_responses}) == 128,
        "invalid_and_request_errors_are_incorrect": True,
        "automatic_retries": 0,
        "official_full_set_accuracy_certificate": False,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    atomic_json(outdir / "summary.json", summary)
    run["status"] = "COMPLETE"
    run["finished_utc"] = summary["finished_utc"]
    run["counts"] = counts
    atomic_json(outdir / "run.json", run)
    print(json.dumps({"status": "COMPLETE", "counts": counts, "request_errors": counts["request_errors"], "invalid": counts["invalid"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
