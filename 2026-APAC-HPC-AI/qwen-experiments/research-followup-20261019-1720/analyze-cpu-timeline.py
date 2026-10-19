from pathlib import Path
import collections,gzip,hashlib,json,re
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');O=R/'research-followup-20261019-1720';snapshot=Path(json.loads((O/'collect-221886.json').read_text())['destination']);seal=json.loads((snapshot/'evidence-sha256.json').read_text());run=snapshot/'runs/221886.pbs111';rows=[]
def union(xs):
 total=0;end=None
 for t,d in sorted(xs):
  if end is None or t>end:total+=d;end=t+d
  elif t+d>end:total+=t+d-end;end=t+d
 return total
for f in sorted((run/'diagnostic-profile').rglob('*.trace.json.gz')):
 assert hashlib.sha256(f.read_bytes()).hexdigest()==seal[str(f.relative_to(snapshot))]
 with gzip.open(f,'rt') as h:t=json.load(h)
 events=[e for e in t['traceEvents'] if e.get('ph')=='X' and e.get('dur',0)>0];cats=collections.Counter(e.get('cat') for e in events);kernels=[e for e in events if e.get('cat')=='kernel'];assert kernels and cats['cpu_op']>0
 rt=collections.Counter();ops=collections.Counter();annotations=collections.Counter()
 for e in events:
  target={'cuda_runtime':rt,'cpu_op':ops,'user_annotation':annotations}.get(e.get('cat'))
  if target is not None:target[e['name']]+=e['dur']
 start=min(e['ts'] for e in kernels);end=max(e['ts']+e['dur'] for e in kernels);span=end-start;busy=union([(e['ts'],e['dur']) for e in kernels])
 rows.append(dict(role=f.parent.name,rank=int(re.search(r'-TP-(\d+)(?:-EP-|\.trace)',f.name).group(1)),trace=str(f),sha256=seal[str(f.relative_to(snapshot))],categories=dict(cats),gpu_kernel_span_us=span,gpu_kernel_busy_union_us=busy,gpu_kernel_uncovered_us=span-busy,gpu_kernel_coverage=busy/span,top_cpu_ops=ops.most_common(10),top_cuda_runtime=rt.most_common(10),top_annotations=annotations.most_common(12)))
for role,n in [('prefill-0',4),('prefill-1',4),('decode-0',8)]:assert sorted(x['rank'] for x in rows if x['role']==role)==list(range(n))
result=dict(job='221886.pbs111',trace_count=len(rows),all_ranks_cpu_and_gpu_present=True,traces=rows,interpretation='Post-score N48 diagnostic with profiling overhead. CPU op durations may nest; CUDA event synchronisation is waiting time, not independent CPU work. Kernel union covers only recorded kernel intervals and gaps may include communication, scheduler waits, transfers, profiler overhead or other causes. Do not treat summed durations or uncovered intervals as causal end-to-end bottleneck fractions.')
(O/'cpu-timeline-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
for role in ['prefill-0','prefill-1','decode-0']:
 a=[x for x in rows if x['role']==role];print(role,'kernel coverage range',min(x['gpu_kernel_coverage'] for x in a),max(x['gpu_kernel_coverage'] for x in a),'rank0 CPU',a[0]['top_cpu_ops'][:5],'rank0 runtime',a[0]['top_cuda_runtime'][:3],flush=True)
