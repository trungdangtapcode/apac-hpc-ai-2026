#!/usr/bin/env python3
"""One-allocation ABBA native rank-density trial: Scotch40 versus Scotch48."""
from pathlib import Path
import hashlib,json,math,os,re,shutil,socket,statistics,subprocess,sys,time
import helpers as h
from native_checks import field_snapshot
from read_rank_proofs import validate_proof_dir
from placement import validate_balanced40
from native_output import review_native_output
from sampler import (preflight as sampler_preflight,start_sampler,stop_sampler,
                     wait_for_first_sample,run_with_sampler,validate_sample_file)

KIT=Path(__file__).resolve().parent
SOURCE_ROOT=Path('/global/exafs/users/rdmaworkshop30/apac2026')
SOURCES={
 40:SOURCE_ROOT/'tripleu-iris-scotch40-cut-20261105T162039Z/artifacts/cut-N40-scotch',
 48:SOURCE_ROOT/'tripleu-iris-scotch48-cut-20261105T073707Z/artifacts/cut-N48-scotch'}
MANIFESTS={40:KIT/'accepted-source-manifest-40.json',48:KIT/'accepted-source-manifest-48.json'}
SUPPLEMENTARY={40:KIT/'supplementary-source-manifest-40.json',48:KIT/'supplementary-source-manifest-48.json'}
PINS={40:KIT/'source-pins-40.json',48:KIT/'source-pins-48.json'}
TEMPLATES={40:KIT/'payload-case-40',48:KIT/'payload-case-48'}
ARMS=[('A1-control48',48,'control48'),('B1-candidate40',40,'candidate40'),
      ('B2-candidate40',40,'candidate40'),('A2-control48',48,'control48')]
SOLVER_CAP=2100
PREP_CAP=180
FINALIZE_RESERVE=480
INTERNAL_SECONDS=10600

def needed_window(arms_left,with_prep=True):
    if not arms_left:return FINALIZE_RESERVE
    if with_prep:return arms_left*(SOLVER_CAP+PREP_CAP)+FINALIZE_RESERVE
    return SOLVER_CAP+(arms_left-1)*(SOLVER_CAP+PREP_CAP)+FINALIZE_RESERVE

def require_window(arms_left,with_prep=True):
    need=needed_window(arms_left,with_prep)
    if h.remaining()<need:raise RuntimeError('not enough time for complete remaining solver arms and final checks')

def compare_same_partition(left,right):
    if len(left)!=len(right) or any(len(a)!=len(b) for a,b in zip(left,right)):
        raise ValueError('same-partition force output shapes differ')
    pairs=[(a,b) for x,y in zip(left,right) for a,b in zip(x,y)]
    deltas=[abs(a-b) for a,b in pairs]
    outside=[d for d,(a,b) in zip(deltas,pairs) if not math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-10)]
    return {'passed':not outside,'tolerance':'math.isclose(rel_tol=1e-9, abs_tol=1e-10)',
            'maximum_absolute_delta_all_columns':max(deltas) if deltas else 0.0,
            'values_outside_repeat_tolerance':len(outside)}

