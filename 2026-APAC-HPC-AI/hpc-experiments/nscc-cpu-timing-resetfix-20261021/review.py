"""Review the sealed native CPU timing diagnostic, never a contest score."""
from pathlib import Path
import json, hashlib, re, math, datetime
r = Path(__file__).resolve().parent
d = r / 'collected/25904765.pbs101'
for relative, digest in json.loads((d / 'evidence-sha256.json').read_text()).items():
    assert hashlib.sha256((d / relative).read_bytes()).hexdigest() == digest
j = json.loads((r / 'terminal-accounting.json').read_text())['jobs']['25904765.pbs101']
assert j['job_state'] == 'F' and j['Exit_status'] == 0
assert j['Resource_List']['ncpus'] == 8 and j['Resource_List']['ngpus'] == 0
assert (d / 'timing-probe.pbs').read_bytes() == (r / 'payload/timing-probe.pbs').read_bytes()
assert (d / 'FOwallClockTimeStatistics').read_bytes() == (r / 'payload/FOwallClockTimeStatistics').read_bytes()
root = d / 'runs/25904765'
semantic = json.loads((root / 'semantic-result.json').read_text())
assert semantic['passed'] and semantic['steps'] == list(range(1, 6))
t = (root / 'logFiles/simpleFoam.log').read_text()
assert 'OPENFOAM=2512' in t and 'scalar=64' in t
assert re.search(r'^End\s*$', t, re.M) and 'FOAM FATAL' not in t
assert 'died from signal' not in t
assert re.search(r'^nProcs\s*:\s*4\s*$', t, re.M)
assert [int(v) for v in re.findall(r'^Time = (\d+)\s*$', t, re.M)] == list(range(1, 6))
average = float(re.search(r'Average wall-clock time per time step\s*=\s*([\deE.+-]+)', t)[1])
assert math.isfinite(average) and average > 0
libs = json.loads((d / 'collection.json').read_text())['compiled_dynamic_libraries']
assert len(libs) == 1 and libs[0]['bytes'] > 0 and len(libs[0]['sha256']) == 64
assert 'Ctoo: functionObjectTemplate.C' in t and 'Creating new library' in t
assert (root / 'phases.log').read_text().strip().endswith('PASS')
env = (root / 'environment.log').read_text()
assert 'EPYC 7713' in env and 'WM_PROJECT_VERSION=2512 WM_PRECISION_OPTION=DP' in env
out = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
           job='25904765.pbs101', state='NATIVE_CPU_TIMING_GATE_PASS',
           walltime_seconds=84, allocated_cpus=8, mpi_ranks=4, ngpus=0,
           estimated_SU_at_reported_rate=8*84/3600, posted_charge_reconciled=False,
           accounting=j['resources_used'], compiled_library=libs[0],
           diagnostic_steps=semantic['steps'], diagnostic_average_seconds_step=average,
           timing_confidence_warning='smaller than the calculated one' in t,
           contest_score=None,
           assessment='Guarded reset fixes observed startup boundary; native official timing code compiles and runs. Historical compilation-stop root cause remains unproven.',
           limitations='Tiny native tutorial, not DrivAer or full-case Cd. No NUMA/bandwidth/network counters collected; account CPU% is coarse. Do not interpret toy Average as optimization performance.')
(r / 'review.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(out, indent=2))
