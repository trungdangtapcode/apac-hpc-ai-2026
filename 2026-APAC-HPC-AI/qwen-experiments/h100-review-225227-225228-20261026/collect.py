#!/usr/bin/env python3
"""Collect bounded terminal H100 evidence; filter PBS fields and omit private/runtime data."""
from pathlib import Path
import datetime,hashlib,io,json,shlex,subprocess,tarfile
Q=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
JOBS={'h100-incumbent-n54-refresh-20261026':'225227.pbs111','eagle3-h100-equal-tp-observer-r2-20261026':'225228.pbs111'}
remote=r'''from pathlib import Path
import io,json,re,sys,tarfile,subprocess
base=Path('/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015'); selected=SELECTED
inventory=[]; total=0; files=[]; qstats=[]
for name,job in selected.items():
 r=subprocess.run(['qstat','-xf',job],capture_output=True,text=True,check=True); vals={};key=None; keep=False; lines=[]
 for line in r.stdout.splitlines():
  m=re.match(r'    ([A-Za-z_.]+) = (.*)',line)
  if line.startswith('Job Id:'): keep=True;lines.append(line)
  elif m:
   key=m[1];keep=key.split('.')[0] in {'job_state','Job_Name','Exit_status','resources_used','Resource_List','Output_Path','Error_Path','exec_host','exec_vnode','stime','mtime','qtime','project','queue','comment','depend'}
   if keep:lines.append(line)
  elif line.startswith('\t') and key and keep:lines.append(line)
  elif line and not line.startswith('\t'):key=None;keep=False
 qstats.append({'job':job,'qstat':lines})
 candidates=[base/name/'runs'/job,base/'runs'/job]
 roots=[x for x in candidates if x.is_dir()]
 inventory.append({'bundle':name,'job':job,'candidate_roots':[str(x) for x in roots]})
 if len(roots)!=1:continue
 root=roots[0]
 for p in sorted(root.rglob('*')):
  if not p.is_file() or p.is_symlink():continue
  rel=p.relative_to(root)
  if any(x in {'home','private','exchange','cache','__pycache__','submitted','submitted-payload','diagnostic-profile','profiles'} for x in rel.parts) or rel.name in {'inputs.json'}:continue
  if p.suffix.lower() not in {'.json','.jsonl','.log','.txt','.tsv','.sha256','.out','.err','.csv'}:continue
  size=p.stat().st_size;inventory.append({'bundle':name,'job':job,'path':str(rel),'bytes':size})
  if size>20*1024**2 or total+size>100*1024**2 or len(files)>3000:continue
  total+=size;files.append((p,Path(name)/'runs'/job/rel))
out={'qstats':qstats,'inventory':inventory}
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz') as tar:
 for p,rel in files:tar.add(str(p),arcname=str(rel),recursive=False)
 data=json.dumps(out,indent=2).encode(); info=tarfile.TarInfo('COLLECTION-INVENTORY.json');info.size=len(data);tar.addfile(info,io.BytesIO(data))
'''.replace('SELECTED',repr(JOBS))
cmd='python3 -c '+shlex.quote(remote)
r=subprocess.run(['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch','bash -lc '+shlex.quote(cmd)],capture_output=True,timeout=180)
if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-1500:])
# The remote process writes one JSON inventory separately to stderr so archive stdout stays binary.
# This first version captures a single stream only: remove binary stdout if not valid tar before retry.
archive=OUT/'raw-terminal-artifacts-curated-r2.tar.gz';assert not archive.exists();archive.write_bytes(r.stdout)
with tarfile.open(archive,'r:gz') as tar:
 manifest=[];inventory=None
 for m in tar.getmembers():
  if m.name=='COLLECTION-INVENTORY.json':inventory=json.load(tar.extractfile(m));continue
  dest=OUT/'curated-r2'/m.name;assert m.isfile() and not dest.exists() and '..' not in Path(m.name).parts
  dest.parent.mkdir(parents=True,exist_ok=True);data=tar.extractfile(m).read();dest.write_bytes(data);manifest.append({'path':m.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(OUT/'COLLECTION-curated-r2.json').write_text(json.dumps({'collected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':manifest,'inventory':inventory,'archive_bytes':len(r.stdout)},indent=2)+'\n')
print('Collected',len(manifest),'files')
