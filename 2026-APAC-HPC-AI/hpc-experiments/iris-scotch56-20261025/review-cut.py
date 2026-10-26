"""Replay the retained native cut and transfer-integrity checks."""
from pathlib import Path
import hashlib,json,re
E=Path(__file__).resolve().parent;d=json.loads((E/'completed-2294040.json').read_text());f=d['files']
for name,row in f.items():
 raw=row['text'].encode('utf-8');assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name
 out=E/'collected'/name;out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():assert out.read_bytes()==raw
 else:out.write_bytes(raw)
for phase in ['before','after']:
 source=json.loads(f['runs/2294040-source-'+phase+'.json']['text'])
 assert source['passed'] and source['all_source_hashes_match']
 expected=json.loads((E/'deployment.json').read_text())['files']
 assert source['files']==len(expected)
mesh=json.loads(f['runs/2294040-mesh-before.json']['text']);assert mesh['passed'] and not mesh['mismatches'] and len(mesh['members'])==8
canonical=json.loads((E/'payload/expected-mesh.json').read_text())['unpacked_members_match_archive']
assert sorted(mesh['members'],key=lambda x:x['file'])==sorted(canonical,key=lambda x:x['file'])
cut=json.loads(f['runs/2294040-cut-validation.json']['text']);assert cut['passed'] and cut['ranks']==56 and cut['mesh_cells']==65334765 and cut['restored_zero_fields']==336
log=f['artifacts/ready-N56-scotch/logFiles/decomposePar.log']['text']
cells=[int(x) for x in re.findall(r'(?m)^\s*Number of cells\s*=\s*(\d+)\s*$',log)]
assert cells==cut['cells_by_rank'] and len(cells)==56 and sum(cells)==65334765
assert re.search(r'(?m)^End\s*$',log) and 'version=v2512' in log and 'scalar=64' in log
assert not re.search(r'FOAM FATAL|MPI_ABORT|FATAL ERROR',log,re.I)
assert 'TRIPLEU_IRIS_SCOTCH56_CUT_NATIVE_PASS' in f['runs/2294040.out']['text']
assert '2294040|COMPLETED|0:0|00:04:27|56|iris005|' in d['accounting']['stdout']
result={'passed':True,'job_id':'2294040','terminal_state':'COMPLETED','exit_code':'0:0','allocation_wall_seconds':267,'allocated_CPUs':56,'estimated_allocated_CPU_hours':56*267/3600,'SU_charge':None,'ranks':56,'cells':sum(cells),'restored_zero_fields':336,'minimum_cells_per_rank':min(cells),'maximum_cells_per_rank':max(cells),'maximum_to_mean_cells_ratio':max(cells)/(sum(cells)/56),'native_decomposition_wall_seconds':243.89,'native_decomposition_maximum_RSS_KiB':33323056,'decomposition_process_CPU_percent':99,'transfer_verified_files':len(f),'limitations':['No parallel initialization, solver, Cd or performance comparison yet','Process resource report is not per-node memory bandwidth or hardware telemetry','Slurm and GNU time peak RSS are different collectors','No Iris SU charging rate exposed']}
(E/'cut-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
