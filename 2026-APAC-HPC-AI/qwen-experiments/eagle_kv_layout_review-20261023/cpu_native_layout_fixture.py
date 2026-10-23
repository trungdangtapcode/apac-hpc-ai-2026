#!/usr/bin/env python3
"""CPU identity fixture for pinned native EAGLE3 MHA PD pointer ordering."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "pinned-source/sgl-workspace/sglang/python/sglang/srt"


def find_method(path, method_name):
    tree = ast.parse(path.read_text())
    for cls in tree.body:
        if isinstance(cls, ast.ClassDef):
            for node in cls.body:
                if isinstance(node, ast.FunctionDef) and node.name == method_name:
                    return node
    raise LookupError(method_name)


def compile_stmts(stmts, name, env):
    mod = ast.Module(body=stmts, type_ignores=[])
    ast.fix_missing_locations(mod)
    exec(compile(mod, name, "exec"), env)


def native_prefill_builder(target, draft):
    path = ROOT / "disaggregation/prefill.py"
    method = find_method(path, "_init_kv_manager")
    selected = [
        stmt for stmt in method.body
        if (stmt.lineno == 208 or stmt.lineno == 217 or stmt.lineno in (227, 228, 229))
    ]
    class Args:
        pass
    args = Args()
    self = type("PrefillStub", (), {
        "token_to_kv_pool": target,
        "draft_token_to_kv_pool": draft,
    })()
    env = {"self": self, "kv_args": args, "transfer_draft_cache": True}
    compile_stmts(selected, str(path), env)
    return args.kv_data_ptrs


def native_nixl_selector(src, dst):
    path = ROOT / "disaggregation/common/conn.py"
    node = find_method(path, "get_mha_kv_ptrs_with_pp")
    node.decorator_list = []
    node.returns = None
    for arg in node.args.args:
        arg.annotation = None
    class Manager:
        pass
    manager = Manager()
    manager.kv_args = type("Args", (), {"prefill_start_layer": 0})()
    env = {"List": list, "Tuple": tuple}
    compile_stmts([node], str(path), env)
    return env[node.name](manager, src, dst)


def pool(label, n):
    # Actual MHATokenToKVPool registration order is k_buffer + v_buffer.
    return [f"{label}.K{i}" for i in range(n)] + [f"{label}.V{i}" for i in range(n)]



def native_decode_builder(target, draft):
    path = ROOT / "disaggregation/decode.py"
    method = find_method(path, "_init_kv_manager")
    selected = [
        stmt for stmt in method.body
        if (stmt.lineno == 434 or stmt.lineno == 453 or stmt.lineno in (464, 465, 466))
    ]
    class Args:
        pass
    args = Args()
    self = type("DecodeStub", (), {
        "token_to_kv_pool": target,
        "draft_token_to_kv_pool": draft,
    })()
    env = {"self": self, "kv_args": args, "transfer_kv_pool": target, "kv_data_mem_kinds": []}
    compile_stmts(selected, str(path), env)
    return args.kv_data_ptrs


def summarize(src, dst):
    sk, sv, dk, dv, stage = native_nixl_selector(src, dst)
    selected_src = list(sk[:stage]) + list(sv[:stage])
    selected_dst = list(dk[:stage]) + list(dv[:stage])
    # Independent expected transfer origin: 94 target layers, plus a draft
    # layer only when prefill itself registered one; decode selection here is
    # the first target-model range for the ordinary no-draft-prefill case.
    if len(src) == 190:
        expected_src = pool("target", 94) + pool("draft", 1)
        expected_dst = pool("target", 94) + pool("draft", 1)
    else:
        expected_src = pool("target", 94)
        expected_dst = pool("target", 94)
    return {
        "source_pointer_count": len(src), "destination_pointer_count": len(dst),
        "selector_intermediate_source_k_95th": sk[94] if len(sk) > 94 else None,
        "selector_intermediate_source_v_first": sv[0] if sv else None,
        "selected_layer_count": stage,
        "final_source_pointer_order_matches_expected_origin_order": selected_src == expected_src,
        "final_destination_pointer_order_matches_expected_origin_order": selected_dst == expected_dst,
        "final_source_pointer_order_equals_input": selected_src == src,
        "final_destination_pointer_order_equals_input": selected_dst == dst,
    }


# Both roles built with EAGLE3: target+draft pointers on each side (190 each).
prefill_built = native_prefill_builder(
    type("Pool", (), {"get_contiguous_buf_infos": lambda self: (pool("target", 94), [], [])})(),
    type("Pool", (), {"get_contiguous_buf_infos": lambda self: (pool("draft", 1), [], [])})(),
)
decode_built = native_decode_builder(
    type("Pool", (), {"get_contiguous_buf_infos": lambda self: (pool("target", 94), [], [])})(),
    type("Pool", (), {"get_contiguous_buf_infos": lambda self: (pool("draft", 1), [], [])})(),
)
# Prefill without speculative draft, EAGLE3 decode: native special case (188 -> 190).
plain_prefill = pool("target", 94)
eagle_decode = decode_built

result = {
    "scope": "CPU pointer-label identity only; no model, CUDA, GPU allocation, NIXL transfer, or runtime execution",
    "builder_source": "disaggregation/prefill.py and disaggregation/decode.py::_init_kv_manager (AST-extracted pointer assembly statements)",
    "pool_order_source": "mem_cache/memory_pool.py::MHATokenToKVPool._pd_registerable_tensors returns k_buffer + v_buffer",
    "selector_source": "disaggregation/common/conn.py::CommonKVManager.get_mha_kv_ptrs_with_pp (AST-extracted method)",
    "both_roles_have_eagle3": summarize(prefill_built, decode_built),
    "plain_prefill_to_eagle_decode": summarize(plain_prefill, eagle_decode),
}
print(json.dumps(result, indent=2, sort_keys=True))
