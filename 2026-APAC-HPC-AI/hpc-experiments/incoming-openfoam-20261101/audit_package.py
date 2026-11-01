"""Replay submitted text evidence without executing package shell scripts."""
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ZIP = HERE / 'original.zip'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def code_block(text, name):
    match = re.search(r'\b' + name + r'\s*#\{(.*?)#\}', text, re.S)
    if not match:
        return None
    code = re.sub(r'/\*.*?\*/|//[^\n]*', '', match[1], flags=re.S)
    return re.sub(r'\s+', '', code)


def audit():
    results = []
    source = ROOT / 'nscc-transfer-campaign-20261027/native-wave/payload/case'
    with zipfile.ZipFile(ZIP) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)), 'Duplicate ZIP members'
        assert sum(i.file_size for i in archive.infolist()) < 20_000_000
        inventory = []
        for info in archive.infolist():
            path = Path(info.filename)
            assert not path.is_absolute() and '..' not in path.parts
            assert (info.external_attr >> 16) & 0o170000 != 0o120000, 'Symlink rejected'
            data = archive.read(info)
            inventory.append({'path': info.filename, 'bytes': len(data), 'sha256': digest(data)})
        def text(path):
            return archive.read('OPENFOAM_Task/' + path).decode('utf-8')

        for nodes, steps in [(1, 40), (2, 80), (4, 150)]:
            log = text(f'results/{nodes}node/simpleFoam.log')
            actual_steps = list(map(int, re.findall(r'^Time = (\d+)\s*$', log, re.M)))
            assert actual_steps == list(range(1, steps + 1))
            samples = list(map(float, re.findall(
                r'^Wall-clock time elapsed during the current time step = ([0-9.eE+-]+) s$', log, re.M)))
            assert len(samples) == steps - 1 and all(math.isfinite(x) and x > 0 for x in samples)
            reported = float(re.search(r'Average wall-clock time per time step = (\S+)', log)[1])
            assert math.isclose(statistics.mean(samples), reported, rel_tol=1e-12)
            assert re.search(r'^End\s*$', log, re.M)
            assert not re.search(r'FOAM FATAL|MPI_ABORT|died from signal', log)
            iterations = collections.defaultdict(list)
            for field, count in re.findall(r'Solving for (\w+),[^\n]*No Iterations (\d+)', log):
                iterations[field].append(int(count))
            for field, expected in [('Ux', 15), ('Uy', 15), ('Uz', 15), ('p', 12), ('k', 8), ('omega', 8)]:
                assert iterations[field] == [expected] * steps, (nodes, field)
            coeff = [list(map(float, line.split())) for line in text(f'results/{nodes}node/coefficient.dat').splitlines()
                     if line.strip() and not line.startswith('#')]
            assert [r[0] for r in coeff] == list(range(1, steps + 1))
            assert all(math.isfinite(v) for row in coeff for v in row)
            cells = sum(map(int, re.findall(r'^\s+Number of cells = (\d+)\s*$', text(f'results/{nodes}node/decomposePar.log'), re.M)))
            assert cells == 65_334_765, (nodes, cells)
            ordered = sorted(samples)
            results.append({'nodes': nodes, 'mpi_ranks': int(re.search(r'^nProcs\s*:\s*(\d+)', log, re.M)[1]),
                            'steps': steps, 'measured_intervals': len(samples),
                            'mean_seconds_per_step': statistics.mean(samples),
                            'reported_mean_seconds_per_step': reported,
                            'population_standard_deviation_seconds': statistics.pstdev(samples),
                            'median_seconds_per_step': statistics.median(samples),
                            'p95_nearest_rank_seconds_per_step': ordered[math.ceil(.95 * len(samples)) - 1],
                            'minimum_seconds_per_step': min(samples), 'maximum_seconds_per_step': max(samples),
                            'final_Cd_dimensionless': coeff[-1][1], 'decomposed_cells': cells,
                            'all_fixed_iteration_counts_pass': True,
                            'host_list': re.findall(r'\((gadi-cpu[^\s()]+) (\d+)\)', log),
                            'scope': 'Replay of supplied logs, not a newly executed solver measurement.'})
        supplied_timer = text('dicts/controlDict')
        reference_timer = (source / 'system/FOwallClockTimeStatistics').read_text()
        timer = {name: code_block(supplied_timer, name) == code_block(reference_timer, name)
                 for name in ['codeInclude', 'codeData', 'codeRead', 'codeExecute', 'codeWrite', 'codeEnd']}
        # Both callbacks retain the same elapsed-time call and timer reset.
        # Statistical bookkeeping differs and is reported, never normalized away.
        boundary_calls = {name: {'supplied': supplied_timer.count(name), 'pinned_source': reference_timer.count(name)}
                          for name in ['wallClock_.elapsedTime()', 'wallClock_.update()']}
    references = list(csv.DictReader((ROOT / 'reference-analysis-20261021/reference-results.csv').open()))
    refs = [r for r in references if r['platform'] == 'Gadi normalsr' and r['reference'] in ['scotch-4node', 'reuse-scotch-4node']]
    mean = results[-1]['mean_seconds_per_step']
    comparisons = [{'reference': r['reference'], 'reference_seconds_per_step': float(r['average_s_step']),
                    'observed_reduction_percent': 100 * (1 - mean / float(r['average_s_step'])),
                    'scope': 'Separate jobs/builds/times. No causal optimization or matched repeat claim.'} for r in refs]
    return {'passed_log_replay': True, 'solver_executed_by_this_audit': False,
            'job_submitted_by_this_audit': False, 'zip_sha256': digest(ZIP.read_bytes()),
            'members': inventory, 'runs': results, 'timer_code_matches_our_pinned_source': timer,
            'timer_boundary_calls': boundary_calls,
            'timer_provenance_limit': 'Statistical code differs from our retained official-case snapshot. Current upstream origin not established; no assertion of misconduct or automatic compliance.',
            'same_platform_reference_comparisons': comparisons,
            'actual_fvSolution_in_zip': any(Path(n).name.startswith('fvSolution') for n in names)}


if __name__ == '__main__':
    result = audit()
    (HERE / 'audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'members'}, indent=2))
