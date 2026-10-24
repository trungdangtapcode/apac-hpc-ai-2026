"""CPU semantic-pair and exact 1600-ID head-gate fixtures."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import warmup_semantic

O = Path(__file__).resolve().parent
results = []

with tempfile.TemporaryDirectory(prefix="eagle3-r4-semantic ") as temporary:
    root = Path(temporary)
    endpoints = root / "endpoints.tsv"
    endpoints.write_text(
        "prefill-0\thttp://127.0.0.1:30100\t9000\n"
        "prefill-1\thttp://127.0.0.1:30101\t9001\n"
        "decode-0\thttp://127.0.0.1:30200\t0\n")
    inventory_hash, pairs, rows = warmup_semantic.inventory(endpoints)
    assert len(pairs) == 2 and set(rows) == {"prefill-0", "prefill-1", "decode-0"}
    receipts = root / "receipts"
    receipts.mkdir()
    token = "a" * 32
    response = {"choices": [{"message": {"role": "assistant", "content": "hello"}}],
                "usage": {"prompt_tokens": 7, "completion_tokens": 2, "total_tokens": 9}}
    for pair in pairs:
        warmup_semantic.write_receipt(receipts, endpoints, token, pair, 200, response)
    checked = warmup_semantic.check(receipts, endpoints, token)
    assert checked["pair_count"] == 2 and checked["inventory_sha256"] == inventory_hash
    results.append({"case": "semantic_receipts_replay_both_expected_pd_routes", "passed": True})
    bad_response = dict(response)
    bad_response["usage"] = dict(response["usage"], total_tokens=99)
    try:
        warmup_semantic.validate_response(200, bad_response)
    except ValueError:
        pass
    else:
        raise AssertionError("contradictory token usage accepted")
    results.append({"case": "semantic_control_rejects_contradictory_response", "passed": True})

# Rebuild the actual head input from the accepted H100 target-control reference.
reference = json.loads((O / "target-reference.json").read_text())
corpus = json.loads((O / "prepared-corpus.json").read_text())
candidate = {"passed": True, "platform": "H100", "cases": reference["cases"],
             "target_identity_sha256": reference["target_identity_sha256"], "stages": {}}
for dst, src in (("draft-a", "target-a"), ("draft-b", "target-b")):
    candidate["stages"][dst] = []
    for row in reference["stages"][src]:
        candidate["stages"][dst].append({"name": row["name"], "request": row["request"],
                                          "response": row["response"], "observed": row["observed"]})
assert len(candidate["stages"]["draft-a"]) + len(candidate["stages"]["draft-b"]) == 8
assert sum(len(row["observed"]["output_ids"]) for stage in candidate["stages"].values() for row in stage) == 1600
with tempfile.TemporaryDirectory(prefix="eagle3-r4-head ") as temporary:
    path = Path(temporary) / "token-control.json"
    path.write_text(json.dumps(candidate))
    good = subprocess.run([sys.executable, str(O / "check-token-result.py"), str(path)],
                          text=True, capture_output=True, timeout=15)
    assert good.returncode == 0, (good.returncode, good.stdout, good.stderr)
    mutated = json.loads(path.read_text())
    mutated["stages"]["draft-a"][0]["observed"]["output_ids"][0] ^= 1
    path.write_text(json.dumps(mutated))
    bad = subprocess.run([sys.executable, str(O / "check-token-result.py"), str(path)],
                         text=True, capture_output=True, timeout=15)
    assert bad.returncode != 0, "head gate accepted one changed actual output ID"
results.append({"case": "existing_h100_reference_control_accepts_1600_ids_and_rejects_mutation", "passed": True})

(O / "semantic-head-validation.json").write_text(json.dumps({
    "passed": True, "cases": results,
    "scope": "Stdlib CPU semantic-receipt replay and existing accepted H100 output-reference head gate; no model/GPU/network.",
    "limits": ["Fixtures do not establish runtime native transfer or completion.",
               "The accepted reference remains the control; no H100 candidate output is fabricated."]
}, indent=2) + "\n")
print("R4 semantic and exact-ID head fixtures PASS:", len(results))
