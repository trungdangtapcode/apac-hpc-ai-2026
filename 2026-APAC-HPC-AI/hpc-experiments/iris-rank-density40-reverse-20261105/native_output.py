from pathlib import Path
import json,math,re,statistics
def review_native_output(arm, expected_ranks=56):
    log = (arm / 'simpleFoam.log').read_text(errors='replace')
    resources = (arm / 'resource-time.log').read_text(errors='replace')
    assert 'OPENFOAM=2512' in log and 'scalar=64' in log
    assert re.search(r'^End\s*$', log, re.M)
    # `trapFpe: Floating point exception trapping enabled` is a normal startup banner.
    assert not re.search(r'FOAM FATAL|FOAM ERROR|MPI_ABORT|died from signal|\bSIGFPE\b|floating point exception occurred|core dumped', log + '\n' + resources, re.I)
    assert re.search(r'^nProcs\s*:\s*'+str(expected_ranks)+r'\s*$', log, re.M)
    assert re.search(r'\(iris\S+\s+'+str(expected_ranks)+r'\)', log), 'native log host/rank line missing'
    steps = [int(x) for x in re.findall(r'^Time = (\d+)\s*$', log, re.M)]
    assert steps == list(range(1, 41)), 'expected exactly steps 1..40'
    timing = [float(x) for x in re.findall(r'Wall-clock time elapsed during the current time step = ([\deE.+-]+)', log)]
    assert len(timing) == 39 and all(math.isfinite(x) and x > 0 for x in timing), 'expected 39 finite positive timings for steps 2..40'
    average_match = re.search(r'Average wall-clock time per time step\s*=\s*([\deE.+-]+)', log)
    assert average_match and abs(statistics.mean(timing) - float(average_match[1])) < 1e-9
    wall = arm / 'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat'
    rows = [list(map(float, line.split())) for line in wall.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')]
    assert [int(r[0]) for r in rows] == list(range(2, 41)), 'wall-clock function object must cover steps 2..40'
    assert all(math.isfinite(v) for row in rows for v in row)
    assert all(abs(a - b[2]) < 1e-8 for a, b in zip(timing, rows))
    counts = {}
    for field, n in re.findall(r'Solving for (\w+),.*?No Iterations (\d+)', log):
        counts.setdefault(field, []).append(int(n))
    expected = {'Ux': 15, 'Uy': 15, 'Uz': 15, 'p': 12, 'k': 8, 'omega': 8}
    assert set(counts) == set(expected)
    assert all(v == [expected[f]] * 40 for f, v in counts.items()), 'native fixed-iteration counters drifted'
    cd = arm / 'postProcessing/forceCoeffsAll/0/coefficient.dat'
    cdrows = [list(map(float, line.split())) for line in cd.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')]
    assert len(cdrows) == 40 and [int(r[0]) for r in cdrows] == steps
    assert all(math.isfinite(v) for row in cdrows for v in row)
    assert 'Exit status: 0' in resources and 'Maximum resident set size (kbytes):' in resources
    return log, timing, cdrows, expected
