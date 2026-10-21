"""Deploy frozen same-node method pair, then submit once under CPU budget lock."""
from pathlib import Path
import base64,datetime,fcntl,hashlib,io,json,re,shlex,subprocess,tarfile
H=Path('/home/apacsc42');R=H/'2026-APAC-HPC-AI/hpc-experiments';E=Path(__file__).resolve().parent;P=E/'payload';helper=str(R/'tools/nscc-cpu-ssh.sh')
def save(name,obj):
 (E/name).write_text(json.dumps(obj,indent=2)+'\n')
def cpu(cmd):
 return subprocess.run([helper,'bash -lc '+shlex.quote(cmd)],capture_output=True,text=True,timeout=120,check=True)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert json.loads((R/'nscc-cpu-numa-scotch128-20261021/review.json').read_text())['state']=='NATIVE_NUMA_SCOTCH_PREPARATION_PASS'
assert json.loads((R/'nscc-cpu-numa-scotch128-20261021/review.json').read_text())['graph_filter']=='PROMISING_FOR_BUDGETED_SOLVER_SCREEN'
assert not (E/'submission-intent.json').exists(),'Submission already attempted; inspect instead of retrying'
hashes=json.loads((E/'payload-sha256.json').read_text());assert all(hashlib.sha256((P/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
root='/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-three-cuts256-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w:gz') as t:
 for k in hashes:t.add(str(P/k),arcname=k,recursive=False)
expected=json.dumps(hashes,indent=2).encode()
# Transmit the archive over SSH stdin, avoiding the OS per-argument size limit.
archive_buffer=io.BytesIO()
with tarfile.open(fileobj=archive_buffer,mode='w:gz') as t:
 for k in hashes:t.add(str(P/k),arcname=k,recursive=False)
 info=tarfile.TarInfo('__deployment_expected_sha256.json');info.size=len(expected);t.addfile(info,io.BytesIO(expected))
remote="""import io,tarfile,hashlib,json,sys
from pathlib import Path
root=Path(ROOT);root.mkdir(exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz') as t:
 for m in t.getmembers():
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
  p=root/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
hashes=json.loads((root/'__deployment_expected_sha256.json').read_text())
for k,v in hashes.items():assert hashlib.sha256((root/k).read_bytes()).hexdigest()==v,k
print(json.dumps(dict(root=str(root),sha256=hashes)))
""".replace('ROOT',repr(root))
res=subprocess.run([helper,'python3 -c '+shlex.quote(remote)],input=archive_buffer.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120,check=True)
deployed=json.loads(res.stdout.decode());assert deployed['root']==root and deployed['sha256']==hashes
save('deployment.json',deployed)
with (R/'nscc-cpu-timing-probe-20261021/cpu-budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 q=cpu('qstat -u apacsc42')
 cpu_jobs=re.findall(r'^(\d+\.\S+)\s+apacsc42\s',q.stdout,re.M)
 assert set(cpu_jobs).issubset({'25907753.pbs101'}),'Unexpected own CPU work; preserve queue'
 parent=json.loads(cpu('qstat -xf -F json 25907753.pbs101').stdout)['Jobs']['25907753.pbs101']
 assert str(parent['project'])=='59000042' and (parent['job_state']!='F' or parent['Exit_status']==0)
 a=subprocess.run(['bash',str(H/'workspace/vpn-rootless/vpn.sh'),'ssh-batch',"bash -lc 'qstat -u apacsc42'"],capture_output=True,text=True,timeout=45,check=True)
 ai_jobs=[s for s in a.stdout.splitlines() if re.search(r'^\d+\S*\s+apacsc42\s',s)];assert len(ai_jobs)+len(cpu_jobs)+1<=3
 project=cpu('myprojects -p 59000042');assert '59000042' in project.stdout
 # Budget balance is checked independently from local planning commitments.
 su=[line for line in project.stdout.splitlines() if line.startswith('| SU')];assert len(su)==1
 values=[float(x.strip()) for x in su[0].split('|')[2:-1]];assert values[2]>100
 b=R/'nscc-cpu-timing-probe-20261021/cpu-budget.json';d=json.loads(b.read_text());assert d['schema']==2 and d['project']=='59000042'
 maximum=24;assert d['consumed_ceiling_SU']+d['outstanding_reserved_max_SU']+maximum<=d['baseline_wave_planning_ceiling_SU']
 save('pre-submit-checks.json',dict(utc=now(),cpu_queue=q.stdout,ai_queue_readonly=a.stdout,cpu_project=project.stdout,combined_jobs_before=len(ai_jobs)+len(cpu_jobs),dependency_afterok="25907753.pbs101",budget_schema=2,consumed_ceiling_SU=d['consumed_ceiling_SU'],new_maximum_SU=maximum))
 intent=dict(utc=now(),root=root,project='59000042',maximum_SU=maximum,state='SUBMISSION_ATTEMPT_MUST_NOT_RETRY_BLINDLY');save('submission-intent.json',intent)
 d['outstanding_reserved_max_SU']+=maximum;d['reserved_max_SU']=d['planning_committed_SU']=d['consumed_ceiling_SU']+d['outstanding_reserved_max_SU'];d['jobs'].append(dict(id=None,state='SUBMISSION_INTENT',root=root,maximum_SU=maximum,branch='N256_three_native_cuts_after_SN_pair',dependency_afterok='25907753.pbs101'));b.write_text(json.dumps(d,indent=2)+'\n')
 try:
  receipt=cpu('cd '+shlex.quote(root)+' && qsub -W depend=afterok:25907753.pbs101 prepare.pbs')
 except Exception as ex:
  save('submission-uncertain.json',dict(utc=now(),root=root,reason=str(ex),stdout=getattr(ex,'stdout',None),stderr=getattr(ex,'stderr',None),instruction='Keep reservation; query server, never resubmit blindly'));raise
 save('submission.json',dict(utc=now(),root=root,returncode=receipt.returncode,stdout=receipt.stdout,stderr=receipt.stderr,project='59000042',maximum_SU=maximum,ncpus=32,serial_tasks=1,mesh_split_ranks=256,cases=3,maximum_seconds=2700,dependency_afterok='25907753.pbs101',ngpus=0))
 job=receipt.stdout.strip();assert re.fullmatch(r'\d+\.pbs\d+',job),job
 d['jobs'][-1].update(id=job,state='SUBMITTED',observed_utc=now());b.write_text(json.dumps(d,indent=2)+'\n')
 print(job)
