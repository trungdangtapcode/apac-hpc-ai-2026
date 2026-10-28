"""Bind a target-reference result to a pinned model/image verification record."""
import hashlib
import json
from pathlib import Path
import re


EXPECTED_REVISION = "e156cb4efae43fbee1a1ab073f946a1377e6b969"
EXPECTED_MODEL_FILES = 33
EXPECTED_WEIGHT_FILES = 24
EXPECTED_FILES = 34
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def verify_asset_identity(manifest_path, model_path, image_path):
    """Validate the captured full-hash record and cheap current-file fingerprints.

    Large model shards and the container image are not rehashed at runtime.
    Their full SHA256 values come from the independently retained PASS record;
    size and stable filesystem timestamps bind the mounted runtime paths to
    those verified files. Small model metadata files are hashed again here.
    """
    manifest_path = Path(manifest_path)
    model_path = Path(model_path).resolve(strict=True)
    image_path = Path(image_path).resolve(strict=True)
    raw = manifest_path.read_bytes()
    manifest_sha256 = hashlib.sha256(raw).hexdigest()
    manifest = json.loads(raw)
    if manifest.get("state") != "PASS" or manifest.get("errors") != []:
        raise ValueError("asset verification manifest is not a clean PASS")
    if manifest.get("model_revision") != EXPECTED_REVISION:
        raise ValueError("asset verification manifest has an unexpected model revision")
    rows = manifest.get("files")
    if not isinstance(rows, list) or len(rows) != EXPECTED_FILES:
        raise ValueError("asset verification manifest must contain exactly 34 files")
    if manifest.get("expected_files") != EXPECTED_FILES:
        raise ValueError("asset verification expected_files count is not 34")

    paths = {}
    for row in rows:
        path = Path(row["path"])
        key = str(path)
        if key in paths:
            raise ValueError(f"duplicate asset path in verification manifest: {key}")
        if row.get("passed") is not True or type(row.get("bytes")) is not int or row["bytes"] <= 0:
            raise ValueError(f"invalid verified asset row: {key}")
        if not isinstance(row.get("sha256"), str) or not HEX_SHA256.fullmatch(row["sha256"]):
            raise ValueError(f"invalid SHA256 in verified asset row: {key}")
        if type(row.get("mtime_ns")) is not int or type(row.get("ctime_ns")) is not int:
            raise ValueError(f"missing stable filesystem timestamps: {key}")
        paths[key] = row

    image_key = str(image_path)
    model_rows = [row for key, row in paths.items() if Path(key).parent == model_path]
    if len(model_rows) != EXPECTED_MODEL_FILES:
        raise ValueError("verification manifest must contain exactly 33 files under the target model path")
    weight_rows = [row for row in model_rows if Path(row["path"]).name.endswith(".safetensors")]
    if len(weight_rows) != EXPECTED_WEIGHT_FILES:
        raise ValueError("verification manifest must contain exactly 24 target weight shards")
    expected_weight_names = {f"model-{index:05d}-of-00024.safetensors" for index in range(1, 25)}
    if {Path(row["path"]).name for row in weight_rows} != expected_weight_names:
        raise ValueError("verification manifest target weight shard names are incomplete")
    if image_key not in paths or len(paths) != EXPECTED_FILES:
        raise ValueError("verification manifest does not bind the configured container image")
    if set(paths) != {str(model_path / Path(row["path"]).name) for row in model_rows} | {image_key}:
        raise ValueError("verification manifest contains paths outside the configured model and image")

    evidence = []
    for key, row in sorted(paths.items()):
        current = Path(key)
        before = current.stat()
        if before.st_size != row["bytes"] or before.st_mtime_ns != row["mtime_ns"]:
            raise ValueError(f"runtime size/mtime differs from full-hash record: {key}")
        if hasattr(before, "st_ctime_ns") and before.st_ctime_ns != row["ctime_ns"]:
            raise ValueError(f"runtime ctime differs from full-hash record: {key}")
        is_model = current.parent == model_path
        is_small = is_model and current.suffix != ".safetensors"
        digest = None
        if is_small:
            digest = hashlib.sha256(current.read_bytes()).hexdigest()
            if digest != row["sha256"]:
                raise ValueError(f"runtime metadata SHA256 differs from full-hash record: {key}")
        after = current.stat()
        stable = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable):
            raise ValueError(f"asset changed while runtime identity was checked: {key}")
        evidence.append({
            "path": key,
            "bytes": row["bytes"],
            "sha256": row["sha256"],
            "runtime_small_file_sha256": digest,
            "mtime_ns": row["mtime_ns"],
            "ctime_ns": row["ctime_ns"],
            "full_hash_from_verification_manifest": True,
        })

    expected_bytes = sum(row["bytes"] for row in rows)
    if manifest.get("expected_bytes") != expected_bytes:
        raise ValueError("asset verification expected_bytes total is inconsistent")
    return {
        "model_revision": EXPECTED_REVISION,
        "model_path": str(model_path),
        "container_image_path": str(image_path),
        "verification_manifest": manifest_path.name,
        "verification_manifest_sha256": manifest_sha256,
        "verified_file_count": EXPECTED_FILES,
        "verified_bytes_total": expected_bytes,
        "files": evidence,
        "runtime_hash_policy": "Full model and image SHA256 values are from the immutable PASS manifest; current runtime checks require exact size/mtime/ctime and rehash all small model metadata files.",
    }
