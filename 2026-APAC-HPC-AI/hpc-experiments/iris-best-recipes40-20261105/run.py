"""Six-arm direct native comparison of three known Iris launch recipes."""
from pathlib import Path
import hashlib
import json
import math
import os
import re
import shutil
import socket
import statistics
import subprocess
import sys
import time

import helpers as h
from native_checks import field_snapshot
from native_output import review_native_output
from sampler import (preflight as sampler_preflight, start_sampler, stop_sampler,
                     wait_for_first_sample, run_with_sampler, validate_sample_file)

KIT=Path(__file__).resolve().parent
SOURCES={
 56:Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch56-20261025T063431Z/artifacts/ready-N56-scotch'),
 48:Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch48-cut-20261105T073707Z/artifacts/cut-N48-scotch')}
MANIFESTS={56:KIT/'accepted-source-manifest-56.json',48:KIT/'accepted-source-manifest-48.json'}
SUPPLEMENTARY={56:KIT/'supplementary-source-manifest-56.json',48:KIT/'supplementary-source-manifest-48.json'}
PINS={56:KIT/'source-pins-56.json',48:KIT/'source-pins-48.json'}
TEMPLATES={56:KIT/'payload-case-56',48:KIT/'payload-case-48'}
ARMS=[('T1-teammate56',56,'teammate56'),('O1-original48',48,'original48'),('H1-hybrid48',48,'hybrid48'),('H2-hybrid48',48,'hybrid48'),('O2-original48',48,'original48'),('T2-teammate56',56,'teammate56')]
SOLVER_CAP=1800
PREP_CAP=150
FINALIZE_RESERVE=480
INTERNAL_SECONDS=13900


def complete_window(arms_left, include_current_prep=True):
    if include_current_prep:
        return arms_left*(SOLVER_CAP+PREP_CAP)+FINALIZE_RESERVE
    return SOLVER_CAP+(arms_left-1)*(SOLVER_CAP+PREP_CAP)+FINALIZE_RESERVE

def require_window(seconds_left, arms_left, include_current_prep=True):
    needed=complete_window(arms_left,include_current_prep)
    if seconds_left<needed:
        raise RuntimeError('insufficient time for complete arms/final checks: need %d s, have %d s'%(needed,seconds_left))

def verify_solver_binding_report(text, ranks):
    found=[]
    for line in text.splitlines():
        match=re.search(r'(?:MCW\s+)?rank\s+(\d+)\s+bound to\b',line,re.I)
        if match: found.append(int(match.group(1)))
    observed=sorted(set(found))
    if observed!=list(range(ranks)):
        raise RuntimeError('solver --report-bindings ranks differ from 0..%d: %s'%(ranks-1,observed))
    return {'passed':True,'rank_count':ranks,'rank_ids':observed,'reports':len(found),
            'source':'Open MPI --report-bindings output; CPU-mask nonoverlap was checked separately by the matching-launch rank probe.'}

def binding_report(text,ranks):
    result=verify_solver_binding_report(text,ranks)
    return result

def max_series_delta(left,right,column):
    if len(left)!=len(right): raise ValueError('force output row counts differ')
    deltas=[abs(a[column]-b[column]) for a,b in zip(left,right)]
    return max(deltas),deltas

def compare_same_partition(left,right):
    if len(left)!=len(right): raise ValueError('within-partition force row count differs')
    if any(len(a)!=len(b) for a,b in zip(left,right)): raise ValueError('within-partition force columns differ')
    deltas=[abs(a-b) for row_a,row_b in zip(left,right) for a,b in zip(row_a,row_b)]
    errors=[abs(a-b) for row_a,row_b in zip(left,right) for a,b in zip(row_a,row_b)
            if not math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-10)]
    return {'passed':not errors,'tolerance':'math.isclose(rel_tol=1e-9, abs_tol=1e-10), existing same-source repeat gate',
            'maximum_absolute_delta_all_columns':max(deltas) if deltas else 0.0,
            'values_outside_repeat_tolerance':len(errors)}

