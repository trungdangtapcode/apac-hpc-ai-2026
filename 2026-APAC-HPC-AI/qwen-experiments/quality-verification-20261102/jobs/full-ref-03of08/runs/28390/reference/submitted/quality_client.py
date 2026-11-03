#!/usr/bin/env python3
"""Prepare and score a reproducible local MMLU-Pro quality comparison.

This is an engineering check, not the competition's undisclosed official score.
Only the standard library is needed for run/compare; prepare additionally needs
Transformers and the exact local tokenizer files pinned in source-provenance.json.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
PROV_PATH = EXP.parent / "mmlu-pro-local-quality-20261024" / "source-provenance.json"
PROVENANCE = json.loads(PROV_PATH.read_text(encoding="utf-8"))
UPSTREAM = EXP.parent / "mmlu-pro-local-quality-20261024" / "upstream" / "evaluate_from_local.py"
CHOICES = "ABCDEFGHIJ"
ANSWER_IS = re.compile(r"answer is \(?([A-J])\)?")
ANSWER_COLON = re.compile(r".*[aA]nswer:\s*([A-J])")
FINAL_LETTER = re.compile(r"\b[A-J]\b(?!.*\b[A-J]\b)", re.DOTALL)
MAX_OUTPUT = 2048


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())


def atomic_json(path: Path, obj: dict[str, Any]) -> None:
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    with tmp.open("x", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def official_parse(text: str | None) -> tuple[str | None, str]:
    """Pinned upstream regex order, but invalid stays wrong (no random guess)."""
    if not text:
        return None, "invalid_empty"
    m = ANSWER_IS.search(text)
    if m:
        return m.group(1), "answer_is"
    m = ANSWER_COLON.search(text)
    if m:
        return m.group(1), "answer_colon"
    m = FINAL_LETTER.search(text)
    if m:
        return m.group(0), "final_standalone_letter"
    return None, "invalid_unparsed"


def strict_parse(text: str | None) -> str | None:
    """Secondary diagnostic only; never substituted for the primary score."""
    if not text:
        return None
    matches = list(re.finditer(r"(?i)\bthe answer is\s*\(([A-J])\)", text))
    if len(matches) != 1 or text[matches[0].end():].strip(" *\t\r\n.!`"):
        return None
    return matches[0].group(1).upper()


def format_example(row: dict[str, Any], including_answer: bool) -> str:
    text = "Question:\n" + row["question"] + "\nOptions:\n"
    for i, option in enumerate(row["options"]):
        text += f"{CHOICES[i]}. {option}\n"
    if including_answer:
        cot = row["cot_content"].replace("A: Let's think step by step.", "Answer: Let's think step by step.")
        text += cot + "\n\n"
    else:
        text += "Answer: Let's think step by step."
    return text


def prompt_for(row: dict[str, Any], demos: list[dict[str, Any]], initial: str, shots: int) -> str:
    prompt = initial.replace("{$}", row["category"]) + "\n"
    for demo in demos[:shots]:
        prompt += format_example(demo, True)
    prompt += format_example(row, False)
    return prompt


def load_tokenizer(path: Path):
    pin = PROVENANCE["target_model_tokenizer"]
    for name, key in (("tokenizer.json", "tokenizer_json_sha256"),
                      ("tokenizer_config.json", "tokenizer_config_json_sha256")):
        p = path / name
        if not p.is_file() or file_sha(p) != pin[key]:
            raise ValueError(f"{p} missing or not the tokenizer file pinned by source-provenance.json")
    config = json.loads((path / "tokenizer_config.json").read_text(encoding="utf-8"))
    template = config.get("chat_template")
    if not isinstance(template, str) or sha(template.encode()) != pin["chat_template_sha256_utf8"]:
        raise ValueError("local chat_template differs from pinned SHA-256")
    try:
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise RuntimeError("prepare requires Transformers available in the CPU runtime") from exc
    tok = AutoTokenizer.from_pretrained(str(path), local_files_only=True, trust_remote_code=False)
    if tok.chat_template != template:
        raise ValueError("loaded tokenizer chat template does not match pinned config")
    return tok


def tokenize(tok: Any, prompt: str) -> list[int]:
    rendered = tok.apply_chat_template([{"role": "user", "content": prompt}],
                                      tokenize=True, add_generation_prompt=True,
                                      return_dict=False)
    # Transformers versions differ in whether chat-template calls default to a
    # BatchEncoding. We request the documented list form above; if a compatible
    # implementation still returns a mapping, accept only explicit input_ids.
    # Never flatten arbitrary batch shapes because that would corrupt token/hash
    # counts without being visible in the prepared manifest.
    if isinstance(rendered, Mapping):
        if "input_ids" not in rendered:
            raise ValueError("tokenizer mapping result has no input_ids key")
        ids = rendered["input_ids"]
    else:
        ids = rendered
    if hasattr(ids, "tolist"):
        ids = ids.tolist()
    if isinstance(ids, tuple):
        ids = list(ids)
    if isinstance(ids, list) and ids and isinstance(ids[0], (list, tuple)):
        if len(ids) != 1:
            raise ValueError(f"tokenizer returned a batch of {len(ids)} sequences for one prompt")
        ids = list(ids[0])
    if not isinstance(ids, list) or any(type(x) is not int for x in ids):
        raise ValueError("tokenizer returned invalid token IDs")
    return ids


def cmd_prepare(a: argparse.Namespace) -> int:
    if a.max_context <= a.max_output_tokens or a.max_output_tokens <= 0:
        raise ValueError("max-context must exceed positive max-output-tokens")
    source = Path(a.corpus)
    validation_path = Path(a.validation)
    corpus = read_jsonl(source)
    validation = read_jsonl(validation_path)
    expected_n = int(a.expected_rows)
    ids = [r["question_id"] for r in corpus]
    if len(corpus) != expected_n or len(set(ids)) != len(ids):
        raise ValueError(f"corpus must contain {expected_n} rows with unique question_id")
    if len(validation) != 70:
        raise ValueError("validation file must contain the pinned 70 rows")
    corpus_manifest_path = source.parent / "manifest.json"
    corpus_manifest = json.loads(corpus_manifest_path.read_text(encoding="utf-8"))
    if len(corpus) != int(corpus_manifest["counts"]["test_prompts"]):
        raise ValueError("corpus row count differs from its frozen manifest")
    if source.name in corpus_manifest["outputs"] and file_sha(source) != corpus_manifest["outputs"][source.name]["sha256"]:
        raise ValueError("input corpus differs from the SHA-256 in its frozen manifest")
    actual_manifest_sha = file_sha(corpus_manifest_path)
    if a.corpus_manifest_sha256 and actual_manifest_sha != a.corpus_manifest_sha256:
        raise ValueError("corpus manifest SHA mismatch")
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in validation:
        by_category[r["category"]].append(r)
    for category in by_category:
        by_category[category].sort(key=lambda x: x["category_shot_rank"])
        if [x["category_shot_rank"] for x in by_category[category]] != [1, 2, 3, 4, 5]:
            raise ValueError(f"validation shots for {category} are not the pinned ordered five")
    initial_path = EXP / "corpus-tools" / "initial_prompt.txt"
    initial = initial_path.read_text(encoding="utf-8")
    if sha(initial.encode()) != PROVENANCE["official_evaluation_code"]["files"]["cot_prompt_lib/initial_prompt.txt"]:
        raise ValueError("initial prompt does not match pinned official evaluator")
    if any(not isinstance(r.get("cot_content"), str) for r in validation):
        raise ValueError("validation rows are missing pinned CoT demonstration text")
    tok_path = Path(a.tokenizer_path).expanduser().resolve()
    tok = load_tokenizer(tok_path)
    prompt_limit = a.max_context - a.max_output_tokens
    strict_limit = a.strict_prompt_lt
    if strict_limit is not None:
        prompt_limit = min(prompt_limit, strict_limit - 1)
    compiled, pilot_ids, unfit = [], [], []
    screen_ids = None
    if a.screen_corpus:
        screen = read_jsonl(Path(a.screen_corpus))
        if len(screen) != 128 or len({x["question_id"] for x in screen}) != 128:
            raise ValueError("pilot source must be the exact 128-question historical screen")
        screen_ids = [x["question_id"] for x in screen]
    for row in corpus:
        demos = by_category[row["category"]]
        expected_demo_ids = [d["question_id"] for d in demos]
        if row.get("validation_fewshot_ids") != expected_demo_ids:
            raise ValueError(f"question {row['question_id']} demo IDs differ from pinned category/source order")
        original = prompt_for(row, demos, initial, 5)
        if original != row.get("prompt") or sha(original.encode()) != row.get("prompt_sha256"):
            raise ValueError(f"question {row['question_id']} five-shot prompt differs from frozen source")
        chosen = None
        for k in range(5, -1, -1):
            text = prompt_for(row, demos, initial, k)
            token_ids = tokenize(tok, text)
            if len(token_ids) <= prompt_limit:
                chosen = (k, text, token_ids)
                break
        status = "READY" if chosen else "UNFIT_ZERO_SHOT"
        if chosen is None:
            unfit.append(row["question_id"])
            k, text, token_ids = 0, prompt_for(row, demos, initial, 0), tokenize(tok, prompt_for(row, demos, initial, 0))
        else:
            k, text, token_ids = chosen
        psha = sha(text.encode())
        messages = [{"role": "user", "content": text}]
        compiled.append({
            "question_id": row["question_id"], "source_row_index": row.get("source_row_index"),
            "category": row["category"], "expected_answer": row["answer"],
            "prompt": text, "messages": messages, "prompt_sha256": psha,
            "prompt_tokens": len(token_ids),
            "token_ids_sha256": sha(json.dumps(token_ids, separators=(",", ":")).encode()),
            "shots_used": k, "validation_fewshot_ids": [d["question_id"] for d in demos[:k]],
            "preparation_status": status,
        })
        if screen_ids is not None and row["question_id"] in set(screen_ids):
            pilot_ids.append(row["question_id"])
    if len(set(pilot_ids)) != 128 if screen_ids is not None else False:
        raise ValueError("historical pilot IDs do not all join to full corpus")
    if unfit and not a.allow_unfit:
        raise ValueError(f"{len(unfit)} rows remain unfit at zero shots; refusing generation corpus; first IDs={unfit[:12]}")
    out = Path(a.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=False)
    compiled_path = out / "compiled-corpus.jsonl"
    write_jsonl(compiled_path, compiled)
    if screen_ids is not None:
        atomic_json(out / "pilot-ids.json", {"source": str(Path(a.screen_corpus).resolve()), "selection": "exact historical 128 IDs in historical screen order", "question_ids": screen_ids})
    manifest = {
        "status": "READY" if not unfit else "UNFIT_ROWS_PRESENT_GENERATION_BLOCKED",
        "purpose": "Local quality comparison; not official BTC certification",
        "dataset_manifest_sha256": actual_manifest_sha,
        "input_corpus": str(source.resolve()), "input_corpus_sha256": file_sha(source),
        "input_validation_sha256": file_sha(validation_path),
        "compiled_corpus_sha256": file_sha(compiled_path), "question_count": len(compiled),
        "unique_question_ids": len(set(ids)), "pilot_count": len(pilot_ids),
        "tokenizer_model_id": PROVENANCE["target_model_tokenizer"]["model_id"],
        "tokenizer_revision": PROVENANCE["target_model_tokenizer"]["revision"],
        "tokenizer_json_sha256": PROVENANCE["target_model_tokenizer"]["tokenizer_json_sha256"],
        "tokenizer_config_json_sha256": PROVENANCE["target_model_tokenizer"]["tokenizer_config_json_sha256"],
        "chat_template_sha256": PROVENANCE["target_model_tokenizer"]["chat_template_sha256_utf8"],
        "tokenizer_local_path": str(tok_path), "max_context": a.max_context,
        "max_output_tokens": a.max_output_tokens, "prompt_token_limit_inclusive": prompt_limit,
        "strict_prompt_lt": strict_limit, "shots_rule": "adaptive first 5, then 4..0; preserve full target question and choices; first k same-category validation rows in source order",
        "shot_counts": dict(sorted(Counter(r["shots_used"] for r in compiled).items())),
        "unfit_question_ids": unfit, "generation_blocked": bool(unfit),
        "prompt_wrapper": "one user message rendered by pinned Qwen chat template with add_generation_prompt=true",
        "official_source_commit": PROVENANCE["official_evaluation_code"]["revision"],
        "official_context_reference": "upstream evaluator uses strict prompt_length < 4096 - 2048; strict_prompt_lt=2048 recreates that prompt budget",
        "quality_claim": "No model quality result or official pass is claimed by corpus preparation.",
    }
    atomic_json(out / "prepare-manifest.json", manifest)
    print(json.dumps({"status": manifest["status"], "compiled": str(compiled_path), "questions": len(compiled), "pilot_ids": len(pilot_ids), "unfit": len(unfit), "shots": manifest["shot_counts"]}, indent=2))
    return 2 if unfit else 0


def endpoint(base: str) -> str:
    u = urllib.parse.urlparse(base)
    if u.scheme not in ("http", "https") or not u.hostname or not u.path.rstrip("/").endswith("/v1"):
        raise ValueError("base URL must be an HTTP(S) OpenAI-compatible /v1 URL")
    return base.rstrip("/") + "/chat/completions"


def post_request(url: str, body: dict[str, Any], timeout: float, api_key: str | None) -> tuple[int | None, str, dict[str, Any] | None]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    req = urllib.request.Request(url, data=json.dumps(body, ensure_ascii=False).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = None
            return resp.status, raw, parsed
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return exc.code, raw, None


def summarize_records(records: list[dict[str, Any]], expected_ids: list[int]) -> dict[str, Any]:
    by_id: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        by_id[int(r["question_id"])].append(r)
    missing = [qid for qid in expected_ids if not by_id.get(qid)]
    duplicate = sorted(qid for qid, rows in by_id.items() if len(rows) != 1)
    correct = 0
    service_errors = 0
    category_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0, "errors": 0})
    for qid in expected_ids:
        rows = by_id.get(qid, [])
        row = rows[0] if len(rows) == 1 else None
        cat = (row or {}).get("category", "unknown")
        cc = category_counts[cat]
        cc["n"] += 1
        if row is None or row.get("status") != "OK":
            service_errors += 1
            cc["errors"] += 1
            continue
        ok = row.get("predicted_answer") == row.get("expected_answer") and row.get("predicted_answer") in CHOICES
        if ok:
            correct += 1
            cc["correct"] += 1
    n = len(expected_ids)
    return {"denominator": n, "correct": correct, "accuracy": correct / n if n else None,
            "service_errors_in_denominator": service_errors, "missing_ids": missing,
            "duplicate_ids": duplicate, "extra_ids": sorted(set(by_id) - set(expected_ids)),
            "coverage_complete": not missing and not duplicate and not (set(by_id) - set(expected_ids)),
            "categories": {k: {**v, "accuracy": v["correct"] / v["n"] if v["n"] else None} for k, v in sorted(category_counts.items())}}


def cmd_run(a: argparse.Namespace) -> int:
    if not a.prepare_manifest:
        raise ValueError("--prepare-manifest is required to bind run to tokenizer and corpus provenance")
    corpus_path = Path(a.corpus)
    rows = read_jsonl(corpus_path)
    ids = [int(x["question_id"]) for x in rows]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("compiled corpus must have unique question IDs")
    if any(x.get("preparation_status") != "READY" for x in rows):
        raise ValueError("compiled corpus has unfit rows; generation is prohibited")
    prep_doc = json.loads(Path(a.prepare_manifest).read_text(encoding="utf-8"))
    if prep_doc.get("status") != "READY" or prep_doc.get("generation_blocked"):
        raise ValueError("prepare manifest is not generation-ready")
    if prep_doc.get("compiled_corpus_sha256") != file_sha(corpus_path):
        raise ValueError("compiled corpus SHA-256 differs from prepare manifest")
    if prep_doc.get("question_count") != len(rows):
        raise ValueError("prepared question count differs from prepare manifest")
    if a.ids_file:
        id_doc = json.loads(Path(a.ids_file).read_text(encoding="utf-8"))
        selected = [int(x) for x in id_doc["question_ids"]]
        if not selected or len(set(selected)) != len(selected) or not set(selected) <= set(ids):
            raise ValueError("ids-file must contain unique IDs present in compiled corpus")
    elif a.shard_count:
        if a.shard_count < 1 or not 0 <= a.shard_index < a.shard_count:
            raise ValueError("invalid stable shard index/count")
        selected = [qid for i, qid in enumerate(ids) if i % a.shard_count == a.shard_index]
    else:
        selected = ids
    by_id = {int(x["question_id"]): x for x in rows}
    selected_rows = [by_id[qid] for qid in selected]
    # Any one run is an immutable, new output namespace.
    out = Path(a.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=False)
    base_url = a.base_url.rstrip("/")
    url = endpoint(base_url)
    deadline = float(a.deadline_epoch) if a.deadline_epoch is not None else None
    api_key = os.environ.get(a.api_key_env) if a.api_key_env else None
    cfg = {
        "status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url, "served_model": a.model, "corpus_sha256": file_sha(corpus_path),
        "prepare_manifest_sha256": file_sha(Path(a.prepare_manifest)) if a.prepare_manifest else None,
        "prepare_protocol": {k: prep_doc.get(k) for k in (
            "dataset_manifest_sha256", "tokenizer_model_id", "tokenizer_revision",
            "tokenizer_json_sha256", "tokenizer_config_json_sha256", "chat_template_sha256",
            "max_context", "max_output_tokens", "prompt_token_limit_inclusive", "strict_prompt_lt",
            "compiled_corpus_sha256", "shots_rule")},
        "selected_question_ids": selected, "selected_count": len(selected),
        "selection": "explicit IDs" if a.ids_file else (f"stable order modulo {a.shard_count}, shard {a.shard_index}" if a.shard_count else "all corpus rows in frozen order"),
        "generation": {"temperature": 0.0, "top_p": 1.0, "max_tokens": MAX_OUTPUT, "stop": ["Question:"], "stream": False},
        "concurrency": a.concurrency, "timeout_seconds": a.timeout,
        "deadline_epoch": deadline, "deadline_safety_seconds": a.deadline_margin,
        "request_retries": 0, "parser": "pinned TIGER-AI-Lab/MMLU-Pro regex order at f418b116db00b065c2aea046518d8fcf74d39872; invalid -> incorrect (random guessing disabled)",
        "response_file": "responses.jsonl", "auth_mode": "bearer from environment" if api_key else "none",
        "quality_claim": "Local engineering comparison only; not official BTC certification.",
    }
    atomic_json(out / "run.json", cfg)
    responses_path = out / "responses.jsonl"
    write_lock = threading.Lock()
    completed = 0
    stop_new = threading.Event()
    progress_correct = 0
    progress_errors = 0
    progress_by_category: dict[str, dict[str, int]] = defaultdict(lambda: {"completed": 0, "correct": 0, "errors": 0})

    def worker(row: dict[str, Any]) -> dict[str, Any]:
        nonlocal completed, progress_correct, progress_errors
        qid = int(row["question_id"])
        start_wall = time.time()
        record = {"question_id": qid, "category": row["category"],
                  "expected_answer": row["expected_answer"], "prompt_sha256": row["prompt_sha256"],
                  "token_ids_sha256": row["token_ids_sha256"], "shots_used": row["shots_used"],
                  "status": "ERROR", "error": None, "http_status": None,
                  "raw_response_body": None, "completion_text": None,
                  "predicted_answer": None, "parse_method": None, "strict_answer": None,
                  "usage": None, "finish_reason": None, "request_id": None,
                  "latency_seconds": None}
        if (deadline is not None and time.time() + a.timeout + a.deadline_margin >= deadline) or stop_new.is_set():
            record.update(status="NOT_STARTED_DEADLINE", error="not started: deadline safety window")
        else:
            body = {"model": a.model, "messages": row["messages"], "temperature": 0.0,
                    "top_p": 1.0, "max_tokens": MAX_OUTPUT, "stop": ["Question:"], "stream": False}
            try:
                status, raw, parsed = post_request(url, body, a.timeout, api_key)
                record["http_status"] = status
                record["raw_response_body"] = raw
                if parsed is None or not 200 <= int(status or 0) < 300:
                    record["error"] = "HTTP error or invalid JSON response"
                else:
                    record["request_id"] = parsed.get("id")
                    choices = parsed.get("choices") or []
                    if not choices or not isinstance(choices[0].get("message", {}).get("content"), str):
                        record["error"] = "response missing choices[0].message.content"
                    else:
                        text = choices[0]["message"]["content"]
                        pred, method = official_parse(text)
                        record.update(status="OK", completion_text=text, predicted_answer=pred,
                                      parse_method=method, strict_answer=strict_parse(text),
                                      usage=parsed.get("usage"), finish_reason=choices[0].get("finish_reason"))
            except Exception as exc:  # service/network error is retained and wrong in the denominator
                record["error"] = f"{type(exc).__name__}: {str(exc)[:1000]}"
            record["latency_seconds"] = round(time.time() - start_wall, 6)
            if record["status"] != "OK" and deadline is not None and time.time() + a.timeout + a.deadline_margin >= deadline:
                stop_new.set()
        with write_lock:
            with responses_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())
            completed += 1
            cat_progress = progress_by_category[record["category"]]
            cat_progress["completed"] += 1
            if record["status"] != "OK":
                progress_errors += 1
                cat_progress["errors"] += 1
            elif record.get("predicted_answer") == record.get("expected_answer") and record.get("predicted_answer") in CHOICES:
                progress_correct += 1
                cat_progress["correct"] += 1
            cfg.update({"completed_records": completed, "progress_fraction": completed / len(selected),
                        "progress_denominator": len(selected), "progress_correct": progress_correct,
                        "progress_accuracy_over_fixed_denominator": progress_correct / len(selected),
                        "progress_service_errors": progress_errors,
                        "progress_by_category": {k: dict(v) for k, v in sorted(progress_by_category.items())},
                        "updated_utc": datetime.now(timezone.utc).isoformat()})
            atomic_json(out / "run.json", cfg)
        return record

    # Submit all tasks to bounded executor; worker enforces deadline before any HTTP call.
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.concurrency) as pool:
        futures = [pool.submit(worker, row) for row in selected_rows]
        for future in concurrent.futures.as_completed(futures):
            future.result()
    records = read_jsonl(responses_path)
    summary = summarize_records(records, selected)
    not_started = sum(r.get("status") == "NOT_STARTED_DEADLINE" for r in records)
    complete = (summary["coverage_complete"] and not summary["missing_ids"]
                and len(records) == len(selected) and not_started == 0)
    cfg.update({"status": "COMPLETE" if complete else "INCOMPLETE", "finished_utc": datetime.now(timezone.utc).isoformat(),
                "summary": summary, "all_selected_ids_have_one_record": summary["coverage_complete"]})
    atomic_json(out / "run.json", cfg)
    atomic_json(out / "summary.json", {"status": cfg["status"], **summary,
                                      "not_started_deadline_records": not_started,
                                      "local_quality_gate_zero_service_errors": summary["service_errors_in_denominator"] == 0,
                                      "official_btc_certification": False})
    print(json.dumps({"run": str(out), "status": cfg["status"], **summary}, indent=2))
    return 0 if complete else 3


def load_run(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    run = json.loads((path / "run.json").read_text(encoding="utf-8"))
    return run, read_jsonl(path / "responses.jsonl")


def compare_compatible(ref: dict[str, Any], cand: dict[str, Any],
                       ref_records: list[dict[str, Any]], cand_records: list[dict[str, Any]]) -> list[str]:
    errors = []
    for field in ("corpus_sha256", "generation", "selected_question_ids", "selected_count"):
        if ref.get(field) != cand.get(field):
            errors.append(f"run mismatch: {field}")
    # Same compiled corpus pins each prompt and tokenizer. Distinct servers and model roles are expected.
    if ref.get("prepare_manifest_sha256") != cand.get("prepare_manifest_sha256"):
        errors.append("run mismatch: prepare_manifest_sha256")
    if ref.get("status") != "COMPLETE" or cand.get("status") != "COMPLETE":
        errors.append("both runs must have COMPLETE run status")
    expected_generation = {"temperature": 0.0, "top_p": 1.0, "max_tokens": 2048,
                          "stop": ["Question:"], "stream": False}
    if ref.get("generation") != expected_generation or cand.get("generation") != expected_generation:
        errors.append("generation settings do not match the pinned local comparison protocol")
    rb = {int(x["question_id"]): x for x in ref_records}
    cb = {int(x["question_id"]): x for x in cand_records}
    for qid in set(rb) & set(cb):
        for key in ("prompt_sha256", "token_ids_sha256", "shots_used", "expected_answer", "category"):
            if rb[qid].get(key) != cb[qid].get(key):
                errors.append(f"paired record {qid} differs in {key}")
                break
    return errors


def cmd_compare(a: argparse.Namespace) -> int:
    ref_path, cand_path = Path(a.reference), Path(a.candidate)
    ref_run, rr = load_run(ref_path)
    cand_run, cr = load_run(cand_path)
    compatibility = compare_compatible(ref_run, cand_run, rr, cr)
    ids = ref_run.get("selected_question_ids", [])
    rs, cs = summarize_records(rr, ids), summarize_records(cr, ids)
    ratio = (cs["accuracy"] / rs["accuracy"]) if rs["accuracy"] else None
    ref_by = {int(r["question_id"]): r for r in rr}
    cand_by = {int(r["question_id"]): r for r in cr}
    discord = Counter()
    for qid in ids:
        x, y = ref_by.get(qid), cand_by.get(qid)
        if not x or not y:
            discord["missing"] += 1
        elif x.get("status") != "OK" or y.get("status") != "OK":
            discord["service_error_pair"] += 1
        else:
            r_ok = x.get("predicted_answer") == x.get("expected_answer")
            c_ok = y.get("predicted_answer") == y.get("expected_answer")
            if r_ok and c_ok: discord["both_correct"] += 1
            elif r_ok: discord["reference_only_correct"] += 1
            elif c_ok: discord["candidate_only_correct"] += 1
            else: discord["both_wrong"] += 1
    gates = {
        "compatible_matched_runs": not compatibility,
        "exact_complete_coverage_both": rs["coverage_complete"] and cs["coverage_complete"] and not rs["missing_ids"] and not cs["missing_ids"],
        "zero_service_errors_both": rs["service_errors_in_denominator"] == 0 and cs["service_errors_in_denominator"] == 0,
        "candidate_at_least_99_percent_reference": ratio is not None and ratio >= 0.99,
    }
    report = {
        "status": "LOCAL_GATE_PASS" if all(gates.values()) else "LOCAL_GATE_FAIL_OR_INCOMPLETE",
        "purpose": "Matched local engineering comparison only; not a BTC-issued quality score or official certification.",
        "reference": {"run_dir": str(ref_path.resolve()), "served_model": ref_run.get("served_model"), **rs},
        "candidate": {"run_dir": str(cand_path.resolve()), "served_model": cand_run.get("served_model"), **cs},
        "candidate_to_reference_accuracy_ratio": ratio,
        "candidate_retains_at_least_99_percent_reference_accuracy": gates["candidate_at_least_99_percent_reference"],
        "discordances": dict(discord), "compatibility_errors": compatibility,
        "gates": gates, "official_btc_certification": False,
        "interpretation": "A pass is evidence only for this pinned local corpus, prompt, tokenizer, sampling configuration and selected endpoint runs. It is not proof against an unpublished organizer suite/reference."}
    if a.out:
        out = Path(a.out).resolve()
        if out.exists(): raise FileExistsError(f"refusing to overwrite {out}")
        out.parent.mkdir(parents=True, exist_ok=True)
        atomic_json(out, report)
    print(json.dumps(report, indent=2))
    return 0 if all(gates.values()) else 4


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("prepare", help="CPU-only exact-tokenizer prompt fit and deterministic pilot")
    q.add_argument("--corpus", required=True); q.add_argument("--validation", required=True)
    q.add_argument("--screen-corpus"); q.add_argument("--tokenizer-path", required=True)
    q.add_argument("--out", required=True); q.add_argument("--expected-rows", type=int, default=12032)
    q.add_argument("--max-context", type=int, default=4096); q.add_argument("--max-output-tokens", type=int, default=2048)
    q.add_argument("--strict-prompt-lt", type=int, default=None, help="set 2048 to reproduce upstream strict prompt <2048 limit")
    q.add_argument("--corpus-manifest-sha256", help="optional asserted corpus-tools/manifest.json SHA-256")
    q.add_argument("--allow-unfit", action="store_true", help="write inspection artifact only; run command still blocks it")
    q.set_defaults(func=cmd_prepare)
    q = sub.add_parser("run", help="bounded concurrent OpenAI-compatible chat evaluation")
    q.add_argument("--corpus", required=True); q.add_argument("--prepare-manifest")
    q.add_argument("--base-url", required=True); q.add_argument("--model", default="qwen")
    q.add_argument("--out", required=True); q.add_argument("--concurrency", type=int, default=16)
    q.add_argument("--timeout", type=float, default=120); q.add_argument("--deadline-epoch", type=float)
    q.add_argument("--deadline-margin", type=float, default=120)
    q.add_argument("--ids-file"); q.add_argument("--shard-index", type=int, default=0); q.add_argument("--shard-count", type=int, default=0)
    q.add_argument("--api-key-env", help="read bearer key from env without persisting it")
    q.set_defaults(func=cmd_run)
    q = sub.add_parser("compare", help="validate exact paired coverage and compute ratio gate")
    q.add_argument("reference"); q.add_argument("candidate"); q.add_argument("--out")
    q.set_defaults(func=cmd_compare)
    a = p.parse_args()
    if getattr(a, "concurrency", 1) < 1: p.error("concurrency must be positive")
    try:
        return a.func(a)
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
