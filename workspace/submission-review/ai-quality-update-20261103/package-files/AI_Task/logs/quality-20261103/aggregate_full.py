#!/usr/bin/env python3
"""Merge full-set MMLU-Pro shards from two independent local deployments."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PINNED_GENERATION = {"temperature": 0.0, "top_p": 1.0, "max_tokens": 2048,
                     "stop": ["Question:"], "stream": False}
CHOICES = "ABCDEFGHIJ"
ANSWER_IS = re.compile(r"answer is \(?([A-J])\)?")
ANSWER_COLON = re.compile(r".*[aA]nswer:\s*([A-J])")
FINAL_LETTER = re.compile(r"\b[A-J]\b(?!.*\b[A-J]\b)", re.DOTALL)


def parse_pinned(text: str) -> str | None:
    """Pinned MMLU-Pro regex order; invalid answer is incorrect, never guessed."""
    match = ANSWER_IS.search(text)
    if match:
        return match.group(1)
    match = ANSWER_COLON.search(text)
    if match:
        return match.group(1)
    match = FINAL_LETTER.search(text)
    return match.group(0) if match else None


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    out = []
    with path.open(encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if line.strip():
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{n}: invalid JSONL") from exc
    return out


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    with tmp.open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def validate_prepared(prep_path: Path, corpus_path: Path,
                      expected_count: int = 12032) -> tuple[dict[int, dict[str, Any]], str, str]:
    prep = read_json(prep_path)
    corpus_sha = file_sha(corpus_path)
    prep_sha = file_sha(prep_path)
    if prep.get("status") != "READY" or prep.get("generation_blocked"):
        raise ValueError("prepared manifest is not READY or marks generation blocked")
    if prep.get("compiled_corpus_sha256") != corpus_sha:
        raise ValueError("compiled corpus SHA-256 differs from prepared manifest")
    if int(prep.get("question_count", -1)) != expected_count:
        raise ValueError(f"prepared manifest question_count is not expected full-set size {expected_count}")
    compiled = read_jsonl(corpus_path)
    if len(compiled) != expected_count:
        raise ValueError(f"compiled corpus contains {len(compiled)} records; expected {expected_count}")
    by_id: dict[int, dict[str, Any]] = {}
    for row in compiled:
        qid = int(row["question_id"])
        if qid in by_id:
            raise ValueError(f"duplicate question ID {qid} in compiled corpus")
        if row.get("preparation_status") != "READY":
            raise ValueError(f"question {qid} is not preparation-ready")
        for key in ("prompt_sha256", "token_ids_sha256", "shots_used", "expected_answer", "category"):
            if key not in row:
                raise ValueError(f"compiled question {qid} has no {key}")
        by_id[qid] = row
    return by_id, corpus_sha, prep_sha


def _protocol_check(run: dict[str, Any], expected_corpus_sha: str,
                    expected_prep_sha: str) -> None:
    if run.get("status") != "COMPLETE":
        raise ValueError(f"source run is not COMPLETE: {run.get('status')}")
    if run.get("corpus_sha256") != expected_corpus_sha:
        raise ValueError("source run corpus hash differs from the prepared full corpus")
    if run.get("prepare_manifest_sha256") != expected_prep_sha:
        raise ValueError("source run prepared-manifest hash differs")
    if run.get("generation") != PINNED_GENERATION:
        raise ValueError("source run generation settings differ from the pinned local protocol")


def aggregate_role(run_dirs: list[Path], expected: dict[int, dict[str, Any]],
                   corpus_sha: str, prep_sha: str) -> dict[str, Any]:
    if not run_dirs:
        raise ValueError("each role needs at least one completed run/shard")
    selected_seen: set[int] = set()
    response_by_id: dict[int, dict[str, Any]] = {}
    source_runs = []
    role_protocol: dict[str, Any] | None = None
    served_models: set[str] = set()
    for run_dir in run_dirs:
        run_json = run_dir / "run.json"
        responses_jsonl = run_dir / "responses.jsonl"
        run = read_json(run_json)
        _protocol_check(run, corpus_sha, prep_sha)
        if role_protocol is None:
            role_protocol = run["generation"]
        elif run["generation"] != role_protocol:
            raise ValueError(f"generation mismatch among shards for {run_dir}")
        claimed = [int(x) for x in run.get("selected_question_ids", [])]
        if not claimed or len(claimed) != int(run.get("selected_count", -1)) or len(set(claimed)) != len(claimed):
            raise ValueError(f"invalid selected-question ID list in {run_dir}")
        overlap = selected_seen.intersection(claimed)
        if overlap:
            raise ValueError(f"overlapping source shards in {run_dir}: {sorted(overlap)[:12]}")
        unknown = set(claimed) - set(expected)
        if unknown:
            raise ValueError(f"source run claims IDs outside compiled corpus: {sorted(unknown)[:12]}")
        selected_seen.update(claimed)
        records = read_jsonl(responses_jsonl)
        got_ids = [int(r["question_id"]) for r in records]
        if len(got_ids) != len(claimed) or len(set(got_ids)) != len(got_ids) or set(got_ids) != set(claimed):
            raise ValueError(f"responses do not contain exactly one first response per selected ID in {run_dir}")
        for record in records:
            qid = int(record["question_id"])
            source = expected[qid]
            for key in ("prompt_sha256", "token_ids_sha256", "shots_used", "expected_answer", "category"):
                if record.get(key) != source.get(key):
                    raise ValueError(f"{run_dir}: question {qid} {key} differs from compiled corpus")
            if qid in response_by_id:
                raise ValueError(f"overlapping response ID {qid}")
            response_by_id[qid] = record
        model = str(run.get("served_model") or "unspecified")
        served_models.add(model)
        source_runs.append({
            "run_dir": str(run_dir.resolve()), "base_url": run.get("base_url"), "served_model": model,
            "run_json_sha256": file_sha(run_json), "responses_jsonl_sha256": file_sha(responses_jsonl),
            "source_selected_ids": claimed, "source_selected_count": len(claimed),
            "status": run["status"],
        })
    missing = sorted(set(expected) - selected_seen)
    extra = sorted(selected_seen - set(expected))
    if missing or extra:
        raise ValueError(f"role does not cover exact full question set: missing={missing[:20]}, extra={extra[:20]}")
    if set(response_by_id) != set(expected):
        raise ValueError("response coverage does not exactly match the prepared full corpus")

    categories: dict[str, dict[str, Any]] = {}
    mutable: dict[str, dict[str, int]] = defaultdict(lambda: {
        "n": 0, "correct": 0, "errors": 0, "invalid_outputs": 0, "truncated_outputs": 0})
    correct_by_id: dict[int, bool] = {}
    invalid = truncated = errors = correct = 0
    for qid, source in expected.items():
        response = response_by_id[qid]
        category = source["category"]
        stat = mutable[category]
        stat["n"] += 1
        raw = response.get("raw_response_body")
        payload = None
        if isinstance(raw, str):
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = None
        choices = payload.get("choices") if isinstance(payload, dict) else None
        content = None
        finish_reason = None
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            message = choices[0].get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                content = message["content"]
                finish_reason = choices[0].get("finish_reason")
        http_status = response.get("http_status")
        status_ok = (response.get("status") == "OK" and isinstance(http_status, int)
                     and 200 <= http_status < 300 and content is not None)
        predicted = parse_pinned(content) if status_ok else None
        if status_ok:
            if response.get("completion_text") != content:
                raise ValueError(f"question {qid}: stored completion differs from raw response body")
            if response.get("predicted_answer") != predicted:
                raise ValueError(f"question {qid}: stored parsed answer differs from pinned parser on raw body")
            if "finish_reason" in response and response.get("finish_reason") != finish_reason:
                raise ValueError(f"question {qid}: stored finish reason differs from raw response body")
        is_correct = bool(status_ok and isinstance(predicted, str) and predicted in CHOICES
                           and predicted == source["expected_answer"])
        correct_by_id[qid] = is_correct
        if is_correct:
            correct += 1
            stat["correct"] += 1
        if not status_ok:
            errors += 1
            stat["errors"] += 1
        if status_ok and (not isinstance(predicted, str) or predicted not in CHOICES):
            invalid += 1
            stat["invalid_outputs"] += 1
        if status_ok and finish_reason in ("length", "max_tokens"):
            truncated += 1
            stat["truncated_outputs"] += 1
    for category, values in sorted(mutable.items()):
        categories[category] = {**values, "accuracy": values["correct"] / values["n"] if values["n"] else None}
    n = len(expected)
    return {
        "n": n, "correct": correct, "accuracy": correct / n,
        "service_errors": errors, "invalid_outputs": invalid, "truncated_outputs": truncated,
        "categories": categories, "served_models": sorted(served_models),
        "source_runs": source_runs, "correct_by_question_id": correct_by_id,
    }


def compare_roles(reference: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    ref_correct = reference["correct_by_question_id"]
    cand_correct = candidate["correct_by_question_id"]
    if set(ref_correct) != set(cand_correct):
        raise ValueError("reference and candidate ID sets differ")
    discordance = Counter()
    for qid in ref_correct:
        r, c = ref_correct[qid], cand_correct[qid]
        if r and c:
            discordance["both_correct"] += 1
        elif r:
            discordance["reference_only_correct"] += 1
        elif c:
            discordance["candidate_only_correct"] += 1
        else:
            discordance["both_wrong"] += 1
    ratio = candidate["accuracy"] / reference["accuracy"] if reference["accuracy"] > 0 else None
    no_errors = reference["service_errors"] == candidate["service_errors"] == 0
    ratio_gate = ratio is not None and ratio >= 0.99
    return {
        "candidate_to_reference_accuracy_ratio": ratio,
        "candidate_at_least_99_percent_reference_accuracy": ratio_gate,
        "zero_service_errors_both_roles": no_errors,
        "discordances": dict(discordance),
        "local_engineering_gate_pass": bool(ratio_gate and no_errors),
    }


def public_role(value: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in value.items() if k != "correct_by_question_id"}


def aggregate(prep_path: Path, corpus_path: Path, reference_dirs: list[Path],
              candidate_dirs: list[Path], expected_count: int = 12032) -> dict[str, Any]:
    expected, corpus_sha, prep_sha = validate_prepared(prep_path, corpus_path, expected_count)
    reference = aggregate_role(reference_dirs, expected, corpus_sha, prep_sha)
    candidate = aggregate_role(candidate_dirs, expected, corpus_sha, prep_sha)
    result = compare_roles(reference, candidate)
    return {
        "status": "LOCAL_FULLSET_GATE_PASS" if result["local_engineering_gate_pass"] else "LOCAL_FULLSET_GATE_FAIL",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Paired local MMLU-Pro test split; not the organizer's private quality evaluation or BTC certification.",
        "prepared_manifest": {"path": str(prep_path.resolve()), "sha256": prep_sha,
                              "compiled_corpus_path": str(corpus_path.resolve()),
                              "compiled_corpus_sha256": corpus_sha, "question_count": len(expected)},
        "reference": public_role(reference), "candidate": public_role(candidate), "comparison": result,
        "interpretation": "This is a local engineering gate on the exact compiled corpus and supplied independent deployments. It is not proof of an official >=99% BTC quality pass.",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prepare-manifest", required=True)
    p.add_argument("--compiled-corpus", required=True)
    p.add_argument("--reference-runs", required=True, nargs="+", help="completed shard run directories for the FP8 reference deployment")
    p.add_argument("--candidate-runs", required=True, nargs="+", help="completed shard run directories for the exact submitted candidate deployment")
    p.add_argument("--out", required=True, help="new JSON report path; refuses overwrite")
    a = p.parse_args()
    try:
        report = aggregate(Path(a.prepare_manifest), Path(a.compiled_corpus),
                           [Path(x) for x in a.reference_runs],
                           [Path(x) for x in a.candidate_runs])
        out = Path(a.out).expanduser().resolve()
        if out.exists():
            raise FileExistsError(f"refusing to overwrite {out}")
        out.parent.mkdir(parents=True, exist_ok=True)
        atomic_json(out, report)
        print(json.dumps({"report": str(out), "status": report["status"],
                          "reference": {k: report["reference"][k] for k in ("n", "correct", "accuracy", "service_errors", "invalid_outputs", "truncated_outputs")},
                          "candidate": {k: report["candidate"][k] for k in ("n", "correct", "accuracy", "service_errors", "invalid_outputs", "truncated_outputs")},
                          "comparison": report["comparison"]}, indent=2))
        return 0 if report["comparison"]["local_engineering_gate_pass"] else 4
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
