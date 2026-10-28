"""Offline positive/negative checks for the full-work Iris pair; no cluster access."""
from pathlib import Path
import hashlib,importlib.util,json,re,shutil,statistics,sys,tempfile

E=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(E))

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module

run=load('iris_full150_run',E/'run.py')
native=load('iris_full150_native',E/'native_output.py')
checks=load('iris_full150_case_checks',E/'case_checks.py')

def reject(fn,label):
    try:fn()
    except (AssertionError,ValueError):return
    raise AssertionError(label+' was accepted')

def native_fixture(root):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    timings=[2.0]*148+[4.0]
    lines=['Build OPENFOAM=2512','Arch: "LSB;label=32;scalar=64"',
           'trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).','nProcs: 56',
           'Hosts:','((iris009.hpcadvisorycouncil.com 56))']
    for step in range(1,151):
        lines.append(f'Time = {step}')
        for field,count in (('Ux',15),('Uy',15),('Uz',15),('p',12),('k',8),('omega',8)):
            lines.append(f'Solving for {field}, Initial residual = 1e-3, Final residual = 1e-4, No Iterations {count}')
        if step>=2:lines.append(f'Wall-clock time elapsed during the current time step = {timings[step-2]}')
    lines += [f'Average wall-clock time per time step = {statistics.mean(timings):.15f}','End']
    (root/'simpleFoam.log').write_text('\n'.join(lines)+'\n')
    rows=[];acc=0.0
    for step,value in zip(range(2,151),timings):acc+=value;rows.append(f'{step} {acc} {value}')
    wall=root/'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat';wall.parent.mkdir(parents=True);wall.write_text('# Time accumulatedWCT timeStepWCT\n'+'\n'.join(rows)+'\n')
    cd=root/'postProcessing/forceCoeffsAll/0/coefficient.dat';cd.parent.mkdir(parents=True);cd.write_text('# Time Cd\n'+''.join(f'{step} {0.44+step/100000:.8f}\n' for step in range(1,151)))
    (root/'resource-time.log').write_text('Maximum resident set size (kbytes): 1234\nExit status: 0\n')
    (root/'solver.stderr').write_text('')
    return timings

with tempfile.TemporaryDirectory(prefix='iris-full150-parser-') as td:
    arm=Path(td)/'positive';expected=native_fixture(arm)
    log,timings,cd,counts=native.review_native_output(arm)
    assert len(timings)==149 and timings==expected and len(cd)==150 and cd[-1][0]==150
    assert counts=={'Ux':15,'Uy':15,'Uz':15,'p':12,'k':8,'omega':8}
    assert timings[-1]==4.0 and max(timings)==4.0,'slow terminal interval must remain in the reported distribution'
    row=run.arm_record(arm,'zyx');assert row['steps']==150 and row['intervals']==149 and row['maximum_seconds_per_step']==4.0
    # Missing terminal step, independent wall-file mismatch, iteration drift, and Cd truncation all fail.
    bad=Path(td)/'missing-step';shutil.copytree(arm,bad)
    (bad/'simpleFoam.log').write_text((bad/'simpleFoam.log').read_text().replace('Time = 150\n','Time = 151\n'))
    reject(lambda:native.review_native_output(bad),'missing terminal step')
    bad=Path(td)/'bad-wct';shutil.copytree(arm,bad)
    w=bad/'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat';w.write_text(w.read_text().replace('75 148.0 2.0','75 148.0 2.5'))
    reject(lambda:native.review_native_output(bad),'WCT mismatch')
    bad=Path(td)/'bad-iterations';shutil.copytree(arm,bad)
    q=bad/'simpleFoam.log';q.write_text(q.read_text().replace('No Iterations 15','No Iterations 14',1))
    reject(lambda:native.review_native_output(bad),'iteration-count drift')
    bad=Path(td)/'short-cd';shutil.copytree(arm,bad)
    q=bad/'postProcessing/forceCoeffsAll/0/coefficient.dat';q.write_text('\n'.join(q.read_text().splitlines()[:-1])+'\n')
    reject(lambda:native.review_native_output(bad),'missing force row')

