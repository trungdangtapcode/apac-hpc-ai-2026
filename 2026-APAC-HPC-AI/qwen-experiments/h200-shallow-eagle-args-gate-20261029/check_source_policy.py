#!/usr/bin/env python3
"""Check pinned SGLang CLI fields and EAGLE top-k=1 draft-slot policy; no runtime import."""
import ast, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "eagle3-preflight-20261020/source/pilot-interfaces/sgl-workspace/sglang/python/sglang/srt"
EXPECTED = {
    "server_args.py": "79d9bbb61b429574e31e7a7e319831fcd129a83a475e6ffe2b7e8a5e8eb06b0f",
    "arg_groups/speculative_hook.py": "6ffb0b4066e92257ac88c03627df28f7e226fef25eae63a5d2771a74f656bac1",
}
for rel, digest in EXPECTED.items():
    p = SRC / rel
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    if actual != digest:
        raise SystemExit(f"FAIL source hash {rel}: {actual} != {digest}")
server = ast.parse((SRC / "server_args.py").read_text())
fields = {n.target.id for n in ast.walk(server) if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)}
required = {"speculative_algorithm", "speculative_draft_model_path", "speculative_num_steps", "speculative_eagle_topk", "speculative_num_draft_tokens", "speculative_draft_attention_backend", "speculative_draft_model_quantization", "tp_size", "ep_size", "dtype", "disaggregation_mode", "disaggregation_transfer_backend"}
if not required <= fields:
    raise SystemExit(f"FAIL ServerArgs fields missing: {sorted(required-fields)}")
hook = ast.parse((SRC / "arg_groups/speculative_hook.py").read_text())
fn = next((n for n in hook.body if isinstance(n, ast.FunctionDef) and n.name == "_handle_eagle_family"), None)
if fn is None:
    raise SystemExit("FAIL pinned EAGLE-family handler absent")
text = ast.unparse(fn)
for marker in ("server_args.speculative_eagle_topk == 1", "server_args.speculative_num_draft_tokens != server_args.speculative_num_steps + 1", "server_args.speculative_num_draft_tokens = server_args.speculative_num_steps + 1"):
    if marker not in text:
        raise SystemExit(f"FAIL expected exact slot policy absent: {marker}")
# For the proposed pair, the pinned policy predicate is false, so this hook does not coerce it.
steps, draft_tokens, topk = 1, 2, 1
if not (topk == 1 and draft_tokens == steps + 1):
    raise SystemExit("FAIL proposed settings do not satisfy pinned top-k=1 slot relation")
print(json.dumps({"state":"PASS_SOURCE_AST_POLICY_ONLY","source_hashes":EXPECTED,"cli_fields_present":sorted(required),"eagle_slot_policy":"topk=1 requires draft_tokens=steps+1; proposed (steps=1,tokens=2) is already canonical and avoids that hook's adjustment branch","proposal":{"algorithm":"EAGLE3","steps":steps,"topk":topk,"draft_tokens":draft_tokens},"scope":"Static AST checks over retained source files with hashes matching recorded native server_args/hook evidence. No argparse invocation, ServerArgs construction, CUDA/device/TP validation, draft/target metadata read, model load, KV, distributed state, P/D, output, or performance proof."}, indent=2))
