"""Avoid whole-pool equal-TP dlists; reuse the image's request transfer path."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'nixl-equal-ondemand'
original = (ROOT / 'nixl-ondemand/original-conn.py').read_text()
tree = ast.parse(original)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'NixlKVManager')
method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_prepare_payload_xfer')
# Restrict this experiment to the tested Qwen TP8/PP1 homogeneous MHA layout.
# Memory registration, head mapping, and all transfer code stay byte-identical.
guard = '''        if (
            self.attn_tp_size == peer_info.decode_tp_size == 8
            and self.pp_size == 1
            and not self.is_mla_backend
            and not self.is_hybrid_mla_backend
            and not peer_info.requires_dcp_relayout
            and self.src_mem_kind == "VRAM"
            and len(self.kv_args.kv_item_lens) > 0
            and self.kv_args.kv_item_lens == peer_info.dst_kv_item_lens
            and self.kv_args.kv_layer_ids == peer_info.dst_kv_layer_ids
            and all(kind == "VRAM" for kind in peer_info.dst_kv_mem_kinds)
        ):
            # With no prepared handles, _send_kvcache_generic uses its original
            # non-prepped path: coalesce request pages and initialize_xfer.
            peer_info.dst_homogeneous_mem_kind = "VRAM"
            logger.info("NIXL_EQUAL_ON_DEMAND peer=%s TP8->TP8; pool dlists skipped",
                        peer_info.agent_name)
            return
'''
lines = original.splitlines(keepends=True)
lines[method.body[0].lineno-1:method.body[0].lineno-1] = [guard]
patched = ''.join(lines)
ast.parse(patched)
OUT.mkdir(exist_ok=True)
(OUT/'original-conn.py').write_text(original)
(OUT/'conn.py').write_text(patched)
(OUT/'nixl-ondemand.patch').write_text(''.join(difflib.unified_diff(
    original.splitlines(keepends=True), patched.splitlines(keepends=True),
    fromfile='a/python/sglang/srt/disaggregation/nixl/conn.py',
    tofile='b/python/sglang/srt/disaggregation/nixl/conn.py')))
meta = {'name':'equal-tp8-request-descriptors-v1',
        'original_sha256':hashlib.sha256(original.encode()).hexdigest(),
        'patched_sha256':hashlib.sha256(patched.encode()).hexdigest(),
        'scope':'TP8->TP8, PP1 MHA, identical layer/stride layout, VRAM, no DCP only. Skip full-pool prepared dlists and reuse original non-prepped transfer. No compute/weight/precision changes.',
        'gpu_validated':False}
(OUT/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta,indent=2))
