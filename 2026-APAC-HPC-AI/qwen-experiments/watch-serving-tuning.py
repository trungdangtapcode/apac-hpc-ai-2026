"""Track frozen tuning jobs; retry time-budget gaps, never count failed jobs as measurements."""
import argparse
import csv
import fcntl
import gzip
import hashlib
import json
import getpass
import shlex
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIR = ROOT/'serving-tuning'
STATE = DIR/'registry.json'
TERMINAL = {'COMPLETED','FAILED','CANCELLED','TIMEOUT','NODE_FAIL','OUT_OF_MEMORY','PREEMPTED','BOOT_FAIL'}

def now():
    return datetime.now(timezone.utc).isoformat()

def save(path, data):
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,indent=2)+'\n')
    temporary.replace(path)

def command(args):
    return subprocess.run(args,cwd=ROOT,capture_output=True,text=True,check=True,timeout=120).stdout

def valid_measurement(row):
    return ((row.get('requests') or 0)>0 and row.get('cancelled_requests')==0
            and row.get('good_output_tokens_s') is not None)

def passing(row):
    return valid_measurement(row) and row.get('sla_pass') and row.get('errors')==0

def account_active_jobs(state):
    """Include independently submitted diagnostics in the account's queue cap."""
    tracked=sum(a['state'] not in TERMINAL for e in state['entries'] for a in e['attempts'])
    queued=command(['squeue','--noheader','--user',getpass.getuser(),'--format=%A'])
    return max(tracked,len({line.strip() for line in queued.splitlines() if line.strip()}))

def compare_output_baseline(smoke, baseline_path):
    """Allow research after a known baseline failure; never declare accuracy passed."""
    result={'policy':'research-baseline-v1','research_eligible':False,
            'accuracy_verified':False,'scope':'Eight-case non-regression diagnostic, not organiser accuracy',
            'candidate_passed':smoke.get('passed'),'candidate_total':smoke.get('total')}
    if not baseline_path.exists():
        result['reason']='Independent monolithic baseline is unavailable';return result
    raw=baseline_path.read_bytes()
    result.update(baseline=str(baseline_path),baseline_sha256=hashlib.sha256(raw).hexdigest())
    try:baseline=[json.loads(line) for line in raw.decode().splitlines()]
    except (ValueError,UnicodeError):
        result['reason']='Baseline journal is incomplete';return result
    if len(baseline)!=132 or any('error' in r for r in baseline):
        result['reason']='Require all 132 baseline responses without transport errors';return result
    long=[r for r in baseline if r.get('phase')=='long-concurrent']
    short=[r for r in baseline if r.get('phase') in ('short-sequential','short-concurrent')]
    cases=smoke.get('cases',[])
    if len(long)!=36 or not all(r.get('passed') is True for r in long) or len(short)!=96:
        result['reason']='Baseline long-context/control checks are incomplete or fail';return result
    if len(cases)!=8 or len({r.get('name') for r in cases})!=8:
        result['reason']='Require the unchanged complete eight-case candidate suite';return result
    known_failed=[];new_failed=[]
    for case in cases:
        ref=[r for r in short if r.get('name')==case.get('name')]
        if (len(ref)!=12 or len({r.get('endpoint') for r in ref})!=3
            or any(r.get('prompt')!=case.get('prompt') or r.get('expected')!=case.get('expected') for r in ref)
            or any(sum(r.get('endpoint')==host for r in ref)!=4 for host in {r.get('endpoint') for r in ref})
            or 'error' in case or not isinstance(case.get('text'),str)
            or not isinstance(case.get('passed'),bool)):
            result['reason']='Candidate case mismatch/error or insufficient independent baseline coverage';return result
        if all(r.get('passed') is False for r in ref):known_failed.append(case['name'])
        elif not all(r.get('passed') is True for r in ref):
            result['reason']='Baseline answer correctness is inconsistent';return result
        if not case['passed'] and case['name'] not in known_failed:new_failed.append(case['name'])
    # This evidence supports only the observed reverse-string baseline failure.
    # A baseline with additional failures must be investigated separately.
    if known_failed!=['reverse']:
        result['reason']='Unexpected baseline failure pattern';return result
    counted=sum(r['passed'] for r in cases)
    if smoke.get('total')!=8 or smoke.get('passed')!=counted:
        result['reason']='Candidate summary does not match its raw case results';return result
    result.update(known_baseline_failed_cases=known_failed,new_failed_cases=new_failed,
                  research_eligible=not new_failed,
                  reason='No newly failed cases versus the independent baseline' if not new_failed else 'New failure versus baseline')
    return result

def research_measurements(entry, concurrency=52):
    """The benchmark and output evidence must belong to the same attempt."""
    rows=[]
    for attempt in entry['attempts']:
        smoke=attempt.get('output_smoke',{})
        okay=(smoke.get('total')==8 and smoke.get('passed')==8) or attempt.get('output_baseline_comparison',{}).get('research_eligible') is True
        if okay:
            rows.extend({**r,'job':attempt['job']} for r in attempt.get('measurements',[])
                        if (concurrency is None or r.get('concurrency')==concurrency) and passing(r))
    return rows

