from pathlib import Path
import json,gzip,re,collections,hashlib
O=Path('research-followup-20261018-1215');job='221284.pbs111';snapshot=Path(json.loads(Path('/tmp/ap42-collect-'+job+'.json').read_text())['destination']);d=snapshot/'runs'/job/'diagnostic-profile';requests=json.loads((d/'requests.json').read_text());protocol=json.loads((d/'protocol.json').read_text());assert protocol['concurrency']==48 and protocol['trace_steps']=={'prefill':4,'decode':32};roles={};rows=[]
for file in sorted(d.rglob('*.trace.json.gz')):
 with gzip.open(file,'rt') as f:t=json.load(f)
 events=[x for x in t['traceEvents'] if x.get('cat')=='kernel' and x.get('dur',0)>0];assert events;role=file.parent.name;rank=int(re.search(r'-TP-(\d+)(?:-EP-|\.trace)',file.name).group(1));row=dict(role=role,rank=rank,trace=str(file),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),kernel_count=len(events),total_us=sum(x['dur'] for x in events));rows.append(row);a=roles.setdefault(role,collections.Counter())
 for x in events:a[x['name']]+=x['dur']
for role,count in [('prefill-0',4),('prefill-1',4),('decode-0',8)]:assert sorted(x['rank'] for x in rows if x['role']==role)==list(range(count))
result=dict(protocol=protocol,trace_count=len(rows),requests=len(requests),successful_requests=sum(x.get('ok') is True and 'error' not in x for x in requests),traces=rows,roles={})
for role,a in roles.items():
 total=sum(a.values());result['roles'][role]=dict(total_summed_kernel_us=total,top_kernels=[dict(name=k,summed_us=v,fraction=v/total) for k,v in a.most_common(25)])
(O/'hpc-profile-kernels.json').write_text(json.dumps(result,indent=2)+'\n');print('requests',result['successful_requests'],result['requests'],'traces',len(rows))
for role,a in roles.items():
 print(role)
 for k,v in a.most_common(9):print(round(100*v/sum(a.values()),3),k[:420])
