#!/usr/bin/env python3
"""Head-process semantic gate. A remote task's exit code is insufficient."""
import hashlib
import json
import sys
from pathlib import Path

from token_observation import observed

root = Path(__file__).resolve().parent
result_path = Path(sys.argv[1])
result = json.loads(result_path.read_text())
corpus = json.loads((root / "prepared-corpus.json").read_text())
assert result["schema"] == "h200-target-reference-v1" and result["passed"] is True
assert result["platform"] == "H200" and result["cases"] == corpus["cases"]
assert result["corpus_sha256"] == hashlib.sha256((root / "prepared-corpus.json").read_bytes()).hexdigest()
assert len(corpus["cases"]) == 4
assert len(next(c["input_ids"] for c in corpus["cases"] if c["name"] == "long4000")) == 4000
assert set(result["stages"]) == {"target-a", "target-b"}
assert result["asset_identity"]["weight_bytes_total"] > 0
assert result["asset_identity"]["container_image_path"]
image_bytes = result["asset_identity"].get("container_image_bytes")
assert image_bytes is None or (type(image_bytes) is int and image_bytes > 0)
assert result["asset_identity"]["large_weight_sha256"].startswith("not_collected")
assert result["asset_identity"]["container_image_sha256"].startswith("not_collected")
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
