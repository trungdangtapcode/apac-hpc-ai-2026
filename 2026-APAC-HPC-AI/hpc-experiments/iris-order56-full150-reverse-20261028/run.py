"""Matched full-work Iris hierarchy-order measurement, xyz then zyx."""
from pathlib import Path
import datetime,hashlib,json,math,os,re,shutil,statistics,subprocess,time,socket
from case_checks import source_check
from native_checks import field_snapshot
from native_output import review_native_output

KIT=Path(__file__).resolve().parent
WORK=KIT.parent
SOURCE=Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-order-init-20261026T133526Z/initialized')
ARM_ORDER=('xyz','zyx')
SOLVER_CAP={'xyz':5400,'zyx':4300}
INTERNAL_DEADLINE_SECONDS=10500
OUTER_TIMEOUT_SECONDS=10770
SECOND_ARM_PREP_SECONDS=600
EXPECTED_FIRST_SOLVER_SECONDS=4700
EXPECTED_SECOND_SOLVER_SECONDS=3700
SECOND_ARM_RESERVE_SECONDS=SECOND_ARM_PREP_SECONDS+EXPECTED_SECOND_SOLVER_SECONDS+300
FIRST_SOLVER_REVIEW_RESERVE_SECONDS=300
FIRST_SOLVER_RESERVE_SECONDS=EXPECTED_FIRST_SOLVER_SECONDS+SECOND_ARM_RESERVE_SECONDS+FIRST_SOLVER_REVIEW_RESERVE_SECONDS
SECOND_SOLVER_REVIEW_RESERVE_SECONDS=300
DEADLINE=0.0
RUN=None

