#!/usr/bin/env python3
"""Fail before model startup unless native argument probe 27153 matches S98."""
import hashlib, json, sys
from pathlib import Path
EXPECTED_SOURCE_SHA256 = '79d9bbb61b429574e31e7a7e319831fcd129a83a475e6ffe2b7e8a5e8eb06b0f'
EXPECTED = {
    'tp_size': 8, 'ep_size': 8, 'dtype': 'bfloat16', 'disaggregation_mode': 'decode',
    'speculative_algorithm': 'EAGLE3', 'speculative_num_steps': 1,
    'speculative_eagle_topk': 1, 'speculative_num_draft_tokens': 2,
    'speculative_draft_model_path': '/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09',
    'speculative_draft_attention_backend': 'flashinfer', 'speculative_draft_model_quantization': None,
    'moe_runner_backend': 'hpc_ops', 'decode_attention_backend': 'flashinfer',
    'flashinfer_allreduce_fusion_backend': 'mnnvl',
}

def validate(path, expected_sha256=None):
    path = Path(path)
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError('native argument evidence SHA-256 mismatch')
    doc = json.loads(raw)
    if doc.get('state') != 'PASS_NATIVE_ARGUMENT_CONFIGURATION_ONLY':
        raise ValueError('native argument probe is not a pass')
    if doc.get('max_cuda_allocated_bytes') != 0 or doc.get('distributed_initialized') is not False or doc.get('binary_weight_reads_allowed') is not False:
        raise ValueError('native argument probe exceeds its safe configuration-only scope')
    if doc.get('source_sha256') != EXPECTED_SOURCE_SHA256:
        raise ValueError('native argument source identity differs from the pinned source')
    resolved = doc.get('resolved')
    if resolved != EXPECTED:
        raise ValueError('native argument tuple does not match exact shallow EAGLE3 configuration')
    return {'state':'PASS_NATIVE_ARGUMENT_PREREQUISITE','job':27153,'evidence_sha256':digest,'resolved':resolved}

if __name__ == '__main__':
    if len(sys.argv) != 3: raise SystemExit('usage: check-native-arg-prereq.py EVIDENCE EXPECTED_SHA256')
    try: result=validate(sys.argv[1],sys.argv[2])
    except Exception as exc:
        print(json.dumps({'state':'FAIL','reason':str(exc)},indent=2)); raise SystemExit(1)
    print(json.dumps(result,indent=2))
