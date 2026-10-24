#!/usr/bin/env python3
"""Compare two complete local screen runs using a predeclared correct-count ratio."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_run(name: str) -> tuple[dict, list[dict]]:
    folder = ROOT / "results" / name
    summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    records = [json.loads(line) for line in (folder / "responses.jsonl").read_text(encoding="utf-8").splitlines() if line]
    return summary, records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", required=True, help="New JSON output path; must not already exist")
    args = parser.parse_args()
    reference, ref_rows = load_run(args.reference)
    candidate, cand_rows = load_run(args.candidate)
    if reference["status"] != "COMPLETE" or candidate["status"] != "COMPLETE":
        raise SystemExit("Both runs must contain complete 128-question responses")
    for summary in (reference, candidate):
        if summary["counts"]["denominator"] != 128 or not summary["all_128_responses_present_once"]:
            raise SystemExit("Run denominator or question coverage is not exactly 128")
    common = ("screen_corpus_sha256", "dataset_manifest_sha256", "tokenizer_json_sha256", "chat_template_sha256_utf8")
    mismatches = {key: [reference.get(key), candidate.get(key)] for key in common if reference.get(key) != candidate.get(key)}
    if mismatches:
        raise SystemExit(f"Paired runs do not use the same corpus/tokenizer/template: {mismatches}")
    ref_by_id = {row["question_id"]: row for row in ref_rows}
    cand_by_id = {row["question_id"]: row for row in cand_rows}
    expected_ids = set(reference["question_ids"])
    if expected_ids != set(candidate["question_ids"]) or expected_ids != set(ref_by_id) or expected_ids != set(cand_by_id):
        raise SystemExit("Paired runs do not contain the same 128 IDs exactly once")
    ref_correct = int(reference["counts"]["correct"])
    cand_correct = int(candidate["counts"]["correct"])
    ratio = (cand_correct / ref_correct) if ref_correct else None
    errors = int(reference["counts"]["request_errors"]) + int(candidate["counts"]["request_errors"])
    paired_both = sum(ref_by_id[qid]["correct"] and cand_by_id[qid]["correct"] for qid in expected_ids)
    candidate_only = sum(cand_by_id[qid]["correct"] and not ref_by_id[qid]["correct"] for qid in expected_ids)
    reference_only = sum(ref_by_id[qid]["correct"] and not cand_by_id[qid]["correct"] for qid in expected_ids)
    qualifies = ratio is not None and ratio >= 0.99 and errors == 0
    result = {
        "reference_run": args.reference,
        "candidate_run": args.candidate,
        "corpus_sha256": reference["screen_corpus_sha256"],
        "denominator_per_run": 128,
        "reference_correct_count": ref_correct,
        "candidate_correct_count": cand_correct,
        "candidate_over_reference_correct_count_ratio": ratio,
        "paired_both_correct": paired_both,
        "candidate_only_correct": candidate_only,
        "reference_only_correct": reference_only,
        "combined_request_errors": errors,
        "predeclared_ratio_gate": 0.99,
        "predeclared_error_gate": 0,
        "local_screen_gate_pass": qualifies,
        "statistical_scope": "This 128-question matched local screen is a triage gate only; it cannot establish at least 99% official full-set benchmark accuracy.",
    }
    out = Path(args.output)
    if out.exists():
        raise SystemExit(f"Refusing to overwrite {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if qualifies else 1


if __name__ == "__main__":
    raise SystemExit(main())
