"""Accept fixed-work solve output; a successful exit alone is insufficient."""
from pathlib import Path
import sys,json,re,math,collections
p=Path(sys.argv[1]);s=(p/'logFiles/simpleFoam.log').read_text()
steps=[int(x) for x in re.findall(r'^Time = (\d+)\s*$',s,re.M)];assert steps==list(range(1,41))
for name,n in [('Ux',15),('Uy',15),('Uz',15),('p',12),('omega',8),('k',8)]:
 counts=[int(x) for x in re.findall(r'Solving for '+name+r',.*?No Iterations (\d+)',s)]
 assert counts==[n]*40,(name,collections.Counter(counts))
average=float(re.search(r'Average wall-clock time per time step\s*=\s*([\deE.+-]+)',s)[1]);assert math.isfinite(average) and average>0
rows=[list(map(float,line.split())) for line in (p/'postProcessing/forceCoeffsAll/0/coefficient.dat').read_text().splitlines() if line.strip() and not line.startswith('#')]
assert [int(row[0]) for row in rows]==steps and all(math.isfinite(v) for row in rows for v in row)
assert 0.3<rows[-1][1]<0.6,'Broad diagnostic sanity bound, not an official accuracy tolerance'
(p/'semantic-result.json').write_text(json.dumps(dict(passed=True,steps=40,average_seconds_step=average,final_Cd_dimensionless=rows[-1][1],scope='One-node ordered method screen; no four-node score'),indent=2)+'\n')