# Named results remain tied to their hierarchy order independent of list position.
selected=run.select_arms_by_order([{'order':'xyz'},{'order':'zyx'}]);assert set(selected)=={'xyz','zyx'}
reject(lambda:run.select_arms_by_order([{'order':'zyx'}]),'missing order')
reject(lambda:run.select_arms_by_order([{'order':'zyx'},{'order':'zyx'}]),'duplicate order')
same={'tools':{'simpleFoam':'sha-a'},'libraries':{'libmpi':'sha-b'}}
assert run.runtime_identity_equal(same,json.loads(json.dumps(same)))
changed={'tools':{'simpleFoam':'sha-c'},'libraries':{'libmpi':'sha-b'}}
assert not run.runtime_identity_equal(same,changed),'runtime drift must block passed comparison'

# Validate exactly the same 41 source pins used by the runtime check, plus only the full-work control.
template=E/'payload-case'
with tempfile.TemporaryDirectory(prefix='iris-full150-source-') as td:
    for order in ('zyx','xyz'):
        src=Path(td)/('order-'+order);shutil.copytree(template,src)
        cdef=src/'system/include/caseDefinition';text=cdef.read_text()
        text,n=re.subn(r'(?m)^nCores .*$', 'nCores              56;',text);assert n==1
        text,n=re.subn(r'(?m)^nHierarchical .*$', 'nHierarchical       (7 4 2);',text);assert n==1;cdef.write_text(text)
        decomp=src/'system/decomposeParDict';text=decomp.read_text()
        text,n=re.subn(r'(?m)^([ \t]+order[ \t]+)xyz;',r'\g<1>'+order+';',text);assert n==1;decomp.write_text(text)
        (src/'Allrun').unlink();(src/'READY').write_text('initialized fixture\n')
        assert checks.source_check(src,order)['passed']
        case=Path(td)/('case-'+order);shutil.copytree(src,case)
        before_start=re.search(r'(?m)^startFrom\s+([^;]+);',(case/'system/controlDict').read_text())[1]
        function_hash=hashlib.sha256((case/'system/forceCoeffsAll').read_bytes()).hexdigest()
        config=run.configure_full_work(case,order)
        assert config['endTime']==150 and config['source_startFrom']==before_start.strip()
        assert (case/'system/fvSolution').read_bytes()==(case/'system/fvSolution.fixedIter').read_bytes()
        assert hashlib.sha256((case/'system/forceCoeffsAll').read_bytes()).hexdigest()==function_hash
        assert re.search(r'(?m)^startFrom\s+'+re.escape(before_start.strip())+r'\s*;',(case/'system/controlDict').read_text())
        bad=Path(td)/('bad-source-'+order);shutil.copytree(src,bad)
        (bad/'constant/transportProperties').write_bytes((bad/'constant/transportProperties').read_bytes()+b'\n// rejected edit\n')
        reject(lambda:checks.source_check(bad,order),'unauthorized physics edit')

# Check the no-deployment runtime boundary: the same 8 scripts plus all 41 pinned case files.
runtime=('run.py','job.sbatch','source-pins.json','native_checks.py','case_checks.py','native_output.py','affinity-probe.py','tree-manifest.py')
files=[E/name for name in runtime]+[p for p in (E/'payload-case').rglob('*') if p.is_file()]
assert len(files)==49 and all(p.is_file() and not p.is_symlink() for p in files)
assert all(p.name!='deploy_submit.py' for p in files)
assert run.ARM_ORDER==('xyz','zyx') and run.SOLVER_CAP=={'xyz':5400,'zyx':4300}
assert run.EXPECTED_FIRST_SOLVER_SECONDS==4700 and run.EXPECTED_SECOND_SOLVER_SECONDS==3700
assert run.FIRST_SOLVER_RESERVE_SECONDS==9600 and run.SECOND_ARM_RESERVE_SECONDS==4600
header=(E/'job.sbatch').read_text();assert '#SBATCH -t 03:00:00' in header and '#SBATCH --exclusive' in header and '#SBATCH -n 56' in header and '#SBATCH --gpus=0' in header
print(json.dumps({'passed':True,'checks':['150 native steps/149 timing rows/150 Cd rows','retained tail sample','bad step/WCT/iterations/Cd rejected','order-keyed matched result association','41 source pins for both orders','endTime-only run-control edit and fixedIter/function-object preservation','physics-source edit rejection','49-file runtime kit','3h exclusive 56-rank zero-GPU Slurm header'],'scope':'Offline only; no remote runtime, deployment, submission, or score claim.'},indent=2))
