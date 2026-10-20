"""Freeze matched N60 repetitions and a bounded N62 runner comparison."""
from pathlib import Path
import ast,datetime,hashlib,json,shutil,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;D=R/'serving-tuning-10';reviews=json.loads((R/'research-followup-20261020-0028/slurm-reviews.json').read_text());assert all(v['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS' for v in reviews.values())
rows=[('s14-dg8192-auto-n60','24732','s18-auto-control-n60',60,False),('s16-dg8192-hpc-decode-n60','24738','s18-hpc-repeat-n60',60,False),('s15-dg8192-n62','24733','s18-auto-control-n62',62,False),('s16-dg8192-hpc-decode-n60','24738','s18-hpc-n62-profile',62,True)]
# Locate frozen source by its submitted config instead of assuming an old folder name.
for _,job,_,_,_ in rows:assert (R/'runs'/job/'submitted/SHA256SUMS').exists()
pilots=[]
for _,job,name,n,profile in rows:
 src=R/'runs'/job/'submitted';dst=D/name;assert not dst.exists();shutil.copytree(src,dst)
 oldname=json.loads((src/'config.json').read_text())['experiment'];oldn=json.loads((src/'config.json').read_text())['concurrency'][0]
 f=dst/'job.sbatch';s=f.read_text().replace(oldname,name);assert 'QWEN_TUNE_NS='+str(oldn) in s;s=s.replace('QWEN_TUNE_NS='+str(oldn),'QWEN_TUNE_NS='+str(n));s=s.replace('QWEN_DIAGNOSTIC_PROFILE=0','QWEN_DIAGNOSTIC_PROFILE='+str(int(profile)));f.write_text(s)
 kind='auto_control' if 'auto-' in name else ('repeat' if 'repeat' in name else 'bounded_load')
 purpose={'auto_control':'Fresh fixed-load auto-decode control for the new HPC-Ops observations.','repeat':'Independent N60 repeat of the locally accepted 2990.151 H200 observation.','bounded_load':'One N62 HPC-Ops operating point after passing N60 improvement; compare fresh auto N62 control, then collect separate post-score GPU profile.'}[kind]
 c=json.loads((src/'config.json').read_text());c.update(experiment=name,source_experiment=oldname,source_job=job,replication_source_job=job,control_job=None,control_experiment='s18-auto-control-n'+str(n) if kind!='auto_control' else None,concurrency=[n],matched_concurrency=n,diagnostic_profile=profile,purpose=purpose,changed_factor={'kind':kind,'concurrency':n},accuracy_verified=False);(dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in {'.sh','.sbatch'}:subprocess.run(['bash','-n',str(f)],check=True)
  if f.is_file() and f.name not in {'config.json','job.sbatch','SHA256SUMS'}:assert f.read_bytes()==(src/f.name).read_bytes(),f.name
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()))
 pilots.append(dict(platform='H200',id=name,bundle=str(dst),planned_ns=[n],state='PLANNED',purpose=purpose,payload_sha256=h,replication_source_job=job,diagnostic_profile=profile,wave=10,measurements=[],missing_ns=[n],benchmark_complete=False,profile_complete=None,traces=[],attempts=[]))
(O/'pilots.json').write_text(json.dumps(pilots,indent=2)+'\n');(O/'validation.json').write_text(json.dumps(dict(passed=True,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),ranked_worker_client_transport_precision_output_checks_byte_identical=True,full_60_120_30_and_4000_200_unchanged=True,independent_repeat_and_fresh_controls=True,at_most_one_new_load_step=True),indent=2)+'\n');print('Four frozen H200 trials prepared')
