#!/usr/bin/env python3
"""Rehash the pinned EAGLE3 draft and verify its architecture-only adapter."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import time

REPOSITORY = "nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507"
REVISION = "ff0f0c0999f6c86b21dfd2f5803eebc4ac712224"
WEIGHT_SHA256 = "bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86"
WEIGHT_BYTES = 1145943008
CONFIG_SHA256 = "fc9573a970a1afd1c78ca29df2837f0d3f9f577721590a2fa132b87f759c9433"
ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "draft-evidence"

def fp(path):
    s = path.stat()
    return {k: getattr(s, k) for k in ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")}

def verify(directory):
    start = time.monotonic()
    directory = directory.resolve(strict=True)
    meta = json.loads((EVIDENCE / "draft-file-metadata.json").read_text())
    if (meta["repository"] != REPOSITORY or meta["revision"] != REVISION or
            meta["entry"]["lfs"]["oid"] != WEIGHT_SHA256 or meta["entry"]["size"] != WEIGHT_BYTES):
        raise ValueError("retained publisher metadata does not match pinned draft")
    weight = directory / "model.safetensors"
    before = fp(weight)
    if before["st_size"] != WEIGHT_BYTES:
        raise ValueError("draft byte length mismatch")
    digest = hashlib.sha256()
    with weight.open("rb") as f:
        while block := f.read(8 * 1024 * 1024): digest.update(block)
    if fp(weight) != before or digest.hexdigest() != WEIGHT_SHA256:
        raise ValueError("draft changed during full hash or publisher digest mismatch")
    with weight.open("rb") as f:
        rawlen = f.read(8)
        if len(rawlen) != 8: raise ValueError("missing safetensors header")
        size = struct.unpack("<Q", rawlen)[0]
        if not 0 < size <= 1024 * 1024: raise ValueError("header exceeds 1 MiB bound")
        header = json.loads(f.read(size))
    if header != json.loads((EVIDENCE / "draft-safetensors-header.json").read_text()):
        raise ValueError("draft tensor header differs from pinned inventory")
    files = []
    configs = {}
    for name in ("config.json", "publisher-config.json"):
        p = directory / name; before_cfg = fp(p); raw = p.read_bytes()
        if fp(p) != before_cfg: raise ValueError(f"draft config changed while read: {name}")
        configs[name] = json.loads(raw)
        files.append({"path": str(p), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "fingerprint": before_cfg})
    if files[0]["sha256"] != CONFIG_SHA256: raise ValueError("adapted draft config hash mismatch")
    adapted, publisher = configs["config.json"], configs["publisher-config.json"]
    differences = {k for k in adapted.keys() | publisher.keys() if adapted.get(k) != publisher.get(k)}
    if differences != {"architectures"} or adapted["architectures"] != ["LlamaForCausalLMEagle3"] or publisher["architectures"] != ["LlamaForCausalLM"]:
        raise ValueError("draft adapter must change only architectures")
    if fp(weight) != before: raise ValueError("draft changed after hash")
    return {"state": "PASS", "verified_utc": datetime.now(timezone.utc).isoformat(), "repository": REPOSITORY,
            "revision": REVISION, "draft_path": str(directory), "files": [{"path": str(weight), "bytes": WEIGHT_BYTES, "sha256": digest.hexdigest(), "fingerprint": before}, *files],
            "weight_sha256_matches_publisher_lfs": True, "all_tensor_header_entries_match_retained_inventory": True,
            "tensor_count": 15, "tensor_dtype_counts": {"BF16": 13, "I32": 2},
            "native_adapter_changes": ["architectures: LlamaForCausalLM -> LlamaForCausalLMEagle3"],
            "elapsed_s": time.monotonic() - start, "gpu_used": False, "native_model_loaded": False,
            "official_accuracy_verified": False, "scope": "Full draft byte and adapter identity only; no native runtime or accuracy claim."}

def main():
    p = argparse.ArgumentParser(); p.add_argument("--draft", type=Path, required=True); p.add_argument("--output", type=Path)
    a = p.parse_args()
    result = verify(a.draft)
    raw = json.dumps(result, indent=2) + "\n"
    if a.output:
        with a.output.open("x") as f: f.write(raw)
    print(raw, end="")
if __name__ == "__main__": main()
