"""CPU-only checks of real native methods and the pinned public draft header.

No runtime imports, model code execution, tensor loading or GPU work. Execute
only the extracted pure configuration remapping and pointer-list helper.
"""
import ast
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import List, Tuple

O = Path(__file__).resolve().parent
R = O.parent
prefix = 'sgl-workspace/sglang/python/sglang/srt'
model_source = O / 'source/native' / prefix / 'configs/model_config.py'
conn_source = O / 'source/interfaces' / prefix / 'disaggregation/common/conn.py'


def method(path, class_name, name, globals_dict):
    tree = ast.parse(path.read_text())
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == class_name)
    func = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == name)
    code = ast.Module(body=[copy.deepcopy(func)], type_ignores=[])
    ast.fix_missing_locations(code)
    exec(compile(code, str(path), 'exec'), globals_dict)
    return globals_dict[name]


config = json.loads((R / 'deepinfer-review-20261020/source/draft/config.json').read_text())
remap = method(model_source, 'ModelConfig', '_config_draft_model', {'MIMO_V2_MODEL_ARCHS': []})
obj = SimpleNamespace(is_draft_model=True, hf_config=SimpleNamespace(**copy.deepcopy(config)))
remap(obj)
assert obj.hf_config.architectures == ['LlamaForCausalLM']
derived = copy.deepcopy(config)
derived['architectures'] = ['LlamaForCausalLMEagle3']
(O / 'derived-draft-config.json').write_text(json.dumps(derived, indent=2) + '\n')
assert {key for key in config if config[key] != derived[key]} == {'architectures'}

header = json.loads((O / 'draft-safetensors-header.json').read_text())
expected = {
    'fc.weight': [4096, 12288], 'lm_head.weight': [64000, 4096],
    'layers.0.self_attn.q_proj.weight': [8192, 8192],
    'layers.0.self_attn.k_proj.weight': [512, 8192],
    'layers.0.self_attn.v_proj.weight': [512, 8192],
    'layers.0.self_attn.o_proj.weight': [4096, 8192],
    'layers.0.mlp.up_proj.weight': [12288, 4096],
    'layers.0.mlp.gate_proj.weight': [12288, 4096],
    'layers.0.mlp.down_proj.weight': [4096, 12288],
    'd2t': [64000], 't2d': [151936],
}
for key, shape in expected.items():
    assert header[key]['shape'] == shape, (key, header[key]['shape'], shape)
    assert header[key]['dtype'] == ('I32' if key in ('d2t', 't2d') else 'BF16')
norm_names = ['layers.0.hidden_norm.weight', 'layers.0.input_layernorm.weight',
              'layers.0.post_attention_layernorm.weight', 'norm.weight']
for key in norm_names:
    assert header[key]['shape'] == [4096] and header[key]['dtype'] == 'BF16'
assert set(header) == {'__metadata__', *expected, *norm_names}

split = method(conn_source, 'CommonKVManager', 'get_mha_kv_ptrs_with_pp',
               {'List': List, 'Tuple': Tuple})
pointer_cases = []
for name, src_draft, dst_draft in [('target-only', False, False),
                                  ('decode-only-draft', False, True),
                                  ('both-sides-draft', True, True)]:
    src = [f'src-K{i}' for i in range(94)] + [f'src-V{i}' for i in range(94)]
    dst = [f'dst-K{i}' for i in range(94)] + [f'dst-V{i}' for i in range(94)]
    if src_draft:
        src += ['src-draft-K', 'src-draft-V']
    if dst_draft:
        dst += ['dst-draft-K', 'dst-draft-V']
    a, b, c, d, count = split(SimpleNamespace(kv_args=SimpleNamespace(prefill_start_layer=0)), src, dst)
    actual = list(zip(a[:count] + b[:count], c[:count] + d[:count]))
    wanted_dst = dst if src_draft else dst[:188]
    assert actual == list(zip(src, wanted_dst)), name
    pointer_cases.append(dict(case=name, pointer_pairs=len(actual), passed=True))

result = dict(state='CPU_HEADER_CONFIG_POINTER_CHECKS_PASS_GPU_INTEGRATION_UNVERIFIED',
              gpu_used=False, tensor_payload_downloaded=False,
              native_remap_keeps_published_llama_arch=True,
              derived_metadata_change={'architectures': ['LlamaForCausalLMEagle3']},
              header_tensor_count=len(header) - 1, pointer_cases=pointer_cases,
              limits=['Header metadata does not prove tensor bytes or a successful loader.',
                      'Pointer-list identity does not validate NIXL byte ranges, page strides or GPU transfers.',
                      'Both EAGLE3 phases need compatible draft state, KV and metadata; decode-only support is not inferred.',
                      'Draft state capture, attention verification, CUDA graphs and greedy equality need a GPU pilot.'],
              source_sha256={str(p.relative_to(O)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (model_source, conn_source)})
(O / 'interface-checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(result['state'])
