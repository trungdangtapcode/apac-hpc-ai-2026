"""Freeze an observed same-deployment N62->N64 frontier after exact reproduction."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,tempfile
O=Path(__file__).resolve().parent;R=O.parent;C=R/'serving-tuning-10/s21-dg8192-hpc-n60-control';B=R/'serving-tuning-10/s28-h200-n62-n64-screen';assert not B.exists(),'Never rewrite a frozen payload'
proof=json.loads((R/'research-review-24962-20261021/REVIEW.json').read_text());assert proof['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS' and proof['full_scored_protocol_equal'] and abs(proof['repeat_delta_goodput_percent'])<.04
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=C,check=True,capture_output=True);B.mkdir();files=[line.split('  ',1)[1] for line in (C/'SHA256SUMS').read_text().splitlines()]
for name in files:shutil.copyfile(C/name,B/name)
p=B/'job.sbatch';t=p.read_text().replace(C.name,B.name).replace('export QWEN_TUNE_NS=60','export QWEN_TUNE_NS="62 64"');p.write_text(t)
p=B/'benchmark.sh';t=p.read_text();assert t.count('run_benchmark "$N" confirm 60 120')==1;t=t.replace('run_benchmark "$N" confirm 60 120','run_benchmark "$N" screen 20 40').replace("r['phase']=='confirm'","r['phase']=='screen'");p.write_text(t)
c=json.loads((B/'config.json').read_text());c.update(experiment=B.name,source_experiment=C.name,source_job='24964',retained_exact_reference_jobs=['24915','24962'],concurrency=[62,64],control_concurrency=62,candidate_concurrency=64,fresh_control_job='same allocation: screen/n62',matched_concurrency=None,changed_factor={'within_deployment_concurrency':[62,64]},purpose='Short unranked observed N62->N64 load screen after exact repeat; respect actual17-minute partition ceiling',phase='screen',confirm_warmup_s=20,confirm_measure_s=40,screen_unranked=True,walltime_minutes=17,quality_validation_required=True,resource_monitor=True,control_experiment='same deployment at N62',practical_gain_gate_fraction=.01,graph_maximum_decode=64,performance_comparison='N64 versus same-job observedN62; observer-off24962 is context only');(B/'config.json').write_text(json.dumps(c,indent=2)+'\n')
for name in files:
 if name in ['benchmark.sh','job.sbatch','config.json']:continue
 assert (B/name).read_bytes()==(C/name).read_bytes(),name
assert '--cuda-graph-max-bs-decode 64' in (B/'worker.sh').read_text();assert '--scheduler-recv-interval 2' not in (B/'worker.sh').read_text()
for p in B.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in list(B.glob('*.sh'))+[B/'job.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
# Execute the actual inherited load-gate loop with controlled fake measurements.
text=(B/'benchmark.sh').read_text();a=text.index('for N in ${QWEN_TUNE_NS');b=text.index('if [[ ${QWEN_DIAGNOSTIC_PROFILE',a);loop=text[a:b];cases=[]
with tempfile.TemporaryDirectory(prefix='n64-gate-') as temporary:
 D=Path(temporary)
 prefix='''set -euo pipefail
ART=$1
export ART
QWEN_TUNE_NS="62 64"
QWEN_BENCHMARK_DEADLINE=$(($(date +%s)+10000))
run_benchmark() {
 echo "$1" >> "$ART/calls"
 python3 - "$1" <<'MEASUREMENT'
import json,os,sys
from pathlib import Path
n=int(sys.argv[1]);row=dict(phase='screen',concurrency=n,sla_pass=os.environ['CASE']!='sla_fail',cancelled_requests=0,errors=int(os.environ['CASE']=='request_error'),requests=10)
(Path(os.environ['ART'])/'summary.json').write_text(json.dumps([row]))
MEASUREMENT
}
'''
 for case,wanted in [('pass',[62,64]),('sla_fail',[62]),('request_error',[62]),('no_time',[])]:
  art=D/case;art.mkdir();script=prefix+('QWEN_BENCHMARK_DEADLINE=0\n' if case=='no_time' else '')+loop
  r=subprocess.run(['bash','-c',script,'gate',str(art)],env={**__import__('os').environ,'CASE':case},capture_output=True,text=True);assert r.returncode==0,r.stderr
  calls=[int(x) for x in (art/'calls').read_text().splitlines()] if (art/'calls').exists() else [];assert calls==wanted,(case,calls)
  cases.append(dict(case=case,actual_run_sequence=calls,expected=wanted,passed=True))
(O/'load-gate-validation.json').write_text(json.dumps(dict(passed=True,cases=cases,scope='Actual inherited shell loop against controlled CPU measurement fixtures; no GPU or AIPerf execution'),indent=2)+'\n')
(B/'SHA256SUMS').write_text(''.join(hashlib.sha256((B/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in files))
pilot=dict(platform='H200',id=B.name,bundle=str(B),planned_ns=[62,64],state='PREPARED_NOT_SUBMITTED',minutes=17,max_su=None,payload_sha256={name:hashlib.sha256((B/name).read_bytes()).hexdigest() for name in files})
(O/'pilots.json').write_text(json.dumps([pilot],indent=2)+'\n');(O/'validation.json').write_text(json.dumps(dict(passed=True,source_bundle=str(C),retained_reference_job='24962',source_native_controls_unchanged=True,benchmark_only_duration_and_screen_label_changed=True,resource_observation_identical_between_points=True,load_sequence=[62,64],load_gate_fixtures=4,minutes=17,gpus=16,pbs_su_reserved=0,scope='One shared observeddeployment; only within-jobofferedconcurrency changes, unmeasured'),indent=2)+'\n');print('Frozen17-minute matched observed short screen; unranked, not submitted')
