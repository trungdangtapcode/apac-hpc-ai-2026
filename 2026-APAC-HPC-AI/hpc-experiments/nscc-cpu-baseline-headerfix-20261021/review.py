"""Review sealed CPU mesh identity and N128 preparation, not solver scoring."""
from pathlib import Path
import json, hashlib, re, datetime
r=Path(__file__).resolve().parent;d=r/'collected/25905006.pbs101'
for relative,digest in json.loads((d/'evidence-sha256.json').read_text()).items():
    assert hashlib.sha256((d/relative).read_bytes()).hexdigest()==digest
j=json.loads((r/'terminal-accounting.json').read_text())['jobs']['25905006.pbs101']
assert j['job_state']=='F' and j['Exit_status']==0
assert j['resources_used']['walltime']=='00:03:07'
assert j['Resource_List']['ncpus']==32 and j['Resource_List']['ngpus']==0
mesh=json.loads((d/'mesh-identity.json').read_text())
assert mesh['archive_md5']=='50393a15d84f53255fda85ac702390e9'
assert mesh['archive_sha256']=='ef30fa8405dbaab77185ace2521b1bedc5650f245e40d7451259a5ac773a5376'
assert len(mesh['unpacked_members_match_archive'])==8
assert (d/'iris-control-semantic.PASS').read_text().strip()=='PASS'
assert not (d/'iris-control-semantic.diff').read_text()
a=d/'artifacts/hierarchical-N128-h1642';ready=json.loads((a/'CUT_READY.json').read_text())
assert ready['ranks']==128 and ready['method']=='hierarchical' and ready['factors']==[16,4,2]
t=(a/'logFiles/decomposePar.log').read_text()
assert re.search(r'^End\s*$',t,re.M) and 'FOAM FATAL' not in t
assert 'OPENFOAM=2512' in t and 'scalar=64' in t and 'hierarchical [128]' in t
cells=[int(v) for v in re.findall(r'^    Number of cells\s*=\s*(\d+)',t,re.M)]
faces=[int(v) for v in re.findall(r'^    Number of processor faces\s*=\s*(\d+)',t,re.M)]
assert len(cells)==len(faces)==128 and sum(cells)==65334765
for p in (a/'system').rglob('*'):
    if p.is_file():assert p.read_bytes()==(r/'payload/case/system'/p.relative_to(a/'system')).read_bytes()
assert 'Restore 0/' in (a/'logFiles/restore0Dir.log').read_text()
assert 'CPU_N128_CUT_PASS' in (d/'tu-cpu-h128r2.o25905006').read_text()
out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),job='25905006.pbs101',
         state='MESH_IDENTITY_AND_CUT_RESTORE_PASS',elapsed_seconds=187,ncpus=32,serial_tasks=1,
         target_mpi_ranks=128,total_cells=sum(cells),cell_min=min(cells),cell_max=max(cells),
         max_processor_faces=max(faces),archive_sha256=mesh['archive_sha256'],
         max_rss_KiB_reported=31795732,max_rss_GiB=31795732/1024**2,
         estimated_base_SU=32*187/3600,posted_charge_reconciled=False,
         remaining='Mandatory renumberMesh, potentialFoam, applyBoundaryLayer and simpleFoam not run here',
         limits='Input checks and processor fields verified on compute by frozen payload and CUT_READY; binary processor trees not downloaded. No hardware bandwidth/NUMA counters; CPUpercent accounting is coarse. No CPU solver score.')
(r/'review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
