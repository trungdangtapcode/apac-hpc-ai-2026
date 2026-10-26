from pathlib import Path
import pathlib,subprocess,sys,tempfile,importlib.util,shutil,json,ast,re
ROOT=Path(__file__).resolve().parent
def fixture_native_review():
    spec = importlib.util.spec_from_file_location('pair_review', ROOT / 'native_output.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='iris-native-fixture-') as td:
        arm = pathlib.Path(td)
        lines = ['Build OPENFOAM=2512', 'Arch: "LSB;label=32;scalar=64"', 'trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).',
                 'nProcs: 56', 'Hosts:', '((iris009.hpcadvisorycouncil.com 56))']
        for step in range(1, 31):
            lines.append(f'Time = {step}')
            for field, count in (('Ux', 15), ('Uy', 15), ('Uz', 15), ('p', 12), ('k', 8), ('omega', 8)):
                lines.append(f'Solving for {field}, Initial residual = 1e-3, Final residual = 1e-4, No Iterations {count}')
            if step >= 2:
                lines.append('Wall-clock time elapsed during the current time step = 2')
        lines += ['Average wall-clock time per time step = 2', 'End']
        (arm / 'simpleFoam.log').write_text('\n'.join(lines) + '\n')
        wall = arm / 'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat'
        wall.parent.mkdir(parents=True)
        wall.write_text('# Time accumulatedWCT timeStepWCT\n' + ''.join(f'{s} {2*(s-1)} 2\n' for s in range(2, 31)))
        cd = arm / 'postProcessing/forceCoeffsAll/0/coefficient.dat'
        cd.parent.mkdir(parents=True)
        cd.write_text('# Time Cd\n' + ''.join(f'{s} 0.44\n' for s in range(1, 31)))
        (arm / 'resource-time.log').write_text('Maximum resident set size (kbytes): 1234\nExit status: 0\n')
        result = module.review_native_output(arm)
        assert len(result[1]) == 29 and len(result[2]) == 30
        (wall).write_text('# Time accumulatedWCT timeStepWCT\n' + ''.join(f'{s} {2*(s-1)} 2\n' for s in range(2, 30)))
        try:
            module.review_native_output(arm)
        except AssertionError:
            pass
        else:
            raise AssertionError('native reviewer accepted missing independent WCT row')
fixture_native_review()
# Use the exact clone command from run.py to reject stale source snapshot reuse.
constants=[n.value for n in ast.walk(ast.parse((ROOT/'run.py').read_text())) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
clone=next(s for s in constants if s.startswith('import shutil,sys;shutil.copytree'))
with tempfile.TemporaryDirectory() as tmp:
 src=Path(tmp)/'source';dst=Path(tmp)/'copy';src.mkdir();dst.mkdir()
 for top in ['system','constant']:(src/top).mkdir()
 for i in range(56):
  for name in ['0','constant']:(src/('processor'+str(i))/name).mkdir(parents=True)
  for f in ['U','p','k','omega','nut','nuTilda']:(src/('processor'+str(i))/'0'/f).write_text(f)
 (src/'source-before.json').write_text('{"stale_raw_cut_snapshot": true}')
 command=[sys.executable,str(ROOT/'tree-manifest.py'),str(src),str(dst)]
 subprocess.run(command+[str(dst/'source-before.json'),'--source-only'],check=True,capture_output=True)
 before=(dst/'source-before.json').read_bytes()
 subprocess.run([sys.executable,'-c',clone,str(src),str(dst)],check=True)
 assert (dst/'source-before.json').read_bytes()==before
 subprocess.run(command+[str(dst/'copy-check.json'),'--compare-copy'],check=True,capture_output=True)
for path in ROOT.glob('*.py'):ast.parse(path.read_text(),feature_version=(3,9))
subprocess.run(['bash','-n',str(ROOT/'job.sbatch')],check=True)
print('PASS: 30-step native output/WCT/Cd/fixed-iteration fixtures; exact initialized-source clone preserves fresh snapshot and independent files; syntax checks.')
