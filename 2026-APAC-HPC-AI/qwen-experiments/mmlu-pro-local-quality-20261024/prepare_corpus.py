#!/usr/bin/env python3
"""Freeze a deterministic 128-question screen from the official MMLU-Pro parquet files."""
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "dataset"
SOURCE = DATA / "source"
SEED = 2026
TEST_ROWS = 12032
VALIDATION_ROWS = 70
SHOTS = 5
CHOICES = "ABCDEFGHIJ"
EXPECTED_SOURCE_SHA256 = {
    "test-00000-of-00001.parquet": "0e24a191921c2f453518a537a8b2117bd137e7714d4ef1565e9ba06c1ecb9ad8",
    "validation-00000-of-00001.parquet": "139423c23722e480c807ac4a191409a710cfce4eba744c1d641cf88e730e2078",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def jsonl_bytes(rows: list[dict]) -> bytes:
    return b"".join(
        (json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        for row in rows
    )


def clean_row(row: dict, row_index: int) -> dict:
    options = [option for option in row["options"] if option != "N/A"]
    if not 2 <= len(options) <= 10:
        raise ValueError(f"question {row['question_id']} has invalid option count {len(options)}")
    answer = row["answer"]
    if answer not in CHOICES[: len(options)]:
        raise ValueError(f"question {row['question_id']} answer {answer!r} is not an available choice")
    return {
        "question_id": int(row["question_id"]),
        "row_index": row_index,
        "category": row["category"],
        "question": row["question"],
        "options": options,
        "answer": answer,
        "answer_index": int(row["answer_index"]),
        "cot_content": row["cot_content"],
        "src": row["src"],
    }


def format_example(example: dict, including_answer: bool) -> str:
    text = "Question:\n" + example["question"] + "\nOptions:\n"
    for i, option in enumerate(example["options"]):
        text += f"{CHOICES[i]}. {option}\n"
    if including_answer:
        cot = example["cot_content"].replace(
            "A: Let's think step by step.", "Answer: Let's think step by step."
        )
        text += cot + "\n\n"
    else:
        text += "Answer: Let's think step by step."
    return text


def build_prompt(category: str, demonstrations: list[dict], question: dict, initial_prompt: str) -> str:
    prompt = initial_prompt.replace("{$}", category) + "\n"
    for example in demonstrations:
        prompt += format_example(example, including_answer=True)
    prompt += format_example(question, including_answer=False)
    return prompt


def main() -> None:
    try:
        import pyarrow
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SystemExit("Preparation requires PyArrow 19.0.1 in a temporary CPU-only environment") from exc
    if pyarrow.__version__ != "19.0.1":
        raise SystemExit(f"Expected PyArrow 19.0.1, got {pyarrow.__version__}")

    source_records = {}
    tables = {}
    for filename, expected_rows in (("test-00000-of-00001.parquet", TEST_ROWS),
                                    ("validation-00000-of-00001.parquet", VALIDATION_ROWS)):
        path = SOURCE / filename
        digest = sha256(path)
        expected = EXPECTED_SOURCE_SHA256[filename]
        if expected and digest != expected:
            raise SystemExit(f"Dataset hash mismatch for {filename}: {digest}")
        table = pq.read_table(path)
        if table.num_rows != expected_rows:
            raise SystemExit(f"Unexpected {filename} row count: {table.num_rows}")
        tables[filename] = table.to_pylist()
        source_records[filename] = {"bytes": path.stat().st_size, "sha256": digest, "rows": expected_rows}

    test = [clean_row(row, i) for i, row in enumerate(tables["test-00000-of-00001.parquet"])]
    validation = [clean_row(row, i) for i, row in enumerate(tables["validation-00000-of-00001.parquet"])]
    categories = sorted({row["category"] for row in test})
    if len(categories) != 14 or sorted({row["category"] for row in validation}) != categories:
        raise SystemExit("Expected the same 14 categories in test and validation")
    validation_groups = {category: [r for r in validation if r["category"] == category] for category in categories}
    if any(len(rows) != SHOTS for rows in validation_groups.values()):
        raise SystemExit("Dataset does not have exactly five validation examples per category")
    if len({row["question_id"] for row in test}) != TEST_ROWS:
        raise SystemExit("Test question IDs are not unique")

    # 9 questions per category (126), then two categories receive one extra.
    # Seed selects the extra categories; each category has an independent stable
    # seed for shuffling its original parquet order.
    extras = set(random.Random(SEED).sample(categories, TEST_ROWS_SCREEN % len(categories)))
    quotas = {category: BASE_PER_CATEGORY + int(category in extras) for category in categories}
    grouped = {category: [row for row in test if row["category"] == category] for category in categories}
    selected = []
    for index, category in enumerate(categories):
        rows = list(grouped[category])
        random.Random(SEED + index).shuffle(rows)
        selected.extend(rows[: quotas[category]])

    initial_prompt_path = ROOT / "upstream/initial_prompt.txt"
    initial_prompt = initial_prompt_path.read_text(encoding="utf-8")
    demos_out = []
    demo_map = {}
    for category in categories:
        demo_map[category] = validation_groups[category]
        for row in validation_groups[category]:
            demos_out.append(row)
    prompts_out = []
    for question in selected:
        prompt_text = build_prompt(question["category"], demo_map[question["category"]], question, initial_prompt)
        prompts_out.append({
            "question_id": question["question_id"],
            "test_row_index": question["row_index"],
            "category": question["category"],
            "question": question["question"],
            "options": question["options"],
            "answer": question["answer"],
            "answer_index": question["answer_index"],
            "prompt": prompt_text,
            "prompt_sha256": hashlib.sha256(prompt_text.encode("utf-8")).hexdigest(),
        })

    demo_path = DATA / "validation-5-per-category.jsonl"
    prompt_path = DATA / "screen-128.jsonl"
    demo_path.write_bytes(jsonl_bytes(demos_out))
    prompt_path.write_bytes(jsonl_bytes(prompts_out))
    manifest = {
        "dataset_repo": "TIGER-Lab/MMLU-Pro",
        "dataset_revision": "b189ec765aa7ed75c8acfea42df31fdae71f97be",
        "config": "default",
        "test_split": "test",
        "validation_split": "validation",
        "selection_seed": SEED,
        "selection_method": "14-category stratified sample: base 9 per category; 2 extra categories selected with random.Random(2026).sample(sorted_categories, 2); rows shuffled by random.Random(2026 + category_index) and taken from that category's dataset-order rows",
        "n_test": TEST_ROWS_SCREEN,
        "n_validation_demos": len(demos_out),
        "shots_per_category": SHOTS,
        "category_quotas": quotas,
        "categories": categories,
        "test_rows_in_source": TEST_ROWS,
        "validation_rows_in_source": VALIDATION_ROWS,
        "dataset_license": "MIT",
        "source_files": source_records,
        "validation_fewshot_ids_by_category": {c: [r["question_id"] for r in demo_map[c]] for c in categories},
        "selected_test_ids_by_category": {c: [r["question_id"] for r in prompts_out if r["category"] == c] for c in categories},
        "initial_prompt_sha256": sha256(initial_prompt_path),
        "validation_jsonl_sha256": hashlib.sha256(demo_path.read_bytes()).hexdigest(),
        "screen_jsonl_sha256": hashlib.sha256(prompt_path.read_bytes()).hexdigest(),
        "pyarrow_version": pyarrow.__version__,
        "preparation_python": "3.9.25",
    }
    manifest_path = DATA / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Prepared {len(prompts_out)} questions across {len(categories)} categories; validation shots={len(demos_out)}")
    print("Category quotas:", json.dumps(quotas, sort_keys=True))
    print("Manifest SHA-256:", sha256(manifest_path))


BASE_PER_CATEGORY = 9
TEST_ROWS_SCREEN = 128

if __name__ == "__main__":
    main()
