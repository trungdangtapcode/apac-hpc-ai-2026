"""Retain pinned official rules and selected public reference logs; no jobs."""
import concurrent.futures,datetime,hashlib,json,urllib.request
from pathlib import Path
O=Path(__file__).resolve().parent
REV='b4df52907f5bbb9152ef6ae902c925fc79d54417'
tree=json.loads((O/'tree.json').read_text());assert tree['sha']==REV and not tree['truncated']
docs=['README.md','2. OpenFOAM HPC Task Rules.md','4.1 OpenFOAM Application Notes - Iris.md','4.2 OpenFOAM Application Notes - Gadi.md','4.3 OpenFOAM Application Notes - ASPIRE-2A.md']
folders=[base+'/'+method+'-'+str(nodes)+'node' for base in ['4.2-gadi-logs','4.3-aspire2a-logs'] for method in ['hierarchical','scotch'] for nodes in [1,2,4]]
folders+=['4.2-gadi-logs/reuse-scotch-4node','4.3-aspire2a-logs/scotch-split-4node']
folders+=['4.3-aspire2a-logs/reuse-scotch-4node-'+str(i) for i in [1,2,3]]
folders+=['4.3-aspire2a-logs/'+setting+'-'+method+'-4node' for setting in ['noxrc','nosrx'] for method in ['hierarchical','scotch']]
selected=[r for r in tree['tree'] if r['type']=='blob' and (r['path'] in docs or any(r['path'].startswith(f+'/') for f in folders) or r['path'] in ['4.3-aspire2a-logs/sigbus-probe/a2a.c','4.3-aspire2a-logs/sigbus-probe/stage.c'])]
assert all(r['size']<1024*1024 for r in selected)
def fetch(row):
 path=row['path'];url='https://raw.githubusercontent.com/hpcac/2026-APAC-HPC-AI/'+REV+'/'+urllib.parse.quote(path)
 p=O/'sources'/path;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():data=p.read_bytes()
 else:
  data=urllib.request.urlopen(url,timeout=40).read()
  assert len(data)==row['size']
  assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['sha']
  p.write_bytes(data)
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['sha']
 return dict(path=path,url=url,bytes=len(data),git_blob=row['sha'],sha256=hashlib.sha256(data).hexdigest())
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(fetch,selected))
manifest=dict(retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),repository='https://github.com/hpcac/2026-APAC-HPC-AI',revision=REV,public_reference_not_our_measurements=True,files=files)
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(files=len(files),bytes=sum(r['bytes'] for r in files),revision=REV)))
