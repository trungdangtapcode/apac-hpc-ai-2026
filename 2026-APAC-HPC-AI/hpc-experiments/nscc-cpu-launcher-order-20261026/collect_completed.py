"""Capture only own diagnostic records; exclude binaries and runtime environment."""
from pathlib import Path
import subprocess,json,datetime,shlex,io,tarfile,hashlib
E=Path(__file__).resolve().parent;R=E.parent;root=json.loads((E/'deployment.json').read_text())['root'];job='25999546'
command='cd '+shlex.quote(root)+' && tar --exclude=mpi-init-probe --exclude=runtime-environment-whitelist.txt -czf - '+shlex.quote('runs/'+job)
p=subprocess.run(['bash',str(R/'tools/nscc-cpu-ssh.sh'),command],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
assert p.returncode==0,p.stderr
out=E/('completed-'+job);out.mkdir(exist_ok=True);archive_path=out/'raw-records.tar.gz'
assert not archive_path.exists(),'Preserve original collection; inspect before repeating'
archive_path.write_bytes(p.stdout);manifest={}
with tarfile.open(fileobj=io.BytesIO(p.stdout),mode='r:gz') as archive:
 for member in archive.getmembers():
  assert '..' not in Path(member.name).parts and not member.name.startswith('/')
  if member.isdir():continue
  assert member.isfile() and member.size<2000000
  raw=archive.extractfile(member).read();dest=out/'collected'/member.name;dest.parent.mkdir(parents=True,exist_ok=True)
  assert not dest.exists();dest.write_bytes(raw)
  manifest[member.name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
p=subprocess.run(['bash',str(R/'tools/nscc-cpu-ssh.sh'),'qstat -fx -F json '+job+'.pbs101'],capture_output=True,text=True,timeout=25)
assert p.returncode==0,p.stderr
j=json.loads(p.stdout)['Jobs'][job+'.pbs101'];j={k:v for k,v in j.items() if k in ['job_state','Exit_status','Resource_List','resources_used','project','queue','stime','obittime','comment','exec_host']}
d={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':root,'job_id':job+'.pbs101','terminal':j,'files':manifest,'archive_sha256':hashlib.sha256(archive_path.read_bytes()).hexdigest(),'scope':'Own diagnostic text and per-rank records only; executable and runtime environment excluded before transfer. Earlier Python per-file pack attempt timed out before retaining an archive; native tar used instead.'}
(out/'collection.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'files':len(manifest),'compressed_bytes':archive_path.stat().st_size,'terminal':j}))
