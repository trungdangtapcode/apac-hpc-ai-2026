#!/usr/bin/env python3
"""Collect selected terminal PBS output streams after safely unfolding qstat paths."""
from pathlib import Path
import hashlib,json,shlex,subprocess,datetime
Q=Path(__file__).resolve().parent.parent;OUT=Q/'h100-recovered-runs-20261026'
selected={'eagle3-pd-serial-init-r6-replacement-20261024':'224554.pbs111','eagle3-h100-single-node-equal-tp-20261024':'224560.pbs111'}
code='''from pathlib import Path
import json,re,subprocess
records=[]
for name,job in SELECTED.items():
 r=subprocess.run(['qstat','-xf',job],capture_output=True,text=True,check=True)
 values={};key=None
 for line in r.stdout.splitlines():
  m=re.match(r'    ([A-Za-z_.]+) = (.*)',line)
  if m:key=m[1];values[key]=m[2]
  elif line.startswith('\\t') and key:values[key]+=line.strip()
 for kind in ('Output_Path','Error_Path'):
  value=values[kind];path=Path(value.split(':',1)[1]);assert str(path).startswith('/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/')
  if not path.is_file():continue
  assert not path.is_symlink() and path.stat().st_size<5*1024**2
  records.append({'bundle':name,'job':job,'kind':kind,'source_path':str(path),'text':path.read_text(errors='replace')})
print(json.dumps(records))
'''.replace('SELECTED',repr(selected))
r=subprocess.run(['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch','bash -lc '+shlex.quote('python3 -c '+shlex.quote(code))],capture_output=True,text=True,timeout=45);assert r.returncode==0,r.stderr[-500:]
rows=json.loads(r.stdout);manifest=[]
for row in rows:
 dest=OUT/row['bundle']/'runs'/row['job']/('scheduler-'+row['kind']+'.log');assert not dest.exists();dest.write_text(row.pop('text'));row.update(local_path=str(dest.relative_to(OUT)),bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest());manifest.append(row)
(OUT/'SCHEDULER-OUTPUT-COLLECTION.json').write_text(json.dumps({'collected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':manifest},indent=2)+'\n');print('Collected',len(manifest),'selected scheduler output streams')
