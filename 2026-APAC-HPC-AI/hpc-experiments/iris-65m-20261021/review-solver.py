"""Review the first sealed 65M Iris solve; Iris is practice, not a scored site."""
from pathlib import Path
import json, re, hashlib, statistics, math, datetime
r = Path(__file__).resolve().parent
d = r / 'collected/2293754'
s = d / 'runs/2293754'
for relative, digest in json.loads((d / 'evidence-sha256.json').read_text()).items():
    assert hashlib.sha256((d / relative).read_bytes()).hexdigest() == digest
c = json.loads((d / 'collection.json').read_text())
assert '2293754|COMPLETED|0:0|925|56|1|iris031' in c['accounting']
receipt = json.loads((d / 'solver40-receipt.json').read_text())
assert receipt['sha256'] == hashlib.sha256((r / 'kit/04-simpleFoam-65M-N56.sbatch').read_bytes()).hexdigest()
assert receipt['stdout'].strip() == '2293754'
assert len(c['processor_links']) == 56
assert all(v.endswith('/artifacts/ready-N56-h742/'+k) for k,v in c['processor_links'].items())
assert c['constant_link'].endswith('/artifacts/ready-N56-h742/constant')
old = r / 'collected/2293753/artifacts/ready-N56-h742/system'
for p in (s / 'system').rglob('*'):
    if p.is_file() and p.name != 'controlDict':
        assert p.read_bytes() == (old / p.relative_to(s/'system')).read_bytes()
control = (s/'system/controlDict').read_text()
assert re.search(r'^startFrom\s+startTime;', control, re.M)
assert re.search(r'^endTime\s+40;', control, re.M)
source = (old/'FOwallClockTimeStatistics').read_text()
assert [v.strip() for v in re.findall(r'#\{(.*?)#\}', source, re.S)] == [v.strip() for v in re.findall(r'#\{(.*?)#\}', control, re.S)]
t = (s/'logFiles/simpleFoam.log').read_text()
assert 'OPENFOAM=2512' in t and 'scalar=64' in t
assert re.search(r'^End\s*$', t, re.M)
assert 'FOAM FATAL' not in t and 'died from signal' not in t
assert re.search(r'^nProcs\s*:\s*56\s*$', t, re.M)
steps = [int(v) for v in re.findall(r'^Time = (\d+)\s*$', t, re.M)]
assert steps == list(range(1,41))
dt = [float(v) for v in re.findall(r'Wall-clock time elapsed during the current time step = ([\deE.+-]+)', t)]
avg = float(re.search(r'Average wall-clock time per time step\s*=\s*([\deE.+-]+)', t)[1])
assert len(dt) == 39 and all(math.isfinite(v) and v>0 for v in dt)
assert abs(statistics.mean(dt)-avg) < 1e-10
wall = s/'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat'
rows = [list(map(float,line.split())) for line in wall.read_text().splitlines() if line.strip() and not line.startswith('#')]
assert [int(x[0]) for x in rows] == list(range(2,41))
assert all(abs(a-b[2])<1e-10 for a,b in zip(dt,rows))
cdrows = [list(map(float,line.split())) for line in (s/'postProcessing/forceCoeffsAll/0/coefficient.dat').read_text().splitlines() if line.strip() and not line.startswith('#')]
assert [int(x[0]) for x in cdrows] == steps and all(math.isfinite(v) for row in cdrows for v in row)
assert '04-simpleFoam-65M-N56: PASS' in (d/'runs/2293754.out').read_text()
stderr = (d/'runs/2293754.err').read_text()
# foamDictionary -set echoes its changed entries to stderr; permit only those.
assert re.sub(r'\s+', ' ', stderr).strip() == 'startFrom startTime; endTime 40;'
iterations = {}
for field, count in re.findall(r'Solving for (\w+),.*?No Iterations (\d+)', t):
    iterations.setdefault(field,{}).setdefault(count,0)
    iterations[field][count] += 1
proof = r.parent/'nscc-cpu-baseline-20261021/collected/25904959.pbs101/iris-control-replay'
a = (proof/'expected-expanded.dict').read_text()
b = (proof/'actual-expanded.dict').read_text()
x, y = '// "system/controlDict"', '// "actual-controlDict"'
assert a.count(x) == b.count(y) == 1
assert a.replace(x, '// "CONTROL_INPUT"') == b.replace(y, '// "CONTROL_INPUT"')
out = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
           job='2293754', state='IRIS_PRACTICE_FULL_CHAIN_PASS',
           complete_predecessors=['2293752','2293753'], elapsed_seconds=925,
           ranks=56, nodes=1, node='iris031', method='hierarchical', factors=[7,4,2],
           iterations=40, measured_steps=39, average_seconds_step=avg,
           median_seconds_step=statistics.median(dt),
           p95_seconds_step=statistics.quantiles(dt,n=100,method='inclusive')[94],
           min_seconds_step=min(dt),max_seconds_step=max(dt),
           final_Cd_dimensionless=cdrows[-1][1],
           basic_Cd_assessment='0.440554 is near the published approximate 40-step value ~0.43; no universal Basic +/-0.5% gate. Not a converged final aerodynamic solution.',
           iteration_count_distribution=iterations,
           omega_bounding_messages=t.count('bounding omega'),
           timing_confidence_warning='smaller than the calculated one' in t,
           max_rss_KiB_reported=139841904,max_rss_GiB=139841904/1024**2,
           total_cpu_time_reported='14:11:24',full_chain_node_seconds=161+103+925,
           contest_score=None,
           limits='Iris practice only; no matched comparator or speedup. Full Iris mesh content identity, billed Iris SU, NUMA/bandwidth/network hardware counters not collected. Bounding messages retained, not zeroed or hidden.')
(r/'solver-review.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
