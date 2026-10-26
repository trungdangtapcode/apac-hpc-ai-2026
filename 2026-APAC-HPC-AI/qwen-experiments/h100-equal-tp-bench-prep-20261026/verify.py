#!/usr/bin/env python3
"""CPU-only source, stage, and N24 scoring-gate fixtures; never GPU evidence."""
from pathlib import Path
import ast,copy,hashlib,json,subprocess,sys,tempfile,shutil,os
ROOT=Path(__file__).resolve().parents[3];Q=ROOT/'2026-APAC-HPC-AI/qwen-experiments'
B=Q/'eagle3-h100-equal-tp-bench-n24-20261026';P=Q/'eagle3-h100-equal-tp-observer-r2-20261026'
H100=Q/'nscc-pbs/h100-cpu-envelope-legacy-n54-79';BASE=Q/'h100-review-225227-225228-20261026/curated-r2/h100-incumbent-n54-refresh-20261026/runs/225227.pbs111'
# Retain only raw expected-input shape, never use identity/metadata of an unrelated score as N24 evidence.
expected=json.loads((B/'expected-input-config.json').read_text());assert expected['phases'][1]['concurrency']==24 and expected['runtime']['workers']==24
assert (B/'worker.sh').read_bytes()==(P/'worker.sh').read_bytes()
assert (B/'placement.tsv').read_bytes()==(P/'placement.tsv').read_bytes()
assert (B/'nixl-conn.py').read_bytes()==(P/'nixl-conn.py').read_bytes()
assert (B/'pd-observer/observer.py').read_bytes()==(P/'pd-observer/observer.py').read_bytes()
assert json.loads((B/'config.json').read_text())['allocation']['max_su']==512.0
assert json.loads((B/'config.json').read_text())['allocation']['wall_seconds']==1800
controller=json.loads(subprocess.check_output(['python3','-B',str(B/'phase-controller.py'),'deadlines','1000'],text=True))
assert controller['main_envelope_seconds']==1720 and controller['teardown_deadline']-controller['t0']==1720
assert subprocess.check_output(['python3','-B',str(B/'phase-controller.py'),'remaining','1000','quality','1390','1390'],text=True).strip()=='250'
# Build a clearly temporary N24 input/export fixture to prove configured N24 is accepted by the local gate.
with tempfile.TemporaryDirectory(prefix='h100-n24-local-gate-fixture-') as td:
 a=Path(td);(a/'confirm/n24/artifacts').mkdir(parents=True)
 (a/'config.json').write_text(json.dumps({'concurrency':24,'benchmark_phase':'confirm'}))
 row={'metadata':{'benchmark_phase':'profiling'},'metrics':{'time_to_first_token':{'value':100.0,'unit':'ms'},'inter_token_latency':{'value':10.0,'unit':'ms'}}}
 exp=copy.deepcopy(expected);exp['endpoint']['urls']=['http://127.0.0.1:8000'];exp['artifacts']['dir']=str(a/'confirm/n24/artifacts')
 export={'input_config':exp,'request_count':{'avg':1,'unit':'requests'},'good_request_fraction':{'avg':1.0,'unit':'ratio'},'goodput':{'avg':1.25,'unit':'requests/sec'},'good_request_count':{'avg':1,'unit':'requests'}}
 (a/'confirm/n24/artifacts/profile_export_aiperf.json').write_text(json.dumps(export))
 (a/'confirm/n24/artifacts/profile_export.jsonl').write_text(json.dumps(row)+'\n')
 (a/'confirm/n24/client.log').write_text('Phase profiling (profiling) complete | completed=1, cancelled=0, errors=0\n')
 (a/'summary.json').write_text(json.dumps([{'phase':'confirm','concurrency':24,'requests':1,'errors':0,'cancelled_requests':0,'sla_pass':True,'good_request_fraction':1.0,'good_output_tokens_s':250.0}]))
 (a/'output-smoke.json').write_text((B/'reference-output-smoke.json').read_text())
 retrieval=[]
 for i in range(12):
  val=str(73160429+i*137);retrieval.append({'name':f'retrieval-{i}','expected':val,'passed':True,'text':val,'response':{'choices':[{'message':{'content':val}}]}})
 (a/'long-context-check.json').write_text(json.dumps({'passed':12,'total':12,'errors':0,'cases':retrieval}))
 r=subprocess.run([sys.executable,'-B',str(B/'check-benchmark.py'),'full',str(a)],capture_output=True,text=True)
 assert r.returncode==0,r.stdout+r.stderr;res=json.loads(r.stdout);assert res['score']['good_output_tokens_per_second']==250.0 and res['smoke']['passed']==7 and res['retrieval']['passed']==12
 # The actual accepted H100 N54 raw profile must be rejected by the new N24 recipe.
 (a/'config.json').write_text(json.dumps({'concurrency':54,'benchmark_phase':'confirm'}))
 r=subprocess.run([sys.executable,'-B',str(B/'check-benchmark.py'),'score',str(a)],capture_output=True,text=True)
 assert r.returncode!=0 and 'differs from expected workload' in r.stdout
# Parent actual N54 full profile passes the parameterized score gate only under its own N54 schema.
with tempfile.TemporaryDirectory(prefix='h100-parent-n54-replay-') as td:
 a=Path(td); shutil.copyfile(BASE/'summary.json',a/'summary.json')
 cfg={'concurrency':54,'benchmark_phase':'confirm'};(a/'config.json').write_text(json.dumps(cfg))
 (a/'confirm/n54').mkdir(parents=True);shutil.copyfile(BASE/'confirm/n54/client.log',a/'confirm/n54/client.log')
 shutil.copytree(BASE/'confirm/n54/artifacts',a/'confirm/n54/artifacts',copy_function=shutil.copy2)
 n54=copy.deepcopy(expected);n54['phases'][0]['concurrency']=54;n54['phases'][1]['concurrency']=54;n54['runtime']['workers']=54
 from importlib.util import spec_from_file_location,module_from_spec
 spec=spec_from_file_location('gates',B/'performance_gates.py');g=module_from_spec(spec);spec.loader.exec_module(g)
 got=g.check_aiperf(a,n54,200);assert got['completed']==1512 and got['good_output_tokens_per_second']>2399
result={'state':'PASS_CPU_PREPARATION_ONLY','checks':['parent serving/device/observer source parity','30-minute stage-deadline arithmetic','synthetic configured N24 score+smoke+retrieval gates accepted','wrong N54 workload rejected under N24 recipe','recovered N54 control accepted by same parameterized raw score gate when using its own N54 recipe'],'limits':'Synthetic N24 fixture validates parser/controller behavior only, not GPU execution or measured score.'}
(PREP:=Q/'h100-equal-tp-bench-prep-20261026').mkdir(exist_ok=True)
(PREP/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result['state'])
