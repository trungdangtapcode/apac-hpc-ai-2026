#!/usr/bin/env python3
"""Compare reported API prompt lengths with frozen CPU preparation, without GPU work."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def records(path):
    # Iterate file records: str.splitlines() also splits legal Unicode characters
    # inside JSON strings and is therefore unsafe for this corpus.
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evaluation-dirs", nargs="+", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    corpus = ROOT / "prepared-4k/compiled-corpus.jsonl"
    prepared = {r["question_id"]: r for r in records(corpus)}
    results = []
    for evaluation in a.evaluation_dirs:
        run = json.loads((evaluation / "run.json").read_text())
        differences, missing, examples, ids = Counter(), [], [], []
        responses = evaluation / "responses.jsonl"
        for r in records(responses):
            qid = r["question_id"]
            ids.append(qid)
            expected = prepared[qid]["prompt_tokens"]
            reported = (r.get("usage") or {}).get("prompt_tokens")
            if not isinstance(reported, int):
                missing.append(qid)
            else:
                differences[reported - expected] += 1
                if reported != expected and len(examples) < 10:
                    examples.append(dict(question_id=qid, prepared=expected, reported=reported))
        complete = (run.get("status") == "COMPLETE" and len(ids) == run["selected_count"]
                    and len(set(ids)) == len(ids) and set(ids) == set(run["selected_question_ids"]))
        passed = complete and not missing and dict(differences) == {0: len(ids)}
        results.append(dict(evaluation_dir=str(evaluation.resolve()), passed=passed,
                            complete=complete, response_count=len(ids),
                            reported_minus_prepared_counts=dict(differences),
                            missing_usage_ids=missing, difference_examples=examples,
                            responses_sha256=digest(responses)))
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                  passed=all(r["passed"] for r in results),
                  corpus_sha256=digest(corpus), runs=results,
                  total_response_records=sum(r["response_count"] for r in results),
                  limit="Checks reported lengths only; exact server input token IDs were not collected.")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(json.dumps({k: report[k] for k in ("passed", "total_response_records", "limit")}))
    raise SystemExit(0 if report["passed"] else 2)
