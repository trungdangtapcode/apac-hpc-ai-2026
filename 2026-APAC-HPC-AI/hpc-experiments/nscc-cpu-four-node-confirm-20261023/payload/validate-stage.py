"""Check native command completion and OpenFOAM precision/process labels."""
from pathlib import Path
import json,re,sys
p=Path(sys.argv[1]);kind=sys.argv[2];rank=int(sys.argv[3]) if len(sys.argv)>3 else None;s=p.read_text(errors='replace')
assert re.search(r'^End\s*$',s,re.M),'native End marker missing'
assert not re.search(r'FOAM FATAL|FATAL ERROR|MPI_ABORT|died from signal|terminated by signal',s,re.I),'native failure marker present'
assert 'OPENFOAM=2512' in s and 'version=v2512' in s and 'Arch   : "LSB;label=32;scalar=64"' in s
if rank is not None: assert re.search(rf'(?m)^nProcs\s*:\s*{rank}\s*$',s),f'nProcs mismatch: expected {rank}'
if kind=='decompose':
 assert re.search(r'Decomposition method\s+scotch\s+\[512\]',s),'native decomposition is not default Scotch [512]'
 cells=[int(x) for x in re.findall(r'^\s+Number of cells\s*=\s*(\d+)',s,re.M)]
 assert len(cells)==512 and sum(cells)==65334765,(len(cells),sum(cells))
 out={'passed':True,'stage':kind,'decomposition':'scotch','ranks':512,'cell_records':len(cells),'total_cells':sum(cells)}
else:out={'passed':True,'stage':kind,'nProcs':rank}
print(json.dumps(out,indent=2))
