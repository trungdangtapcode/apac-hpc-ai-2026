"""Validate both immutable Basic case inputs before any new initialization."""
from pathlib import Path
import hashlib,json
c=json.loads(Path('inputs.json').read_text());h=json.loads(Path('accepted-inputs.json').read_text())
assert 'init_job=25905114.pbs101' in Path(c['control_init_receipt']).read_text()
for role,method in [('control','hierarchical'),('candidate','scotch')]:
 p=Path(c[role]);ready=json.loads((p/'CUT_READY.json').read_text())
 assert ready['method']==method and ready['ranks']==128 and ready['total_cells']==65334765
 for name,digest in h[role].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,(role,name)
 assert sorted(v.name for v in p.glob('processor*') if v.is_dir())==sorted('processor'+str(i) for i in range(128))
Path('INPUTS_VALIDATED.json').write_text(json.dumps(dict(passed=True,inputs=c),indent=2)+'\n')
