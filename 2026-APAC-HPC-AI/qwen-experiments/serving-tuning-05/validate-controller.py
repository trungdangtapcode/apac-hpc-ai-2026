"""Validate round-robin confirmation and load bracketing without a real sbatch."""
import copy
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rr_watcher',ROOT/'watch-serving-tuning.py')
watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
original=json.loads((ROOT/'serving-tuning-05/load-plan.json').read_text())
for step in original['steps']:step.update(state='PLANNED');step.pop('job',None)
original['refinement']={'id':'s5-rr-midpoint','state':'UNDECIDED'}
original['repeat']={'id':'s5-rr-best-repeat','state':'UNDECIDED'}
calls=[];external=[0]
watch.account_active_jobs=lambda state:max(external[0],sum(e['state']=='ACTIVE' for e in state['entries']))

def measured(name,n,rate,sla=True):
    row=dict(concurrency=n,requests=100,errors=0,cancelled_requests=0,good_output_tokens_s=rate,sla_pass=sla)
    return dict(id=name,state='MEASURED',planned_ns=[n],measurements=[row],attempts=[dict(job='96000',state='COMPLETED',
                measurements=[row],output_smoke=dict(passed=7,total=8),output_baseline_comparison=dict(research_eligible=True))])

def fake_submit(state,name,source,ns,purpose,**kwargs):
    assert kwargs['wave']==5 and source['id']=='s4-prefill-roundrobin-n52' and len(ns)==1
    calls.append((name,ns[0]));state['entries'].append(dict(id=name,state='ACTIVE',planned_ns=ns,measurements=[],
        attempts=[dict(job=str(97000+len(calls)),state='SUBMITTED',measurements=[])]))
watch.submit_followup=fake_submit

def finish(state,name,rate,sla=True):
    index=next(i for i,e in enumerate(state['entries']) if e['id']==name)
    old=state['entries'][index];new=measured(name,old['planned_ns'][0],rate,sla)
    new['attempts'][0]['job']=old['attempts'][0]['job'];state['entries'][index]=new

with tempfile.TemporaryDirectory(prefix='apac42-roundrobin-load-') as temp:
    directory=Path(temp);(directory/'serving-tuning-05').mkdir();path=directory/'serving-tuning-05/load-plan.json';watch.ROOT=directory
    def fresh():
        calls.clear();external[0]=0;path.write_text(json.dumps(copy.deepcopy(original)))
        return dict(entries=[measured('s4-prefill-roundrobin-n52',52,2402.64)])
    state=fresh();watch.advance_load_refinement(state,wave=5)
    assert calls==[('s5-rr-repeat-n52',52),('s5-rr-n50',50)]
    finish(state,'s5-rr-repeat-n52',2401);finish(state,'s5-rr-n50',2380)
    watch.advance_load_refinement(state,wave=5);assert calls[-1]==('s5-rr-n54',54)
    finish(state,'s5-rr-n54',1800,False);watch.advance_load_refinement(state,wave=5)
    assert calls[-1]==('s5-rr-midpoint',53)
    finish(state,'s5-rr-midpoint',2430);watch.advance_load_refinement(state,wave=5)
    assert calls[-1]==('s5-rr-best-repeat',53)
    finish(state,'s5-rr-best-repeat',2429);assert not watch.advance_load_refinement(state,wave=5)
    watch.advance_load_refinement(state,wave=5);assert len(calls)==5
    assert 'wave_5_load_plan' in state and 'load_refinement_plan' not in state

    state=fresh();watch.advance_load_refinement(state,wave=5)
    finish(state,'s5-rr-repeat-n52',1800,False);finish(state,'s5-rr-n50',2350)
    watch.advance_load_refinement(state,wave=5)
    assert ('s5-rr-n54',54) not in calls and calls[-1]==('s5-rr-midpoint',51)
    finish(state,'s5-rr-midpoint',2390);watch.advance_load_refinement(state,wave=5)
    assert calls[-1]==('s5-rr-best-repeat',51), 'Repeat still required if the original peak does not reproduce'

    state=fresh();external[0]=4;assert watch.advance_load_refinement(state,wave=5) and not calls

report=dict(passed=True,actual_sbatch_calls=0,repeat_n52_before_n54=True,lower_n50_independent=True,
            failed_n54_refines_n53=True,failed_n52_refines_n51=True,
            best_repeat_even_below_original_peak=True,queue_cap_enforced=True,
            distinct_wave_state=True,no_duplicates=True,at_most_five_jobs=True)
(ROOT/'serving-tuning-05/controller-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
