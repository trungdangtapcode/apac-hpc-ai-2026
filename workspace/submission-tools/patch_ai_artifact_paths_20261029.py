#!/usr/bin/env python3
"""Publish only reviewed AI postprocessor fixes; preserve HPC and presentation bytes."""
from pathlib import Path
import copy,datetime,fcntl,hashlib,json,os,shutil,stat,subprocess,zipfile
W=Path('/home/apacsc42/workspace');Q=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
F=Q/'portable-artifact-path-fix-20261029';T=W/'VNUHCM - TripleU';Z=W/'VNUHCM - TripleU.zip';O=W/'submission-review/ai-artifact-path-fix-20261029'
RAW=Q/'submission-replay-20261028/VNUHCM - TripleU/AI_Task/logs/reruns/27136'
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(x):return (json.dumps(x,indent=2)+'\n').encode()
def inventory():return {str(p.relative_to(T)):p.read_bytes() for p in sorted(T.rglob('*')) if p.is_file()}
def atomic(p,b,mode=0o644):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name('.'+p.name+'.ai29-tmp');assert not tmp.exists();tmp.write_bytes(b);tmp.chmod(mode);tmp.replace(p)
def main():
 O.mkdir(parents=True,exist_ok=True)
 with (W/'.submission-publication.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=F,check=True,stdout=subprocess.DEVNULL)
  tests=subprocess.run(['python3','-B',str(F/'test_artifact_paths.py')],capture_output=True,text=True);assert tests.returncode==0,tests.stderr
  gate=subprocess.run(['python3','-B',str(F/'score-gate.py'),str(RAW),'64'],capture_output=True,text=True);assert gate.returncode==0,gate.stdout+gate.stderr;recovered=json.loads(gate.stdout)
  summary=subprocess.run(['python3','-B',str(F/'summarize.py'),str(RAW)],capture_output=True,text=True);assert summary.returncode==0,summary.stderr;rows=json.loads(summary.stdout);assert len(rows)==1
  before=inventory();after=dict(before);now=datetime.datetime.now(datetime.timezone.utc)
  hpc={p:sha(b) for p,b in before.items() if p.startswith('HPC_Task/')}
  modes={str(p.relative_to(T)):stat.S_IMODE(p.stat().st_mode) for p in (T/'HPC_Task').rglob('*')}
  deck='Presentation/TripleU_APAC2026_Presentation.pptx';deckhash=sha(before[deck])
  frozen=Q/'submission-replay-20261028/VNUHCM - TripleU/AI_Task/job_scripts'
  # Every GPU/model/client/submit byte remains exactly the tested source.
  for p in ['worker.sh','submit.sbatch','deploy-and-benchmark.sh','official-benchmark.sh','config.json','nixl-conn.py','warm-topology.py','warmup_semantic.py']:
   assert before['AI_Task/job_scripts/'+p]==(frozen/p).read_bytes(),p
  for name in ['artifact_paths.py','score-gate.py','summarize.py']:after['AI_Task/job_scripts/'+name]=(F/name).read_bytes()
  sums='AI_Task/job_scripts/SHA256SUMS';names=[]
  for line in before[sums].decode().splitlines():
   _,name=line.split('  ',1);names.append(name)
  if 'artifact_paths.py' not in names:names.append('artifact_paths.py')
  after[sums]=''.join(sha(after['AI_Task/job_scripts/'+n])+'  '+n+'\n' for n in sorted(names)).encode()
  replay=json.loads(before['AI_Task/logs/replay-status.json'])
  replay.update(updated_utc=now.isoformat(),portable_entry_gpu_replayed=False,
    portable_gpu_model_and_official_command={'job':27136,'scheduler_state':'FAILED','exit_code':'1:0','command_completed':True,'original_gate_failure':'AIPerf default namespace was not resolved','corrected_postprocessor_on_retained_raw':'PASS','full_end_to_end_repeat_after_reader_fix':'NOT_SUBMITTED'},
    recovered_performance=recovered,quality_scope='Official full-set accuracy UNKNOWN; separate smoke/retrieval suite was not run in this portable allocation.')
  after['AI_Task/logs/replay-status.json']=enc(replay)
  evidence='AI_Task/logs/measured/portable-replay-27136-20261029.json'
  after[evidence]=enc({'job':27136,'scheduler':'FAILED1:0 after completed AIPerf','repaired_raw_gate':recovered,'summary':rows,'limits':['Original failure is preserved.','This offline reader repair does not change a scheduler receipt.','No separate smoke/retrieval or hardware time series collected in this allocation.','Official full-set accuracy UNKNOWN.'],'runtime_payload_changed':False})
  note='AI_Task/logs/measured/artifact-path-fix-20261029.md'
  after[note]=b'''# Portable reader correction, 29 October 2026 Vietnam time\n\nActual GPU job27136 initialized all workers and both semantic P/D routes, then completed the official N64 AIPerf command. It ended1:0 because local readers assumed exports directly under artifacts/. AIPerf0.12 placed them in artifacts/qwen-openai-chat-concurrency64/.\n\nThe corrected readers accept exactly one complete pair at the artifact root or one immediate child and reject ambiguity, missing/incomplete pairs and symlink namespaces. Phase exports are excluded. The official command, model/worker flags, score formula and SLA limits remain unchanged. Eight regression tests and the repaired gate on retained raw data pass.\n\nRecovered performance:3050.225487 good output tokens/s,1880 of1906 good requests (98.635887%), zero errors/cancellations. TTFT mean/p95=1102.185717/1297.447714ms; request-mean ITL mean/p95=15.011058/15.165369ms. This is an individual protocol observation after postprocessing repair, not a validated new optimization or a successful original scheduler job. Original failure and raw evidence are preserved. No hardware sampler or separate smoke/retrieval suite ran here; official full-set accuracy remains UNKNOWN.\n\nThe patched postprocessors were validated on real retained raw data. A subsequent end-to-end GPU replay remains separate until its receipt and review. Historical delivery checks describe the earlier package; this correction has its own targeted validation.\n'''
  latest='AI_Task/logs/measured/latest-results.md';after[latest]=b'> 29 October 2026 update: the portable GPU/model/client replay completed, but job27136 failed in postprocessing because of an unhandled AIPerf output namespace. Readers are corrected and actual raw performance rechecks pass. See artifact-path-fix-20261029.md and portable-replay-27136-20261029.json. Full end-to-end repeat and official quality remain unverified.\n\n'+before[latest]
  mf='AI_Task/logs/FILE_MANIFEST.json';gs='AI_Task/logs/SHA256SUMS'
  after[mf]=enc({'created_utc':now.isoformat(),'paths_relative_to_team_directory':True,'files':[{'path':p,'bytes':len(b),'sha256':sha(b)} for p,b in sorted(after.items()) if p not in [mf,gs]]})
  after[gs]=''.join(sha(b)+'  '+os.path.relpath(T/p,T/'AI_Task/logs')+'\n' for p,b in sorted(after.items()) if p!=gs).encode()
  changed=[p for p,b in after.items() if before.get(p)!=b];assert all(p.startswith('AI_Task/') for p in changed)
  assert {p:sha(b) for p,b in after.items() if p.startswith('HPC_Task/')}==hpc and sha(after[deck])==deckhash
  with zipfile.ZipFile(Z) as old:
   infos={i.filename:copy.copy(i) for i in old.infolist()};archive_files={i.filename for i in old.infolist() if not i.is_dir()}
   assert archive_files=={T.name+'/'+p for p in before},'Current folder and ZIP differ; stop for concurrent publication'
   for p,b in before.items():assert sha(old.read(T.name+'/'+p))==sha(b),p
  temp=O/'VNUHCM - TripleU.patched.zip'
  with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as new:
   for name,i in infos.items():
    if i.is_dir():new.writestr(i,b'')
   for p,b in sorted(after.items()):
    name=T.name+'/'+p;i=copy.copy(infos[name]) if name in infos else zipfile.ZipInfo(name,now.timetuple()[:6])
    if name not in infos:i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=(stat.S_IFREG|0o644)<<16
    new.writestr(i,b)
  with zipfile.ZipFile(temp) as new:
   assert new.testzip() is None
   for p,b in after.items():assert sha(new.read(T.name+'/'+p))==sha(b),p
   for p in hpc:
    a=infos[T.name+'/'+p];b=new.getinfo(T.name+'/'+p);assert (a.date_time,a.external_attr,a.comment)==(b.date_time,b.external_attr,b.comment)
  assert inventory()==before,'Source changed during review'
  backup=W/'submission-archive'/('before-ai-artifact-path-fix-'+now.strftime('%Y%m%dT%H%M%SZ'));backup.mkdir()
  for p in changed:
   if p in before:atomic(backup/p,before[p],stat.S_IMODE((T/p).stat().st_mode))
  shutil.copy2(Z,backup/Z.name);shutil.copy2(W/'VNUHCM - TripleU.zip.sha256',backup/'VNUHCM - TripleU.zip.sha256')
  for p in changed:atomic(T/p,after[p],stat.S_IMODE((T/p).stat().st_mode) if (T/p).exists() else 0o644)
  atomic(Z,temp.read_bytes());atomic(W/'VNUHCM - TripleU.zip.sha256',(sha(temp.read_bytes())+'  VNUHCM - TripleU.zip\n').encode())
  actual=inventory();assert actual==after
  assert {str(p.relative_to(T)):stat.S_IMODE(p.stat().st_mode) for p in (T/'HPC_Task').rglob('*')}==modes
  for root in [T/'AI_Task/job_scripts',T/'AI_Task/logs']:subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=root,check=True,stdout=subprocess.DEVNULL)
  report={'passed':True,'updated_utc':now.isoformat(),'changed_paths':changed,'HPC_files_preserved':len(hpc),'HPC_modes_and_ZIP_attributes_preserved':True,'presentation_sha256_unchanged':deckhash,'targeted_tests':8,'real_raw_gate':recovered,'benchmark_model_and_submit_hashes_unchanged':True,'zip_sha256':sha(Z.read_bytes()),'zip_bytes':Z.stat().st_size,'backup':str(backup),'organiser_upload':False}
  (O/'publication-validation.json').write_bytes(enc(report));(O/'regression-tests.log').write_text(tests.stdout+tests.stderr);(O/'recovered-gate-27136.json').write_bytes(gate.stdout.encode());print(json.dumps(report,indent=2))
if __name__=='__main__':main()
