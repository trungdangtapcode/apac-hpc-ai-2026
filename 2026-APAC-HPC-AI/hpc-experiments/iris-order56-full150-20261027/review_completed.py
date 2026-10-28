"""Replay the native full150 reviewer and compare retained summaries."""
from pathlib import Path
import importlib.util, json, math, statistics, hashlib

E=Path(__file__).resolve().parent
C=E/'completed-2294234'/'collected'
OUT=E/'completed-2294234'
spec=importlib.util.spec_from_file_location('native_output',E/'native_output.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
summary=json.loads((C/'runs/2294234/comparison.json').read_text())
assert summary['passed'] is True and summary['runtime_identity_stable_before_after'] is True
acct=json.loads((OUT/'collection.json').read_text())
assert '2294234|tu-iris-full150|COMPLETED|0:0|7585|56|iris024|' in acct['accounting']
review={}
for order in ['zyx','xyz']:
    arm=C/'cases'/order
    log,timings,cd,iterations=mod.review_native_output(arm)
    saved=summary['arms_by_order'][order]
    assert timings==saved['timings_seconds'],f'{order}: native replay timings differ from comparison.json'
    assert cd==saved['Cd_by_step'],f'{order}: native replay force-coefficient rows differ from comparison.json'
    assert len(timings)==149 and len(cd)==150
    checks=json.loads((C/f'runs/2294234/{order}-source-check.json').read_text())
    before=json.loads((arm/'source-before.json').read_text())
    after=json.loads((arm/'source-after.json').read_text())
    clone=json.loads((arm/'copy-check.json').read_text())
    src_seal=json.loads((C/f'runs/2294234/{order}-source-field-seal.json').read_text())
    copy_seal=json.loads((arm/'copy-field-seal.json').read_text())
    solver_seal=json.loads((C/f'runs/2294234/{order}-solver-field-seal.json').read_text())
    control=json.loads((arm/'full150-control-validation.json').read_text())
    rc=json.loads((arm/'return-code.json').read_text())
    for obj,label in [(checks,'source check'),(src_seal,'source field seal'),(copy_seal,'copy field seal'),(solver_seal,'solver field seal'),(control,'control validation')]:
        assert obj.get('passed') is True,f'{order}: {label} failed'
    assert before==after,f'{order}: source changed during solve'
    assert before['files']==clone['files'],f'{order}: cloned input differs from sealed source'
    assert src_seal==copy_seal==solver_seal,f'{order}: field seals differ'
    assert control['allowed_run_control_edits']==['system/controlDict:endTime']
    assert control['ranks']==56 and control['hierarchy']==[7,4,2] and control['endTime']==150
    assert rc['returncode']==0
    resource=(arm/'resource-time.log').read_text()
    assert 'Exit status: 0' in resource
    vals=sorted(timings)
    p95=statistics.quantiles(timings,n=100,method='inclusive')[94]
    p99=statistics.quantiles(timings,n=100,method='inclusive')[98]
    confidence=[line.strip() for line in log.splitlines() if 'Minimum number of measured time steps' in line]
    review[order]={
      'steps':150,'timed_intervals':len(timings),'mean_seconds_per_step':statistics.mean(timings),
      'median_seconds_per_step':statistics.median(timings),'p95_seconds_per_step':p95,
      'p99_seconds_per_step':p99,'max_seconds_per_step':max(timings),
      'solver_elapsed_seconds':rc['elapsed_seconds'],'solver_cap_seconds':rc['effective_cap_seconds'],
      'minimum_sample_recommendation_line':confidence,'native_confidence_warning':saved['confidence_warning_present'],
      'native_parser_passed':True,'native_timer_table_exactly_matches_log':True,
      'force_coefficient_rows_exactly_match_comparison_json':True,'iterations_by_field':iterations,
      'field_seals_equal':True,'source_tree_unchanged':True,'clone_matches_sealed_source':True,
      'resource_exit_status':0,
      'gnu_time_selected':{k:next((ln.strip()[len(k)+1:].strip() for ln in resource.splitlines() if ln.strip().startswith(k+':')),None)
       for k in ['User time (seconds)','System time (seconds)','Percent of CPU this job got','Elapsed (wall clock) time (h:mm:ss or m:ss)','Maximum resident set size (kbytes)','Major (requiring I/O) page faults','Minor (reclaiming a frame) page faults','Voluntary context switches','Involuntary context switches','Swaps','File system inputs','File system outputs']},
      'whole_node_procfs_snapshots_present':all((arm/(x+'-node-snapshot.json')).is_file() for x in ['solver-before','solver-after'])
    }
# Verify all recorded phase process results returned zero and both runtime identities match.
phases=[json.loads(line) for line in (C/'runs/2294234/phases.jsonl').read_text().splitlines()]
phase_exits=[p for p in phases if p.get('state')=='exit']
assert phase_exits and all(p.get('returncode')==0 for p in phase_exits)
kit_hashes=json.loads((OUT/'collection.json').read_text())['remote_runtime_hashes']
expected=json.loads((C/'kit/payload-sha256.json').read_text())['files']
assert kit_hashes==expected
identity=json.loads((C/'runs/2294234/runtime-identity-comparison.json').read_text())
assert identity['identical'] is True
zyx=review['zyx'];xyz=review['xyz']
reduction=(xyz['mean_seconds_per_step']-zyx['mean_seconds_per_step'])/xyz['mean_seconds_per_step']*100
zyxcd=summary['arms_by_order']['zyx']['Cd_by_step'];xyzcd=summary['arms_by_order']['xyz']['Cd_by_step']
assert len(zyxcd)==len(xyzcd)==150
# Force coefficient column 1 is total Cd. This is a descriptive trajectory difference,
# not an imposed tolerance gate for the native Basic task.
delta=[float(a[1])-float(b[1]) for a,b in zip(zyxcd,xyzcd)]
absdelta=[abs(x) for x in delta]
final_delta=delta[-1]
result={
 'reviewed_utc':'2026-10-28','job_id':'2294234','scheduler_state':'COMPLETED','scheduler_exit_code':'0:0',
 'elapsed_raw_seconds':7585,'allocated_cpus':56,'node':'iris024','exclusive_single_node':True,
 'submitted_payload_sha256_verified':True,'runtime_executable_and_library_identity_stable':True,
 'all_recorded_phase_commands_returncode_zero':True,'all_native_gates_passed':True,
 'orders':['zyx','xyz'],'hierarchy_factors':[7,4,2],'steps_per_arm':150,'timings_per_arm':149,
 'performance':{'zyx_mean_seconds_per_step':zyx['mean_seconds_per_step'],'xyz_mean_seconds_per_step':xyz['mean_seconds_per_step'],
   'zyx_time_reduction_vs_xyz_percent':reduction,'claim':'One full-length matched pair on Iris; not NSCC and not contest score.'},
 'arms':review,
 'force_coefficient_trajectory':{'compared_field':'total Cd, coefficient.dat column 2 (index 1)',
   'rows_each':150,'max_absolute_stepwise_difference':max(absdelta),
   'mean_absolute_stepwise_difference':statistics.mean(absdelta),'final_zyx_Cd':zyxcd[-1][1],
   'final_xyz_Cd':xyzcd[-1][1],'final_delta_zyx_minus_xyz':final_delta,
   'final_delta_percent_of_xyz':final_delta/xyzcd[-1][1]*100,
   'interpretation':'Descriptive difference only; no accuracy tolerance was specified for this native task.'},
 'phase_durations_seconds':[{ 'phase':p.get('phase'),'state':p.get('state'),'elapsed_seconds':p.get('elapsed_seconds'),'returncode':p.get('returncode')} for p in phases if p.get('state')=='exit'],
 'telemetry_limits':['GNU time command-level counters were collected for each mpirun; MaxRSS and page-fault attribution are not per-rank measurements.',
   'Before/after whole-node procfs snapshots exist but do not identify solver-specific memory bandwidth or NUMA traffic.',
   'CPU inventory/runtime environment were collected; no hardware memory-bandwidth counter, per-process NUMA map, or per-rank CPU-frequency trace was collected.',
   'Serial timing steps within one solver arm are correlated observations, not independent allocation-level repetitions.'],
 'source_confidence_limits':['Native log recommends 0 samples for zyx and 51 for xyz to meet its 2%/95% rule; both arms have 149 timed samples.',
   'That native recommendation is not an independent-run confidence interval and does not establish repeatability across nodes or allocations.'],
 'next_hypothesis':'Repeat the full 150-step hierarchy-order pair with reversed execution order (xyz then zyx) on a fresh matched Iris allocation; compare candidate/control after accounting for per-run order and node effects.',
 'limits':['One full matched pair was measured in zyx-then-xyz order on a single Iris allocation; run-order and node-to-node repeatability remain untested at full length.','This is an Iris CPU timing result, not NSCC performance or a contest score.','Whole-node procfs snapshots do not measure hardware memory bandwidth or per-process attribution.','Native confidence recommendations and serial step samples do not create independent allocation-level confidence intervals.']}
(OUT/'REVIEW.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'job_id':'2294234','native_gate_pass':True,'zyx_mean':zyx['mean_seconds_per_step'],'xyz_mean':xyz['mean_seconds_per_step'],'reduction_percent':reduction,'zyx_p95':zyx['p95_seconds_per_step'],'xyz_p95':xyz['p95_seconds_per_step'],'cd_max_abs_delta':max(absdelta),'phases':len(phase_exits),'files_collected':len(acct['files'])+len(json.loads((OUT/'collected-addendum/collection.json').read_text())['files'])},sort_keys=True))
