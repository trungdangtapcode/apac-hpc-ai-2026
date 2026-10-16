#!/usr/bin/env python3
"""Offline comparison of native SGLang greedy /generate captures. No model/network."""
import argparse
import hashlib
import json
from pathlib import Path

TARGET_REVISION = "e156cb4efae43fbee1a1ab073f946a1377e6b969"
NEUTRAL = {"temperature": 0, "top_k": 1, "top_p": 1, "min_p": 0,
           "repetition_penalty": 1, "frequency_penalty": 0, "presence_penalty": 0,
           "n": 1}
SAMPLING_KEYS = set(NEUTRAL) | {"max_new_tokens", "min_new_tokens", "ignore_eos",
    "stop", "stop_token_ids", "skip_special_tokens", "no_stop_trim"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def token_ids(value, label, allow_empty=False):
    require(isinstance(value, list) and (allow_empty or len(value) > 0),
            label + " must be a nonempty list")
    require(all(type(t) is int and t >= 0 for t in value), label + " has invalid token IDs")


def validate(capture):
    require(isinstance(capture, dict), "capture must be an object")
    require(capture.get("schema") == 1, "unsupported capture schema")
    require(capture.get("target_revision") == TARGET_REVISION, "wrong/missing target revision")
    tokenizer_hash = capture.get("tokenizer_sha256", "")
    require(isinstance(tokenizer_hash, str) and len(tokenizer_hash) == 64 and
            all(c in "0123456789abcdef" for c in tokenizer_hash), "missing tokenizer SHA256")
    cases = capture.get("cases")
    require(isinstance(cases, list) and len(cases) > 0, "empty/missing cases")
    indexed = {}
    for case in cases:
        require(isinstance(case, dict), "case must be an object")
        name = case.get("case_id")
        require(isinstance(name, str) and name and name not in indexed, "duplicate/missing case_id")
        req, resp = case.get("request"), case.get("response")
        require(isinstance(req, dict) and isinstance(resp, dict), name + ": missing request/response")
        require(set(req) == {"input_ids", "sampling_params", "stream", "return_prompt_token_ids"},
                name + ": request must use explicit native token-input contract")
        require(req["stream"] is False and req["return_prompt_token_ids"] is True,
                name + ": require nonstreaming and prompt-token capture")
        token_ids(req["input_ids"], name + ": input_ids")
        params = req["sampling_params"]
        require(isinstance(params, dict) and not (set(params) - SAMPLING_KEYS),
                name + ": unsupported sampling/grammar settings")
        require(all(type(params.get(k)) in (int, float) and params[k] == v
                    for k, v in NEUTRAL.items()), name + ": non-greedy/non-neutral settings")
        maximum = params.get("max_new_tokens")
        require(type(maximum) is int and maximum > 0, name + ": invalid max_new_tokens")
        require(type(params.get("min_new_tokens")) is int and
                0 <= params["min_new_tokens"] <= maximum, name + ": invalid min_new_tokens")
        for key in ("ignore_eos", "skip_special_tokens", "no_stop_trim"):
            require(type(params.get(key)) is bool, name + ": missing boolean " + key)
        require(params.get("stop") in (None, []) and params.get("stop_token_ids") in (None, []),
                name + ": initial contract uses EOS/length only, no custom stops")
        require("error" not in resp, name + ": response error")
        token_ids(resp.get("output_ids"), name + ": output_ids")
        token_ids(resp.get("prompt_token_ids"), name + ": prompt_token_ids")
        require(resp["prompt_token_ids"] == req["input_ids"], name + ": prompt IDs changed")
        meta = resp.get("meta_info")
        require(isinstance(meta, dict), name + ": missing meta_info")
        require(type(meta.get("completion_tokens")) is int and
                meta["completion_tokens"] == len(resp["output_ids"]),
                name + ": completion/token length mismatch; investigate capture")
        require(type(meta.get("prompt_tokens")) is int and
                meta["prompt_tokens"] == len(req["input_ids"]), name + ": prompt count mismatch")
        reason = meta.get("finish_reason")
        require(isinstance(reason, dict) and reason.get("type") in ("stop", "length"),
                name + ": missing/aborted/unsupported finish reason")
        size = len(resp["output_ids"])
        require(params["min_new_tokens"] <= size <= maximum, name + ": invalid generated length")
        require(reason["type"] != "length" or size == maximum, name + ": premature length finish")
        indexed[name] = case
    return indexed


def compare(control, candidate):
    left, right = validate(control), validate(candidate)
    require(control["tokenizer_sha256"] == candidate["tokenizer_sha256"], "tokenizer hashes differ")
    require(left.keys() == right.keys(), "case sets differ")
    results = []
    for name in sorted(left):
        a, b = left[name], right[name]
        require(a["request"] == b["request"], name + ": requests differ")
        x, y = a["response"]["output_ids"], b["response"]["output_ids"]
        first = next((i for i in range(min(len(x), len(y))) if x[i] != y[i]), None)
        if first is None and len(x) != len(y):
            first = min(len(x), len(y))
        finish_equal = a["response"]["meta_info"]["finish_reason"] == b["response"]["meta_info"]["finish_reason"]
        results.append({"case_id": name, "control_tokens": len(x), "candidate_tokens": len(y),
                        "token_ids_equal": x == y, "finish_reason_equal": finish_equal,
                        "first_difference_index": first,
                        "control_token": x[first] if first is not None and first < len(x) else None,
                        "candidate_token": y[first] if first is not None and first < len(y) else None})
    passed = all(r["token_ids_equal"] and r["finish_reason_equal"] for r in results)
    return {"state": "CAPTURED_CASES_MATCH" if passed else "CAPTURED_CASES_DIFFER",
            "case_count": len(results), "cases": results,
            "limits": ["Only the supplied cases and declared provenance are compared; runtime/image/env must be audited separately.",
                       "No organiser accuracy, stochastic equivalence, performance or job submission gate is certified.",
                       "Keep raw IDs including EOS; never reconstruct IDs from decoded text or discard mismatch tails."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("control", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    require(not args.out.exists(), "output exists; preserve old evidence")
    inputs = {}
    try:
        captures = []
        for role, path in (("control", args.control), ("candidate", args.candidate)):
            raw = path.read_bytes()
            inputs[role] = {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}
            captures.append(json.loads(raw))
        report = compare(*captures)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        report = {"state": "INVALID_OR_INCOMPLETE_CAPTURE", "error": str(exc)}
    report["inputs"] = inputs
    with args.out.open("x") as output:
        json.dump(report, output, ensure_ascii=False, indent=2, allow_nan=False)
        output.write("\n")
    print(report["state"])
    return {"CAPTURED_CASES_MATCH": 0, "CAPTURED_CASES_DIFFER": 1}.get(report["state"], 2)


if __name__ == "__main__":
    raise SystemExit(main())
