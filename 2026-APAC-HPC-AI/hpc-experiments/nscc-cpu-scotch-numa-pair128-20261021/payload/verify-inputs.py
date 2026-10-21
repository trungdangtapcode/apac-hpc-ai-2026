"""Verify accepted initialized default Scotch and fresh NUMA candidate inputs."""
from pathlib import Path
import hashlib,json
c=json.loads(Path('inputs.json').read_text());h=json.loads(Path('accepted-inputs.json').read_text())
assert json.loads(Path(c['control_solve_receipt']).read_text())['passed'] is True
for role in ['control','candidate']:
 p=Path(c[role]);ready=json.loads((p/'CUT_READY.json').read_text());assert ready['method']=='scotch' and ready['ranks']==128 and ready['total_cells']==65334765
 if role=='candidate':assert ready['domains']==[8,16] and ready['domainWeights']==[1,0.1]
 for name,digest in h[role].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,(role,name)
 assert sorted(v.name for v in p.glob('processor*') if v.is_dir())==sorted('processor'+str(i) for i in range(128))
Path('INPUTS_VALIDATED.json').write_text(json.dumps(dict(passed=True,inputs=c),indent=2)+'\n')
