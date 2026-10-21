"""Validate sealed mandatory native initialization before the first solver."""
from pathlib import Path
import hashlib, json, re, datetime
r = Path(__file__).resolve().parent
d = r / 'collected/2293753'
a = d / 'artifacts/ready-N56-h742'
for relative, digest in json.loads((d / 'evidence-sha256.json').read_text()).items():
    assert hashlib.sha256((d / relative).read_bytes()).hexdigest() == digest
c = json.loads((d / 'collection.json').read_text())
assert '2293753|COMPLETED|0:0|103|56|1|iris031' in c['accounting']
assert sorted(c['processors']) == sorted('processor'+str(i) for i in range(56))
receipt = json.loads((d / 'init65-receipt.json').read_text())
assert receipt['returncode'] == 0 and receipt['stdout'].strip() == '2293753'
assert receipt['sha256'] == hashlib.sha256((r / 'kit/03.2-init-65M-N56.sbatch').read_bytes()).hexdigest()
assert '03.2-init-65M-N56: PASS' in (d / 'runs/2293753.out').read_text()
assert not (d / 'runs/2293753.err').read_text().strip()
ready = dict(line.split('=', 1) for line in (a / 'READY').read_text().splitlines())
assert ready == dict(N='56', method='hierarchical', nHierarchical='(7 4 2)',
                     mesh='occDrivAer-65M',
                     stages='decomposePar restore0Dir renumberMesh potentialFoam applyBoundaryLayer')
rows = []
for name, flags in [('renumberMesh', '-constant -overwrite -parallel'),
                    ('potentialFoam', '-initialiseUBCs -parallel'),
                    ('applyBoundaryLayer', '-ybl 0.0450244 -parallel')]:
    t = (a / 'logFiles' / (name+'.log')).read_text()
    assert re.search(r'^End\s*$', t, re.M)
    assert 'FOAM FATAL' not in t and 'died from signal' not in t
    assert 'OPENFOAM=2512' in t and 'scalar=64' in t
    assert re.search(r'^nProcs\s*:\s*56\s*$', t, re.M)
    assert 'Exec   : '+name+' '+flags in t
    rows.append(dict(stage=name, clock_seconds=int(re.findall(r'ClockTime = (\d+) s', t)[-1])))
for relative in ['system/fvSchemes', 'system/fvSolution', 'system/controlDict',
                 'system/include/caseDefinition', 'system/decomposeParDict']:
    assert (a / relative).read_bytes() == (r / 'collected/2293752/artifacts/ready-N56-h742' / relative).read_bytes()
t = (a / 'logFiles/potentialFoam.log').read_text()
out = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
           job='2293753', state='MANDATORY_INITIALIZATION_PASS', elapsed_seconds=103,
           allocated_cpus=56, nodes=1, node='iris031', mpi_ranks=56, stages=rows,
           max_rss_KiB_reported=89855312, max_rss_GiB=89855312/1024**2,
           total_cpu_time_reported='01:29:32',
           potential_continuity_error=float(re.search(r'Continuity error = ([\deE.+-]+)', t)[1]),
           potential_velocity_interpolation_error=float(re.search(r'Interpolated velocity error = ([\deE.+-]+)', t)[1]),
           solver_completed=False, score=None,
           limits='Accounting RSS is the reported batch value, not per-rank RSS or bandwidth. No CPU/NUMA/network hardware counters or billed SU collected. Full binary fields not archived; full mesh content hash remains unverified.')
(r / 'init-review.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(out, indent=2))
