#!/usr/bin/env python3
"""Execute pinned descriptor methods with real NumPy and a CPU memory backend."""
from pathlib import Path
from types import MethodType, ModuleType, SimpleNamespace
from typing import List, Tuple
from unittest.mock import patch
import hashlib
import json
import logging
import sys
import numpy as np
import descriptor as d

O = Path(__file__).resolve().parent
helper = d.extract(O / 'staging_buffer.py', 'compute_head_slice_params', globs={'Tuple': Tuple})
module = ModuleType('sglang.srt.disaggregation.common.staging_buffer')
module.compute_head_slice_params = helper
scope = {'np': np, 'List': List, 'Tuple': Tuple, 'logger': logging.getLogger(__name__),
         '_nixl_device_id': d.extract(O / 'nixl-conn.py', '_nixl_device_id')}
init = d.extract(O / 'nixl-conn.py', '_init_hetero_tp_prep_handle', 'NixlKVManager', scope)
send = d.extract(O / 'nixl-conn.py', 'send_kvcache_slice', 'NixlKVManager', scope)
select = d.extract(O / 'source/common-conn.py', 'get_mha_kv_ptrs_with_pp', 'CommonKVManager', scope)
size = 190 * d.PAGE_COUNT * d.STRIDE
rows = []
for case_i, (case, src_layers, dst_layers) in enumerate(d.CASES):
    for dst_rank in range(8):
        src_rank = dst_rank // 2
        src_base, dst_base = 0x1000000, 0x2000000
        source = bytearray(size)
        dest = bytearray([0xA5]) * size
        for region in range(190):
            for page in range(d.PAGE_COUNT):
                off = (region*d.PAGE_COUNT + page) * d.STRIDE
                source[off:off+d.STRIDE] = d.pattern(src_rank, case_i, region, page)
        class CPUBackend:
            posted = 0
            def get_xfer_descs(self, descriptors, kind):
                assert kind == 'VRAM'
                return np.array(descriptors, copy=True)
            def initialize_xfer(self, op, source_rows, dest_rows, peer, notification):
                assert op == 'WRITE' and peer == 'registered-peer'
                assert len(source_rows) == len(dest_rows) == src_layers*4
                self.source_rows, self.dest_rows = source_rows, dest_rows
                return 'cpu-handle'
            def transfer(self, handle):
                assert handle == 'cpu-handle'
                self.posted += 1
                for (sp, sn, sd), (dp, dn, dd) in zip(self.source_rows, self.dest_rows):
                    sp, dp, sn, dn = map(int, (sp, dp, sn, dn))
                    assert sn == dn == d.STRIDE and int(sd) == int(dd) == 0
                    dest[dp-dst_base:dp-dst_base+dn] = source[sp-src_base:sp-src_base+sn]
                return 'IN PROGRESS'
        backend = CPUBackend()
        args = SimpleNamespace(engine_rank=src_rank, prefill_start_layer=0, page_size=1,
            total_kv_head_num=4, kv_head_num=1, gpu_id=0,
            kv_item_lens=[d.STRIDE] * (2*src_layers),
            kv_data_ptrs=[src_base+i*4*d.STRIDE for i in range(2*src_layers)])
        peer = SimpleNamespace(decode_tp_size=8, decode_tp_rank=dst_rank,
            dst_kv_item_len=d.STRIDE, gpu_id=0,
            dst_kv_ptrs=[dst_base+i*4*d.STRIDE for i in range(2*dst_layers)])
        manager = SimpleNamespace(kv_args=args, attn_tp_size=4,
            agent=d.guarded_agent(backend, [(src_base, size)], [(dst_base, size)]))
        manager.get_mha_kv_ptrs_with_pp = MethodType(select, manager)
        with patch.dict(sys.modules, {module.__name__: module}):
            init(manager, 'registered-peer', peer)
        handle = send(manager, 'registered-peer', d.SRC_PAGES, d.DST_PAGES, 'cpu-notification')
        assert handle == 'cpu-handle' and backend.posted == 1
        assert bytes(dest) == d.expected_destination(case_i, src_rank, src_layers)
        rows.append({'case': case, 'src_rank': src_rank, 'dst_rank': dst_rank,
            'descriptor_pairs': len(backend.source_rows), 'sha256': hashlib.sha256(dest).hexdigest()})
print(json.dumps({'passed': True, 'numpy_version': np.__version__, 'python_version': sys.version,
    'native_method_cases': len(rows), 'actual_whole_head_coalescing_branch': True,
    'rows': rows, 'scope': 'CPU descriptor math and mocked copy only; no GPU, NIXL registration or network backend'}, indent=2))
