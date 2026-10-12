"""Make a reviewable transport-only patch against the supplied image's source."""
import ast
import argparse
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/tmp/apac42-repair-source/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py')
OUT = ROOT / 'nixl-ondemand'

INIT = '''    def _init_hetero_tp_prep_handle(
        self, peer_name, decode_kv_args, src_mem_kind="VRAM", dst_mem_kind="VRAM"
    ):
        # Preserve the original head geometry; build descriptors per request
        # rather than enumerating every unused slot in the entire KV pool.
        decode_tp_size = decode_kv_args.decode_tp_size
        prefill_tp_size = self.attn_tp_size
        page_size = self.kv_args.page_size
        total_kv_heads = getattr(self.kv_args, "total_kv_head_num", 0)
        if total_kv_heads <= 0:
            total_kv_heads = self.kv_args.kv_head_num * prefill_tp_size
        src_heads_per_rank = max(1, total_kv_heads // prefill_tp_size)
        dst_heads_per_rank = max(1, total_kv_heads // decode_tp_size)
        dst_kv_item_len = decode_kv_args.dst_kv_item_len
        bytes_per_head_slice = dst_kv_item_len // page_size // dst_heads_per_rank
        if prefill_tp_size > decode_tp_size:
            src_replication = max(1, prefill_tp_size // total_kv_heads)
            local_tp_rank = self.kv_args.engine_rank % prefill_tp_size
            num_heads_to_send = src_heads_per_rank
            head_group_idx = 0
            unique_head_idx = local_tp_rank // src_replication
            dst_head_start = (unique_head_idx * src_heads_per_rank) % dst_heads_per_rank
            dst_head_offset = dst_head_start * bytes_per_head_slice
        else:
            from sglang.srt.disaggregation.common.staging_buffer import compute_head_slice_params
            src_head_start, num_heads_to_send, _, _ = compute_head_slice_params(
                prefill_tp_size, decode_tp_size, self.kv_args.engine_rank,
                decode_kv_args.decode_tp_rank, total_kv_heads,
            )
            head_group_idx = src_head_start // dst_heads_per_rank
            dst_head_offset = 0
        src_kv_item_len = self.kv_args.kv_item_lens[0]
        src_k, src_v, dst_k, dst_v, layers = self.get_mha_kv_ptrs_with_pp(
            self.kv_args.kv_data_ptrs, decode_kv_args.dst_kv_ptrs
        )
        if not hasattr(self, "_ondemand_slice_plans"):
            self._ondemand_slice_plans = {}
        self._ondemand_slice_plans[peer_name] = dict(
            src_ptrs=np.asarray(list(src_k[:layers])+list(src_v[:layers]), dtype=np.uint64),
            dst_ptrs=np.asarray(list(dst_k[:layers])+list(dst_v[:layers]), dtype=np.uint64),
            src_stride=src_kv_item_len // page_size,
            dst_stride=dst_kv_item_len // page_size,
            length=num_heads_to_send * bytes_per_head_slice,
            src_offset=head_group_idx * num_heads_to_send * bytes_per_head_slice,
            dst_offset=dst_head_offset,
            src_mem_kind=src_mem_kind, dst_mem_kind=dst_mem_kind,
            dst_gpu_id=decode_kv_args.gpu_id,
        )
        logger.info(
            "NIXL_ON_DEMAND peer=%s geometry ready: TP%d->TP%d; pool dlists skipped",
            peer_name, prefill_tp_size, decode_tp_size,
        )
'''

