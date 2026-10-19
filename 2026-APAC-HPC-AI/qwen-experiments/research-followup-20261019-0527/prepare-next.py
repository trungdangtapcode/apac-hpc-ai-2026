"""Freeze independent repeats and one load step from passing H200/H100 points."""
from pathlib import Path
import ast,datetime,hashlib,json,shutil,subprocess,tarfile
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;pilots=[];payloads={}
for platform,source,source_job,old_n,rows in [
 ('H200','s14-dg8192-n60','24722',60,[('s15-dg8192-n60-repeat',60),('s15-dg8192-n62',62)]),
 ('H100','h100-hpc-both-n54-38','221590.pbs111',54,[('h100-hpc-both-n54-repeat-39',54),('h100-hpc-both-n56-40',56)])]:
 parent=R/('serving-tuning-10' if platform=='H200' else 'nscc-pbs');src=parent/source
 proof=json.loads((O/(source_job+'-review.json')).read_text());assert proof['state'] in {'LOCAL_PROTOCOL_SLA_OUTPUT_PASS','LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'}
 for name,n in rows:
  dst=parent/name;assert not dst.exists();shutil.copytree(src,dst);jobfile='job.sbatch' if platform=='H200' else 'benchmark.pbs';f=dst/jobfile;s=f.read_text().replace(source,name)
  before='QWEN_TUNE_NS='+str(old_n) if platform=='H200' else 'QWEN_TUNE_NS="'+str(old_n)+'"';after='QWEN_TUNE_NS='+str(n) if platform=='H200' else 'QWEN_TUNE_NS="'+str(n)+'"';assert before in s;s=s.replace(before,after);f.write_text(s)
  purpose=('Independent repeat of the newly passing N'+str(old_n)+' operating point' if n==old_n else 'One load step from fully passing N'+str(old_n)+' to N'+str(n)+'; compare independent same-platform control, no automatic higher load')
  c=json.loads((dst/'config.json').read_text());c.update(experiment=name,source_experiment=source,source_job=source_job,replication_source_job=source_job,control_job=source_job,fresh_control_job=None,control_experiment=rows[0][0],concurrency=[n],matched_concurrency=n,purpose=purpose,accuracy_verified=False,diagnostic_profile=False,changed_factor={'kind':'control' if n==old_n else 'load','concurrency':n});(dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
  for f in dst.iterdir():
   if f.suffix=='.py':ast.parse(f.read_text())
   if f.suffix in {'.sh','.sbatch','.pbs'}:subprocess.run(['bash','-n',str(f)],check=True)
   if f.is_file() and f.name not in {jobfile,'config.json','SHA256SUMS'}:assert f.read_bytes()==(src/f.name).read_bytes(),f.name
  h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));payloads[name]=h
  p=dict(platform=platform,id=name,bundle=str(dst),planned_ns=[n],state='PLANNED',purpose=purpose,payload_sha256=h,replication_source_job=source_job,control_experiment=rows[0][0])
  if platform=='H200':p.update(wave=10,diagnostic_profile=False,measurements=[],missing_ns=[n],benchmark_complete=False,profile_complete=None,traces=[],attempts=[])
  else:p.update(minutes=45,max_su=1536)
  pilots.append(p)
with tarfile.open(O/'pbs-bundles.tar.gz','w:gz') as tar:
 for p in pilots:
  if p['platform']=='H100':tar.add(p['bundle'],arcname=p['id'])
(O/'pilots.json').write_text(json.dumps(pilots,indent=2)+'\n');(O/'validation.json').write_text(json.dumps(dict(passed=True,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),payloads=payloads,client_worker_precision_quality_transport_byte_identical=True,caveat='New load still requires full GPU acceptance; no automatic higher step or unchanged failure retry.'),indent=2)+'\n');print('Four source-gated bundles frozen; not submitted')
