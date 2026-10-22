#!/usr/bin/env python3
"""Revalidate the staged public draft against pinned retained publisher evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import time

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "eagle3-preflight-20261020"
REPOSITORY = "nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507"
REVISION = "ff0f0c0999f6c86b21dfd2f5803eebc4ac712224"
WEIGHT_SHA256 = "bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86"
WEIGHT_BYTES = 1145943008
CONFIG_SHA256 = "fc9573a970a1afd1c78ca29df2837f0d3f9f577721590a2fa132b87f759c9433"


def fingerprint(stat):
    return {key: getattr(stat, key) for key in
            ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")}


def verify(directory):
    started = time.monotonic()
    directory = directory.resolve(strict=True)
    metadata_path = SOURCE / "draft-file-metadata.json"
    metadata = json.loads(metadata_path.read_text())
    if (metadata["repository"] != REPOSITORY or metadata["revision"] != REVISION
            or metadata["entry"]["lfs"]["oid"] != WEIGHT_SHA256
            or metadata["entry"]["size"] != WEIGHT_BYTES):
        raise ValueError("retained pinned publisher metadata does not match the draft contract")
    weight = directory / "model.safetensors"
    before = fingerprint(weight.stat())
    if before["st_size"] != WEIGHT_BYTES:
        raise ValueError("draft byte length differs from the pinned publisher record")
    digest = hashlib.sha256()
    with weight.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    after = fingerprint(weight.stat())
    if before != after or digest.hexdigest() != WEIGHT_SHA256:
        raise ValueError("draft changed while reading or full SHA256 differs from publisher LFS")
    # The full digest covers the header too; replay it against the retained
    # inspected tensor inventory without loading torch or allocating a GPU.
    with weight.open("rb") as stream:
        length_bytes = stream.read(8)
        if len(length_bytes) != 8:
            raise ValueError("missing safetensors header length")
        length = struct.unpack("<Q", length_bytes)[0]
        if not 0 < length <= 1024 * 1024:
            raise ValueError("safetensors header exceeds the bounded parser")
        header = json.loads(stream.read(length))
    retained_header_path = SOURCE / "draft-safetensors-header.json"
    if header != json.loads(retained_header_path.read_text()):
        raise ValueError("draft tensor inventory differs from the inspected pinned header")
    files = [{"path": str(weight), "bytes": WEIGHT_BYTES,
              "sha256": digest.hexdigest(), "fingerprint": before}]
    configs = {}
    for name in ("config.json", "publisher-config.json"):
        path = directory / name
        before_config = fingerprint(path.stat())
        raw = path.read_bytes()
        if before_config != fingerprint(path.stat()):
            raise ValueError(f"draft metadata changed while reading: {name}")
        configs[name] = json.loads(raw)
        files.append({"path": str(path), "bytes": len(raw),
                      "sha256": hashlib.sha256(raw).hexdigest(),
                      "fingerprint": before_config})
    if files[1]["sha256"] != CONFIG_SHA256:
        raise ValueError("adapted native draft config differs from retained staged identity")
    adapted, publisher = configs["config.json"], configs["publisher-config.json"]
    differences = {key for key in adapted.keys() | publisher.keys()
                   if adapted.get(key) != publisher.get(key)}
    if (differences != {"architectures"}
            or adapted["architectures"] != ["LlamaForCausalLMEagle3"]
            or publisher["architectures"] != ["LlamaForCausalLM"]):
        raise ValueError("native adapter must change only the draft architecture name")
    if fingerprint(weight.stat()) != after:
        raise ValueError("draft changed after its full hash was checked")
    tensors = {key: row for key, row in header.items() if key != "__metadata__"}
    dtypes = {}
    for tensor in tensors.values():
        dtype = tensor["dtype"]
        dtypes[dtype] = dtypes.get(dtype, 0) + 1
    return {
        "state": "PASS", "verified_utc": datetime.now(timezone.utc).isoformat(),
        "repository": REPOSITORY, "revision": REVISION,
        "draft_path": str(directory), "files": files,
        "weight_sha256_matches_publisher_lfs": True,
        "all_tensor_header_entries_match_retained_inventory": True,
        "tensor_count": len(tensors), "tensor_dtype_counts": dtypes,
        "native_adapter_changes": ["architectures: LlamaForCausalLM -> LlamaForCausalLMEagle3"],
        "source_evidence_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (metadata_path, retained_header_path)},
        "elapsed_s": time.monotonic() - started,
        "gpu_used": False, "native_model_loaded": False,
        "actual_h200_speculative_runtime_verified": False,
        "official_accuracy_verified": False,
        "scope": "Current staged draft byte identity and tensor-header/metadata consistency only; no full-model speculative output or performance claim. No weight bytes captured."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", type=Path, default=ROOT / "hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Reserve the output exclusively so an old verification is never overwritten.
    with args.output.open("x") as output:
        try:
            result = verify(args.draft)
        except Exception as error:
            result = {"state": "FAIL", "verified_utc": datetime.now(timezone.utc).isoformat(),
                      "failure": {"type": type(error).__name__, "message": str(error)},
                      "gpu_used": False}
        output.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result.get(key) for key in
                      ("state", "elapsed_s", "tensor_count", "tensor_dtype_counts", "failure")}))
    raise SystemExit(0 if result["state"] == "PASS" else 1)


if __name__ == "__main__":
    main()
