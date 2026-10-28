#!/usr/bin/env python3
"""CPU functional check of native batching against exact tokenizer IDs."""
import asyncio,hashlib,json,os
from pathlib import Path
from transformers import AutoTokenizer
from sglang.srt.managers.async_dynamic_batch_tokenizer import AsyncDynamicbatchTokenizer
import sglang.srt.managers.async_dynamic_batch_tokenizer as native
Q=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');D=Q/'h200-dynamic-tokenizer-20261028'
source=D/'source/sgl-workspace/sglang/python/sglang/srt/managers/async_dynamic_batch_tokenizer.py'
assert hashlib.sha256(Path(native.__file__).read_bytes()).digest()==hashlib.sha256(source.read_bytes()).digest()
assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
tok=AutoTokenizer.from_pretrained('/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8',local_files_only=True,trust_remote_code=True)
texts=[f'Request {i}: '+(['To be, or not to be: that is the question. '*300,'The quality of mercy is not strained. '*300,'Unicode: Việt Nam 日本語 你好. '*200,'def compute(x): return x * 2\n'*200][i%4]) for i in range(64)]
reference=[tok(x)['input_ids'] for x in texts]
async def check(wait):
 b=AsyncDynamicbatchTokenizer(tok,max_batch_size=32,batch_wait_timeout_s=wait)
 try:
  got=await asyncio.wait_for(asyncio.gather(*(b.encode(x) for x in texts)),timeout=60)
  assert [x['input_ids'] for x in got]==reference
  single=await asyncio.wait_for(b.encode(texts[0]),timeout=10);assert single['input_ids']==reference[0]
 finally:
  if b._batcher_task:
   b._batcher_task.cancel()
   try:await b._batcher_task
   except asyncio.CancelledError:pass
  b._executor.shutdown(wait=True)
 return {'wait_seconds':wait,'batch_requests':64,'single_request':1,'exact_input_ids':'PASS'}
async def main():return [await check(w) for w in [0.0002,0.002]]
r={'state':'EXACT_DYNAMIC_TOKENIZER_IDS_PASS','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':asyncio.run(main()),'gpu_performance':'NOT_MEASURED'}
(Q/f'runs/{os.environ["SLURM_JOB_ID"]}/tokenizer-proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
