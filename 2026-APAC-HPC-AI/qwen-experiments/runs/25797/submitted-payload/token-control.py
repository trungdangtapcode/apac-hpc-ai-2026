#!/usr/bin/env python3
"""Capture two target-only greedy /generate passes as an exact-ID reference."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.request

from token_observation import observed
from asset_identity import verify_asset_identity


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("gateway")
    ap.add_argument("model", type=Path)
    ap.add_argument("artifact", type=Path)
    args = ap.parse_args()
    out = args.artifact / "target-reference.json"
    if out.exists():
        raise FileExistsError(f"refusing to overwrite {out}")
    corpus = json.loads((Path(__file__).parent / "prepared-corpus.json").read_text())
    cases = corpus["cases"]
    assert len(cases) == 4 and len(next(c["input_ids"] for c in cases if c["name"] == "long4000")) == 4000
    result = {
        "schema": "h200-target-reference-v1", "created_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_id": os.environ["QWEN_EXPERIMENT_ID"], "platform": "H200", "passed": False,
        "scope": "Target-only exact token-ID reference; no EAGLE3 candidate, ranked score, or accuracy claim",
        "corpus_sha256": hashlib.sha256((Path(__file__).parent / "prepared-corpus.json").read_bytes()).hexdigest(),
        "cases": cases, "stages": {}, "asset_identity": {},
    }
    try:
        if not args.model.is_dir():
            raise FileNotFoundError(f"model path is not a directory: {args.model}")
        image_path = os.environ.get("QWEN_IMAGE_PATH")
        if not image_path:
            raise ValueError("QWEN_IMAGE_PATH is required for asset identity verification")
        result["asset_identity"] = verify_asset_identity(
            Path(__file__).resolve().parent / "asset-verification.json", args.model, image_path)
        result["stages"] = {"target-a": [], "target-b": []}
        deadline = float(os.environ["QWEN_CLIENT_DEADLINE_EPOCH"])
        for stage in ("target-a", "target-b"):
            for case in cases:
                if time.time() >= deadline:
                    raise TimeoutError("absolute exact-token client deadline exhausted")
                body = {
                    "input_ids": case["input_ids"], "stream": False, "return_logprob": True,
                    "logprob_start_len": -1, "return_text_in_logprobs": False,
                    "sampling_params": {"temperature": 0.0, "top_p": 1.0, "sampling_seed": 2026,
                                        "max_new_tokens": 200, "ignore_eos": True},
                }
                req = urllib.request.Request("http://" + args.gateway + "/generate", json.dumps(body).encode(),
                                             {"Content-Type": "application/json"})
                start = time.monotonic()
                request_timeout = max(0.1, min(45.0, deadline - time.time()))
                with urllib.request.urlopen(req, timeout=request_timeout) as response:
                    if response.status != 200:
                        raise ValueError(f"/generate returned HTTP {response.status}")
                    raw = response.read(2 * 1024 * 1024 + 1)
                if len(raw) > 2 * 1024 * 1024:
                    raise ValueError("response exceeded 2 MiB capture bound")
                payload = json.loads(raw)
                row = {"name": case["name"], "request": body, "response": payload,
                       "elapsed_s": time.monotonic() - start}
                row["observed"] = observed(payload, len(case["input_ids"]))
                result["stages"][stage].append(row)
                out.write_text(json.dumps(result, indent=2) + "\n")
        comparisons = []
        if len(result["stages"]["target-a"]) != 4 or len(result["stages"]["target-b"]) != 4:
            raise ValueError("both target passes must contain all four corpus cases")
        for a, b in zip(result["stages"]["target-a"], result["stages"]["target-b"]):
            comparisons.append({"name": a["name"], "exact_ids_and_finish_equal":
                                a["request"] == b["request"] and a["observed"] == b["observed"]})
        result["comparisons"] = comparisons
        if len(comparisons) != 4 or not all(r["exact_ids_and_finish_equal"] for r in comparisons):
            raise ValueError("two target-only passes differ in request, complete IDs, or finish reason")
        result["passed"] = True
    except Exception as error:
        result["failure"] = {"type": type(error).__name__, "message": str(error)}
    out.write_text(json.dumps(result, indent=2) + "\n")
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
