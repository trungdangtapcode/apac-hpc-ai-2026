"""Collect bounded terminal rank-policy diagnostic artifacts; never submit a job."""
from pathlib import Path
import base64,hashlib,json,sys
from iris_bridge import run_json
E=Path(sys.argv[1]).resolve();receipt=json.loads((E/'submission-receipt.json').read_text());job=receipt['job_id'];assert str(job).isdigit();root=receipt['root'];C=E/('completed-'+job);assert not C.exists()
body='ROOT='+repr(root)+'\nJOB='+repr(job)+'''\nfrom pathlib import Path
import subprocess,json,hashlib,base64,datetime
k=Path(ROOT)/'kit';files={}
p=subprocess.run(['sacct','-j',JOB,'-X','-P','-n','-o','JobID,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList'],capture_output=True,text=True,timeout=15)
assert p.returncode==0
row=p.stdout.strip().split('|');assert row[0]==JOB and row[1] in ['COMPLETED','FAILED','TIMEOUT','CANCELLED','NODE_FAIL','OUT_OF_MEMORY'],row
for f in list((k/'runs').rglob('*'))+[k/'runtime-environment.txt',k/(JOB+'.out'),k/(JOB+'.err')]:
 if f.is_file() and not f.is_symlink():
  raw=f.read_bytes();assert len(raw)<500000
  files[str(f.relative_to(k))]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'base64':base64.b64encode(raw).decode()}
result={'utc':datetime.datetime.utcnow().isoformat()+'Z','accounting':p.stdout,'files':files}
'''
r=run_json(body,timeout=55);C.mkdir()
for n,m in r['files'].items():
 assert not Path(n).is_absolute() and '..' not in Path(n).parts
 raw=base64.b64decode(m.pop('base64'),validate=True);assert len(raw)==m['bytes'] and hashlib.sha256(raw).hexdigest()==m['sha256']
 p=C/'collected'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
(C/'collection.json').write_text(json.dumps(r,indent=2)+'\n')
for arm in ['inherited','interleave']:
 rows=[json.loads(p.read_text()) for p in (C/'collected/runs'/arm).glob('rank-*.json')]
 print(arm,'ranks',len(rows),'policies',sorted(set(x['numactl_show'].splitlines()[0] for x in rows)),'exact',all(x['mapping']['exact_mapping_accounting'] for x in rows),'nodecounts',sorted(set(tuple(sorted(x['mapping']['numa_node_pages'].items())) for x in rows)))
print(r['accounting'],len(r['files']))
