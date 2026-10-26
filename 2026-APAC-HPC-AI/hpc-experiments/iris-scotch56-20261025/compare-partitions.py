"""Compare native partition summaries; never infer bytes or solver speedup."""
from pathlib import Path
import hashlib,json,re,tarfile
E=Path(__file__).resolve().parent;old=E.parent/'iris-65m-20261021/collected/2293752'
pins=json.loads((old/'evidence-sha256.json').read_text());tar=old/'raw-text-evidence.tar.gz'
assert hashlib.sha256(tar.read_bytes()).hexdigest()==pins[tar.name]
member='artifacts/ready-N56-h742/logFiles/decomposePar.log'
with tarfile.open(tar) as archive:raw=archive.extractfile(member).read()
assert hashlib.sha256(raw).hexdigest()==pins[member]
new=(E/'collected/artifacts/ready-N56-scotch/logFiles/decomposePar.log').read_bytes()
def parse(raw):
 text=raw.decode();cells=[int(v) for v in re.findall(r'(?m)^[ \t]+Number of cells\s*=\s*(\d+)\s*$',text)]
 faces=[int(v) for v in re.findall(r'(?m)^[ \t]+Number of processor faces\s*=\s*(\d+)\s*$',text)]
 total=int(re.search(r'(?m)^Number of processor faces = (\d+)',text).group(1))
 patches=int(re.search(r'(?m)^Max number of processor patches = (\d+)',text).group(1))
 assert len(cells)==len(faces)==56 and sum(cells)==65334765 and sum(faces)==2*total
 return {'ranks':56,'cells':sum(cells),'maximum_cells_over_mean_percent':100*(max(cells)/(sum(cells)/56)-1),'unique_processor_faces':total,'maximum_processor_faces_per_rank':max(faces),'maximum_neighbor_patches':patches,'log_sha256':hashlib.sha256(raw).hexdigest()}
a,b=parse(raw),parse(new)
r={'hierarchical_job':'2293752','scotch_job':'2294040','hierarchical':a,'scotch':b,'unique_processor_face_reduction_percent':100*(1-b['unique_processor_faces']/a['unique_processor_faces']),'maximum_processor_faces_per_rank_reduction_percent':100*(1-b['maximum_processor_faces_per_rank']/a['maximum_processor_faces_per_rank']),'meaning':'Static same-mesh same-rank decomposition comparison; not network bytes or a timing comparison. All 56 ranks are intended on one Iris node.','assessment':'Scotch reduces interface-face proxies but worsens cell balance and maximum neighbor degree. Test actual solver timing after complete initialization; no speedup established.'}
(E/'partition-comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
