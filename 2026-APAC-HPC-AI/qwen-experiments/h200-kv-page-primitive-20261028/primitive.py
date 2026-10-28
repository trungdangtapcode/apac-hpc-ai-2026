#!/usr/bin/env python3
"""One-H200 BF16 native NHD pool and paged attention correctness primitive."""
import hashlib,inspect,json,math,os,traceback
from pathlib import Path
Q=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');D=Q/'h200-kv-page-primitive-20261028';A=Q/f'runs/{os.environ["SLURM_JOB_ID"]}'
result={'state':'RUNNING','scope':'One GPU, one constructed layer; no model serving, P/D transfer, accuracy or speed claim.','cases':[]}
def write():
 (A/'primitive.json').write_text(json.dumps(result,indent=2)+'\n')
try:
 import torch,flashinfer
 from types import SimpleNamespace
 from sglang.srt.mem_cache.memory_pool import MHATokenToKVPool
 assert torch.cuda.is_available() and torch.cuda.device_count()==1
 assert 'H200' in torch.cuda.get_device_name(0)
 pool_source=Path(inspect.getfile(MHATokenToKVPool));actual=hashlib.sha256(pool_source.read_bytes()).hexdigest()
 assert actual=='29ef7b37d2e12b1a4b674b97c33b3ceb05cd8421a3742eb33cb6a75f52896ddc'
 decode_source=Path(inspect.getfile(flashinfer.BatchDecodeWithPagedKVCacheWrapper));decode_sha=hashlib.sha256(decode_source.read_bytes()).hexdigest()
 assert decode_sha=='e7ee044795fa8e9885087c04987a80cf417d1b0d6456547839d455a4f7305307'
 model=Path('/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8/config.json');cfg=json.loads(model.read_text())
 assert (cfg['num_attention_heads'],cfg['num_key_value_heads'],cfg['head_dim'])==(64,4,128)
 result.update(pool_source_sha256=actual,flashinfer_decode_sha256=decode_sha,model_config_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),gpu_name=torch.cuda.get_device_name(0),gpu_uuid=str(torch.cuda.get_device_properties(0).uuid),constructed_layer_ids=[0],head_geometry_scope='Metadata-derived local GQA1 for TP4/TP8; does not establish observed full-model D-role registration heads.',full_role_attention_backend='NOT_STARTED; source predicts prefill automatic FA3 to FlashInfer change above page1')
 torch.manual_seed(2026);maxlen=4000;keys=torch.randn(maxlen,1,128,device='cuda',dtype=torch.bfloat16);values=torch.randn_like(keys)
 workspace=torch.zeros(128*1024*1024,device='cuda',dtype=torch.uint8)
 previous={}
 for tp in [4,8]:
  qheads=cfg['num_attention_heads']//tp;q=torch.randn(1,qheads,128,device='cuda',dtype=torch.bfloat16)
  for page in [1,16]:
   size=math.ceil(maxlen/page)*page
   pool=MHATokenToKVPool(size=size,page_size=page,dtype=torch.bfloat16,head_num=1,head_dim=128,layer_num=1,device='cuda',enable_memory_saver=False,kv_cache_layout='nhd')
   kbuf,vbuf=pool.get_kv_buffer(0);assert pool.store_dtype==torch.bfloat16 and pool.kv_cache_layout=='nhd'
   ptrs,lens,item_lens=pool.get_contiguous_buf_infos();assert len(ptrs)==len(lens)==len(item_lens)==2
   assert item_lens==[page*128*2]*2
   wrapper=flashinfer.BatchDecodeWithPagedKVCacheWrapper(workspace,kv_layout='NHD',use_tensor_cores=True)
   geometry={'tp_hypothesis':tp,'q_heads':qheads,'kv_heads':1,'page_tokens':page,'pool_class':type(pool).__name__,'layout':pool.kv_cache_layout,'dtype':str(pool.store_dtype),'k_shape':list(kbuf.shape),'v_shape':list(vbuf.shape),'k_stride':list(kbuf.stride()),'v_stride':list(vbuf.stride()),'region_lengths_bytes':lens,'item_lengths_bytes':item_lens,'token_stride_bytes':[x//page for x in item_lens],'layer_ids':'Constructed layer0 only; no real model layer registry'}
   for length in [15,16,17,31,32,33,4000]:
    loc=torch.arange(page,page+length,device='cuda',dtype=torch.int64)
    pool.set_kv_buffer(SimpleNamespace(layer_id=0),loc,keys[:length],values[:length]);torch.cuda.synchronize()
    assert torch.equal(kbuf[loc],keys[:length]) and torch.equal(vbuf[loc],values[:length])
    npages=math.ceil(length/page)
    indptr=torch.tensor([0,npages],device='cuda',dtype=torch.int32);indices=torch.arange(1,npages+1,device='cuda',dtype=torch.int32);last=torch.tensor([(length-1)%page+1],device='cuda',dtype=torch.int32)
    wrapper.plan(indptr,indices,last,num_qo_heads=qheads,num_kv_heads=1,head_dim=128,page_size=page,q_data_type=torch.bfloat16,kv_data_type=torch.bfloat16)
    output=wrapper.run(q,(kbuf.view(-1,page,1,128),vbuf.view(-1,page,1,128)));torch.cuda.synchronize()
    assert output.shape==q.shape and output.dtype==torch.bfloat16 and torch.isfinite(output).all()
    scores=torch.einsum('hd,ld->hl',q[0].float(),keys[:length,0].float())/math.sqrt(128)
    oracle=torch.einsum('hl,ld->hd',torch.softmax(scores,dim=-1),values[:length,0].float()).unsqueeze(0)
    rel=(torch.linalg.vector_norm(output.float()-oracle)/torch.linalg.vector_norm(oracle).clamp_min(1e-12)).item();maxabs=(output.float()-oracle).abs().max().item()
    assert rel<=0.01 and maxabs<=0.005,(tp,page,length,rel,maxabs)
    key=(tp,length)
    page_delta=None
    if page==1:previous[key]=output.clone()
    else:
     base=previous[key];page_delta=(torch.linalg.vector_norm(output.float()-base.float())/torch.linalg.vector_norm(base.float()).clamp_min(1e-12)).item();assert page_delta<=0.01
    result['cases'].append({'geometry':geometry,'length_tokens':length,'cache_write_exact':True,'relative_l2_vs_fp32_oracle':rel,'max_absolute_error_vs_fp32_oracle':maxabs,'relative_l2_vs_page1':page_delta,'primitive_backend':str(getattr(wrapper,'_backend','not_exposed'))});write()
   del pool,wrapper,kbuf,vbuf
 assert len(result['cases'])==28
 result['state']='PASS_NATIVE_BF16_PAGE1_PAGE16_PRIMITIVE';write();print(result['state'])
except BaseException as e:
 result.update(state='FAIL',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());write();raise
