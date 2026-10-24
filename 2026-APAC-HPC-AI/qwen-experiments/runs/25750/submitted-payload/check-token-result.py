#!/usr/bin/env python3
"""Head-process semantic gate. A remote task's exit code is insufficient."""
import hashlib
import json
import os
import sys
from pathlib import Path

from asset_identity import verify_asset_identity
from token_observation import observed

root = Path(__file__).resolve().parent
result_path = Path(sys.argv[1])
model_path = Path(sys.argv[2])
result = json.loads(result_path.read_text())
corpus = json.loads((root / "prepared-corpus.json").read_text())
image_path = os.environ.get("QWEN_IMAGE_PATH")
assert image_path, "QWEN_IMAGE_PATH is required for independent asset identity verification"
verified_identity = verify_asset_identity(root / "asset-verification.json", model_path, image_path)
assert result["schema"] == "h200-target-reference-v1" and result["passed"] is True
assert result["platform"] == "H200" and result["cases"] == corpus["cases"]
assert result["corpus_sha256"] == hashlib.sha256((root / "prepared-corpus.json").read_bytes()).hexdigest()
assert len(corpus["cases"]) == 4
assert len(next(c["input_ids"] for c in corpus["cases"] if c["name"] == "long4000")) == 4000
assert set(result["stages"]) == {"target-a", "target-b"}
assert result["asset_identity"] == verified_identity
for stage in ("target-a", "target-b"):
    rows = result["stages"][stage]
    assert len(rows) == 4
    for case, row in zip(corpus["cases"], rows):
        assert row["name"] == case["name"]
        assert row["request"] == {
            "input_ids": case["input_ids"], "stream": False, "return_logprob": True,
            "logprob_start_len": -1, "return_text_in_logprobs": False,
            "sampling_params": {"temperature": 0.0, "top_p": 1.0, "sampling_seed": 2026,
                                 "max_new_tokens": 200, "ignore_eos": True}}
        assert row["observed"] == observed(row["response"], len(case["input_ids"]))
for a, b in zip(result["stages"]["target-a"], result["stages"]["target-b"]):
    assert a["request"] == b["request"] and a["observed"] == b["observed"]
assert sum(len(row["observed"]["output_ids"]) for stage in result["stages"].values() for row in stage) == 1600
assert len(result["comparisons"]) == 4
assert all(c["exact_ids_and_finish_equal"] for c in result["comparisons"])
print("H200_TARGET_REFERENCE_SEMANTIC_GATE_PASSED")
