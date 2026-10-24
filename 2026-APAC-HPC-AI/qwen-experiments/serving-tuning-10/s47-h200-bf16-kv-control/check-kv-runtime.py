#!/usr/bin/env python3
"""Fail-closed role-log proof of resolved KV arguments and allocated logical cache dtype."""
import argparse
import importlib.util
import json
from pathlib import Path
import re


def load_parser(path: Path):
    spec = importlib.util.spec_from_file_location('capacity_parser', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._value_for


def check(bundle: Path, artdir: Path, role: str, expected_kv: str) -> dict:
    config = json.loads((bundle / 'config.json').read_text())
    p = json.loads((artdir / 'kv-scale-provenance.json').read_text())
    if p.get('status') != 'PASS_METADATA_ONLY' or p.get('checkpoint_kv_scale_key_count') != 0:
        raise ValueError('checkpoint KV-scale provenance preflight missing or unexpected')
    if p.get('weight_shards_opened') is not False:
        raise ValueError('CPU preflight must not open weight shards')
    if p.get('quantization_param_path') is not None:
        raise ValueError('unexpected quantization parameter path')

    log = artdir / f'{role}.log'
    text = log.read_text(errors='replace')
    value_for = load_parser(bundle / 'audit-capacity.py')
    arg_lines = [line for line in text.splitlines() if 'server_args=ServerArgs(' in line]
    if not arg_lines:
        raise ValueError(f'{role}: no resolved ServerArgs log, cannot prove KV setting')
    parsed = []
    for line in arg_lines:
        names = ('kv_cache_dtype', 'quantization_param_path', 'dtype', 'max_running_requests',
                 'tp_size', 'ep_size', 'chunked_prefill_size', 'moe_runner_backend',
                 'disaggregation_mode', 'cuda_graph_backend_prefill')
        row = {name: value_for(line, name) for name in names}
        if role == 'decode-0':
            row['decode_attention_backend'] = value_for(line, 'decode_attention_backend')
        parsed.append(row)
    if len({json.dumps(row, sort_keys=True) for row in parsed}) != 1:
        raise ValueError(f'{role}: resolved ServerArgs records disagree')
    args = parsed[0]
    expected_role = {
        'prefill-0': (4, 1, 64, 'deep_gemm', 'prefill'),
        'prefill-1': (4, 1, 64, 'deep_gemm', 'prefill'),
        'decode-0': (8, 8, 256, 'hpc_ops', 'decode'),
    }[role]
    checks = {
        'kv_cache_dtype': expected_kv,
        'quantization_param_path': None,
        'dtype': 'bfloat16',
        'tp_size': expected_role[0],
        'ep_size': expected_role[1],
        'max_running_requests': expected_role[2],
        'chunked_prefill_size': 8192,
        'moe_runner_backend': expected_role[3],
        'disaggregation_mode': expected_role[4],
        'cuda_graph_backend_prefill': 'disabled',
    }
    for key, value in checks.items():
        if args[key] != value:
            raise ValueError(f'{role}: ServerArgs {key}={args[key]!r}, expected {value!r}')
    if role == 'decode-0' and args['decode_attention_backend'] != 'flashinfer':
        raise ValueError(f"decode-0: resolved decode_attention_backend={args['decode_attention_backend']!r}")

    expected_dtype = 'torch.bfloat16' if expected_kv == 'auto' else 'torch.float8_e4m3fn'
    allocations = []
    for line in text.splitlines():
        if 'KV Cache is allocated.' not in line:
            continue
        match = re.search(r'KV Cache is allocated\. dtype: ([^, ]+)', line)
        rank = re.search(r'TP(\d+)', line)
        if match:
            allocations.append({'dtype': match.group(1), 'rank': int(rank.group(1)) if rank else None, 'line': line.strip()})
    if not allocations:
        raise ValueError(f'{role}: missing actual KV Cache allocation log; runtime cache proof is required')
    if {row['dtype'] for row in allocations} != {expected_dtype}:
        raise ValueError(f'{role}: logical KV allocation dtype set differs: {sorted({row["dtype"] for row in allocations})}')
    ranks = {row['rank'] for row in allocations if row['rank'] is not None}
    expected_ranks = set(range(expected_role[0]))
    if ranks != expected_ranks:
        raise ValueError(f'{role}: KV allocation rank proof {sorted(ranks)} != {sorted(expected_ranks)}')

    scale_status = 'uncalibrated default 1.0 inferred from no quantization_param_path, no checkpoint k_scale/v_scale keys, and pinned source; per-layer runtime scale values are not logged'
    return {
        'status': 'PASS_RUNTIME_KV_ALLOCATION', 'role': role,
        'resolved_server_args': args,
        'logical_cache_dtype': expected_dtype,
        'allocation_rank_count': len(ranks), 'allocation_ranks': sorted(ranks),
        'allocation_records': allocations,
        'physical_store_dtype': 'torch.uint8 (source-derived: pinned memory_pool.py maps FP8 logical cache buffers to uint8)',
        'backend_scale_status': scale_status,
        'quality_status': 'UNKNOWN; this is an unranked screen and not an official accuracy result',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--artdir', type=Path, required=True)
    parser.add_argument('--role', choices=('prefill-0', 'prefill-1', 'decode-0'), required=True)
    parser.add_argument('--expected', choices=('auto', 'fp8_e4m3'), required=True)
    args = parser.parse_args()
    try:
        result = check(args.bundle, args.artdir, args.role, args.expected)
    except Exception as error:
        result = {'status': 'FAIL', 'role': args.role, 'error': str(error), 'runtime_cache_proof_required': True}
    out = args.artdir / f'kv-runtime-{args.role}.json'
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result['status'] == 'PASS_RUNTIME_KV_ALLOCATION' else 1)


if __name__ == '__main__':
    main()
