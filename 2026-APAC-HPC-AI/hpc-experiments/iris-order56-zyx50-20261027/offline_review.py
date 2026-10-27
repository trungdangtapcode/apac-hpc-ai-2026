"""Offline fixtures for 50-step native evidence, ordering, seals, and gates."""
from pathlib import Path
import importlib.util, tempfile, sys, hashlib, json
E=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
run=load('zyx50_run',E/'run.py'); native=load('zyx50_native',E/'native_output.py'); dep=load('zyx50_deploy',E/'deploy_submit.py')

def fixture(root):
    arm=Path(root);lines=['Build OPENFOAM=2512','Arch: "LSB;label=32;scalar=64"','trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).','nProcs: 56','Hosts:','((iris009.hpcadvisorycouncil.com 56))']
    for step in range(1,51):
        lines.append(f'Time = {step}')
        for field,count in (('Ux',15),('Uy',15),('Uz',15),('p',12),('k',8),('omega',8)):
            lines.append(f'Solving for {field}, Initial residual = 1e-3, Final residual = 1e-4, No Iterations {count}')
        if step>=2:lines.append('Wall-clock time elapsed during the current time step = 2')
    lines+=['Average wall-clock time per time step = 2','End'];(arm/'simpleFoam.log').write_text('\n'.join(lines)+'\n')
    wall=arm/'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat';wall.parent.mkdir(parents=True);wall.write_text('# Time accumulatedWCT timeStepWCT\n'+''.join(f'{s} {2*(s-1)} 2\n' for s in range(2,51)))
    cd=arm/'postProcessing/forceCoeffsAll/0/coefficient.dat';cd.parent.mkdir(parents=True);cd.write_text('# Time Cd\n'+''.join(f'{s} 0.44\n' for s in range(1,51)))
    (arm/'resource-time.log').write_text('Maximum resident set size (kbytes): 1234\nExit status: 0\n')
    return arm

def rejected(fn,label):
    try:fn()
    except (AssertionError,ValueError):return
    raise AssertionError(label+' was accepted')
with tempfile.TemporaryDirectory(prefix='iris-zyx50-native-') as td:
    arm=Path(td)/'positive';arm.mkdir();arm=fixture(arm)
    log,timing,cd,counts=native.review_native_output(arm)
    assert len(timing)==49 and len(cd)==50 and counts=={'Ux':15,'Uy':15,'Uz':15,'p':12,'k':8,'omega':8}
    # Incomplete solver history: missing final native step.
    bad=Path(td)/'missing-step';import shutil;shutil.copytree(arm,bad)
    (bad/'simpleFoam.log').write_text((bad/'simpleFoam.log').read_text().replace('Time = 50\n','Time = 500\n'))
    rejected(lambda:native.review_native_output(bad),'missing step 50')
    # A mismatch between native log and independent wall-clock function data.
    bad=Path(td)/'mismatch-wct';shutil.copytree(arm,bad)
    w=bad/'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat';w.write_text(w.read_text().replace('25 48 2','25 48 3'))
    rejected(lambda:native.review_native_output(bad),'mismatched WCT')
    # Fixed iteration count drift and incomplete Cd output are independently rejected.
    bad=Path(td)/'mismatch-iterations';shutil.copytree(arm,bad)
    (bad/'simpleFoam.log').write_text((bad/'simpleFoam.log').read_text().replace('No Iterations 15','No Iterations 14',1))
    rejected(lambda:native.review_native_output(bad),'fixed iteration mismatch')
    bad=Path(td)/'missing-cd';shutil.copytree(arm,bad)
    c=bad/'postProcessing/forceCoeffsAll/0/coefficient.dat';c.write_text('\n'.join(c.read_text().splitlines()[:-1])+'\n')
    rejected(lambda:native.review_native_output(bad),'missing final Cd row')
# The result is associated with the named sole arm and never by positional comparison.
row={'order':'zyx','steps':50,'intervals':49};result=run.single_arm_result(row)
assert result['arms_by_order']=={'zyx':row} and result['comparison'] is False
for bad in [{'order':'xyz','steps':50,'intervals':49},{'order':'zyx','steps':49,'intervals':48}]:
    rejected(lambda bad=bad:run.single_arm_result(bad),'invalid single-arm result')
# Positive and negative payload sealing checks on isolated fixtures; no local seal is written.
with tempfile.TemporaryDirectory(prefix='iris-zyx50-seal-') as td:
    root=Path(td);files=[]
    for name,data in [('run.py',b'runner'),('payload-case/a',b'case')]:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);files.append(p)
    manifest=dep.compute_files(files);assert len(manifest)==2
    assert all(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest for name,digest in manifest.items())
    (root/'payload-case/a').write_bytes(b'tampered');assert dep.compute_files(files)!=manifest
    files.pop();assert set(dep.compute_files(files))!=set(manifest)
assert len(dep.expected_paths())==49
# Both the local budget and remote Iris queue gates fail closed on own active jobs.
assert not dep.require_no_active_local_jobs({'jobs':[{'state':'COMPLETED_0_0'}]})
rejected(lambda:dep.require_no_active_local_jobs({'jobs':[{'state':'RESERVED_SUBMISSION_UNCERTAIN'}]}),'local active job')
assert dep.require_no_own_jobs('123|unrelated-name|RUNNING\n') is None
rejected(lambda:dep.require_no_own_jobs('124|tu-old|PENDING\n'),'remote tu job')
assert (E/'PREPARATION.json').is_file() and not (E/'deployment.json').exists()
assert run.ORDER=='zyx' and run.STEPS==50 and run.INTERVALS==49 and run.SOLVER_CAP==1250 and run.PRE_SOLVER_REMAINING==1360
print('PASS: exact 1..50 native steps, 49 WCT rows, 50 Cd/fixed-count rows; incomplete/mismatch negatives; single-arm name-keying; seal mutation/missing-file tests; local/remote own-job gates; 49-file boundary.')