def refresh_output_diagnostic(statuses, notes):
    path=ROOT/'serving-tuning-02/output-diagnostic-job.json'
    if not path.exists():return False
    record=json.loads(path.read_text());job=record['job'];run=ROOT/'runs'/job
    record['status']=statuses.get(job,{})
    record['state']=record['status'].get('State','SUBMITTED').split()[0].rstrip('+')
    rows=[]
    journal=run/'output-diagnostic.jsonl'
    if journal.exists():
        for line in journal.read_text().splitlines(keepends=True):
            if line.endswith('\n'):rows.append(json.loads(line))
    record.update(responses_recorded=len(rows),correct_responses=sum(r['passed'] for r in rows),
                  response_errors=sum('error' in r for r in rows),updated_utc=now())
    record['responses_complete']=len(rows)==record['planned_requests'] and record['response_errors']==0
    save(path,record)
    lines=['# Output transport diagnostic','',f"Updated UTC: {now()}",'',
           f"Job {job}: {record['state']}. Recorded {len(rows)}/{record['planned_requests']} responses; "
           f"{record['correct_responses']} satisfy their expected answers; {record['response_errors']} request errors.",'',
           'The job uses unmodified monolithic TP4/EP1 and TP8/EP8 instances of the same FP8 checkpoint, with no NIXL KV transfer. '
           'It is not a ranked contest P/D benchmark or the organiser accuracy gate.', '',
           'Reason: job 23128 passed the performance gate (1977.08 good tokens/s, 97.14% SLA), '
           'but only 7/8 hand-written output checks. The reverse case returned `.retsulc GNITSOER` '
           'instead of `retsulc`. The original output remains a failure; it has not been normalized into a pass.', '',
           'Identical eight short questions run twice sequentially and twice at concurrency four on each of three endpoints. '
           'Twelve additional long-context retrieval prompts check independent labels on each endpoint. '
           'Actual prompt token counts and all API responses are retained. Differences alone cannot identify NIXL as the cause: '
           'batching and numerical differences must also be considered.', '',
           f'- [Frozen deployment](s2-output-monolithic/config.json)',
           f'- [Recorded job](output-diagnostic-job.json)',
           f'- [CPU validation](output-diagnostic-cpu-validation.json)',
           f'- [Raw responses](../runs/{job}/output-diagnostic.jsonl)',
           f'- [Summary](../runs/{job}/output-diagnostic-summary.json)']
    if record['responses_complete']:
        failed=[r for r in rows if not r['passed']]
        if len(failed)==12 and all(r['name']=='reverse' for r in failed):
            lines+=['','Completed finding: all twelve reverse-string attempts fail even without NIXL, across both TP layouts and both concurrency settings. '
                    'The other 120 responses pass, including all 36 long-context retrieval checks. This shows the observed failure is not exclusive to NIXL; '
                    'it does not prove the patched deployment is correct on all prompts.', '',
                    'Research continuation uses a separate baseline comparison: all eight original cases must be recorded, '
                    'with no transport error or newly failed case versus this independent baseline. '
                    'The original score stays 7/8; this is not the organiser 99% accuracy gate.']
    (ROOT/'serving-tuning-02/OUTPUT_DIAGNOSTIC.md').write_text('\n'.join(lines)+'\n')
    notes[job]={'topology':'Monolithic TP4/EP1 (2 instances) + TP8/EP8 (1 instance); no P/D',
                'purpose':record['scope'],'finding':f"Slurm {record['state']}; {len(rows)} diagnostic responses.",
                'performance_evidence':False,'provenance_note':'Frozen payload: '+record['bundle'],
                'lesson':'Output correctness and performance are separate; preserve failed output checks.'}
    return record['state'] not in TERMINAL

def trace_summary(run):
    directory=run/'diagnostic-profile'
    rows=[]
    for path in sorted(directory.glob('*/*trace.json*')):
        try:
            opener=gzip.open if path.suffix=='.gz' else open
            with opener(path,'rt') as handle:payload=json.load(handle)
            events=[e for e in payload.get('traceEvents',[]) if e.get('ph')=='X'
                    and str(e.get('cat','')).lower()=='kernel' and e.get('dur',0)>0]
            totals={}
            for event in events:
                name=event.get('name','unknown')
                totals[name]=totals.get(name,0)+event['dur']
            summed=sum(totals.values())
            collective=sum(d for n,d in totals.items() if any(s in n.lower() for s in ('nccl','allreduce','all_reduce','allgather','reduce_scatter')))
            moe=sum(d for n,d in totals.items() if any(s in n.lower() for s in ('fused_moe','moe_kernel','grouped_gemm','gemm_grouped','moe_align')))
            rows.append({'trace':str(path.relative_to(ROOT)), 'kernels':len(events),
                         'summed_kernel_us':summed,
                         'collective_fraction_of_summed_kernel_time':collective/summed if summed else None,
                         'moe_fraction_of_summed_kernel_time':moe/summed if summed else None,
                         'top_kernels':[{'name':n,'summed_us':d} for n,d in sorted(totals.items(),key=lambda item:item[1],reverse=True)[:20]]})
        except (OSError,ValueError) as error:
            rows.append({'trace':str(path.relative_to(ROOT)),'read_error':str(error)})
    if rows:
        save(directory/'kernel-summary.json',{'traces':rows,
             'interpretation':'Per-rank summed GPU kernel durations; overlap can double-count wall time. Not a speedup or accuracy measurement.'})
    return rows

def freeze_retry(entry, missing, profile_missing):
    previous=Path(entry['attempts'][-1]['bundle'])
    retry=DIR/(entry['id']+'-retry-'+str(len(entry['attempts'])+1))
    retry.mkdir()
    for source in previous.iterdir():
        if source.is_file() and source.name!='SHA256SUMS':
            shutil.copyfile(source,retry/source.name)
    config=json.loads((retry/'config.json').read_text())
    # Preserve each profiling experiment's matched load on a budget-only retry.
    ns=missing or ([48] if entry['id']=='profile-control' else entry['planned_ns'])
    config.update(concurrency=ns,retry_of=entry['attempts'][-1]['job'],diagnostic_profile=profile_missing)
    save(retry/'config.json',config)
    script=(retry/'job.sbatch').read_text()
    script=script.replace(str(previous),str(retry))
    lines=script.splitlines()
    lines=[('export QWEN_TUNE_NS='+shlex.quote(' '.join(map(str,ns)))) if line.startswith('export QWEN_TUNE_NS=') else line for line in lines]
    lines=[('export QWEN_DIAGNOSTIC_PROFILE='+str(int(profile_missing))) if line.startswith('export QWEN_DIAGNOSTIC_PROFILE=') else line for line in lines]
    (retry/'job.sbatch').write_text('\n'.join(lines)+'\n')
    for name in ('job.sbatch','worker.sh','benchmark.sh','topology-job.sh'):
        command(['bash','-n',str(retry/name)])
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(retry.iterdir())}
    (retry/'SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name,digest in hashes.items()))
    subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=retry,capture_output=True,check=True)
    for p in retry.iterdir():p.chmod(0o444)
    retry.chmod(0o555)
    job=command(['sbatch','--parsable',str(retry/'job.sbatch')]).strip().split(';')[0]
    assert job.isdigit()
    attempt={'job':job,'bundle':str(retry),'state':'SUBMITTED','submitted_utc':now(),'payload_sha256':hashes}
    entry['attempts'].append(attempt)
    print(now(),'BUDGET_RETRY',entry['id'],job,ns,flush=True)

