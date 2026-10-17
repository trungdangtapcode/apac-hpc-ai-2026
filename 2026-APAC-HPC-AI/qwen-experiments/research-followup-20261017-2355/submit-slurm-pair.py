"""Prepare two evidence-driven jobs and arm the existing non-AI Slurm watcher."""
from pathlib import Path
import json,shutil,subprocess,hashlib,datetime
R=Path.cwd();D=R/'serving-tuning-10';O=R/'research-followup-20261017-2355';now=datetime.datetime.now(datetime.timezone.utc).isoformat();new=[];validation={}
# Both use confirmed DeepGEMM chunk4096 with graphs on; neither combines pending changes.
for name,kind in [('s10-prefill-deepgemm-n54','load'),('s10-prefill-deepgemm-profile-n56','profile')]:
 src=D/'s10-prefill-deepgemm-n56';dst=D/name;assert not any(x['id']==name for x in json.loads((D/'prepared-pilots.json').read_text())['pilots']);shutil.copytree(src,dst,dirs_exist_ok=True)
 f=dst/'job.sbatch';s=f.read_text().replace(src.name,name)
 if kind=='load':assert 'QWEN_TUNE_NS=56' in s;s=s.replace('QWEN_TUNE_NS=56','QWEN_TUNE_NS=54')
 else:assert 'QWEN_DIAGNOSTIC_PROFILE=0' in s;s=s.replace('QWEN_DIAGNOSTIC_PROFILE=0','QWEN_DIAGNOSTIC_PROFILE=1')
 f.write_text(s)
 f=dst/'config.json';c=json.loads(f.read_text());c.update(experiment=name,source_job='24327',concurrency=[54] if kind=='load' else [56],matched_concurrency=54 if kind=='load' else 56,diagnostic_profile=kind=='profile',purpose='Bracket confirmed DeepGEMM N56/N58 with N54; do not assume higher concurrency wins' if kind=='load' else 'Profile changed prefill backend after scored N56 benchmark; compare separate N48 diagnostic with prior 24263, 4 prefill/32 decode steps, 16 ranks')
 if kind=='profile':c.update(diagnostic_concurrency=48,diagnostic_prefill_steps=4,diagnostic_decode_steps=32,profile_reference_job='24263')
 f.write_text(json.dumps(c,indent=2)+'\n')
 for f in src.iterdir():
  if f.is_file() and f.name not in ['job.sbatch','config.json','SHA256SUMS']:assert f.read_bytes()==(dst/f.name).read_bytes(),f.name
 for f in list(dst.glob('*.sh'))+[dst/'job.sbatch']:subprocess.run(['bash','-n',str(f)],check=True)
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));validation[name]=h
 if kind=='profile':
  # Exact diagnostic payload and execution ordering match the earlier audited profiler.
  for file in ['profile-serving.py','benchmark.sh','topology-job.sh']:assert (dst/file).read_bytes()==(D/'s10-combo-profile-n56'/file).read_bytes()
  assert (dst/'benchmark.sh').read_text().index('if [[ ${QWEN_DIAGNOSTIC_PROFILE')>(dst/'benchmark.sh').read_text().index('run_benchmark "$N" confirm 60 120')
 new.append(dict(id=name,bundle=str(dst),planned_ns=[54] if kind=='load' else [56],state='PLANNED',wave=10,purpose=c['purpose'],diagnostic_profile=kind=='profile',expected_profile_ranks={'prefill-0':4,'prefill-1':4,'decode-0':8} if kind=='profile' else {},payload_sha256=h,measurements=[],missing_ns=[54] if kind=='load' else [56],benchmark_complete=False,profile_complete=False if kind=='profile' else None,traces=[],attempts=[],replication_source_job='24327'))
q=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True);assert len(q.splitlines())+len(new)<=5,'Queue cap reached; bundles prepared but not armed'
f=D/'prepared-pilots.json';p=json.loads(f.read_text());assert not any(x['id'] in {z['id'] for z in new} for x in p['pilots']);p['pilots'].extend(new);p['updated_utc']=now;tmp=f.with_suffix('.n54-profile.tmp');tmp.write_text(json.dumps(p,indent=2)+'\n');tmp.replace(f)
(O/'validation.json').write_text(json.dumps(dict(created_utc=now,payloads=validation,max_gpus_per_job=16,max_minutes_per_job=17,profile_window='After scored measurement; separate N48 traffic',benchmark_unchanged_except_load_in_n54=True,queue_cap_checked=True),indent=2)+'\n');print('Armed DeepGEMM N54 and post-measurement N56 profile; waiting for watcher receipts')
