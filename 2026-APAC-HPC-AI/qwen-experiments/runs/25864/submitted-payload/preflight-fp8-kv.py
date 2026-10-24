#!/usr/bin/env python3
"""Read model config/index metadata only; never open any model weight shard."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def inspect(model: Path) -> dict:
    config_path = model / 'config.json'
    index_path = model / 'model.safetensors.index.json'
    if not config_path.is_file() or not index_path.is_file():
        raise FileNotFoundError('model config.json or model.safetensors.index.json is missing')
    config = json.loads(config_path.read_text())
    index = json.loads(index_path.read_text())
    weight_map = index.get('weight_map')
    if not isinstance(weight_map, dict):
        raise ValueError('checkpoint index has no weight_map object')
    scale_keys = sorted(k for k in weight_map if re.search(r'(^|\.)(k|v)_scale(_inv)?$', k, re.I))
    quant_config = config.get('quantization_config') or {}
    kv_algo = quant_config.get('kv_cache_quant_algo')
    result = {
        'status': 'PASS_METADATA_ONLY',
        'scope': 'CPU metadata inspection only; config and safetensors index read, tensor weights not opened.',
        'model_path': str(model),
        'config_sha256': sha256(config_path),
        'index_sha256': sha256(index_path),
        'model_type': config.get('model_type'),
        'num_hidden_layers': config.get('num_hidden_layers'),
        'num_key_value_heads': config.get('num_key_value_heads'),
        'head_dim': config.get('head_dim'),
        'quantization_method': quant_config.get('quant_method'),
        'kv_cache_quant_algo_key_present': 'kv_cache_quant_algo' in quant_config,
        'kv_cache_quant_algo': kv_algo,
        'index_tensor_count': len(weight_map),
        'checkpoint_kv_scale_keys': scale_keys,
        'checkpoint_kv_scale_key_count': len(scale_keys),
        'quantization_param_path': None,
        'scale_source_status': 'no checkpoint KV scale keys and no quantization parameter file; pinned SGLang source documents default KV scales as 1.0',
        'runtime_scale_status': 'not observed by this CPU preflight; runtime logs must report args and allocation dtype; per-layer backend scale values are not emitted by inspected source',
        'quality_status': 'UNKNOWN; exploratory unranked screen; official >=99% gate not established',
        'weight_shards_opened': False,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = inspect(args.model)
    if result['num_hidden_layers'] != 94 or result['num_key_value_heads'] != 4 or result['head_dim'] != 128:
        raise SystemExit('model geometry differs from the H200 KV traffic derivation')
    if result['checkpoint_kv_scale_key_count'] != 0:
        raise SystemExit('checkpoint now contains K/V scale keys; stop and review scale provenance')
    rendered = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    print(rendered, end='')


if __name__ == '__main__':
    main()
