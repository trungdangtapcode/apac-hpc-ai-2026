#!/usr/bin/env python3
"""Positive and negative offline fixtures for source pins and copy isolation."""
import json, os, pathlib, shutil, subprocess, sys, tempfile
import importlib.util
ROOT = pathlib.Path(__file__).resolve().parent
CASE = ROOT / 'payload-case'
PINS = ROOT / 'source-pins.json'
OBS = ROOT / 'source-observations.json'
pins = json.loads(PINS.read_text())['files']

def invoke_source(method, mutate=None):
    arm = 'H' if method == 'hierarchical' else 'S'
    with tempfile.TemporaryDirectory(prefix='iris-pair-fixture-') as td:
        source = pathlib.Path(td) / 'source'
        shutil.copytree(CASE, source, ignore=shutil.ignore_patterns('*.expected', 'caseDefinition.hierarchical56', 'Allrun'))
        expected_case = CASE / f'system/include/caseDefinition.{arm}.expected'
        shutil.copy2(expected_case, source / 'system/include/caseDefinition')
        source.joinpath('READY').write_text(json.loads(OBS.read_text())[arm]['READY'])
        if mutate:
            mutate(source)
        return subprocess.run([sys.executable, str(ROOT / 'lib/verify-inputs.py'), '--source', str(source), '--method', method,
                               '--pins', str(PINS), '--case', str(CASE), '--observations', str(OBS)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).returncode

def fixture_copy():
    with tempfile.TemporaryDirectory(prefix='iris-copy-fixture-') as td:
        src, dst = pathlib.Path(td) / 'src', pathlib.Path(td) / 'dst'
        (src / 'system').mkdir(parents=True)
        (src / 'constant').mkdir()
        (src / 'system/fvSchemes').write_text('pinned\n')
        (src / 'constant/transportProperties').write_text('pinned\n')
        for i in range(56):
            (src / f'processor{i}/0').mkdir(parents=True)
            (src / f'processor{i}/constant').mkdir()
            for field in ('U', 'k', 'nuTilda', 'nut', 'omega', 'p'):
                (src / f'processor{i}/0/{field}').write_text(f'{i}:{field}\n')
        dst.mkdir()
        out = dst / 'source-before.json'
        manifest = [sys.executable, str(ROOT / 'lib/tree-manifest.py'), str(src), str(dst), str(out)]
        assert subprocess.run(manifest + ['--source-only'], capture_output=True).returncode == 0
        assert subprocess.run([sys.executable, str(ROOT / 'lib/copy-case.py'), str(src), str(dst)], capture_output=True).returncode == 0
        copied = [sys.executable, str(ROOT / 'lib/tree-manifest.py'), str(src), str(dst), str(dst / 'source-after-copy.json'), '--compare-copy']
        assert subprocess.run(copied, capture_output=True).returncode == 0
        # The post-run check compares the source with its initial snapshot; arm-local controls may differ.
        (dst / 'system/fvSchemes').write_text('arm-local control change\n')
        after = [sys.executable, str(ROOT / 'lib/tree-manifest.py'), str(src), str(dst), str(dst / 'source-after-run.json'), '--source-only', '--compare-source-snapshot']
        assert subprocess.run(after, capture_output=True).returncode == 0
        (dst / 'system/fvSchemes').write_text('pinned\n')
        (dst / 'processor0/0/U').unlink()
        os.link(src / 'processor0/0/U', dst / 'processor0/0/U')
        assert subprocess.run(copied, capture_output=True).returncode != 0
        (dst / 'processor0/0/U').unlink()
        (dst / 'processor0/0/U').write_text('field drift\n')
        assert subprocess.run(copied, capture_output=True).returncode != 0

def fixture_native_review():
    spec = importlib.util.spec_from_file_location('pair_review', ROOT / 'review-pair.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='iris-native-fixture-') as td:
        arm = pathlib.Path(td)
        lines = ['Build OPENFOAM=2512', 'Arch: "LSB;label=32;scalar=64"', 'trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).',
                 'nProcs: 56', 'Hosts:', '((iris009.hpcadvisorycouncil.com 56))']
        for step in range(1, 151):
            lines.append(f'Time = {step}')
            for field, count in (('Ux', 15), ('Uy', 15), ('Uz', 15), ('p', 12), ('k', 8), ('omega', 8)):
                lines.append(f'Solving for {field}, Initial residual = 1e-3, Final residual = 1e-4, No Iterations {count}')
            if step >= 2:
                lines.append('Wall-clock time elapsed during the current time step = 2')
        lines += ['Average wall-clock time per time step = 2', 'End']
        (arm / 'simpleFoam.log').write_text('\n'.join(lines) + '\n')
        wall = arm / 'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat'
        wall.parent.mkdir(parents=True)
        wall.write_text('# Time accumulatedWCT timeStepWCT\n' + ''.join(f'{s} {2*(s-1)} 2\n' for s in range(2, 151)))
        cd = arm / 'postProcessing/forceCoeffsAll/0/coefficient.dat'
        cd.parent.mkdir(parents=True)
        cd.write_text('# Time Cd\n' + ''.join(f'{s} 0.44\n' for s in range(1, 151)))
        (arm / 'resource-time.log').write_text('Maximum resident set size (kbytes): 1234\nExit status: 0\n')
        result = module.review_native_output(arm)
        assert len(result[1]) == 149 and len(result[2]) == 150
        (wall).write_text('# Time accumulatedWCT timeStepWCT\n' + ''.join(f'{s} {2*(s-1)} 2\n' for s in range(2, 150)))
        try:
            module.review_native_output(arm)
        except AssertionError:
            pass
        else:
            raise AssertionError('native reviewer accepted missing independent WCT row')

assert invoke_source('hierarchical') == 0, 'valid H source was rejected'
assert invoke_source('scotch') == 0, 'valid S source was rejected'
assert invoke_source('scotch', lambda s: (s / 'system/fvSchemes').write_text('numerical drift\n')) != 0
assert invoke_source('hierarchical', lambda s: (s / '0.orig/U').unlink()) != 0
assert invoke_source('scotch', lambda s: (s / 'Allrun').write_text('unexpected\n')) != 0
assert invoke_source('scotch', lambda s: (s / 'system/include/caseDefinition').write_text((s / 'system/include/caseDefinition').read_text().replace('38.889', '38.890', 1))) != 0
fixture_copy()
fixture_native_review()
print('PASS: H/S positive pins; source-drift negatives; bounded baseline/copy/post-run sequence; 56-rank copy hash/inode checks; native 150-step timing/WCT/Cd/fixed-iteration review and negative missing-row fixture')
