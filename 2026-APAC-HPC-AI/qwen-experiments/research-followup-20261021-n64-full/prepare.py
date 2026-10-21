"""Freeze fresh equally observed full N62/N64 deployments after short acceptance."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,shutil,subprocess
O=Path(__file__).resolve().parent;R=O.parent;C=R/'serving-tuning-10/s21-dg8192-hpc-n60-control'
review=json.loads((R/'research-review-25339-20261021/REVIEW.json').read_text());assert review['state']=='SHORT_LOCAL_PROTOCOL_SLA_OUTPUT_PASS' and review['practical_one_percent_screen_gate']
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=C,check=True,capture_output=True)
files=[line.split('  ',1)[1] for line in (C/'SHA256SUMS').read_text().splitlines()];pilots=[]
for n,bid in [(62,'s29-h200-observed-n62-full-control'),(64,'s30-h200-observed-n64-full-candidate')]:
 B=R/'serving-tuning-10'/bid;assert not B.exists(),'Never rewrite frozen payload';B.mkdir()
 for name in files:shutil.copyfile(C/name,B/name)
 p=B/'job.sbatch';t=p.read_text();assert 'export QWEN_TUNE_NS=60' in t;t=t.replace(C.name,B.name).replace('export QWEN_TUNE_NS=60',f'export QWEN_TUNE_NS={n}');assert '#SBATCH -t 00:17:00' in t;p.write_text(t)
 c=json.loads((B/'config.json').read_text());c.update(experiment=bid,source_experiment=C.name,source_job='24964',concurrency=[n],control_concurrency=62,candidate_concurrency=64,changed_factor={'between_deployment_concurrency':[62,64]},purpose='Fresh full matched-observer confirmation of accepted short N64 frontier',phase='confirm',confirm_warmup_s=60,confirm_measure_s=120,grace_s=30,screen_unranked=False,walltime_minutes=17,quality_validation_required=True,resource_monitor=True,control_experiment='s29-h200-observed-n62-full-control',practical_gain_gate_fraction=.01,graph_maximum_decode=64,short_source_job='25339',short_gain_percent=review['within_job_gain_percent'],performance_comparison='N64 vs fresh equally observed N62; observer-off best24962 is context only');(B/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 assert 'run_benchmark "$N" confirm 60 120' in (B/'benchmark.sh').read_text()
 for name in files:
  if name not in ['job.sbatch','config.json']:assert (B/name).read_bytes()==(C/name).read_bytes(),name
 for p in B.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 for p in list(B.glob('*.sh'))+[B/'job.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
 (B/'SHA256SUMS').write_text(''.join(hashlib.sha256((B/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in files))
 pilots.append(dict(platform='H200',id=bid,bundle=str(B),planned_ns=[n],state='PREPARED_NOT_SUBMITTED',minutes=17,max_su=None,payload_sha256={name:hashlib.sha256((B/name).read_bytes()).hexdigest() for name in files}))
(O/'pilots.json').write_text(json.dumps(pilots,indent=2)+'\n');(O/'validation.json').write_text(json.dumps(dict(passed=True,checked_utc=datetime.now(timezone.utc).isoformat(),source_job='25339',short_protocol_passed=True,source_native_controls_unchanged=True,all_operational_files_byte_identical=True,concurrency_pair=[62,64],full_protocol='60 warmup /120 measured /30 grace',minutes_each=17,gpus_each=16,pbs_su_reserved=0,scope='Fresh independent deployments, identical observation and serving settings; only offered concurrency changes between pair'),indent=2)+'\n')
print('Frozen two fresh full equally observed deployments; no submission yet')
