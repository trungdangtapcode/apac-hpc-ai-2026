#!/usr/bin/env python3
"""Check the inherited runtime assets and bind the pinned Qwen model config."""
from pathlib import Path
import hashlib
import json
from asset_identity import verify_asset_identity

BUNDLE = Path(__file__).parent
MODEL = Path("/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8")
IMAGE = Path("/scratch/enroot-images/sglang-harbor.sqsh")
BINDING = json.loads((BUNDLE / "model-config-binding.json").read_text())
model_realpath = MODEL.resolve(strict=True)
config = model_realpath / "config.json"
raw = config.read_bytes()
config = json.loads(raw)
assert str((model_realpath / "config.json").resolve(strict=True)) == BINDING["model_config_realpath"]
assert hashlib.sha256(raw).hexdigest() == BINDING["model_config_sha256"]
for key in ("num_hidden_layers", "num_key_value_heads", "head_dim"):
    assert config.get(key) == BINDING[key], f"model config {key} differs from reviewed binding"
asset = verify_asset_identity(BUNDLE / "asset-verification.json", MODEL, IMAGE)
config_rows = [row for row in asset["files"] if row["path"] == str(model_realpath / "config.json")]
assert len(config_rows) == 1 and config_rows[0]["runtime_small_file_sha256"] == BINDING["model_config_sha256"]
print(json.dumps({"asset_identity": asset, "model_config_binding": BINDING}, indent=2, sort_keys=True))