def verify_input_pins_match():
    p56=json.loads(PINS[56].read_text())['files'];p48=json.loads(PINS[48].read_text())['files']
    if set(p56)!=set(p48): raise ValueError('48/56 case input pin paths differ')
    differing=[name for name in p56 if p56[name]!=p48[name]]
    if differing!=['system/include/caseDefinition']:
        raise ValueError('expected rank-only case input difference, got '+repr(differing))
    return {'passed':True,'common_pinned_inputs':len(p56)-1,'rank_specific_input':'system/include/caseDefinition',
            'n56_case_definition_sha256':p56[differing[0]],'n48_case_definition_sha256':p48[differing[0]]}

def main():
    assert os.environ.get('SLURM_NTASKS')=='56'
    assert os.environ.get('SLURM_JOB_NUM_NODES')=='1'
    assert os.environ.get('SLURM_CPUS_ON_NODE')=='56'
    h.DEADLINE=time.monotonic()+INTERNAL_SECONDS
    h.RUN=KIT/'runs'/os.environ['SLURM_JOB_ID'];h.RUN.mkdir(parents=True,exist_ok=False);run=h.RUN
    h.bounded('payload-before',['sha256sum','-c',KIT/'payload-sha256.txt'],KIT,20)
    h.save(run/'intent.json',{'question':'Does applying the teammate MPI socket/core mapping and collated handler to the promising 48-rank source improve native per-step time in absolute seconds against both the direct teammate 56-rank recipe and our 48-rank default recipe?',
      'arm_order':[x[0] for x in ARMS],'ranks_by_arm':{name:n for name,n,recipe in ARMS},'recipe_by_arm':{name:recipe for name,n,recipe in ARMS},'solver_steps':40,'timed_intervals':39,
      'solver_cap_seconds_each':SOLVER_CAP,'preparation_cap_seconds_each':PREP_CAP,'internal_deadline_seconds':INTERNAL_SECONDS,
      'request_maximum_allocated_CPU_hours':224,'gpu_hours':0,'scored_result':False,
      'rank_mapping':'Original48 uses default mapping; teammate56 and hybrid48 use --map-by socket --bind-to core. Matching MPI probe and solver launcher reports are retained; no socket rank count is assumed.',
      'controlled_change':'Recipe is deliberately varied across three treatments: teammate56 socket/core+collated; original48 default mapping+default uncollated; hybrid48 socket/core+collated. Sources, physics, native runtime, fixed iteration settings, 56-CPU node, and 40-step horizon are held fixed within source.'})
    free=shutil.disk_usage(KIT).free
    h.save(run/'space-preflight.json',{'filesystem_free_bytes':free,'required_free_bytes':96*1024**3,'scope':'Filesystem free space only; not quota or reserved allocation.'})
    assert free>=96*1024**3,'less than 96 GiB free for six isolated clones'
    source_pin_review=verify_input_pins_match();h.save(run/'rank-only-input-pin-review.json',source_pin_review)
    assert os.environ.get('WM_PROJECT_VERSION')=='v2512',os.environ.get('WM_PROJECT_VERSION')
    assert os.environ.get('WM_PRECISION_OPTION')=='DP',os.environ.get('WM_PRECISION_OPTION')
    assert not os.environ.get('FOAM_FILEHANDLER'),'FOAM_FILEHANDLER override must be unset for default handler'
    before=h.runtime_snapshot('runtime-before')
    source_fields={}
    for ranks in (56,48):
        source=SOURCES[ranks]
        h.bounded('accepted-source-%d-before'%ranks,['python3',KIT/'source_checks.py','--source',source,
            '--template',TEMPLATES[ranks],'--pins',PINS[ranks],'--manifest',MANIFESTS[ranks],
            '--supplementary',SUPPLEMENTARY[ranks],'--ranks',str(ranks),'--output',run/('source-observation-%d.json'%ranks)],KIT,150)
        source_fields[ranks]=field_snapshot(source,ranks);h.save(run/('source-fields-%d.json'%ranks),source_fields[ranks])
    telemetry_preflight=sampler_preflight(reads=5,max_read_ms=50.0);h.save(run/'sampler-preflight.json',telemetry_preflight)
    require_window(h.remaining(),len(ARMS))
    results=[]
    mpirun=shutil.which('mpirun');assert mpirun
    for index,(label,ranks,recipe) in enumerate(ARMS):
        arms_left=len(ARMS)-index;require_window(h.remaining(),arms_left)
        source=SOURCES[ranks];dest=run/'arms'/label;dest.parent.mkdir(exist_ok=True)
        h.save(run/(label+'-source-selection.json'),{'rank_count':ranks,'source':str(source),
          'core_manifest_sha256':hashlib.sha256(MANIFESTS[ranks].read_bytes()).hexdigest(),
          'supplementary_manifest_sha256':hashlib.sha256(SUPPLEMENTARY[ranks].read_bytes()).hexdigest(),
          'source_pins_sha256':hashlib.sha256(PINS[ranks].read_bytes()).hexdigest()})
        prep_result=run/(label+'-preparation.json')
        h.bounded(label+'-preparation',['python3',KIT/'prepare_arm.py','--source',source,'--destination',dest,
          '--manifest',MANIFESTS[ranks],'--supplementary',SUPPLEMENTARY[ranks],'--rank-count',str(ranks),
          '--probe-script',KIT/'rank_probe.py','--mpirun',mpirun,'--recipe',recipe,'--result',prep_result],KIT,PREP_CAP)
        prep=json.loads(prep_result.read_text());assert prep['passed'] and prep['cpu_affinity_nonoverlap'] and prep['rank_count_complete']
        require_window(h.remaining(),arms_left,include_current_prep=False)
        mpi_flags=['--map-by','socket','--bind-to','core'] if recipe in ('teammate56','hybrid48') else []
        command=[mpirun,'--report-bindings','--display-map',*mpi_flags,'-np',str(ranks),'--','simpleFoam','-parallel']
        if recipe in ('teammate56','hybrid48'): command += ['-fileHandler','collated']
        h.save(dest/'command.json',{'command':command,'rank_count':ranks,'cap_seconds':SOLVER_CAP,
          'recipe':recipe,'file_handler_expected':'collated' if recipe!='original48' else 'uncollated','rank_mapping':'Default mapping for original48; --map-by socket --bind-to core for teammate56/hybrid48.'})
        assert field_snapshot(dest,ranks)==source_fields[ranks]
        h.node_snapshot('solver-before',dest)
        telemetry_path=dest/'telemetry-samples.jsonl';telemetry_stderr=dest/'telemetry-stderr.log'
        sampler_process=None;sampler_stop_state=None
        telemetry_status={'state':'disabled_by_preflight','preflight_reason':telemetry_preflight.get('reason')}
        if telemetry_preflight.get('enabled'):
            try:
                sampler_process=start_sampler(telemetry_path,interval=5.0,stderr_path=telemetry_stderr)
                ready=wait_for_first_sample(sampler_process,telemetry_path,timeout_seconds=1.0)
                if ready.get('available'):
                    telemetry_status={'state':'sampling','interval_seconds':5.0,'first_sample_seen':True}
                else:
                    telemetry_status={'state':'unavailable','reason':ready.get('reason')}
                    sampler_stop_state=stop_sampler(sampler_process);sampler_process=None;telemetry_status['stop']=sampler_stop_state
            except Exception as exc:
                telemetry_status={'state':'unavailable','reason':type(exc).__name__}
                if sampler_process is not None:
                    sampler_stop_state=stop_sampler(sampler_process);sampler_process=None;telemetry_status['stop']=sampler_stop_state
        start=time.monotonic();h.phase(label,'solver-start',{'ranks':ranks,'command':command,'cap_seconds':SOLVER_CAP,
          'sampler_state':telemetry_status['state']})
        try:
            with (dest/'simpleFoam.log').open('w') as out,(dest/'solver.stderr').open('w') as err:
                p,sampler_stop_state=run_with_sampler(sampler_process,
                  ['/usr/bin/time','-v','-o',str(dest/'resource-time.log'),'timeout','--signal=TERM','--kill-after=15s',str(SOLVER_CAP)+'s',*command],
                  cwd=dest,stdout=out,stderr=err,timeout=SOLVER_CAP+30)
                sampler_process=None
        finally:
            stop_state=stop_sampler(sampler_process) if sampler_process is not None else sampler_stop_state or {'process_was_started':False}
            sample_check=validate_sample_file(telemetry_path)
            telemetry_status.update({'stop':stop_state,'sample_count':sample_check['sample_count'],
              'sample_bytes':sample_check['bytes'],'sample_file_present':sample_check['present'],
              'scope':'Whole-node aggregate procfs diagnostic; collection duration is not an interference estimate.'})
            h.save(dest/'telemetry-status.json',telemetry_status)
        elapsed=time.monotonic()-start;h.save(dest/'return-code.json',{'returncode':p.returncode,'elapsed_seconds':elapsed})
        h.phase(label,'solver-exit',{'returncode':p.returncode,'elapsed_seconds':elapsed})
        if p.returncode!=0: raise RuntimeError('%s did not complete successfully: %d'%(label,p.returncode))
        log,timings,forces,iterations=review_native_output(dest,ranks)
        solver_report=binding_report(log+'\n'+(dest/'solver.stderr').read_text(errors='replace'),ranks)
        h.save(dest/'solver-binding-review.json',solver_report)
        if field_snapshot(dest,ranks)!=source_fields[ranks]: raise RuntimeError('%s changed initialized time-zero fields'%label)
        h.save(dest/'postsolve-fields.json',field_snapshot(dest,ranks))
        expected_handler='uncollated' if recipe=='original48' else 'collated'
        if not re.search(r'^I/O\s*:\s*'+expected_handler+r'\b',log,re.M): raise RuntimeError('%s did not use expected %s file handler'%(label,expected_handler))
        if re.search(r'FOAM FATAL|MPI_ABORT|died from signal|core dumped',(dest/'solver.stderr').read_text(errors='replace'),re.I):
            raise RuntimeError('%s stderr contains a fatal marker'%label)
        h.node_snapshot('solver-after',dest)
        row={'arm':label,'recipe':recipe,'rank_count':ranks,'source':str(source),'file_handler':expected_handler,'steps':40,'intervals':39,
          'mean_s_step':statistics.mean(timings),'median_s_step':statistics.median(timings),'maximum_s_step':max(timings),
          'timings_seconds':timings,'force_coefficients_by_step':forces,'Cd_final':forces[-1][1],
          'fixed_iterations':iterations,'solver_elapsed_seconds':elapsed,'rank_probe':prep_result.read_text(),
          'solver_binding_reports':solver_report,'copy_elapsed_seconds':prep['elapsed_seconds'],
          'telemetry':telemetry_status}
        results.append(row);h.save(run/'partial-results.json',{'arms':results,'complete':False,'scored_result':False})
        h.phase(label,'reviewed',{'rank_count':ranks,'mean_s_step':row['mean_s_step']})
    after=h.runtime_snapshot('runtime-after')
    if not h.runtime_identity_equal(before,after): raise RuntimeError('OpenFOAM/MPI binary or library identity changed during allocation')
    for ranks in (56,48):
        h.bounded('accepted-source-%d-after'%ranks,['python3',KIT/'source_checks.py','--source',SOURCES[ranks],
            '--template',TEMPLATES[ranks],'--pins',PINS[ranks],'--manifest',MANIFESTS[ranks],
            '--supplementary',SUPPLEMENTARY[ranks],'--ranks',str(ranks),'--output',run/('source-after-%d.json'%ranks)],KIT,150)
    h.bounded('payload-after',['sha256sum','-c',KIT/'payload-sha256.txt'],KIT,20)
    by_arm={row['arm']:row for row in results}
    repeats={}
    for recipe,left,right in (('teammate56','T1-teammate56','T2-teammate56'),('original48','O1-original48','O2-original48'),('hybrid48','H1-hybrid48','H2-hybrid48')):
        repeats[recipe]=compare_same_partition(by_arm[left]['force_coefficients_by_step'],by_arm[right]['force_coefficients_by_step'])
        if not repeats[recipe]['passed']:
            raise RuntimeError('%s same-recipe force repeats exceeded existing repeat tolerance'%recipe)
    same_source_recipe_drift={}
    for left,right in (('O1-original48','H1-hybrid48'),('O2-original48','H2-hybrid48')):
        drift=compare_same_partition(by_arm[left]['force_coefficients_by_step'],by_arm[right]['force_coefficients_by_step'])
        same_source_recipe_drift[left+'_vs_'+right]=drift
        if not drift['passed']:
            raise RuntimeError('%s and %s same-source 48-rank force drift exceeded existing repeat tolerance'%(left,right))
    comparisons={}
    for recipe,left,right in (('teammate56','T1-teammate56','T2-teammate56'),('original48','O1-original48','O2-original48'),('hybrid48','H1-hybrid48','H2-hybrid48')):
        m=(by_arm[left]['mean_s_step']+by_arm[right]['mean_s_step'])/2
        med=(by_arm[left]['median_s_step']+by_arm[right]['median_s_step'])/2
        comparisons[recipe]={'arms':[left,right],'mean_seconds_per_step':m,'mean_of_arm_medians_seconds':med,
          'arm_mean_difference_seconds':by_arm[right]['mean_s_step']-by_arm[left]['mean_s_step'],
          'arm_mean_difference_percent':100*(by_arm[right]['mean_s_step']/by_arm[left]['mean_s_step']-1)}
    comparisons['hybrid48_vs_teammate56']={'mean_seconds_per_step_delta':comparisons['hybrid48']['mean_seconds_per_step']-comparisons['teammate56']['mean_seconds_per_step'],
      'percent':100*(comparisons['hybrid48']['mean_seconds_per_step']/comparisons['teammate56']['mean_seconds_per_step']-1)}
    comparisons['hybrid48_vs_original48']={'mean_seconds_per_step_delta':comparisons['hybrid48']['mean_seconds_per_step']-comparisons['original48']['mean_seconds_per_step'],
      'percent':100*(comparisons['hybrid48']['mean_seconds_per_step']/comparisons['original48']['mean_seconds_per_step']-1)}
    h.save(run/'comparison.json',{'passed':True,'complete_six_arm_recipe_comparison':True,'scored_result':False,
      'arm_order':[row['arm'] for row in results],'arms':results,'recipe_means':comparisons,
      'within_recipe_force_repeats':repeats,'same_source_48_recipe_force_drift':same_source_recipe_drift,'runtime_identity_stable':True,
      'question':'Directly compare absolute native seconds per step for teammate56, original48, and hybrid48, especially hybrid48 against both controls.',
      'limits':['Single six-arm 40-step Iris allocation; not a full solver horizon, cross-platform result, contest score, or promotion.',
       'Treatment bundles rank count, mapping/binding flags, and file handler by recipe; this does not isolate an individual flag effect.',
       'Intermediate/final Cd trajectories may differ across ranks; no cross-decomposition Basic equality gate is imposed. Same-recipe repeats and paired original48/hybrid48 same-source drift use the existing math.isclose tolerance as an unchanged-partition regression guard.',
       'Launcher binding output and pre-MPI_Init OS affinity probes do not establish post-MPI solver-helper affinity or NUMA page placement.',
       'Absolute timings are reported from measured values; this result makes no historical-record claim.']})
    print('IRIS_BEST_RECIPES40_COMPLETE')


if __name__=='__main__': main()
