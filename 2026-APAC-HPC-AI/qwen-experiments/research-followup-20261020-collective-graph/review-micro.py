"""Review every rank and use the worst-rank graph latency in the paired screen."""
from pathlib import Path
import argparse,collections,gzip,hashlib,json,statistics
parser=argparse.ArgumentParser();parser.add_argument('snapshot',type=Path);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();snapshot=args.snapshot;seal=json.loads((snapshot/'evidence-sha256.json').read_text())
for name,digest in seal.items():assert hashlib.sha256((snapshot/name).read_bytes()).hexdigest()==digest,name
runs=list((snapshot/'runs').iterdir());assert len(runs)==1;run=runs[0];accounting=(snapshot/'pbs-accounting.txt').read_text();assert 'Exit_status = 0' in accounting
config=json.loads((run/'submitted/config.json').read_text());shapes=config['token_counts'];operations=config['graph_operations'];assert operations==32;rank_files=sorted((run/'micro').glob('rank-*-results.json'));assert len(rank_files)==8
points=collections.defaultdict(list);ranks=set()
for file in rank_files:
 data=json.loads(file.read_text());assert data['complete'];rank=data['metadata']['rank'];assert rank not in ranks;ranks.add(rank);assert data['metadata']['world_size']==8 and 'H100' in data['metadata']['gpu'];assert data['metadata']['config']==config
 rows=data['points'];assert len(rows)==len(shapes)*3*2
 expected={(m,s,r) for m in shapes for s in ['auto','oneshot','twoshot'] for r in range(2)}
 assert {(p['tokens'],p['strategy'],p['repetition']) for p in rows}==expected
 for row in rows:
  assert row['local_numerical_check_passed'] and row['inputs_unchanged'];samples=row['graph_us_samples'];assert len(samples)==5 and all(0<t<1e6 for t in samples);assert row['median_graph_us']==statistics.median(samples);assert row['graph_operations']==operations;assert row['median_collective_us']==row['median_graph_us']/operations;assert row['collective_us_samples']==[v/operations for v in samples]
  expected_strategy=('ONESHOT' if row['tokens']<=16 else 'TWOSHOT') if row['strategy']=='auto' else row['strategy'].upper();assert row['resolved_strategy']==expected_strategy
  points[(row['tokens'],row['strategy'],row['repetition'])].append(dict(rank=rank,median_us=row['median_graph_us']/operations,max_norm_abs_error=row['max_norm_abs_error'],max_residual_abs_error=row['max_residual_abs_error']))
assert ranks==set(range(8));trace_files=list((run/'micro').glob('*.trace.json.gz'));assert len(trace_files)==24
traces=[]
for file in trace_files:
 with gzip.open(file,'rt') as handle:trace=json.load(handle)
 counts=collections.Counter(event['name'] for event in trace['traceEvents'] if event.get('cat')=='kernel');assert counts
 traces.append(dict(path=str(file.relative_to(snapshot)),kernels=dict(counts)))
summary=[]
for m in shapes:
 for repetition in range(2):
  values={s:max(p['median_us'] for p in points[(m,s,repetition)]) for s in ['auto','oneshot','twoshot']}
  summary.append(dict(tokens=m,repetition=repetition,worst_rank_collective_us=values,oneshot_vs_auto_percent=(values['oneshot']/values['auto']-1)*100))
result=dict(job=run.name,state='LOCAL_MICROBENCH_COMPLETENESS_NUMERICAL_TRACE_PASS',graph_operations=operations,rank_count=8,point_count=sum(len(v) for v in points.values()),trace_count=len(traces),summary=summary,traces=traces,model_goodput_measured=False,official_accuracy_verified=False,interpretation='Worst-rank median per-collective CUDA-event time from 32-call graphs; two reversed-order rounds, not a confidence interval or a model speedup. Kernel numerical tolerance is local sanity only. Require a model/control experiment and full output gates before any serving claim.')
args.out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(job=run.name,state=result['state'],summary=summary),indent=2))
