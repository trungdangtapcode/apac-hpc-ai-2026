"""Review immutable native Scotch preparation and conservative resource evidence."""
from pathlib import Path
import json,hashlib,re,datetime,statistics
r=Path(__file__).resolve().parent;job=json.loads((r/'submission.json').read_text())['stdout'].strip();d=r/'collected'/job
for relative,digest in json.loads((d/'evidence-sha256.json').read_text()).items():assert hashlib.sha256((d/relative).read_bytes()).hexdigest()==digest
j=json.loads((r/'terminal-accounting.json').read_text())['jobs'][job];assert j['job_state']=='F' and j['Exit_status']==0
assert j['Resource_List']['ncpus']==32 and j['Resource_List']['ngpus']==0
mesh=json.loads((d/'mesh-identity.json').read_text());assert mesh['archive_md5']=='50393a15d84f53255fda85ac702390e9'
assert mesh['archive_sha256']=='ef30fa8405dbaab77185ace2521b1bedc5650f245e40d7451259a5ac773a5376' and len(mesh['unpacked_members_match_archive'])==8
assert (d/'iris-control-semantic.PASS').read_text().strip()=='PASS' and not (d/'iris-control-semantic.diff').read_text()
a=d/'artifacts/scotch-N128';ready=json.loads((a/'CUT_READY.json').read_text());assert ready['method']=='scotch' and ready['ranks']==128 and ready['total_cells']==65334765
t=(a/'logFiles/decomposePar.log').read_text();assert re.search(r'^End\s*$',t,re.M) and 'FOAM FATAL' not in t
assert 'OPENFOAM=2512' in t and 'scalar=64' in t and 'scotch [128]' in t
cells=[int(v) for v in re.findall(r'^    Number of cells\s*=\s*(\d+)',t,re.M)]
faces=[int(v) for v in re.findall(r'^    Number of processor faces\s*=\s*(\d+)',t,re.M)]
neighbors=[int(v) for v in re.findall(r'^    Number of processor patches\s*=\s*(\d+)',t,re.M)]
assert len(cells)==len(faces)==len(neighbors)==128 and sum(cells)==65334765
for p in (a/'system').rglob('*'):
 if p.is_file():assert p.read_bytes()==(r/'payload/case/system'/p.relative_to(a/'system')).read_bytes()
assert 'Restore 0/' in (a/'logFiles/restore0Dir.log').read_text()
output=d/('tu-cpu-s128.o'+job.split('.')[0]);assert 'CPU_N128_CUT_PASS' in output.read_text()
seal=json.loads((d/'control-initial-fields.json').read_text());assert seal['baseline_job']=='25905114.pbs101'
assert len(seal['files'])>=768 and len(set(x['file'] for x in seal['files']))==len(seal['files'])
assert all(re.fullmatch('[0-9a-f]{64}',x['sha256']) for x in seal['files'])
h,m,s=map(int,j['resources_used']['walltime'].split(':'));elapsed=h*3600+m*60+s
rss=int(re.fullmatch(r'(\d+)kb',j['resources_used']['mem'])[1])
out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),job=job,state='MESH_IDENTITY_AND_SCOTCH_CUT_RESTORE_PASS',elapsed_seconds=elapsed,ncpus=32,serial_tasks=1,target_mpi_ranks=128,total_cells=sum(cells),cell_min=min(cells),cell_max=max(cells),cell_mean=statistics.mean(cells),max_cell_over_mean_fraction=max(cells)/statistics.mean(cells)-1,max_processor_faces=max(faces),unique_interface_faces=sum(faces)//2,max_processor_neighbors=max(neighbors),max_rss_KiB_reported=rss,max_rss_GiB=rss/1024**2,estimated_base_SU=32*elapsed/3600,posted_charge_reconciled=False,control_zero_fields_sealed=len(seal['files']),remaining='Candidate mandatory parallel initialization and both 40-step solves must pass. Prep completion is not a score.',limitations='Processor trees stay on cluster. Graph cuts do not prove a CPU or NUMA bottleneck. Hardware counters, bandwidth, page placement and power not collected. Batch CPU/memory are coarse maxima.')
(r/'review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