SEND = '''    def send_kvcache_slice(self, peer_name, prefill_kv_indices, dst_kv_indices, notif):
        plan = self._ondemand_slice_plans[peer_name]
        page_size = self.kv_args.page_size
        src_pages = np.asarray(prefill_kv_indices, dtype=np.uint64)
        dst_pages = np.asarray(dst_kv_indices, dtype=np.uint64)
        if len(src_pages) != len(dst_pages) or len(src_pages) == 0:
            raise ValueError("NIXL slice requires nonempty equal-length page lists")
        offsets = np.arange(page_size, dtype=np.uint64)
        src_tokens = (src_pages[:, None] * page_size + offsets[None, :]).ravel()
        dst_tokens = (dst_pages[:, None] * page_size + offsets[None, :]).ravel()
        length = plan["length"]
        lengths = np.full(len(src_tokens), length, dtype=np.uint64)
        # Merge only when each transferred token occupies the WHOLE source
        # and destination token. Partial head slices must retain their stride.
        if length == plan["src_stride"] == plan["dst_stride"]:
            boundary = np.ones(len(src_tokens), dtype=bool)
            boundary[1:] = ((src_tokens[1:] != src_tokens[:-1]+1)
                            | (dst_tokens[1:] != dst_tokens[:-1]+1))
            starts = np.flatnonzero(boundary)
            ends = np.concatenate((starts[1:], [len(src_tokens)]))
            lengths = (ends-starts).astype(np.uint64) * length
            src_tokens, dst_tokens = src_tokens[starts], dst_tokens[starts]
        src_addr = (plan["src_ptrs"][:, None]
                    + src_tokens[None, :] * np.uint64(plan["src_stride"])
                    + np.uint64(plan["src_offset"])).ravel()
        dst_addr = (plan["dst_ptrs"][:, None]
                    + dst_tokens[None, :] * np.uint64(plan["dst_stride"])
                    + np.uint64(plan["dst_offset"])).ravel()
        lens = np.tile(lengths, len(plan["src_ptrs"]))
        src_array = np.column_stack((src_addr, lens, np.full_like(
            src_addr, _nixl_device_id(plan["src_mem_kind"], self.kv_args.gpu_id))))
        dst_array = np.column_stack((dst_addr, lens, np.full_like(
            dst_addr, _nixl_device_id(plan["dst_mem_kind"], plan["dst_gpu_id"]))))
        src_descs = self.agent.get_xfer_descs(src_array, plan["src_mem_kind"])
        dst_descs = self.agent.get_xfer_descs(dst_array, plan["dst_mem_kind"])
        handle = self.agent.initialize_xfer(
            "WRITE", src_descs, dst_descs, peer_name, notif.encode("ascii"))
        if not handle:
            raise Exception("KVSender failed to create on-demand slice transfer")
        if self.agent.transfer(handle) == "ERR":
            raise Exception("KVSender failed to post on-demand slice transfer")
        return handle
'''

def build(source=None):
    if source is None:
        source=OUT/'original-conn.py' if (OUT/'original-conn.py').exists() else SOURCE
    original = source.read_text()
    tree = ast.parse(original)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'NixlKVManager')
    replacements = {'_init_hetero_tp_prep_handle': INIT, 'send_kvcache_slice': SEND}
    lines = original.splitlines(keepends=True)
    nodes = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in replacements]
    assert len(nodes) == 2
    for n in sorted(nodes, key=lambda n:n.lineno, reverse=True):
        lines[n.lineno-1:n.end_lineno] = [replacements[n.name]]
    patched = ''.join(lines)
    ast.parse(patched)
    OUT.mkdir(exist_ok=True)
    (OUT/'original-conn.py').write_text(original)
    (OUT/'conn.py').write_text(patched)
    (OUT/'nixl-ondemand.patch').write_text(''.join(difflib.unified_diff(
        original.splitlines(keepends=True), patched.splitlines(keepends=True),
        fromfile='a/python/sglang/srt/disaggregation/nixl/conn.py',
        tofile='b/python/sglang/srt/disaggregation/nixl/conn.py')))
    meta={'name':'hetero-tp-request-descriptors-v1',
          'original_sha256':hashlib.sha256(original.encode()).hexdigest(),
          'patched_sha256':hashlib.sha256(patched.encode()).hexdigest(),
          'scope':'Only heterogeneous-TP KV descriptor preparation/transfer; equal-TP path, weights, precision, head mapping and notifications retained.'}
    (OUT/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,help='Original conn.py extracted from the supplied image')
    build(parser.parse_args().source)