def main():
    assert os.environ.get('SLURM_NTASKS')=='56'
    assert os.environ.get('SLURM_JOB_NUM_NODES')=='1'
    assert os.environ.get('SLURM_CPUS_ON_NODE')=='56'
    h.DEADLINE=time.monotonic()+INTERNAL_SECONDS
    h.RUN=KIT/'runs'/os.environ['SLURM_JOB_ID'];h.RUN.mkdir(parents=True,exist_ok=False);run=h.RUN
    h.bounded('payload-before',['sha256sum','-c',KIT/'payload-sha256.txt'],KIT,20)
    h.save(run/'intent.json',{'question':'On one Iris allocation and the same 65,334,765-cell physical case, does the initialized 40-domain Scotch decomposition reduce native seconds per step versus the initialized 48-domain decomposition?',
      'arm_order':[x[0] for x in ARMS],'ranks_by_arm':{n:r for n,r,_ in ARMS},
      'solver_steps':40,'timed_intervals':39,'rank_mapping':'Control48 default; candidate40 socket/core, actual 20/20 pre-MPI NUMA balance checked.',
      'file_handler':'OpenFOAM default uncollated for both; FOAM_FILEHANDLER must be unset.',
      'controlled_change':'Partition count plus placement differ. Physics, fixed iteration work, precision, node, I/O and horizon common; no single-factor causal claim.',
      'request_maximum_allocated_CPU_hours':168,'gpu_hours':0,'scored_result':False,
      'interpretation_limit':'This native 40-step one-node screen is not a full official simulation, a cross-platform estimate, or proof of a stable winner.'})
    free=shutil.disk_usage(KIT).free
    h.save(run/'space-preflight.json',{'filesystem_free_bytes':free,'required_free_bytes':96*1024**3,'scope':'Filesystem free space only; not quota or reserved allocation.'})
    assert free>=96*1024**3
    assert os.environ.get('WM_PROJECT_VERSION')=='v2512'
    assert os.environ.get('WM_PRECISION_OPTION')=='DP'
    assert not os.environ.get('FOAM_FILEHANDLER')
    before=h.runtime_snapshot('runtime-before')
    source_fields={}
    for ranks in (40,48):
        output=run/('source-observation-%d.json'%ranks)
        h.bounded('accepted-source-%d-before'%ranks,['python3',KIT/'source_checks.py','--source',SOURCES[ranks],
          '--template',TEMPLATES[ranks],'--pins',PINS[ranks],'--manifest',MANIFESTS[ranks],
          '--supplementary',SUPPLEMENTARY[ranks],'--ranks',str(ranks),'--output',output],KIT,180)
        source_fields[ranks]=field_snapshot(SOURCES[ranks],ranks)
        h.save(run/('source-fields-%d.json'%ranks),source_fields[ranks])
    sampler_info=sampler_preflight(reads=5,max_read_ms=50.0);h.save(run/'sampler-preflight.json',sampler_info)
    require_window(len(ARMS))
    mpirun=shutil.which('mpirun');assert mpirun
    # Qualify placement before spending a full control solver arm.
    probe=run/'probes'/'balanced40';probe.mkdir(parents=True)
    h.bounded('balanced40-placement-probe',[mpirun,'--report-bindings','--display-map','--map-by','socket','--bind-to','core','-np','40','--',sys.executable,KIT/'probe_writer.py','--proof-dir',probe],KIT,45)
    h.save(run/'probes'/'balanced40-placement.json',validate_balanced40(validate_proof_dir(probe,40)))
    results=[]
    for index,(label,ranks,recipe) in enumerate(ARMS):
        left=len(ARMS)-index;require_window(left)
        dest=run/'arms'/label;dest.parent.mkdir(exist_ok=True)
        h.save(run/(label+'-source-selection.json'),{'rank_count':ranks,'source':str(SOURCES[ranks]),
          'core_manifest_sha256':hashlib.sha256(MANIFESTS[ranks].read_bytes()).hexdigest(),
          'supplementary_manifest_sha256':hashlib.sha256(SUPPLEMENTARY[ranks].read_bytes()).hexdigest(),
          'source_pins_sha256':hashlib.sha256(PINS[ranks].read_bytes()).hexdigest()})
        preparation=run/(label+'-preparation.json')
        h.bounded(label+'-preparation',['python3',KIT/'prepare_arm.py','--source',SOURCES[ranks],
          '--destination',dest,'--manifest',MANIFESTS[ranks],'--supplementary',SUPPLEMENTARY[ranks],
          '--template',TEMPLATES[ranks],'--pins',PINS[ranks],'--rank-count',str(ranks),
          '--probe-writer',KIT/'probe_writer.py','--proof-reader',KIT/'validate_arm_proofs.py',
          '--mpirun',mpirun,'--recipe',recipe,'--result',preparation],KIT,PREP_CAP)
        prep=json.loads(preparation.read_text());assert prep['passed'] and prep['rank_count_complete'] and prep['rank_binding_reports_complete']
        require_window(left,with_prep=False)
        if ranks==40:
            h.save(dest/'placement-validation.json',validate_balanced40(json.loads((dest/'rank-proofs.json').read_text())))
        flags=['--map-by','socket','--bind-to','core'] if ranks==40 else []
        command=[mpirun,'--report-bindings','--display-map',*flags,'-np',str(ranks),'--','simpleFoam','-parallel']
        h.save(dest/'command.json',{'command':command,'rank_count':ranks,'cap_seconds':SOLVER_CAP,
          'file_handler_expected':'uncollated','mapping':'Candidate40 socket/core; control48 default.'})
        if field_snapshot(dest,ranks)!=source_fields[ranks]:raise RuntimeError('arm input time-zero fields changed during clone')
        h.node_snapshot('solver-before',dest)
        sampler_process=None;sampler_stop=None;telemetry={'state':'disabled','reason':sampler_info.get('reason')}
        if sampler_info.get('enabled'):
            try:
                sampler_process=start_sampler(dest/'telemetry-samples.jsonl',interval=5.,stderr_path=dest/'telemetry-stderr.log')
                first=wait_for_first_sample(sampler_process,dest/'telemetry-samples.jsonl',timeout_seconds=1.0)
                telemetry={'state':'sampling','interval_seconds':5.0} if first.get('available') else {'state':'unavailable','reason':first.get('reason')}
                if telemetry['state']=='unavailable':sampler_stop=stop_sampler(sampler_process);sampler_process=None
            except Exception as exc:
                telemetry={'state':'unavailable','reason':type(exc).__name__}
                if sampler_process is not None:sampler_stop=stop_sampler(sampler_process);sampler_process=None
        start=time.monotonic();h.phase(label,'solver-start',{'rank_count':ranks,'command':command,'telemetry':telemetry['state']})
        try:
            with (dest/'simpleFoam.log').open('w') as out,(dest/'solver.stderr').open('w') as err:
                proc,sampler_stop=run_with_sampler(sampler_process,
                  ['/usr/bin/time','-v','-o',str(dest/'resource-time.log'),'timeout','--signal=TERM','--kill-after=15s',str(SOLVER_CAP)+'s',*command],
                  cwd=dest,stdout=out,stderr=err,timeout=SOLVER_CAP+30)
                sampler_process=None
        finally:
            stopped=stop_sampler(sampler_process) if sampler_process is not None else sampler_stop or {'process_was_started':False}
            samples=validate_sample_file(dest/'telemetry-samples.jsonl',optional=True)
            telemetry.update({'stop':stopped,'sample_count':samples['sample_count'],'sample_file_present':samples['present'],
                              'scope':'Whole-node aggregate; not process attribution or causal bandwidth evidence.'})
            h.save(dest/'telemetry-status.json',telemetry)
        h.save(dest/'return-code.json',{'returncode':proc.returncode,'elapsed_seconds':time.monotonic()-start})
        if proc.returncode:raise RuntimeError('%s solver returned %d'%(label,proc.returncode))
        log,timings,forces,iterations=review_native_output(dest,ranks)
        if not re.search(r'^I/O\s*:\s*uncollated\b',log,re.M):raise RuntimeError('native log did not use uncollated handler')
        if re.search(r'FOAM FATAL|MPI_ABORT|died from signal|core dumped',(dest/'solver.stderr').read_text(errors='replace'),re.I):
            raise RuntimeError('solver stderr contains a native fatal marker')
        fields=field_snapshot(dest,ranks)
        if fields!=source_fields[ranks]:raise RuntimeError('%s changed initialized time-zero input fields'%label)
        h.save(dest/'postsolve-fields.json',fields);h.node_snapshot('solver-after',dest)
        row={'arm':label,'recipe':recipe,'rank_count':ranks,'source':str(SOURCES[ranks]),'file_handler':'uncollated',
          'steps':40,'intervals':39,'mean_s_step':statistics.mean(timings),'median_s_step':statistics.median(timings),
          'maximum_s_step':max(timings),'timings_seconds':timings,'force_coefficients_by_step':forces,
          'fixed_iterations':iterations,'solver_elapsed_seconds':json.loads((dest/'return-code.json').read_text())['elapsed_seconds'],
          'preparation_result':prep,'rank_proof_result':str(dest/'rank-proofs.json'),'telemetry':telemetry}
        results.append(row);h.save(run/'partial-results.json',{'arms':results,'complete':False,'scored_result':False})
        h.phase(label,'reviewed',{'rank_count':ranks,'mean_s_step':row['mean_s_step']})
    after=h.runtime_snapshot('runtime-after')
    if not h.runtime_identity_equal(before,after):raise RuntimeError('OpenFOAM/MPI tool or library identity changed')
    for ranks in (40,48):
        h.bounded('accepted-source-%d-after'%ranks,['python3',KIT/'source_checks.py','--source',SOURCES[ranks],
          '--template',TEMPLATES[ranks],'--pins',PINS[ranks],'--manifest',MANIFESTS[ranks],
          '--supplementary',SUPPLEMENTARY[ranks],'--ranks',str(ranks),'--output',run/('source-after-%d.json'%ranks)],KIT,180)
    h.bounded('payload-after',['sha256sum','-c',KIT/'payload-sha256.txt'],KIT,20)
    arms={x['arm']:x for x in results}
    f40=compare_same_partition(arms['B1-candidate40']['force_coefficients_by_step'],arms['B2-candidate40']['force_coefficients_by_step'])
    f48=compare_same_partition(arms['A1-control48']['force_coefficients_by_step'],arms['A2-control48']['force_coefficients_by_step'])
    if not f40['passed'] or not f48['passed']:raise RuntimeError('same-decomposition force repeat gate failed')
    mean40=(arms['B1-candidate40']['mean_s_step']+arms['B2-candidate40']['mean_s_step'])/2
    mean48=(arms['A1-control48']['mean_s_step']+arms['A2-control48']['mean_s_step'])/2
    comparison={'passed':True,'complete_four_arm_comparison':True,'scored_result':False,'arm_order':[x[0] for x in ARMS],
      'arms':results,'rank40_mean_s_step':mean40,'rank48_mean_s_step':mean48,
      'rank40_vs_rank48_time_delta_s_step':mean40-mean48,
      'rank40_vs_rank48_time_percent':100*(mean40/mean48-1),
      'within_partition_force_repeat_checks':{'40':f40,'48':f48},'runtime_identity_stable':True,
      'question':'Does balanced20/20 N40 beat default-mapped N48 on this Iris physical case?',
      'limits':['One four-arm ABBA allocation and 40-step microbenchmark; not full horizon or scored official result.',
        'Partition count and placement both differ; whole-configuration comparison, not a single-factor causal effect.',
        'Rank proof records launcher OS affinity before MPI_Init; not proof of solver-helper binding or NUMA page placement.',
        'Any performance difference can include partition-dependent numerical and communication effects; this comparison does not isolate a single hardware bottleneck.',
        'No prior unstable I/O treatment is repeated; uncollated default file handling is fixed across both rank counts.']}
    h.save(run/'comparison.json',comparison)
    print('IRIS_RANK_DENSITY40_VS48_COMPLETE')
if __name__=='__main__':main()