def submit_followup(state, name, source_entry, ns, purpose, role_flags=None, wave=None):
    """One bounded next trial; old payloads are never edited."""
    if any(e['id']==name for e in state['entries']):
        return
    source=Path(source_entry['bundle'])
    bundle=DIR/name
    bundle.mkdir()
    for path in source.iterdir():
        if path.is_file() and path.name!='SHA256SUMS':
            shutil.copyfile(path,bundle/path.name)
    config=json.loads((bundle/'config.json').read_text())
    config.update(experiment=name,concurrency=ns,diagnostic_profile=False,purpose=purpose)
    if wave is not None:config['wave']=wave
    if role_flags:
        role, flags=role_flags
        worker=(bundle/'worker.sh').read_text()
        declaration='extra=()\nif [[ $role == '+role+' ]]; then\n  extra=('+shlex.join(flags)+')\nfi\n'
        assert 'extra=()' not in worker, 'Use the unchanged control payload for a new engine factor'
        worker=worker.replace('exec python3 -m sglang.launch_server',declaration+'exec python3 -m sglang.launch_server')
        worker=worker.replace('"$@" --host','"${extra[@]}" "$@" --host')
        (bundle/'worker.sh').write_text(worker)
        config[role+'_extra_flags']=flags
        if role=='prefill':config['prefill_chunk_size']=4096
    save(bundle/'config.json',config)
    script=(bundle/'job.sbatch').read_text().replace(str(source),str(bundle))
    lines=script.splitlines()
    lines=[('#SBATCH -J ap42-tune-'+name[:12]) if line.startswith('#SBATCH -J ') else line for line in lines]
    lines=[('export QWEN_TUNE_NS='+shlex.quote(' '.join(map(str,ns)))) if line.startswith('export QWEN_TUNE_NS=') else line for line in lines]
    lines=[('export QWEN_DIAGNOSTIC_PROFILE=0') if line.startswith('export QWEN_DIAGNOSTIC_PROFILE=') else line for line in lines]
    (bundle/'job.sbatch').write_text('\n'.join(lines)+'\n')
    for script in ('job.sbatch','worker.sh','topology-job.sh','benchmark.sh'):
        command(['bash','-n',str(bundle/script)])
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.iterdir())}
    (bundle/'SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name,digest in hashes.items()))
    subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
    for p in bundle.iterdir():p.chmod(0o444)
    bundle.chmod(0o555)
    job=command(['sbatch','--parsable',str(bundle/'job.sbatch')]).strip().split(';')[0]
    assert job.isdigit()
    state['entries'].append({'id':name,'bundle':str(bundle),'planned_ns':ns,'purpose':purpose,
        'state':'ACTIVE','attempts':[{'job':job,'bundle':str(bundle),'state':'SUBMITTED','submitted_utc':now()}],
        'payload_sha256':hashes,'measurements':[],'missing_ns':ns,'benchmark_complete':False,
        'profile_complete':None,'traces':[]})
    if wave is not None:state['entries'][-1]['wave']=wave
    save(STATE,state)
    print(now(),'FOLLOWUP_SUBMITTED',name,job,ns,flush=True)

def advance_plan(state):
    """At most four follow-ups, chosen using completed full runs and traces."""
    initial={e['id']:e for e in state['entries'] if e['id'] in ('control-load','dense-decode-graphs','profile-control')}
    if len(initial)!=3 or any(e['state']=='ACTIVE' for e in initial.values()):
        return
    control=initial['control-load']
    controls=[r for key in ('control-load','profile-control') for r in initial[key]['measurements']
              if r['concurrency']==48 and passing(r)]
    if not controls:
        state['advance_note']='No passing new N48 control; do not launch kernel or scheduling changes without a working control.'
        return
    load_points=[r for r in control['measurements'] if passing(r)]
    if load_points:
        best_load=max(load_points,key=lambda r:r['good_output_tokens_s'])
        if best_load['good_output_tokens_s']>1912.2999551030798*1.03:
            submit_followup(state,'load-best-repeat',control,[best_load['concurrency']],
                f"Independent full repeat at N{best_load['concurrency']} after a higher passing goodput in the control load search; confirm stability before promotion.")
    # Historical full-run logs show queued prefill and requests split at 8192.
    submit_followup(state,'prefill-chunk4096',control,[48,52],
       'Prefill chunk 4096 versus original 8192; keep decode, KV, model, NIXL patch and client protocol unchanged.',
       ('prefill',['--chunked-prefill-size','4096']))
    profile=initial['profile-control']
    decode_traces=[t for t in profile['traces'] if '/decode-0/' in t['trace'] and t.get('kernels',0)>0]
    fraction=max((t.get('moe_fraction_of_summed_kernel_time') or 0 for t in decode_traces),default=0)
    if profile['profile_complete'] and fraction>=.20:
        submit_followup(state,'decode-deepgemm',control,[48,52],
            f'Decode DeepGEMM MoE runner versus original auto/Triton; profile MoE kernel fraction up to {fraction:.1%}. Separate quality validation required before promotion.',
            ('decode',['--moe-runner-backend','deep_gemm']))
    else:
        state['moe_trial_note']='DeepGEMM not queued: require all P/D traces and >=20% identified MoE kernel time on decode.'
    dense=[r for r in initial['dense-decode-graphs']['measurements'] if r['concurrency']==48 and passing(r)]
    mean=sum(r['good_output_tokens_s'] for r in controls)/len(controls)
    if dense and max(r['good_output_tokens_s'] for r in dense)>mean*1.03:
        submit_followup(state,'dense-graphs-repeat',initial['dense-decode-graphs'],[48],
            'Independent repeat of dense decode graphs after a >3% N48 gain over new controls; no automatic submission promotion.')

def advance_second_wave(state):
    plan_path=ROOT/'serving-tuning-02/backend-pilots.json'
    if not plan_path.exists():
        return False
    plan=json.loads(plan_path.read_text())
    active=account_active_jobs(state)
    for pilot in plan['pilots']:
        existing=next((e for e in state['entries'] if e['id']==pilot['id']),None)
        if existing:
            pilot['state']=existing['state']
            pilot['job']=existing['attempts'][-1]['job']
            continue
        parent=next((e for e in state['entries'] if e['id']==pilot['matched_control']),None)
        if parent is None:
            planned_parent=next((p for p in plan['pilots'] if p['id']==pilot['matched_control']),None)
            if planned_parent and planned_parent['state'].startswith('SKIPPED'):
                pilot['state']='SKIPPED_PARENT_NOT_VALIDATED'
                pilot['reason']='The matched backend control was not eligible to run.'
            continue
        if parent['state']=='ACTIVE':
            pilot['state']='WAITING_MATCHED_CONTROL'
            pilot['reason']='Waiting for the matched full measurement and output checks.'
            continue
        metrics=research_measurements(parent)
        if not metrics:
            pilot['state']='SKIPPED_PARENT_NOT_VALIDATED'
            pilot['reason']='Matched parent lacks a passing full N52 run with output research eligibility on the same attempt.'
            continue
        pilot['state']='PLANNED'
        pilot['reason']='Matched parent is eligible for research; organiser accuracy remains unverified.'
        pilot['control_evidence_jobs']=[r['job'] for r in metrics]
        if active>=plan['max_active_jobs']:
            continue
        bundle=Path(pilot['bundle'])
        subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
        job=command(['sbatch','--parsable',str(bundle/'job.sbatch')]).strip().split(';')[0]
        assert job.isdigit()
        state['entries'].append({**pilot,'state':'ACTIVE','attempts':[{'job':job,'bundle':str(bundle),
              'state':'SUBMITTED','submitted_utc':now()}],'measurements':[],'missing_ns':[52],
              'benchmark_complete':False,'profile_complete':None,'traces':[]})
        save(STATE,state)
        pilot['state']='SUBMITTED';pilot['job']=job;active+=1
        save(plan_path,plan)
        print(now(),'BACKEND_PILOT_SUBMITTED',pilot['id'],job,flush=True)
    save(plan_path,plan)
    initial_ids={'s2-control-n52','s2-chunk4096-n52','s2-chunk4096-dense-n52','s2-chunk16384-n52'}
    initial=[e for e in state['entries'] if e['id'] in initial_ids]
    if len(initial)==4 and all(e['state']!='ACTIVE' for e in initial):
        ranked=[]
        for e in initial:
            rows=research_measurements(e)
            if rows:
                ranked.append((max(r['good_output_tokens_s'] for r in rows),e))
        ranked.sort(key=lambda pair:pair[0],reverse=True)
        for rank,(rate,entry) in enumerate(ranked[:2]):
            name='s2-repeat-best' if rank==0 else 's2-repeat-runner'
            if any(e['id']==name for e in state['entries']):continue
            if active>=plan['max_active_jobs']:break
            submit_followup(state,name,entry,[52],
               f"Independent standalone N52 repeat of {entry['id']} after {rate:.2f} good tokens/s; candidate ranking remains provisional.")
            state['entries'][-1]['wave']=2
            state['entries'][-1]['repeat_of_experiment']=entry['id']
            save(STATE,state);active+=1
    pending=any(p['state']=='PLANNED' for p in plan['pilots'])
    repeat_pending=len(initial)==4 and all(e['state']!='ACTIVE' for e in initial) and bool(ranked) and any(
        not any(e['id']==name for e in state['entries'])
        for name in ('s2-repeat-best','s2-repeat-runner')[:min(2,len(ranked))])
    state['backend_pilot_plan']=[{'id':p['id'],'state':p['state'],'job':p.get('job'),
                                 'matched_control':p['matched_control']} for p in plan['pilots']]
    return pending or repeat_pending

def advance_load_refinement(state, wave=3):
    path=ROOT/f'serving-tuning-{wave:02d}/load-plan.json'
    if not path.exists():return False
    plan=json.loads(path.read_text());active=account_active_jobs(state)
    entries={e['id']:e for e in state['entries']}
    source=entries.get(plan['source_experiment'])
    if not source or not research_measurements(source):
        plan['state']='BLOCKED_SOURCE_NOT_VALIDATED';save(path,plan);return False

    def launch(step):
        nonlocal active
        if active>=plan['max_active_jobs']:
            step['state']='PLANNED';return
        submit_followup(state,step['id'],source,[step['n']],step['purpose'],wave=wave)
        entry=state['entries'][-1];entries[entry['id']]=entry
        step.update(state='SUBMITTED',job=entry['attempts'][-1]['job'])
        active+=1;save(path,plan)

    for step in plan['steps']:
        existing=entries.get(step['id'])
        if existing:
            step.update(state=existing['state'],job=existing['attempts'][-1]['job']);continue
        parent=entries.get(step['parent'])
        if not parent:
            planned=next((s for s in plan['steps'] if s['id']==step['parent']),None)
            step['state']='SKIPPED_PARENT_NOT_VALIDATED' if planned and planned['state'].startswith('SKIPPED') else 'WAITING_PARENT'
            continue
        if parent['state']=='ACTIVE':step['state']='WAITING_PARENT';continue
        if not research_measurements(parent,concurrency=None):
            step.update(state='SKIPPED_PARENT_NOT_VALIDATED',reason='Parent has no full passing measurement with output research eligibility.');continue
        launch(step)

    coarse_done=all(s['state'] not in ('ACTIVE','SUBMITTED','PLANNED','WAITING_PARENT') for s in plan['steps'])
    if coarse_done:
        coarse=[entries[s['id']] for s in plan['steps'] if s['id'] in entries]
        accepted=[r for e in coarse for r in research_measurements(e,None)]
        recorded=[r for e in coarse for r in e.get('measurements',[]) if valid_measurement(r)]
        refinement=plan['refinement']
        if refinement['state']=='UNDECIDED':
            failed=sorted((r for r in recorded if not passing(r)),key=lambda r:r['concurrency'])
            lower=[];upper=None
            if failed:
                upper=failed[0]
                if upper.get('errors')==0:
                    lower=[r for r in accepted if r['concurrency']<upper['concurrency']]
            elif accepted:
                upper=max(accepted,key=lambda r:r['concurrency'])
                lower=[r for r in accepted if r['concurrency']<upper['concurrency'] and r['good_output_tokens_s']>upper['good_output_tokens_s']]
            if lower and upper:
                low=max(lower,key=lambda r:r['concurrency']);n=(low['concurrency']+upper['concurrency'])//2
                if low['concurrency']<n<upper['concurrency']:
                    label=plan.get('configuration_label','BF16 chunk4096/dense-graph')
                    refinement.update(n=n,state='PLANNED',purpose=f"Independent N{n} midpoint between N{low['concurrency']} and N{upper['concurrency']}; same {label} serving config.")
                else:refinement['state']='SKIPPED_NO_INTERIOR_INTEGER'
            else:refinement['state']='SKIPPED_NO_BRACKET'
        current=entries.get(refinement['id'])
        if current:refinement.update(state=current['state'],job=current['attempts'][-1]['job'])
        elif refinement['state']=='PLANNED':launch(refinement)
        if refinement['state'] not in ('ACTIVE','SUBMITTED','PLANNED','UNDECIDED'):
            if current:accepted.extend(research_measurements(current,None))
            repeat=plan['repeat'];current_repeat=entries.get(repeat['id'])
            if current_repeat:repeat.update(state=current_repeat['state'],job=current_repeat['attempts'][-1]['job'])
            elif repeat['state']=='UNDECIDED':
                best=max(accepted,key=lambda r:r['good_output_tokens_s']) if accepted else None
                if best and (plan.get('repeat_always') or best['good_output_tokens_s']>=plan['reference_good_tokens_s']*(1+plan['repeat_min_gain_fraction'])):
                    repeat.update(n=best['concurrency'],state='PLANNED',purpose=f"Independent confirmation at N{best['concurrency']} after {best['good_output_tokens_s']:.2f} good tokens/s in load refinement; no automatic submission promotion.")
                else:repeat['state']='SKIPPED_GAIN_BELOW_THRESHOLD'
            if repeat['state']=='PLANNED':launch(repeat)
    pending=any(s['state'] in ('PLANNED','WAITING_PARENT','UNDECIDED','ACTIVE','SUBMITTED')
                for s in [*plan['steps'],plan['refinement'],plan['repeat']])
    plan.update(state='ACTIVE' if pending else 'FINISHED',updated_utc=now());save(path,plan)
    state['load_refinement_plan' if wave==3 else f'wave_{wave}_load_plan']=[{k:s[k] for k in ('id','state','n','job') if k in s}
                                   for s in [*plan['steps'],plan['refinement'],plan['repeat']]]
    return pending

def advance_prefill_pilots(state, wave=4):
    filename='prefill-pilots.json' if wave==4 else 'prepared-pilots.json'
    path=ROOT/f'serving-tuning-{wave:02d}'/filename
    if not path.exists():return False
    plan=json.loads(path.read_text());validation=path.with_name('cpu-validation.json')
    if not validation.exists() or not json.loads(validation.read_text()).get('passed'):
        plan['state']='BLOCKED_CPU_VALIDATION';save(path,plan);return False
    source=next((e for e in state['entries'] if e['id']==plan['source_experiment']),None)
    if source is None or not research_measurements(source):
        plan['state']='BLOCKED_SOURCE_NOT_VALIDATED';save(path,plan);return False
    active=account_active_jobs(state)
    for pilot in plan['pilots']:
        existing=next((e for e in state['entries'] if e['id']==pilot['id']),None)
        if existing:
            pilot.update(state=existing['state'],job=existing['attempts'][-1]['job']);continue
        if active>=plan['max_active_jobs']:continue
        bundle=Path(pilot['bundle'])
        subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
        job=command(['sbatch','--parsable',str(bundle/'job.sbatch')]).strip().split(';')[0]
        assert job.isdigit()
        entry={**pilot,'state':'ACTIVE','attempts':[dict(job=job,bundle=str(bundle),state='SUBMITTED',submitted_utc=now())]}
        state['entries'].append(entry);save(STATE,state)
        pilot.update(state='SUBMITTED',job=job);active+=1;save(path,plan)
        print(now(),'PREPARED_PILOT_SUBMITTED' if wave!=4 else 'PREFILL_PILOT_SUBMITTED',pilot['id'],job,flush=True)
    pending=any(p['state'] in ('PLANNED','SUBMITTED','ACTIVE') for p in plan['pilots'])
    plan.update(state='ACTIVE' if pending else 'FINISHED',updated_utc=now());save(path,plan)
    state['prefill_pilot_plan' if wave==4 else f'wave_{wave}_prepared_plan']=[dict(id=p['id'],state=p['state'],job=p.get('job')) for p in plan['pilots']]
    return pending

def complete_profile_attempt(entry,traces):
    expected=entry.get('expected_profile_ranks') or {'prefill-0':1,'prefill-1':1,'decode-0':1}
    # Never combine partial rank coverage from separate deployments into a pass.
    return any(all(sum(t.get('kernels',0)>0 and t['trace'].startswith('runs/'+a['job']+'/diagnostic-profile/'+role+'/')
                       for t in traces)>=count for role,count in expected.items()) for a in entry['attempts'])

def advance_backend_followups(state, wave=6):
    path=ROOT/f'serving-tuning-{wave:02d}'/'followup-plan.json'
    if not path.exists():return False
    plan=json.loads(path.read_text());entries={e['id']:e for e in state['entries']}
    control=entries.get(plan['matched_control'])
    if control is None or control['state']=='ACTIVE':return True
    controls=research_measurements(control)
    if not controls:
        plan.update(state='BLOCKED_CONTROL_NOT_VALIDATED',updated_utc=now());save(path,plan);return False
    reference=max(plan['reference_good_tokens_s'],max(r['good_output_tokens_s'] for r in controls))
    floor=reference*(1+plan['min_gain_fraction']);active=account_active_jobs(state)

    def queue(step,source,n):
        nonlocal active
        if active>=plan['max_active_jobs']:
            step['state']='PLANNED';return
        submit_followup(state,step['id'],source,[n],step['purpose'],wave=wave)
        e=state['entries'][-1];entries[e['id']]=e
        step.update(state='SUBMITTED',job=e['attempts'][-1]['job'],n=n)
        active+=1;save(path,plan)

    for candidate in plan['candidates']:
        source=entries.get(candidate['source_experiment']);repeat=candidate['repeat'];higher=candidate['higher_load']
        if source is None or source['state']=='ACTIVE':continue
        existing=entries.get(repeat['id']);rows=research_measurements(source)
        if existing:
            repeat.update(state=existing['state'],job=existing['attempts'][-1]['job'])
        elif rows and max(r['good_output_tokens_s'] for r in rows)>=floor:
            queue(repeat,source,52)
        else:
            repeat.update(state='SKIPPED_NO_VALIDATED_GAIN',reason='Need a full passing N52 point with output research eligibility and at least 2% gain over both controls.')
        existing=entries.get(repeat['id'])
        if existing is None:
            if repeat['state'].startswith('SKIPPED'):higher['state']='SKIPPED_NO_REPEAT'
            continue
        if existing['state']=='ACTIVE':continue
        existing_higher=entries.get(higher['id'])
        if existing_higher:
            higher.update(state=existing_higher['state'],job=existing_higher['attempts'][-1]['job']);continue
        repeated=research_measurements(existing)
        good=[r for r in repeated if r['good_output_tokens_s']>=floor and r['good_request_fraction']>=plan['higher_min_sla']
              and r['itl_avg_ms']<=plan['higher_max_itl_ms']]
        if good:queue(higher,source,54)
        else:higher['state']='SKIPPED_REPEAT_OR_ITL_MARGIN'
    pending=any(s['state'] in ('UNDECIDED','PLANNED','SUBMITTED','ACTIVE')
                for c in plan['candidates'] for s in (c['repeat'],c['higher_load']))
    plan.update(state='ACTIVE' if pending else 'FINISHED',updated_utc=now(),comparison_floor_good_tokens_s=floor)
    save(path,plan)
    state['backend_followup_plan' if wave==6 else f'wave_{wave}_backend_followup_plan']=[dict(id=s['id'],state=s['state'],job=s.get('job'))
                                   for c in plan['candidates'] for s in (c['repeat'],c['higher_load'])]
    return pending

def refresh(allow_retry=False):
    state=json.loads(STATE.read_text())
    attempts=[a for e in state['entries'] for a in e['attempts']]
    ids=[a['job'] for a in attempts]
    diagnostic_path=ROOT/'serving-tuning-02/output-diagnostic-job.json'
    if diagnostic_path.exists():ids.append(json.loads(diagnostic_path.read_text())['job'])
    output=command(['sacct','-X','-j',','.join(ids),'-P','--format=JobID,State%30,ExitCode,Elapsed,Start,End'])
    statuses={r['JobID']:r for r in csv.DictReader(output.splitlines(),delimiter='|')}
    all_status=json.loads((ROOT/'job-status.json').read_text());all_status.update(statuses);save(ROOT/'job-status.json',all_status)
    notes=json.loads((ROOT/'run-notes.json').read_text())
    diagnostic_active=refresh_output_diagnostic(statuses,notes)
    new_rows=[]
    for entry in state['entries']:
        measured=[];active=False;traces=[];stopped=False
        for attempt in entry['attempts']:
            job=attempt['job'];run=ROOT/'runs'/job
            attempt['status']=statuses.get(job,{})
            attempt['state']=attempt['status'].get('State','SUBMITTED').split()[0].rstrip('+')
            active=active or attempt['state'] not in TERMINAL
            rows=[]
            if run.is_dir():
                rows=json.loads(command(['python3',str(ROOT/'summarize.py'),str(run)]))
                save(run/'summary.json',rows)
                if (run/'output-smoke.json').exists():
                    smoke=json.loads((run/'output-smoke.json').read_text())
                    attempt['output_smoke']={'passed':smoke['passed'],'total':smoke['total']}
                    comparison=compare_output_baseline(smoke,ROOT/'runs/23146/output-diagnostic.jsonl')
                    attempt['output_baseline_comparison']=comparison
                    save(run/'output-baseline-comparison.json',comparison)
                if attempt['state'] in TERMINAL:traces.extend(trace_summary(run))
                stopped=stopped or (run/'stop-increase-n.txt').exists()
            attempt['measurements']=rows
            measured.extend({'job':job,'experiment':entry['id'],'topology':'P8-TP4_D8-TP8-EP8',
                             'output_smoke':attempt.get('output_smoke'),
                             'output_baseline_comparison':attempt.get('output_baseline_comparison'),**r} for r in rows)
            notes[job]={'topology':'P8-TP4_D8-TP8-EP8','purpose':entry['purpose'],
                'finding':f"Slurm {attempt['state']}; {len(rows)} canonical exports. Failed deployment is not a benchmark result.",
                'lesson':'Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.',
                'performance_evidence':bool(rows),'provenance_note':'Frozen payload before submission: '+attempt['bundle']}
        done_ns={r['concurrency'] for r in measured if valid_measurement(r)}
        # A measured failing N is data; higher N is intentionally not attempted.
        failed_ns={r['concurrency'] for r in measured if valid_measurement(r) and not passing(r)}
        limit=min(failed_ns) if failed_ns else None
        wanted=[n for n in entry['planned_ns'] if limit is None or n<=limit]
        missing=sorted(set(wanted)-done_ns)
        wants_profile=entry['id']=='profile-control' or entry.get('diagnostic_profile',False)
        profile_done=complete_profile_attempt(entry,traces)
        profile_missing=wants_profile and not profile_done
        entry.update(measurements=measured,missing_ns=missing,stopped_load_increase=stopped,
                     higher_ns_skipped_after_failed_gate=[n for n in entry['planned_ns'] if limit is not None and n>limit],
                     traces=traces,profile_complete=profile_done if wants_profile else None)
        latest=entry['attempts'][-1]
        last_run=ROOT/'runs'/latest['job']
        budget_deferred=(last_run/'deferred-ns.txt').exists() or (last_run/'diagnostic-profile-deferred.txt').exists()
        if allow_retry and not active and (missing or profile_missing) and budget_deferred and len(entry['attempts'])<3:
            freeze_retry(entry,missing,profile_missing)
            active=True
            # Persist immediately after sbatch; later reporting must not lose the ID.
            save(STATE,state)
        entry['state']='ACTIVE' if active else 'MEASURED' if not missing and not profile_missing else 'INCOMPLETE'
        entry['benchmark_complete']=not missing
        new_rows.extend(measured)
    pending_plan=False
    if allow_retry:
        advance_plan(state)
        pending_plan=advance_second_wave(state)
        pending_plan=advance_load_refinement(state) or pending_plan
        pending_plan=advance_prefill_pilots(state) or pending_plan
        pending_plan=advance_load_refinement(state,wave=5) or pending_plan
        pending_plan=advance_prefill_pilots(state,wave=6) or pending_plan
        pending_plan=advance_backend_followups(state) or pending_plan
        pending_plan=advance_prefill_pilots(state,wave=7) or pending_plan
        pending_plan=advance_backend_followups(state,wave=7) or pending_plan
        pending_plan=advance_prefill_pilots(state,wave=8) or pending_plan
        pending_plan=advance_backend_followups(state,wave=8) or pending_plan
        pending_plan=advance_prefill_pilots(state,wave=9) or pending_plan
        pending_plan=advance_prefill_pilots(state,wave=10) or pending_plan
    state['updated_utc']=now()
    state['benchmark_complete']=all(e['benchmark_complete'] for e in state['entries'])
    state['profile_complete']=all(e['profile_complete'] for e in state['entries'] if e['id']=='profile-control' or e.get('diagnostic_profile'))
    state['active']=any(e['state']=='ACTIVE' for e in state['entries']) or pending_plan or diagnostic_active
    save(STATE,state);save(ROOT/'run-notes.json',notes)
    old=json.loads((ROOT/'comparison.json').read_text())
    new_ids={a['job'] for e in state['entries'] for a in e['attempts']}
    combined=[r for r in old if r['job'] not in new_ids]+new_rows
    save(ROOT/'comparison.json',combined)
    lines=['# Qwen serving tuning — next wave','',f"Updated UTC: {now()}",'',
        'Control: measured job 22415, TP4 prefill → TP8/EP8 decode, BF16 KV, request-scoped NIXL patch.',
        'Every ranked point uses 60 s warmup, 120 s measurement, 30 s grace. Profiling traffic is separate.',
        'Full results are required; FAILED/TIMEOUT without an export is never a completed benchmark.','',
        '| Experiment | Jobs / states | Missing N | Status |', '|---|---|---|---|']
    for e in state['entries']:
        jobs=', '.join(f"{a['job']}:{a['state']}" for a in e['attempts'])
        lines.append(f"| {e['id']} | {jobs} | {e['missing_ns']} | {e['state']} |")
    lines+=['','| Job | Experiment | N | Good tokens/s | SLA | TTFT mean ms | ITL mean ms | Errors | Cancelled | Gate |',
             '|---|---|---:|---:|---:|---:|---:|---:|---:|---|']
    def fmt(value):return f'{value:.2f}' if value is not None else '—'
    for r in new_rows:
        fraction=r.get('good_request_fraction')
        lines.append(f"| {r['job']} | {r['experiment']} | {r['concurrency']} | {fmt(r['good_output_tokens_s'])} | {fmt(fraction*100 if fraction is not None else None)}% | {fmt(r['ttft_avg_ms'])} | {fmt(r['itl_avg_ms'])} | {r['errors']} | {r['cancelled_requests']} | {'PASS' if passing(r) else 'FAIL / incomplete'} |")
    if state.get('backend_pilot_plan'):
        lines+=['','## Backend pilots','',
                '| Pilot | Matched control | State | Job |','|---|---|---|---|']
        for p in state['backend_pilot_plan']:
            lines.append(f"| {p['id']} | {p['matched_control']} | {p['state']} | {p.get('job') or '—'} |")
    if state.get('load_refinement_plan'):
        lines+=['','## Load refinement','', '| Trial | N | State | Job |','|---|---:|---|---|']
        for p in state['load_refinement_plan']:
            lines.append(f"| {p['id']} | {p.get('n','—')} | {p['state']} | {p.get('job') or '—'} |")
    if state.get('prefill_pilot_plan'):
        lines+=['','## Prefill routing/admission pilots','', '| Trial | State | Job |','|---|---|---|']
        for p in state['prefill_pilot_plan']:
            lines.append(f"| {p['id']} | {p['state']} | {p.get('job') or '—'} |")
        lines.append('\n[Research and measured TTFT failure analysis](serving-tuning-04/RESEARCH.md). Same N52 benchmark, one prefill factor per pilot.')
    if state.get('wave_5_load_plan'):
        lines+=['','## Round-robin confirmation and load refinement','', '| Trial | N | State | Job |','|---|---:|---|---|']
        for p in state['wave_5_load_plan']:
            lines.append(f"| {p['id']} | {p.get('n','—')} | {p['state']} | {p.get('job') or '—'} |")
    if state.get('wave_6_prepared_plan'):
        lines+=['','## Round-robin backend/profile experiments','', '| Trial | State | Job |','|---|---|---|']
        for p in state['wave_6_prepared_plan']:
            lines.append(f"| {p['id']} | {p['state']} | {p.get('job') or '—'} |")
    if state.get('backend_followup_plan'):
        lines+=['','## Backend follow-ups','', '| Trial | State | Job |','|---|---|---|']
        for p in state['backend_followup_plan']:
            lines.append(f"| {p['id']} | {p['state']} | {p.get('job') or '—'} |")
    for key,title in [('wave_10_prepared_plan','MNNVL + FlashInfer replication'),
                      ('wave_9_prepared_plan','MNNVL interaction pilots'),
                      ('wave_8_prepared_plan','DP-attention architecture pilot'),
                      ('wave_8_backend_followup_plan','DP-attention architecture follow-ups'),
                      ('wave_7_prepared_plan','Profile-guided decode kernels'),
                      ('wave_7_backend_followup_plan','Profile-guided kernel follow-ups')]:
        if state.get(key):
            lines+=['',f'## {title}','', '| Trial | State | Job |','|---|---|---|']
            for p in state[key]:
                lines.append(f"| {p['id']} | {p['state']} | {p.get('job') or '—'} |")
    controls=[r for r in new_rows if r['experiment'] in ('control-load','profile-control') and r['concurrency']==48 and passing(r)]
    candidates=[r for r in new_rows if r['experiment']=='dense-decode-graphs' and r['concurrency']==48 and passing(r)]
    lines+=['','## Interpretation','']
    if controls and candidates:
        mean=sum(r['good_output_tokens_s'] for r in controls)/len(controls)
        for candidate in candidates:
            speedup=(candidate['good_output_tokens_s']/mean-1)*100
            lines.append(f"Dense graph N48 versus mean of {len(controls)} new N48 controls: {speedup:+.2f}%. One candidate run remains provisional; repeated confirmation is needed before promotion.")
    else:lines.append('No new measured speedup yet. Keep the existing submission configuration.')
    load_points=[r for r in new_rows if r['experiment']=='control-load' and passing(r)]
    if load_points:
        best_load=max(load_points,key=lambda r:r['good_output_tokens_s'])
        speedup=(best_load['good_output_tokens_s']/1912.2999551030798-1)*100
        lines.append(f"Highest new load point: N{best_load['concurrency']}, {best_load['good_output_tokens_s']:.2f} good tokens/s, {best_load['good_request_fraction']:.2%} SLA ({speedup:+.2f}% versus job 22415). Provisional until independently repeated; the submission is unchanged.")
    all_passing=[r for r in new_rows if passing(r)]
    if all_passing:
        best=max(all_passing,key=lambda r:r['good_output_tokens_s'])
        lines.append(f"Highest single full measurement: {best['experiment']} / job {best['job']} / N{best['concurrency']}: {best['good_output_tokens_s']:.2f} good tokens/s, {best['good_request_fraction']:.2%} SLA. Backend/FP8 quality remains unverified; the largest single run is not automatically the final configuration.")
    repeated=[r for r in new_rows if r['experiment'] in ('s2-chunk4096-dense-n52','s2-repeat-best') and passing(r)]
    if len(repeated)==2:
        rates=[r['good_output_tokens_s'] for r in repeated];mean=sum(rates)/2
        lines.append(f"Repeated BF16 chunk4096/dense-graph candidate at N52: {mean:.2f} mean good tokens/s across jobs "
                     f"{', '.join(r['job'] for r in repeated)} (range {min(rates):.2f}–{max(rates):.2f}). "
                     'Two deployments agree closely; this does not establish accuracy or variability under all cluster conditions.')
    rr=[r for r in new_rows if r['experiment']=='s4-prefill-roundrobin-n52' and passing(r)]
    if rr:
        r=rr[0]
        lines.append(f"Round-robin prefill pilot / job {r['job']}: {r['good_output_tokens_s']:.2f} good tokens/s, "
                     f"{r['good_request_fraction']:.2%} SLA, mean TTFT {r['ttft_avg_ms']:.2f}ms and ITL {r['itl_avg_ms']:.2f}ms. "
                     'ITL is close to its20ms limit; independent confirmation and a lower-load comparison are required before selection.')
    standalone=[r for r in new_rows if r['experiment'].startswith(('s2-','s3-','s4-','s5-')) and passing(r)]
    if standalone:
        lines+=['','Standalone measurements above begin directly at their listed concurrency; they do not run a lower-load benchmark first.']
        for r in standalone:
            if r.get('output_smoke'):
                smoke=r['output_smoke']
                lines.append(f"Job {r['job']} output sanity: {smoke['passed']}/{smoke['total']}. These eight cases are not the organiser accuracy gate.")
                if r.get('output_baseline_comparison',{}).get('research_eligible'):
                    lines.append('No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.')
    lines+=['','## Traces','']
    for e in state['entries']:
        if e.get('traces'):
            lines.append(f"{e['id']}: {len(e['traces'])} trace files; kernel summaries are beside the traces. Summed GPU time is not wall-time speedup.")
    followups=('Wave 2: four standalone N52 configurations, up to three backend pilots gated by matched controls and complete output checks (8/8 or no new failures against the independently measured baseline), '
               'then two independent scheduling repeats. The independent output diagnostic is included in the four-job account cap.'
               if any(e.get('wave')==2 for e in state['entries']) else
               'Bounded automatic follow-ups: independent load repeat; chunk 4096; DeepGEMM after profiling; dense-graph repeat after >3% N48 gain.')
    if state.get('load_refinement_plan'):
        followups='Wave 3: fresh N52 control and N54 on the twice-measured BF16 chunk4096/dense-graph configuration; advance to N56 and N60 only after their preceding load passes. Optional midpoint and winner repeat, at most six deployments. See [load plan](serving-tuning-03/PLAN.md).'
    if state.get('wave_5_load_plan'):
        followups='Wave5: independently repeat round-robin N52 and compare N50 for ITL headroom; N54 only after the N52 repeat passes. Optional midpoint and best-new-point repeat, at most five deployments. See [round-robin plan](serving-tuning-05/PLAN.md).'
    lines+=['','## Next steps','',*[f'- {axis}.' for axis in state['next_axes']],
            '', followups,
            '', 'Accuracy against the organiser reference remains unverified. No official score is claimed.']
    if diagnostic_path.exists():
        record=json.loads(diagnostic_path.read_text())
        lines+=['',f"Output diagnostic job {record['job']}: {record['state']}; "
                f"{record['responses_recorded']}/{record['planned_requests']} responses recorded. "
                '[Status and purpose](serving-tuning-02/OUTPUT_DIAGNOSTIC.md). Not a ranked benchmark.']
    (ROOT/'SERVING_TUNING_RESULTS.md').write_text('\n'.join(lines)+'\n')
    command(['python3',str(ROOT/'audit-runs.py')])
    return state

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');args=parser.parse_args()
    with (DIR/'watcher.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if not args.run:
            result=refresh();print(json.dumps({'active':result['active'],'benchmark_complete':result['benchmark_complete']}))
        else:
            while True:
                try:
                    result=refresh(allow_retry=True)
                    if not result['active']:
                        print(now(),'WAVE_FINISHED',result['benchmark_complete'],result['profile_complete'],flush=True)
                        break
                except Exception as error:
                    print(now(),'WATCH_ERROR',repr(error),flush=True)
                time.sleep(45)
