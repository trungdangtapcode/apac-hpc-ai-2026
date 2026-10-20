"""Isolate PDL in the current AUTO collective instead of forcing a losing strategy."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,tarfile
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;src=R/'nscc-pbs/h100-mnnvl-graph32-micro-53';dst=R/'nscc-pbs/h100-mnnvl-pdl-micro-54';assert not dst.exists();assert json.loads((R/'research-followup-20261020-collective-graph/222023-micro-review.json').read_text())['state']=='LOCAL_MICROBENCH_COMPLETENESS_NUMERICAL_TRACE_PASS'
shutil.copytree(src,dst);p=dst/'benchmark.pbs';p.write_text(p.read_text().replace(src.name,dst.name).replace('ap42-mnnvl-graph53','ap42-mnnvl-pdl54'))
p=dst/'bench.py';s=p.read_text();old="""    strategies = [('auto', None, MNNVLAllreduceFusionStrategy.AUTO),
                  ('oneshot', True, MNNVLAllreduceFusionStrategy.ONESHOT),
                  ('twoshot', False, MNNVLAllreduceFusionStrategy.TWOSHOT)]""";new="""    strategies = [('pdl_on', None, MNNVLAllreduceFusionStrategy.AUTO, True),
                  ('pdl_off', None, MNNVLAllreduceFusionStrategy.AUTO, False)]""";assert old in s;s=s.replace(old,new).replace('for name, force, strategy in ordering:', 'for name, force, strategy, launch_pdl in ordering:').replace('launch_with_pdl=True, residual_out=', 'launch_with_pdl=launch_pdl, residual_out=').replace('repetition=repetition, graph_us_samples=samples,','repetition=repetition, launch_with_pdl=launch_pdl, graph_us_samples=samples,');p.write_text(s)
p=dst/'config.json';d=json.loads(p.read_text());d.update(experiment=dst.name,source_experiment=src.name,source_job='222023.pbs111',strategies=['pdl_on','pdl_off'],changed_factor='launch_with_pdl only; AUTO reduction strategy retained',timing_refinement='32 collectives per graph,10 replays per sample; PDL on/off screen');p.write_text(json.dumps(d,indent=2)+'\n')
for p in dst.iterdir():
 if p.suffix=='.py':ast.parse(p.read_text())
 if p.suffix in {'.pbs','.sh'}:subprocess.run(['bash','-n',str(p)],check=True)
 if p.name not in {'benchmark.pbs','bench.py','config.json','SHA256SUMS'}:assert p.read_bytes()==(src/p.name).read_bytes()
h={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dst.iterdir()) if p.is_file() and p.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()))
(O/'pilot.json').write_text(json.dumps(dict(id=dst.name,bundle=str(dst),platform='H100',kind='isolated_microbenchmark',requested_gpus=8,minutes=10,max_su=8*128/6,payload_sha256=h,state='PREPARED_NOT_SUBMITTED',planned_ns=[],model_loaded=False),indent=2)+'\n')
with tarfile.open(O/'pbs-bundles.tar.gz','w:gz') as t:t.add(dst,arcname=dst.name)
(O/'validation.json').write_text(json.dumps(dict(passed=True,python_shell_syntax_pass=True,auto_strategy_retained=True,launch_with_pdl_only_factor=True,graph32_timing_and_numerical_gates_unchanged=True,new_gpu_behavior_unverified=True),indent=2)+'\n');print('Prepared isolated PDL on/off screen')
