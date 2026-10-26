#!/usr/bin/env python3
"""Collect bounded, filtered, terminal PBS225306 evidence through existing VPN SSH."""
from pathlib import Path
import datetime,hashlib,json,shlex,subprocess,tarfile
Q=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
assert not (OUT/'raw-terminal-artifacts.tar.gz').exists()
remote=r'''from pathlib import Path
import io,json,re,sys,tarfile,subprocess
base=Path('/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015');job='225306.pbs111'
r=subprocess.run(['qstat','-xf',job],capture_output=True,text=True);assert r.returncode==0,r.stderr
selected=[];key=None;keep=False
for line in r.stdout.splitlines():
 m=re.match(r'    ([A-Za-z_.]+) = (.*)',line)
 if line.startswith('Job Id:'):keep=True;selected.append(line)
 elif m:
  key=m[1];keep=key.split('.')[0] in {'job_state','Job_Name','Exit_status','resources_used','Resource_List','Output_Path','Error_Path','exec_host','exec_vnode','stime','mtime','qtime','project','queue','comment','depend'}
  if keep:selected.append(line)
 elif line.startswith('\\t') and key and keep:selected.append(line)
 elif line and not line.startswith('\\t'):key=None;keep=False
state=next((x for x in selected if 'job_state =' in x),'')
exitcode=next((x for x in selected if 'Exit_status =' in x),'')
assert 'job_state = F' in state,(state,selected)
roots=[p for p in [base/'eagle3-h100-equal-tp-bench-n24-20261026/runs'/job,base/'runs'/job] if p.is_dir()]
assert len(roots)==1,[str(p) for p in roots]
root=roots[0];files=[];inventory=[];total=0
for p in sorted(root.rglob('*')):
 if not p.is_file() or p.is_symlink():continue
 rel=p.relative_to(root)
 if any(x in {'home','private','exchange','cache','__pycache__','submitted','submitted-payload','profiles'} for x in rel.parts) or rel.name in {'inputs.json'}:continue
 if p.suffix.lower() not in {'.json','.jsonl','.log','.txt','.tsv','.sha256','.out','.err','.csv'}:continue
 size=p.stat().st_size;inventory.append({'path':str(rel),'bytes':size})
 if size>20*1024**2 or total+size>120*1024**2 or len(files)>3000:continue
 total+=size;files.append((p,Path('runs/225306.pbs111')/rel))
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz') as tar:
 for p,rel in files:tar.add(str(p),arcname=str(rel),recursive=False)
 data=json.dumps({'qstat_filtered':selected,'job_root':str(root),'artifact_inventory':inventory,'selected_bytes':total,'selected_count':len(files)},indent=2).encode();info=tarfile.TarInfo('COLLECTION-INVENTORY.json');info.size=len(data);tar.addfile(info,io.BytesIO(data))
'''
cmd='python3 -c '+shlex.quote(remote);r=subprocess.run(['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch','bash -lc '+shlex.quote(cmd)],capture_output=True,timeout=180);assert r.returncode==0,r.stderr.decode(errors='replace')[-2000:]
archive=OUT/'raw-terminal-artifacts.tar.gz';archive.write_bytes(r.stdout)
with tarfile.open(archive,'r:gz') as tar:
 manifests=[];inventory=None
 for m in tar.getmembers():
  if m.name=='COLLECTION-INVENTORY.json':inventory=json.load(tar.extractfile(m));continue
  rel=Path(m.name);assert m.isfile() and not rel.is_absolute() and '..' not in rel.parts
  dest=OUT/'curated-runs'/rel;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);data=tar.extractfile(m).read();dest.write_bytes(data);manifests.append({'path':str(rel),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
proof={'collected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':manifests,'inventory':inventory,'archive_bytes':len(r.stdout)}
(OUT/'COLLECTION.json').write_text(json.dumps(proof,indent=2)+'\n');print('Collected',len(manifests),'files; selected bytes',inventory['selected_bytes'])
