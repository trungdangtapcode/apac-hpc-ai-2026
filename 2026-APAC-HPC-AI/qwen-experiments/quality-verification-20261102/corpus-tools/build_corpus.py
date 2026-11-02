#!/usr/bin/env python3
"""Build the complete five-shot MMLU-Pro corpus using the pinned official renderer."""
from __future__ import annotations

import hashlib
import json
import platform
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / "qwen-experiments/mmlu-pro-local-quality-20261024"
SOURCE = OLD / "dataset/source"
UPSTREAM = OLD / "upstream"
TEST_N = 12032
VAL_N = 70
SHOTS = 5
CHOICES = "ABCDEFGHIJKLMNOP"
DATASET_REVISION = "b189ec765aa7ed75c8acfea42df31fdae71f97be"
UPSTREAM_COMMIT = "f418b116db00b065c2aea046518d8fcf74d39872"
EXPECTED = {
    "test-00000-of-00001.parquet": (4144185, "0e24a191921c2f453518a537a8b2117bd137e7714d4ef1565e9ba06c1ecb9ad8", TEST_N),
    "validation-00000-of-00001.parquet": (42857, "139423c23722e480c807ac4a191409a710cfce4eba744c1d641cf88e730e2078", VAL_N),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def format_cot_example(example: dict, including_answer: bool = True) -> str:
    # Kept byte-for-byte equivalent to the pinned official evaluator function.
    prompt = "Question:\n"
    question = example["question"]
    options = example["options"]
    prompt += question + "\n"
    prompt += "Options:\n"
    for i, opt in enumerate(options):
        prompt += "{}. {}\n".format(CHOICES[i], opt)
    if including_answer:
        cot_content = example["cot_content"].replace(
            "A: Let's think step by step.", "Answer: Let's think step by step."
        )
        prompt += cot_content + "\n\n"
    else:
        prompt += "Answer: Let's think step by step."
    return prompt


def official_five_shot_prompt(initial_prompt: str, category: str,
                              demonstrations: list[dict], question: dict) -> str:
    # Equivalent to official generate_cot_prompt(..., k=5): first five rows of
    # this category in validation source order, then the unanswered test row.
    prompt = initial_prompt.replace("{$}", category) + "\n"
    for example in demonstrations[:SHOTS]:
        prompt += format_cot_example(example, including_answer=True)
    prompt += format_cot_example(question, including_answer=False)
    return prompt


def clean(row: dict, index: int) -> dict:
    options = [x for x in row["options"] if x != "N/A"]
    if not 2 <= len(options) <= 10:
        raise ValueError(f"row {index}, id {row['question_id']}: invalid options={len(options)}")
    if row["answer"] not in CHOICES[:len(options)]:
        raise ValueError(f"row {index}, id {row['question_id']}: answer not represented by options")
    return {
        "question_id": int(row["question_id"]),
        "source_row_index": index,
        "category": row["category"],
        "question": row["question"],
        "options": options,
        "answer": row["answer"],
        "answer_index": int(row["answer_index"]),
        "cot_content": row["cot_content"],
        "src": row["src"],
    }


def jsonl_dump(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def main() -> None:
    if pyarrow.__version__ != "19.0.1":
        raise SystemExit(f"Expected PyArrow 19.0.1, got {pyarrow.__version__}")
    source_info = {}
    data = {}
    for name, (expected_bytes, expected_hash, expected_rows) in EXPECTED.items():
        path = SOURCE / name
        raw = path.read_bytes()
        digest = sha(raw)
        if (len(raw), digest) != (expected_bytes, expected_hash):
            raise SystemExit(f"Pinned source mismatch {name}: bytes={len(raw)}, sha256={digest}")
        table = pq.read_table(path)
        if table.num_rows != expected_rows:
            raise SystemExit(f"Pinned row count mismatch {name}: {table.num_rows}")
        data[name] = [clean(row, i) for i, row in enumerate(table.to_pylist())]
        source_info[name] = {"bytes": len(raw), "sha256": digest, "rows": table.num_rows}

    test = data["test-00000-of-00001.parquet"]
    validation = data["validation-00000-of-00001.parquet"]
    test_ids = [row["question_id"] for row in test]
    val_ids = [row["question_id"] for row in validation]
    if len(set(test_ids)) != TEST_N:
        raise SystemExit("Test question IDs are not unique")
    if len(set(val_ids)) != VAL_N or set(test_ids) & set(val_ids):
        raise SystemExit("Validation IDs are duplicated or overlap test IDs")
    categories = sorted({row["category"] for row in test})
    if len(categories) != 14 or sorted({row["category"] for row in validation}) != categories:
        raise SystemExit("Expected 14 matching categories in test and validation")
    val_by_category = defaultdict(list)
    for row in validation:
        val_by_category[row["category"]].append(row)
    if any(len(val_by_category[c]) != SHOTS for c in categories):
        raise SystemExit("Expected exactly five validation demonstrations in each category")

    initial_path = HERE / "initial_prompt.txt"
    original_initial = "".join((UPSTREAM / "initial_prompt.txt").read_text(encoding="utf-8").splitlines(keepends=True))
    initial = initial_path.read_text(encoding="utf-8")
    if initial != original_initial:
        raise SystemExit("Copied initial prompt differs from pinned upstream source")

    # Store all validation examples once, including answers, so the five-shot
    # provenance and exact source order are auditable. This is local corpus data;
    # it is not sent to an inference endpoint by this builder.
    val_out = []
    for category in categories:
        for rank, row in enumerate(val_by_category[category], start=1):
            val_out.append({**row, "category_shot_rank": rank})
    prompts_out = []
    for row in test:
        demos = val_by_category[row["category"]]
        prompt = official_five_shot_prompt(initial, row["category"], demos, row)
        prompts_out.append({
            "question_id": row["question_id"],
            "source_row_index": row["source_row_index"],
            "category": row["category"],
            "question": row["question"],
            "options": row["options"],
            "answer": row["answer"],
            "answer_index": row["answer_index"],
            "validation_fewshot_ids": [d["question_id"] for d in demos],
            "prompt": prompt,
            "prompt_sha256": sha(prompt.encode("utf-8")),
        })

    val_path = HERE / "validation-70.jsonl"
    test_path = HERE / "test-prompts-12032.jsonl"
    jsonl_dump(val_out, val_path)
    jsonl_dump(prompts_out, test_path)

    # Verify every full prompt against the same renderer and frozen five-shot IDs.
    if len(prompts_out) != TEST_N or len({x["question_id"] for x in prompts_out}) != TEST_N:
        raise SystemExit("Full test prompt set is incomplete or has duplicate IDs")
    for row, built in zip(test, prompts_out):
        expected_prompt = official_five_shot_prompt(initial, row["category"], val_by_category[row["category"]], row)
        if built["prompt"] != expected_prompt or len(built["validation_fewshot_ids"]) != SHOTS:
            raise SystemExit(f"Prompt/shot verification failed for test ID {row['question_id']}")
    if Counter(x["category"] for x in prompts_out) != Counter(x["category"] for x in test):
        raise SystemExit("Test category distribution changed")

    official_script = UPSTREAM / "evaluate_from_local.py"
    manifest = {
        "purpose": "Full local MMLU-Pro test corpus rendered with the pinned official five-shot CoT prompt construction; no inference performed",
        "dataset": {"repo": "TIGER-Lab/MMLU-Pro", "revision": DATASET_REVISION, "config": "default", "license": "MIT", "test_split": "test", "validation_split": "validation", "source_files": source_info},
        "prompt_source": {"repo": "TIGER-AI-Lab/MMLU-Pro", "commit": UPSTREAM_COMMIT, "license": "Apache-2.0", "official_renderer": "evaluate_from_local.py::generate_cot_prompt + format_cot_example", "renderer_sha256": file_sha(official_script), "local_renderer_sha256": file_sha(HERE / "build_corpus.py"), "initial_prompt_sha256": file_sha(initial_path), "shots": 5, "shot_rule": "first five same-category validation rows in original source order; no truncation or shot reduction"},
        "counts": {"test_prompts": len(prompts_out), "unique_test_question_ids": len(set(test_ids)), "validation_rows": len(validation), "unique_validation_ids": len(set(val_ids)), "categories": categories, "test_rows_by_category": dict(sorted(Counter(x["category"] for x in prompts_out).items())), "validation_shots_by_category": dict(sorted(Counter(x["category"] for x in val_out).items()))},
        "runtime": {"python": platform.python_version(), "pyarrow": pyarrow.__version__, "cpu_only": True},
        "outputs": {"test-prompts-12032.jsonl": {"bytes": test_path.stat().st_size, "sha256": file_sha(test_path)}, "validation-70.jsonl": {"bytes": val_path.stat().st_size, "sha256": file_sha(val_path)}, "initial_prompt.txt": {"bytes": initial_path.stat().st_size, "sha256": file_sha(initial_path)}},
        "integrity_checks": ["source byte counts and SHA-256 match frozen manifest", "test has 12,032 rows and unique question IDs", "validation has 70 unique rows and exactly five shots per each of 14 categories", "test and validation IDs are disjoint", "all 12,032 prompts use exactly the first five same-category validation rows in source order", "each prompt exactly matches the pinned official renderer logic", "no truncation or dynamic shot reduction"],
        "not_claimed": ["model quality score", "official contest pass/fail", "tokenizer length fit", "generation feasibility", "inference result"],
    }
    manifest_path = HERE / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "test_rows": len(prompts_out), "unique_ids": len(set(test_ids)), "validation_shots": len(val_out), "categories": len(categories), "test_jsonl_bytes": test_path.stat().st_size, "test_jsonl_sha256": file_sha(test_path), "manifest": str(manifest_path)}, indent=2))


if __name__ == "__main__":
    main()
