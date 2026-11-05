"""Read-only boundary-face proxy under the actual launch probes; no solver."""
from pathlib import Path
import hashlib,json,re,sys
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E.parent/'tools'));from iris_bridge import run_json
root=json.loads((E/'deployment.json').read_text())['root'];core=json.loads((E/'accepted-source-manifest-48.json').read_text())
body='ROOT='+repr(root)+'\nPINS='+repr({k:v for k,v in core['files'].items() if k.endswith('/constant/polyMesh/boundary')})+'''\nfrom pathlib import Path
import re,json,hashlib,datetime
k=Path(ROOT)/'kit';r=k/'runs/2294920';src=Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch48-cut-20261105T073707Z/artifacts/cut-N48-scotch')
hardware=(k/'runs/2294920-hardware.txt').read_text();nodes={}
def cpu_list(text):
 values=set()
 for item in text.strip().split(','):
  if '-' in item:
   a,b=map(int,item.split('-'));values.update(range(a,b+1))
  else:values.add(int(item))
 return values
for node,text in re.findall(r'^NUMA node(\\d+) CPU\\(s\\):\\s*(.+)$',hardware,re.M):nodes[int(node)]=cpu_list(text)
assert len(nodes)==2
maps={};counts={}
for label in ['O1-original48','H1-hybrid48']:
 p=json.loads((r/(label+'-preparation.json')).read_text());assert p['passed'] and p['rank_count']==48
 mapping={}
 for rank,cpus in p['cpu_affinity_masks'].items():
  mask=set(cpus);matches=[n for n,ids in nodes.items() if mask and mask<=ids];assert len(matches)==1
  mapping[int(rank)]=matches[0]
 assert set(mapping)==set(range(48));maps[label]=mapping;counts[label]={str(n):list(mapping.values()).count(n) for n in nodes}
edges={};files={};total_bytes=0
assert len(PINS)==48
for rank in range(48):
 name='processor%d/constant/polyMesh/boundary'%rank;assert (src/name).stat().st_size<100000;raw=(src/name).read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest==PINS[name];total_bytes+=len(raw);files[name]={'sha256':digest,'bytes':len(raw)}
 for block in re.findall(r'\\{([^{}]*)\\}',raw.decode(),re.S):
  if 'neighbProcNo' not in block:continue
  assert re.search(r'\\btype\\s+processor\\s*;',block)
  mine=int(re.search(r'\\bmyProcNo\\s+(\\d+)\\s*;',block).group(1));other=int(re.search(r'\\bneighbProcNo\\s+(\\d+)\\s*;',block).group(1));faces=int(re.search(r'\\bnFaces\\s+(\\d+)\\s*;',block).group(1))
  assert mine==rank and 0<=other<48 and other!=rank and faces>0
  edges[(rank,other)]=edges.get((rank,other),0)+faces
assert edges and all(edges[(j,i)]==faces for (i,j),faces in edges.items())
unique=[(i,j,n) for (i,j),n in edges.items() if i<j]
result={'utc':datetime.datetime.utcnow().isoformat()+'Z','job_id':'2294920','scope':'Read-only logical interface-face proxy, under PRE-MPI_Init rank probe masks matched to recorded compute-node NUMA CPU topology. Not bytes, communication time, page placement or a causal speed explanation.','node_topology_from_job_lscpu':{str(n):sorted(ids) for n,ids in nodes.items()},'rank_counts_by_NUMA':counts,'unique_interface_faces':sum(n for i,j,n in unique),'cross_NUMA_unique_faces':{label:sum(n for i,j,n in unique if mapping[i]!=mapping[j]) for label,mapping in maps.items()},'boundary_bytes_read':total_bytes,'boundary_files_verified':files,'graph_edges':unique,'rank_maps':{label:{str(i):n for i,n in mapping.items()} for label,mapping in maps.items()}}
'''
r=run_json(body,timeout=55)
cut=(E.parent/'iris-scotch48-cut-20261105/completed-2294914/collected/artifacts/cut-N48-scotch/logFiles/decomposePar.log').read_text()
expected=int(re.search(r'(?m)^Number of processor faces\s*=\s*(\d+)',cut).group(1))
assert expected==r['unique_interface_faces']
r.update(native_cut_unique_processor_faces=expected,native_cut_face_total_replayed=True)
(E/'rank-interface-proxy-2294920.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['node_topology_from_job_lscpu','boundary_files_verified','graph_edges','rank_maps']},indent=2))
