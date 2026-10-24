"""Bounded read-only collection of three owned CPU jobs; no fields or auth state."""
from pathlib import Path
import base64, datetime, hashlib, json, shlex, subprocess
E=Path(__file__).resolve().parent
R=E.parents[1]
JOBS={'25957267':'tripleu-mpi-affinity-matrix-20261024T032702Z'}
REMOTE=r'''
from pathlib import Path
import base64,hashlib,json,subprocess,datetime
jobs=JOBS
base=Path('/scratch/users/industry/ai-hpc/apacsc42/apac2026')
files={};total=0
for job,name in jobs.items():
 root=base/name;run=root/'runs'/job
 selected=[p for p in run.iterdir() if p.is_file() and p.suffix in ('.json','.jsonl','.tsv','.txt','.log','.stderr')]
 selected+=list((run/'logs').glob('*'))
 for arm in ['identity','candidate']:selected+=list((run/arm).glob('*.txt'))+list((run/arm).glob('*.json'))
 selected+=list(root.glob('*.o'+job))
 if job=='25940700':
  selected+=[run/'case'/p for p in ['logFiles/simpleFoam.log','postProcessing/solverInfo/0/solverInfo.dat','postProcessing/wallClockTimeStatistics/0/wallClockTime.dat','postProcessing/forceCoeffsAll/0/coefficient.dat']]
 for p in selected:
  assert p.is_file() and not p.is_symlink(),str(p)
  b=p.read_bytes();assert len(b)<2_000_000,str(p)
  b.decode('utf-8');total+=len(b);assert total<12_000_000
  rel=job+'/'+str(p.relative_to(root))
  files[rel]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'base64':base64.b64encode(b).decode()}
q=subprocess.run(['qstat','-fx','-F','json']+[j+'.pbs101' for j in jobs],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=20,check=True)
raw=json.loads(q.stdout)['Jobs'];safe={}
for job,v in raw.items():
 assert v['job_state']=='F' and str(v['project'])=='59000042'
 safe[job]={k:v[k] for k in ['job_state','project','Exit_status','resources_used','Resource_List','stime','obittime','comment'] if k in v}
print(json.dumps({'checked_utc':datetime.datetime.utcnow().isoformat()+'Z','files':files,'terminal':safe}))
'''.replace('JOBS',repr(JOBS))
output=E/'collected';assert not output.exists(),'Preserve earlier collection'
r=subprocess.run(['bash',str(R/'tools/nscc-cpu-ssh.sh'),'python3 -c '+shlex.quote(REMOTE)],capture_output=True,text=True,timeout=90,check=True)
data=json.loads(r.stdout);output.mkdir()
for rel,item in data['files'].items():
 p=Path(rel);assert not p.is_absolute() and '..' not in p.parts
 b=base64.b64decode(item.pop('base64'));assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256']
 target=output/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
(output/'collection.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'checked_utc':data['checked_utc'],'files':len(data['files']),'bytes':sum(i['bytes'] for i in data['files'].values()),'terminal':data['terminal']},indent=2))
