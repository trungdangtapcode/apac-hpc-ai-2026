#!/usr/bin/env python3
"""Validate DP chunk division and page-size alignment against pinned source, CPU only."""
import hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent
source_path=B/'pinned-source/sgl-workspace/sglang/python/sglang/srt/server_args.py'
source=source_path.read_text()
required=('self.chunked_prefill_size = self.chunked_prefill_size // self.dp_size',
          'assert self.tp_size % self.dp_size == 0',
          'self.chunked_prefill_size % self.page_size == 0',
          'chunked_prefill_size must be divisible by page_size')
missing=[term for term in required if term not in source]
if missing: raise SystemExit('FAIL_CLOSED pinned ServerArgs chunk constraints changed: '+repr(missing))
source_sha=hashlib.sha256(source_path.read_bytes()).hexdigest()
def derive(global_chunk, dp_size, page_size):
    resolved=global_chunk//dp_size
    return {'global_chunk':global_chunk,'dp_size':dp_size,'resolved_per_rank_chunk':resolved,
            'page_size':page_size,'global_floor_division_remainder':global_chunk%dp_size,
            'page_divisibility_remainder':resolved%page_size,
            'valid':resolved%page_size==0}
worker=(B/'worker.sh').read_text()
if worker.count('--chunked-prefill-size 10240') != 1: raise SystemExit('FAIL_CLOSED worker global chunk flag is not exactly 10240')
fixtures=[derive(8192,5,64),derive(10240,5,64)]
assert fixtures[0]['resolved_per_rank_chunk']==1638 and fixtures[0]['page_divisibility_remainder']==38 and not fixtures[0]['valid']
assert fixtures[1]['resolved_per_rank_chunk']==2048 and fixtures[1]['page_divisibility_remainder']==0 and fixtures[1]['valid']
actual=derive(10240,5,64)
if not actual['valid']: raise SystemExit('FAIL_CLOSED candidate chunk does not align with page size')
result={'state':'PASS_CPU_SOURCE_BACKED_CHUNK_PREFLIGHT','source':str(source_path.relative_to(B)),'source_sha256':source_sha,'constraints_verified':required,'fixtures':fixtures,'candidate':actual,'model_imported':False,'gpu_imported':False}
if len(sys.argv)>1: Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,sort_keys=True))
