"""Replay transferred cut evidence without changing the frozen payload."""
from pathlib import Path
import hashlib,json,re
E=Path(__file__).resolve().parent;O=E/'completed-2294919';c=json.loads((O/'collection.json').read_text());root=O/'collected'
for name,row in c['files'].items():
 b=(root/name).read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
def j(n):return json.loads((root/n).read_text())
for phase in ['before','after']:
 x=j('kit/runs/2294919-source-'+phase+'.json');assert x['passed'] and x['all_source_hashes_match'] and x['files']==45
mesh=j('kit/runs/2294919-mesh-before.json');canonical=json.loads((E/'payload/expected-mesh.json').read_text())['unpacked_members_match_archive']
assert mesh['passed'] and not mesh['mismatches'] and sorted(mesh['members'],key=lambda x:x['file'])==sorted(canonical,key=lambda x:x['file'])
cut=j('kit/runs/2294919-cut-validation.json');assert cut['passed'] and cut['ranks']==40 and cut['mesh_cells']==65334765 and cut['restored_zero_fields']==240
log=(root/'artifacts/cut-N40-scotch/logFiles/decomposePar.log').read_text()
cells=[int(x) for x in re.findall(r'(?m)^\s*Number of cells\s*=\s*(\d+)\s*$',log)]
assert len(cells)==40 and cells==cut['cells_by_rank'] and sum(cells)==65334765 and min(cells)>0
assert 'version=v2512' in log and 'scalar=64' in log and re.search(r'(?m)^End\s*$',log) and not re.search(r'FOAM FATAL|MPI_ABORT|FATAL ERROR',log,re.I)
assert 'TRIPLEU_IRIS_SCOTCH40_CUT_NATIVE_PASS' in (root/'kit/runs/2294919.out').read_text()
rows=[x.split('|') for x in c['accounting']['stdout'].splitlines() if x]
assert c['accounting']['rc']==0 and [x for x in rows if x[0]=='2294919']==[['2294919','COMPLETED','0:0','255','56','iris001']]
res=(root/'artifacts/cut-N40-scotch/logFiles/decomposePar.resource.txt').read_text()
rss=int(re.search(r'Maximum resident set size \(kbytes\):\s*(\d+)',res).group(1))
cpu=int(re.search(r'Percent of CPU this job got:\s*(\d+)%',res).group(1))
result={'passed':True,'job_id':'2294919','terminal_state':'COMPLETED','exit_code':'0:0','elapsed_seconds':255,'allocated_CPUs':56,'allocated_CPU_hours':255*56/3600,'ranks':40,'cells':sum(cells),'restored_zero_fields':240,'minimum_cells_per_rank':min(cells),'maximum_cells_per_rank':max(cells),'maximum_to_mean_cells_ratio':max(cells)/(sum(cells)/40),'process_peak_RSS_KiB':rss,'process_CPU_percent':cpu,'verified_files':len(c['files']),'limitations':['Cut only; not initialized READY or solver score','Cell balance is not a performance prediction','GNU time process resources are not node memory-bandwidth telemetry','Hardware counters and per-rank communication telemetry not collected','Site SU rate unknown']}
(E/'cut-review.json').write_text(json.dumps(result,indent=2)+'\n');(O/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
