"""Check one complete official split before marking it reusable."""
from pathlib import Path
import json,re,sys,hashlib
root=Path(sys.argv[1]);role=sys.argv[2];case=root/'artifacts'/role;spec=json.loads((root/'case-inputs.json').read_text())[role]
for name,digest in spec['sha256'].items():assert hashlib.sha256((case/name).read_bytes()).hexdigest()==digest,(role,name)
s=(case/'logFiles/decomposePar.log').read_text();assert re.search(r'^End\s*$',s,re.M) and 'FOAM FATAL' not in s and 'OPENFOAM=2512' in s and 'scalar=64' in s
assert spec['method']+' [256]' in s
assert sorted(p.name for p in case.glob('processor*') if p.is_dir())==sorted('processor'+str(i) for i in range(256))
cells=[int(x) for x in re.findall(r'^    Number of cells\s*=\s*(\d+)',s,re.M)];assert len(cells)==256 and sum(cells)==65334765
for rank in range(256):
 assert all((case/('processor'+str(rank))/'0'/n).is_file() for n in ['U','p','k','omega','nut','nuTilda'])
(case/'CUT_READY.json').write_text(json.dumps(dict(ranks=256,method=spec['method'],domains=spec['domains'],hierarchical_factors=spec['hierarchical_factors'],total_cells=sum(cells),scope='Native cut and restored initial fields; mandatory parallel initialization not yet run'),indent=2)+'\n')
