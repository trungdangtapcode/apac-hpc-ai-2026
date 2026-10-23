"""Validate native OpenFOAM completion and default Scotch decomposition."""
from pathlib import Path
import json,re,sys
s=Path(sys.argv[1]).read_text(errors='replace');kind=sys.argv[2];r=int(sys.argv[3]);assert re.search(r'^End\s*$',s,re.M),'End marker absent';assert not re.search(r'FOAM FATAL|FATAL ERROR|MPI_ABORT|died from signal|terminated by signal',s,re.I);assert 'OPENFOAM=2512' in s and 'version=v2512' in s and 'Arch   : "LSB;label=32;scalar=64"' in s;assert re.search(rf'(?m)^nProcs\s*:\s*{r}\s*$',s)
if kind=='decompose':
 assert re.search(rf'Decomposition method\s+scotch\s+\[{r}\]',s),'decomposition not default Scotch'; cells=[int(x) for x in re.findall(r'^\s+Number of cells\s*=\s*(\d+)',s,re.M)];assert len(cells)==r and sum(cells)==65334765,(len(cells),sum(cells));o={'passed':True,'stage':kind,'ranks':r,'method':'scotch','total_cells':sum(cells)}
else:o={'passed':True,'stage':kind,'ranks':r}
print(json.dumps(o,indent=2))
