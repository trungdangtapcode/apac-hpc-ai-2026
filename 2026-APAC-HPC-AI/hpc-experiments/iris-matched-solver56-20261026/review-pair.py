#!/usr/bin/env python3
"""Offline review from retained source/copy manifests and native run logs."""
import hashlib, json, math, pathlib, re, statistics, sys

FIELDS = ('U', 'k', 'nuTilda', 'nut', 'omega', 'p')
PINNED_SOURCE_PATHS = ('0.orig/U', '0.orig/k', '0.orig/nuTilda', '0.orig/nut', '0.orig/omega', '0.orig/p')

def load_manifest(arm):
    before = json.loads((arm / 'source-before.json').read_text())
    copied = json.loads((arm / 'source-after-copy.json').read_text())
    after = json.loads((arm / 'source-after-run.json').read_text())
    assert before == copied == after, 'source/copy input manifest changed'
    assert len(before['files']) > 336
    assert len([p for p in before['files'] if re.fullmatch(r'processor\d+/0/(U|k|nuTilda|nut|omega|p)', p)]) == 336
    return before

def review_native_output(arm):
    log = (arm / 'simpleFoam.log').read_text(errors='replace')
    resources = (arm / 'resource-time.log').read_text(errors='replace')
    assert 'OPENFOAM=2512' in log and 'scalar=64' in log
    assert re.search(r'^End\s*$', log, re.M)
    # `trapFpe: Floating point exception trapping enabled` is a normal startup banner.
    assert not re.search(r'FOAM FATAL|FOAM ERROR|MPI_ABORT|died from signal|\bSIGFPE\b|floating point exception occurred|core dumped', log + '\n' + resources, re.I)
    assert re.search(r'^nProcs\s*:\s*56\s*$', log, re.M)
    assert re.search(r'\(iris\S+\s+56\)', log), 'native log host/rank line missing'
    steps = [int(x) for x in re.findall(r'^Time = (\d+)\s*$', log, re.M)]
    assert steps == list(range(1, 151)), 'expected exactly steps 1..150'
    timing = [float(x) for x in re.findall(r'Wall-clock time elapsed during the current time step = ([\deE.+-]+)', log)]
    assert len(timing) == 149 and all(math.isfinite(x) and x > 0 for x in timing), 'expected 149 finite positive timings'
    average_match = re.search(r'Average wall-clock time per time step\s*=\s*([\deE.+-]+)', log)
    assert average_match and abs(statistics.mean(timing) - float(average_match[1])) < 1e-9
    wall = arm / 'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat'
    rows = [list(map(float, line.split())) for line in wall.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')]
    assert [int(r[0]) for r in rows] == list(range(2, 151)), 'wall-clock function object must cover steps 2..150'
    assert all(math.isfinite(v) for row in rows for v in row)
    assert all(abs(a - b[2]) < 1e-8 for a, b in zip(timing, rows))
    counts = {}
    for field, n in re.findall(r'Solving for (\w+),.*?No Iterations (\d+)', log):
        counts.setdefault(field, []).append(int(n))
    expected = {'Ux': 15, 'Uy': 15, 'Uz': 15, 'p': 12, 'k': 8, 'omega': 8}
    assert set(counts) == set(expected)
    assert all(v == [expected[f]] * 150 for f, v in counts.items()), 'native fixed-iteration counters drifted'
    cd = arm / 'postProcessing/forceCoeffsAll/0/coefficient.dat'
    cdrows = [list(map(float, line.split())) for line in cd.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')]
    assert len(cdrows) == 150 and [int(r[0]) for r in cdrows] == steps
    assert all(math.isfinite(v) for row in cdrows for v in row)
    assert 'Exit status: 0' in resources and 'Maximum resident set size (kbytes):' in resources
    return log, timing, cdrows, expected

def review_arm(pair, name, method):
    arm = pair / name
    assert (arm / 'return-code.txt').read_text().strip() == '0'
    manifest = load_manifest(arm)
    copy_proof = (arm / 'copy-validation.log').read_text()
    assert 'PASS:' in copy_proof and 'no shared inodes' in copy_proof
    affinity = json.loads((arm / 'rank-affinity/validated-map.json').read_text())
    assert affinity['passed'] and affinity['ranks'] == 56 and len(affinity['affinity_by_rank']) == 56
    status = (pair / 'source-validation.txt').read_text()
    assert f'method={method} ready_n=56 pin_review=PASS' in status
    case_key = 'system/include/caseDefinition'
    assert manifest['files'].get(case_key)
    assert (arm / 'solver-control-hashes.txt').is_file()
    controls = {}
    for line in (arm / 'solver-control-hashes.txt').read_text().splitlines():
        digest, path = line.split(None, 1)
        controls[path.strip()] = digest
    assert controls['system/include/caseDefinition'] == manifest['files'][case_key]
    # controlDict and fvSolution are intentionally arm-local, and their exact source variants are pinned.
    assert controls['system/fvSolution'] == manifest['files']['system/fvSolution.fixedIter']
    active_control = (arm / 'system/controlDict').read_text()
    pinned_control = (arm / 'system/controlDict.noWrite').read_text()
    assert controls['system/controlDict'] == hashlib.sha256(active_control.encode()).hexdigest()
    def control_signature(text):
        text = re.sub(r'(?m)^\s*(startFrom|endTime)\s+[^;]+;[^\n]*\n?', '', text)
        return ' '.join(text.split())
    assert control_signature(active_control) == control_signature(pinned_control), 'controlDict has changes beyond startFrom/endTime'
    definition = (arm / 'system/include/caseDefinition').read_text()
    assert re.search(rf'^nCores\s+56;', definition, re.M)
    assert re.search(rf'^decompositionMethod\s+{method};', definition, re.M)
    assert re.search(r'^nHierarchical\s+\(7 4 2\);', definition, re.M)
    assert re.search(r'^startFrom\s+startTime;', (arm / 'system/controlDict').read_text(), re.M)
    assert re.search(r'^endTime\s+150;', (arm / 'system/controlDict').read_text(), re.M)

    log, timing, cdrows, expected_counts = review_native_output(arm)
    if 'bounding omega' in log:
        bounding = len(re.findall('bounding omega', log, re.I))
    else:
        bounding = 0
    timings_sorted = sorted(timing)
    p95 = statistics.quantiles(timing, n=100, method='inclusive')[94]
    return {'arm': name, 'method': method, 'steps': 150, 'timings': 149,
            'mean_seconds_per_step': statistics.mean(timing), 'median_seconds_per_step': statistics.median(timing),
            'p95_seconds_per_step': p95, 'minimum_seconds_per_step': timings_sorted[0],
            'maximum_seconds_per_step': timings_sorted[-1], 'final_Cd': cdrows[-1][1],
            'bounding_omega_messages': bounding, 'iteration_counts_each_step': expected_counts,
            'input_manifest_sha256': hashlib.sha256((arm / 'source-before.json').read_bytes()).hexdigest(),
            'interpretation_limit': 'single same-allocation H-then-S pair; order effect and temporal drift remain; no general solver-gain claim'}

def review(pair):
    assert (pair / 'START_EPOCH').exists() or (pair / 'start.utc').exists() or (pair / 'source-validation.txt').is_file()
    h = review_arm(pair, 'H', 'hierarchical')
    s = review_arm(pair, 'S', 'scotch')
    hm = json.loads((pair / 'H/source-before.json').read_text())
    sm = json.loads((pair / 'S/source-before.json').read_text())
    for path in set(hm['files']) & set(sm['files']):
        if (path.startswith('system/') and path != 'system/include/caseDefinition') or path.startswith('constant/') or path in ('transportProperties', 'turbulenceProperties'):
            assert hm['files'][path] == sm['files'][path], f'numerical input differs across arms: {path}'
    # The one intended numerical case difference is the decomposition algorithm;
    # source comments may also differ, so compare uncommented tokens.
    def case_tokens(path):
        text = (pair / path).read_text()
        text = re.sub(r'//[^\n]*', '', text)
        text = re.sub(r'(?m)^(\s*decompositionMethod\s+)\w+', r'\1METHOD', text)
        return ' '.join(text.split())
    assert case_tokens('H/system/include/caseDefinition') == case_tokens('S/system/include/caseDefinition'), 'non-decomposition caseDefinition drift'
    return {'passed': True, 'order': ['H', 'S'], 'arms': [h, s], 'claim': None,
            'limitations': ['one allocation only', 'H always precedes S, so order effects cannot be separated', 'no solver-gain claim']}

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: review-pair.py RUNROOT')
    run = pathlib.Path(sys.argv[1])
    result = review(run)
    (run / 'review.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
