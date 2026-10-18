"""Reclassify both profiles with source-backed DeepGEMM grouped-GEMM recognition."""
from pathlib import Path
import gzip,json,re,statistics,hashlib,datetime
R=Path.cwd();O=R/'research-followup-20261018-0800';results={}
for job in ['24263','24429']:
 run=R/'runs'/job;d=run/'diagnostic-profile';protocol=json.loads((d/'protocol.json').read_text());assert protocol['concurrency']==48 and protocol['trace_steps']=={'prefill':4,'decode':32};requests=json.loads((d/'requests.json').read_text());assert all(x.get('ok') is True and 'error' not in x for x in requests)
 rows=[]
 for file in sorted(d.rglob('*.trace.json.gz')):
  with gzip.open(file,'rt') as f:trace=json.load(f)
  events=[x for x in trace['traceEvents'] if x.get('cat')=='kernel' and x.get('dur',0)>0]
  total=sum(x['dur'] for x in events);assert total>0
  old=sum(x['dur'] for x in events if any(s in x.get('name','').lower() for s in ['fused_moe','moe_kernel','grouped_gemm','gemm_grouped','moe_align']))
  grouped=sum(x['dur'] for x in events if 'deep_gemm::' in x.get('name','') and re.search(r'\(deep_gemm::GemmType\)[12](?:,|>)',x['name']))
  reorder=sum(x['dur'] for x in events if any(s in x.get('name','').lower() for s in ['pre_reorder_deepgemm','post_reorder_deepgemm']) and not any(s in x.get('name','').lower() for s in ['fused_moe','moe_kernel','grouped_gemm','gemm_grouped','moe_align']))
  coll=sum(x['dur'] for x in events if any(s in x.get('name','').lower() for s in ['nccl','allreduce','all_reduce','allgather','reduce_scatter']))
  role=file.parent.name;rank=int(re.search(r'-TP-(\d+)(?:-EP-|\.trace)',file.name).group(1));rows.append(dict(trace=str(file),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),role=role,rank=rank,kernels=len(events),summed_kernel_us=total,legacy_moe_fraction=old/total,deepgemm_grouped_fraction=grouped/total,deepgemm_reorder_fraction=reorder/total,moe_associated_fraction=(old+grouped+reorder)/total,collective_fraction=coll/total))
 roles={}
 for role,count in [('prefill-0',4),('prefill-1',4),('decode-0',8)]:
  a=[x for x in rows if x['role']==role];assert len(a)==count and {x['rank'] for x in a}==set(range(count));roles[role]={k:statistics.mean(x[k] for x in a) for k in ['legacy_moe_fraction','deepgemm_grouped_fraction','deepgemm_reorder_fraction','moe_associated_fraction','collective_fraction']}
 results[job]=dict(roles=roles,trace_count=len(rows),successful_diagnostic_requests=len(requests),protocol=protocol,traces=rows,control_warnings=json.loads((d/'profile-control.json').read_text()))
(O/'profile-comparison.json').write_text(json.dumps(dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),classifier_source='Exact staged DeepGEMM types.cuh: Normal=0, MGroupedContiguous=1, MGroupedMasked=2. Include MoE-associated pre/post reorder names; normal GEMMs stay excluded.',scope='Descriptive shares of summed GPU kernel durations, not wall time or predicted speedup. Equal request concurrency/capture counts do not guarantee equal batches.',profiles=results),indent=2)+'\n')
for j,x in results.items():print(j,x['trace_count'],x['successful_diagnostic_requests'],x['roles'])
