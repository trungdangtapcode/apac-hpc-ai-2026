#!/usr/bin/env python3
"""Run and retain a deterministic semantic readiness probe against one worker."""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: semantic_probe.py BASE_URL OUTPUT_JSON")
    base, output = sys.argv[1].rstrip("/"), Path(sys.argv[2])
    body = {
        "model": "qwen",
        "messages": [{"role": "user", "content": "What is 17 + 25? Reply with only the number."}],
        "temperature": 0.0,
        "max_tokens": 16,
        "stream": False,
    }
    request = urllib.request.Request(
        base + "/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
            status = response.status
        parsed = json.loads(raw)
        content = parsed["choices"][0]["message"]["content"]
        passed = status == 200 and re.search(r"(?<!\d)42(?!\d)", content) is not None
        record = {
            "url": base,
            "http_status": status,
            "elapsed_seconds": round(time.time() - started, 6),
            "request": body,
            "response_body": parsed,
            "response_text": content,
            "semantic_check": "response contains standalone numeric answer 42",
            "passed": passed,
        }
    except Exception as exc:
        record = {
            "url": base,
            "elapsed_seconds": round(time.time() - started, 6),
            "request": body,
            "error": f"{type(exc).__name__}: {exc}",
            "passed": False,
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"url": base, "passed": record["passed"], "elapsed_seconds": record["elapsed_seconds"]}), flush=True)
    return 0 if record["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
