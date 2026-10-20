"""Amortise host graph-launch cadence before interpreting the kernel strategy."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,tarfile
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;src=R/'nscc-pbs/h100-mnnvl-strategy-micro-52';dst=R/'nscc-pbs/h100-mnnvl-graph32-micro-53';assert not dst.exists()
assert json.loads((R/'research-followup-20261020-collective/222022-micro-review.json').read_text())['state']=='LOCAL_MICROBENCH_COMPLETENESS_NUMERICAL_TRACE_PASS'
shutil.copytree(src,dst)
f=dst/'benchmark.pbs';f.write_text(f.read_text().replace(src.name,dst.name).replace('ap42-mnnvl-micro52','ap42-mnnvl-graph53'))
f=dst/'bench.py';s=f.read_text();before="                with torch.cuda.graph(graph):\n                    run()";after="                with torch.cuda.graph(graph):\n                    for _ in range(config['graph_operations']):\n                        run()";assert s.count(before)==1;s=s.replace(before,after)
s=s.replace('for _ in range(20):',"for _ in range(config['graph_replays_per_sample']):").replace('start.elapsed_time(end) * 1000 / 20',"start.elapsed_time(end) * 1000 / config['graph_replays_per_sample']")
needle="median_graph_us=statistics.median(samples),";replacement=needle+" graph_operations=config['graph_operations'],\n                           collective_us_samples=[v / config['graph_operations'] for v in samples],\n                           median_collective_us=statistics.median(samples) / config['graph_operations'],";assert s.count(needle)==1;s=s.replace(needle,replacement);f.write_text(s)
f=dst/'config.json';c=json.loads(f.read_text());c.update(experiment=dst.name,source_experiment=src.name,source_job='222022.pbs111',graph_operations=32,graph_replays_per_sample=10,timing_refinement='32 collectives per captured graph to amortise CPU graph-launch cadence; no model speedup inferred');f.write_text(json.dumps(c,indent=2)+'\n')
for f in dst.iterdir():
 if f.suffix=='.py':ast.parse(f.read_text())
 if f.suffix in {'.pbs','.sh'}:subprocess.run(['bash','-n',str(f)],check=True)
 if f.name not in {'benchmark.pbs','bench.py','config.json','SHA256SUMS'}:assert f.read_bytes()==(src/f.name).read_bytes()
h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()))
pilot=dict(id=dst.name,bundle=str(dst),platform='H100',kind='isolated_microbenchmark',requested_gpus=8,minutes=10,max_su=8*128/6,payload_sha256=h,state='PREPARED_NOT_SUBMITTED',planned_ns=[],model_loaded=False);(O/'pilot.json').write_text(json.dumps(pilot,indent=2)+'\n')
with tarfile.open(O/'pbs-bundles.tar.gz','w:gz') as t:t.add(dst,arcname=dst.name)
(O/'validation.json').write_text(json.dumps(dict(passed=True,python_shell_syntax_pass=True,graph_operations=32,graph_replays_per_sample=10,shapes_precision_strategy_and_numerical_gates_unchanged=True,unmodified_operational_files_byte_identical=True,gpu_behavior_unverified=True),indent=2)+'\n')
print('Frozen graph32 strategy screen')
