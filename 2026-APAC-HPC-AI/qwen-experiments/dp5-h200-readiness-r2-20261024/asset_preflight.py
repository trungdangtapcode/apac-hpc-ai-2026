#!/usr/bin/env python3
"""Read only the model config and safetensors header; never read tensor data."""

import hashlib
import json
import struct
import sys
from pathlib import Path


EXPECTED_CONFIG_SHA256 = "f056921e486d3e22aed125b5218b87146ea2ac838ccf1521dea5b08f809e8d59"
EXPECTED = {
    "model.layers.0.mlp.experts.0.gate_proj.weight": ["F8_E4M3", [1536, 4096]],
    "model.layers.0.mlp.experts.0.up_proj.weight": ["F8_E4M3", [1536, 4096]],
    "model.layers.0.mlp.experts.0.down_proj.weight": ["F8_E4M3", [4096, 1536]],
    "model.layers.0.mlp.experts.0.gate_proj.weight_scale_inv": ["BF16", [12, 32]],
    "model.layers.0.mlp.experts.0.up_proj.weight_scale_inv": ["BF16", [12, 32]],
    "model.layers.0.mlp.experts.0.down_proj.weight_scale_inv": ["BF16", [32, 12]],
}


def main(model_dir: str) -> int:
    root = Path(model_dir)
    config_bytes = (root / "config.json").read_bytes()
    config_sha = hashlib.sha256(config_bytes).hexdigest()
    if config_sha != EXPECTED_CONFIG_SHA256:
        raise SystemExit(f"FATAL: model config SHA mismatch: {config_sha}")
    config = json.loads(config_bytes)
    if (config.get("num_experts"), config.get("num_key_value_heads"), config.get("num_hidden_layers")) != (128, 4, 94):
        raise SystemExit("FATAL: Qwen3 model geometry differs from reviewed actual config")
    if config.get("quantization_config", {}).get("weight_block_size") != [128, 128]:
        raise SystemExit("FATAL: model FP8 block metadata mismatch")
    shard = root / "model-00001-of-00024.safetensors"
    with shard.open("rb") as stream:
        header_size = struct.unpack("<Q", stream.read(8))[0]
        if not 0 < header_size <= 4 * 1024 * 1024:
            raise SystemExit("FATAL: safetensors header length outside the predeclared bound")
        header_bytes = stream.read(header_size)
    if len(header_bytes) != header_size or header_size > 4 * 1024 * 1024:
        raise SystemExit("FATAL: invalid or unexpectedly large safetensors header")
    header = json.loads(header_bytes)
    observed = {}
    for name, (dtype, shape) in EXPECTED.items():
        item = header.get(name)
        if not item or item.get("dtype") != dtype or item.get("shape") != shape:
            raise SystemExit(f"FATAL: safetensors header mismatch for {name}")
        observed[name] = {"dtype": item["dtype"], "shape": item["shape"]}
    print(json.dumps({
        "status": "PASS_HEADER_ONLY",
        "config_sha256": config_sha,
        "safetensors_header_bytes": header_size,
        "tensor_payload_read": False,
        "observed_expert_tensors": observed,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: asset_preflight.py MODEL_DIR")
    raise SystemExit(main(sys.argv[1]))
