"""Classify actual sealed H200 both-phase profile kernels; no speed predictions."""
from pathlib import Path
import collections,gzip,hashlib,json,re
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent
run=R/'runs/24927';snapshot=R;d=run/'diagnostic-profile';seal={r['path']:r['sha256'] for r in json.loads((run/'artifact-manifest.json').read_text())['files']}
def checked(file):
 assert hashlib.sha256(file.read_bytes()).hexdigest()==seal[str(file.relative_to(snapshot))]
 return file
protocol=json.loads(checked(d/'protocol.json').read_text());requests=json.loads(checked(d/'requests.json').read_text());assert protocol['concurrency']==48 and protocol['trace_steps']=={'prefill':4,'decode':32}
roles={};rows=[]
for file in sorted(d.rglob('*.trace.json.gz')):
 checked(file)
 with gzip.open(file,'rt') as f:trace=json.load(f)
 kernels=[x for x in trace['traceEvents'] if x.get('cat')=='kernel' and x.get('dur',0)>0];assert kernels
 role=file.parent.name;rank=int(re.search(r'-TP-(\d+)(?:-EP-|\.trace)',file.name).group(1));rows.append(dict(role=role,rank=rank,trace=str(file),sha256=seal[str(file.relative_to(snapshot))],kernel_count=len(kernels),summed_kernel_us=sum(x['dur'] for x in kernels)))
 counter=roles.setdefault(role,collections.Counter())
 for k in kernels:counter[k['name']]+=k['dur']
for role,count in [('prefill-0',4),('prefill-1',4),('decode-0',8)]:assert sorted(x['rank'] for x in rows if x['role']==role)==list(range(count))
result=dict(job='24927',protocol=protocol,trace_count=len(rows),requests=len(requests),successful_requests=sum(x.get('ok') is True and 'error' not in x for x in requests),traces=rows,roles={},interpretation='Separate N48 diagnostic, not ranked traffic. Durations summed across ranks/events, not elapsed critical-path shares. No automatic attribution of unnamed kernels or end-to-end speed prediction.')
assert result['successful_requests']==len(requests)>0
for role,counter in roles.items():
 total=sum(counter.values());result['roles'][role]=dict(total_summed_kernel_us=total,top_kernels=[dict(name=name,summed_us=us,fraction=us/total) for name,us in counter.most_common(25)],named_hpc_group_gemm_fraction=sum(us for name,us in counter.items() if 'group_gemm_blockwise_fp8' in name)/total)
 result['roles'][role]['named_mnnvl_collective_fraction']=sum(us for name,us in counter.items() if 'trtllm_mnnvl_allreduce' in name)/total
 result['roles'][role]['named_flashinfer_paged_attention_fraction']=sum(us for name,us in counter.items() if 'BatchPrefillWithPagedKVCacheKernel' in name)/total
 result['roles'][role]['named_deep_gemm_fraction']=sum(us for name,us in counter.items() if 'deep_gemm::' in name)/total
 print(role,'named HPC group GEMM',round(100*result['roles'][role]['named_hpc_group_gemm_fraction'],3),'%')
 for name,us in counter.most_common(7):print(round(100*us/total,3),name[:220])
(O/'24927-profile.json').write_text(json.dumps(result,indent=2)+'\n');print('Requests',result['successful_requests'],'/',result['requests'],'traces',len(rows),flush=True)
