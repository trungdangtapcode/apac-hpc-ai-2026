"""Verify fresh official two-node cases before mandatory initialization."""
from pathlib import Path
import json,hashlib
c=json.loads(Path('inputs.json').read_text());h=json.loads(Path('accepted-inputs.json').read_text())
for role,method in [('control','hierarchical'),('candidate','scotch')]:
 p=Path(c[role]);ready=json.loads((p/'CUT_READY.json').read_text());assert ready['ranks']==256 and ready['method']==method and ready['total_cells']==65334765
 if role=='control':assert ready['hierarchical_factors']==[16,8,2]
 for name,digest in h[role].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,(role,name)
 assert sorted(x.name for x in p.glob('processor*') if x.is_dir())==sorted('processor'+str(i) for i in range(256))
Path('INPUTS_VALIDATED.json').write_text(json.dumps(dict(passed=True,inputs=c),indent=2)+'\n')