def save(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')

def remaining():
    return int(DEADLINE-time.monotonic())

def phase(label,state,extra=None):
    row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':label,'state':state}
    if extra: row.update(extra)
    with (RUN/'phases.jsonl').open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n')

def bounded(label,args,cwd,cap):
    left=remaining()-60
    assert left>0,('shared internal deadline before '+label,left)
    limit=min(cap,left)
    started=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    phase(label,'start',{'cap_seconds':limit})
    with (RUN/(label+'.log')).open('w') as f:
        try:
            p=subprocess.run(['timeout','--signal=TERM','--kill-after=10s',str(limit)+'s',*map(str,args)],cwd=str(cwd),stdout=f,stderr=subprocess.STDOUT,timeout=limit+20)
            rc=p.returncode
        except subprocess.TimeoutExpired:
            rc=124
    result={'returncode':rc,'cap_seconds':limit,'elapsed_seconds':time.monotonic()-started,'utc_start':utc,'command':list(map(str,args))}
    save(RUN/(label+'.status.json'),result);phase(label,'exit',{'returncode':rc,'elapsed_seconds':result['elapsed_seconds']})
    assert rc==0,(label,rc)
    return result

def node_snapshot(label,dest):
    started=time.monotonic_ns()
    snap={'label':label,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'time_ns':time.time_ns(),
          'scope':'Whole-node procfs counters; not per-process hardware bandwidth or attribution.'}
    for name in ('meminfo','vmstat','pressure/memory'):
        p=Path('/proc')/name
        try:snap[name]=p.read_text()
        except Exception as exc:snap[name+'_error']={'type':type(exc).__name__,'message':str(exc)}
    snap['collection_elapsed_ms']=(time.monotonic_ns()-started)/1e6
    save(Path(dest)/(label+'-node-snapshot.json'),snap)

def runtime_snapshot(label):
    tools={}
    for name in ('simpleFoam','mpirun'):
        found=shutil.which(name)
        assert found,(name,'not present on PATH')
        real=Path(found).resolve();tools[name]={'path':found,'resolved_path':str(real),'sha256':hashlib.sha256(real.read_bytes()).hexdigest()}
    ldd=subprocess.run(['ldd',tools['simpleFoam']['resolved_path']],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True)
    libraries={}
    for line in ldd.stdout.splitlines():
        m=re.search(r'=>\s+(/\S+)',line)
        if not m: m=re.match(r'\s*(/\S+)\s+\(',line)
        if m:
            path=Path(m.group(1)).resolve()
            if path.is_file():libraries[str(path)]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
    assert libraries,'ldd produced no resolved library identities'
    assert 'not found' not in ldd.stdout,'unresolved OpenFOAM runtime library'
    snapshot={'label':label,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ldd_simpleFoam':ldd.stdout,'tools':tools,'libraries':libraries}
    save(RUN/(label+'.json'),snapshot)
    return snapshot

def configure_full_work(case,order):
    case=Path(case)
    original=(case/'system/controlDict').read_bytes()
    text=original.decode()
    text,n=re.subn(r'(?m)^endTime[ \t]+[^;\n]+;[^\n]*$','endTime 150;',text);assert n==1
    expected=text.encode()
    # Keep the source startFrom and every other control/function-object byte unchanged.
    ctrl=case/'system/controlDict';ctrl.write_bytes(expected)
    fv=(case/'system/fvSolution');fixed=(case/'system/fvSolution.fixedIter')
    source_fixed=fixed.read_bytes();assert fv.read_bytes()==source_fixed,'initialized source is not already fixedIter'
    actual=ctrl.read_bytes();assert actual==expected
    assert re.search(rb'(?m)^endTime\s+150\s*;',actual)
    start_from=re.search(rb'(?m)^startFrom\s+([^;]+);',actual);assert start_from
    cdef=(case/'system/include/caseDefinition').read_text()
    decomp=(case/'system/decomposeParDict').read_text()
    assert re.search(r'(?m)^nCores\s+56\s*;',cdef)
    assert re.search(r'(?m)^nHierarchical\s+\(7 4 2\)\s*;',cdef)
    assert re.search(r'(?m)^\s*method\s+\$decompositionMethod\s*;',decomp)
    assert re.search(r'(?m)^decompositionMethod\s+hierarchical\s*;',cdef)
    assert re.search(r'(?m)^\s*order\s+'+order+r'\s*;',decomp)
    return {'passed':True,'order':order,'endTime':150,'source_startFrom':start_from[1].decode().strip(),'ranks':56,'hierarchy':[7,4,2],
            'allowed_run_control_edits':['system/controlDict:endTime'],
            'fvSolution_equals_frozen_fixedIter':True,'physics_and_function_objects':'copied byte-identically from initialized source; no code injection or patch'}

def arm_record(case,order):
    log,timings,cd,counts=review_native_output(case)
    confidence=re.search(r'Minimum number of measured time steps[^\n]*=\s*(\d+)',log)
    by_step={str(step):value for step,value in zip(range(2,151),timings)}
    return {'order':order,'steps':150,'intervals':149,'mean_seconds_per_step':statistics.mean(timings),
            'median_seconds_per_step':statistics.median(timings),
            'p95_seconds_per_step':statistics.quantiles(timings,n=100,method='inclusive')[94],
            'maximum_seconds_per_step':max(timings),'final_Cd':cd[-1][1],'Cd_by_step':cd,
            'fixed_iterations':counts,'native_minimum_samples':int(confidence[1]) if confidence else None,
            'confidence_warning_present':'smaller than the calculated one' in log,
            'timings_seconds':timings,'timing_by_step_seconds':by_step}

def select_arms_by_order(rows):
    by_order={row['order']:row for row in rows}
    assert len(rows)==2 and set(by_order)=={'zyx','xyz'},'expected exactly one full result for each hierarchy order'
    return by_order

def runtime_identity_equal(before,after):
    return before['tools']==after['tools'] and before['libraries']==after['libraries']

def run_arm(order):
    src=SOURCE/('order-'+order)
    assert (src/'READY').is_file(),('initialized source not READY',src)
    save(RUN/(order+'-source-check.json'),source_check(src,order))
    source_fields=field_snapshot(src)
    save(RUN/(order+'-source-field-seal.json'),source_fields)
    dest=WORK/'cases'/order
    assert not dest.exists(),('case path already exists; preserve it',dest)
    dest.mkdir(parents=True)
    bounded(order+'-source-before',['python3',KIT/'tree-manifest.py',src,dest,dest/'source-before.json','--source-only'],KIT,180)
    bounded(order+'-clone',['python3','-c','import shutil,sys;shutil.copytree(sys.argv[1],sys.argv[2],symlinks=True,dirs_exist_ok=True,ignore=shutil.ignore_patterns("source-before.json","source-after-copy.json","source-after-init.json"))',src,dest],KIT,300)
    bounded(order+'-clone-check',['python3',KIT/'tree-manifest.py',src,dest,dest/'copy-check.json','--compare-copy'],KIT,180)
    copied_fields=field_snapshot(dest)
    assert copied_fields==source_fields,order+' initialized time-zero fields differ from source'
    save(dest/'copy-field-seal.json',copied_fields)
    config=configure_full_work(dest,order);save(dest/'full150-control-validation.json',config)
    save(dest/'runtime-source-hashes.json',{'source_check':json.loads((RUN/(order+'-source-check.json')).read_text()),
                                            'source_manifest':json.loads((dest/'copy-check.json').read_text())})
    return src,dest,config

def main():
    global RUN,DEADLINE
    started=time.monotonic();DEADLINE=started+INTERNAL_DEADLINE_SECONDS
    job=os.environ['SLURM_JOB_ID']
    assert int(os.environ.get('SLURM_NTASKS','0'))==56,os.environ.get('SLURM_NTASKS')
    assert int(os.environ.get('SLURM_JOB_NUM_NODES','0'))==1,os.environ.get('SLURM_JOB_NUM_NODES')
    RUN=WORK/'runs'/job;RUN.mkdir(parents=True,exist_ok=False)
    (WORK/'cases').mkdir(parents=True,exist_ok=True)
    save(RUN/'run-intent.json',{'job_id':job,'utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                'requested_nodes':1,'requested_ranks':56,'exclusive':True,
                                'actual_slurm_ntasks':int(os.environ['SLURM_NTASKS']),
                                'actual_slurm_job_num_nodes':int(os.environ['SLURM_JOB_NUM_NODES']),
                                'slurm_nodelist':os.environ.get('SLURM_JOB_NODELIST'),
                                'walltime_seconds':10800,'maximum_allocated_cpu_hours':168,
                                'internal_deadline_seconds':INTERNAL_DEADLINE_SECONDS,'outer_timeout_seconds':OUTER_TIMEOUT_SECONDS,
                                'arm_order':list(ARM_ORDER),'solver_caps_seconds':SOLVER_CAP,
                                'scope':'Full 150-step matched hierarchy-order measurement; no NSCC timing comparison.'})
    bounded('kit-before',['sha256sum','-c','payload-sha256.txt'],KIT,45)
    runtime_snapshot('runtime-before')
    results=[]
    for index,order in enumerate(ARM_ORDER):
        before=remaining()
        required=FIRST_SOLVER_RESERVE_SECONDS if index==0 else SECOND_ARM_RESERVE_SECONDS
        assert before>=required,('insufficient shared time before '+order,{'remaining_seconds':before,'required_seconds':required})
        phase(order,'arm-prepare-start',{'remaining_seconds':before,'reserved_for_next_or_review_seconds':required})
        src,dest,config=run_arm(order)
        after_prepare=remaining()
        solver_cap=SOLVER_CAP[order]
        if index==0:
            # Protect the expected second zyx solve, its preparation and final review.
            assert after_prepare>=FIRST_SOLVER_RESERVE_SECONDS,(
                'zyx preparation consumed the protected xyz copy/solve/review window',after_prepare)
            solver_cap=min(SOLVER_CAP[order],after_prepare-SECOND_ARM_RESERVE_SECONDS-FIRST_SOLVER_REVIEW_RESERVE_SECONDS)
            assert solver_cap>=EXPECTED_FIRST_SOLVER_SECONDS,('time guard would shorten xyz below its planning window',solver_cap)
        else:
            assert after_prepare>=EXPECTED_SECOND_SOLVER_SECONDS+SECOND_SOLVER_REVIEW_RESERVE_SECONDS,(
                'insufficient time for the 150-step zyx planning window plus review',after_prepare)
            solver_cap=min(SOLVER_CAP[order],after_prepare-SECOND_SOLVER_REVIEW_RESERVE_SECONDS)
            assert solver_cap>=EXPECTED_SECOND_SOLVER_SECONDS,('time guard would shorten zyx below its planning window',solver_cap)
        phase(order,'solver-start',{'remaining_seconds':remaining(),'configured_solver_cap_seconds':SOLVER_CAP[order],
                                    'effective_solver_cap_seconds':solver_cap})
        node_snapshot('solver-before',dest)
        resource=dest/'resource-time.log';out=(dest/'simpleFoam.log').open('w');err=(dest/'solver.stderr').open('w')
        solver_start=time.monotonic();utc_solver=datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            p=subprocess.run(['/usr/bin/time','-v','-o',str(resource),'timeout','--signal=TERM','--kill-after=15s',
                              str(solver_cap)+'s','mpirun','-np','56','--','simpleFoam','-parallel'],
                             cwd=str(dest),stdout=out,stderr=err,timeout=solver_cap+25)
            rc=p.returncode
        except subprocess.TimeoutExpired:
            rc=124
        finally:
            out.close();err.close()
        elapsed=time.monotonic()-solver_start
        save(dest/'return-code.json',{'returncode':rc,'configured_cap_seconds':SOLVER_CAP[order],
             'effective_cap_seconds':solver_cap,'elapsed_seconds':elapsed,'utc_start':utc_solver})
        node_snapshot('solver-after',dest);phase(order,'solver-exit',{'returncode':rc,'elapsed_seconds':elapsed})
        assert rc==0,(order,'solver did not complete cleanly',rc)
        solver_fields=field_snapshot(dest)
        expected_fields=json.loads((RUN/(order+'-source-field-seal.json')).read_text())
        assert solver_fields==expected_fields,order+' solver changed sealed initialized time-zero fields'
        save(RUN/(order+'-solver-field-seal.json'),solver_fields)
        row=arm_record(dest,order)
        assert not re.search(r'FOAM FATAL|MPI_ABORT|died from signal|core dumped',(dest/'solver.stderr').read_text(),re.I)
        bounded(order+'-source-after',['python3',KIT/'tree-manifest.py',src,dest,dest/'source-after.json','--source-only','--compare-source-snapshot'],KIT,180)
        row.update({'solver_elapsed_seconds':elapsed,'solver_cap_seconds':solver_cap,'configured_solver_cap_seconds':SOLVER_CAP[order],'control_validation':config,
                    'source_runtime_hashes':json.loads((dest/'runtime-source-hashes.json').read_text())})
        results.append(row);save(RUN/'partial-results.json',{'arms':results,'completed_order':[r['order'] for r in results],
                                                               'full150_gates_passed_so_far':True})
        phase(order,'arm-complete',{'mean_seconds_per_step':row['mean_seconds_per_step'],'intervals':row['intervals']})
    after=runtime_snapshot('runtime-after')
    before=json.loads((RUN/'runtime-before.json').read_text())
    runtime_equal=runtime_identity_equal(before,after)
    save(RUN/'runtime-identity-comparison.json',{'identical':runtime_equal,'scope':'Resolved executable and shared-library identities before/after the matched pair.'})
    if not runtime_equal:
        save(RUN/'comparison.json',{'passed':False,'reason':'runtime executable/library identity changed during the pair',
                                    'completed_arms':[r['order'] for r in results],
                                    'runtime_before':before,'runtime_after':after})
        raise AssertionError('runtime identity changed; no passed matched comparison may be claimed')
    bounded('kit-after',['sha256sum','-c','payload-sha256.txt'],KIT,45)
    by_order=select_arms_by_order(results)
    save(RUN/'comparison.json',{'passed':True,'orders':['xyz','zyx'],'arms_by_order':by_order,
          'timing_change_zyx_vs_xyz_percent':100*(by_order['zyx']['mean_seconds_per_step']/by_order['xyz']['mean_seconds_per_step']-1),
          'runtime_identity_stable_before_after':runtime_equal,'runtime_before':before,'runtime_after':after,
          'hostname':socket.getfqdn(),'steps_each':150,'timed_intervals_each':149,
          'scored_result':False,'limits':['Single reverse-order matched pair; one allocation does not establish independent repeatability.',
          'Whole-node procfs snapshots do not measure hardware memory bandwidth or per-process attribution.',
          'Native confidence recommendation and serial step samples do not create independent confidence intervals.']})
    print('IRIS_FULL150_ZYX_XYZ_MATCHED_PASS')

if __name__=='__main__':
    main()
