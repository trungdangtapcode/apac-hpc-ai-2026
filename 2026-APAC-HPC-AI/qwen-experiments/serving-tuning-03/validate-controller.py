"""Exercise staged load increases, failed-gate refinement and queue limits without sbatch."""
import copy
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('load_watcher',ROOT/'watch-serving-tuning.py')
watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
original=json.loads((ROOT/'serving-tuning-03/load-plan.json').read_text())
for step in original['steps']:
    step['state']='PLANNED';step.pop('job',None)
original['refinement']={'id':'s3-midpoint','state':'UNDECIDED'}
original['repeat']={'id':'s3-best-load-repeat','state':'UNDECIDED'}
submitted=[];external=[0]
watch.account_active_jobs=lambda state:max(external[0],sum(e['state']=='ACTIVE' for e in state['entries']))

def metric(n,rate=2100,sla=True,errors=0):
    return dict(concurrency=n,requests=100,errors=errors,cancelled_requests=0,
                good_output_tokens_s=rate,sla_pass=sla)

def entry(name,n,rate=2100):
    row=metric(n,rate)
    return dict(id=name,state='MEASURED',planned_ns=[n],measurements=[row],attempts=[dict(job='88000',state='COMPLETED',
                measurements=[row],output_smoke=dict(passed=7,total=8),output_baseline_comparison=dict(research_eligible=True,accuracy_verified=False))])

def fake_submit(state,name,source,ns,purpose,**kwargs):
    assert len(ns)==1 and kwargs['wave']==3
    assert source['id']=='s2-repeat-best'
    submitted.append((name,ns[0]))
    state['entries'].append(dict(id=name,state='ACTIVE',planned_ns=ns,measurements=[],attempts=[dict(job=str(89000+len(submitted)),state='SUBMITTED',measurements=[])]))
watch.submit_followup=fake_submit

def finish(state,name,rate,sla=True,errors=0):
    e=next(e for e in state['entries'] if e['id']==name)
    row=metric(e['planned_ns'][0],rate,sla,errors);e.update(state='MEASURED',measurements=[row])
    e['attempts'][0].update(state='COMPLETED',measurements=[row],output_smoke=dict(passed=7,total=8),output_baseline_comparison=dict(research_eligible=True,accuracy_verified=False))

with tempfile.TemporaryDirectory(prefix='apac42-load-controller-') as temp:
    directory=Path(temp);(directory/'serving-tuning-03').mkdir();path=directory/'serving-tuning-03/load-plan.json'
    watch.ROOT=directory
    def fresh():
        submitted.clear();external[0]=0;path.write_text(json.dumps(copy.deepcopy(original)))
        return dict(entries=[entry('s2-repeat-best',52,2079)])
    state=fresh();assert watch.advance_load_refinement(state)
    assert submitted==[('s3-control-n52',52),('s3-best-n54',54)]
    finish(state,'s3-control-n52',2080);finish(state,'s3-best-n54',2150)
    watch.advance_load_refinement(state);assert submitted[-1]==('s3-best-n56',56)
    finish(state,'s3-best-n56',2180);watch.advance_load_refinement(state);assert submitted[-1]==('s3-best-n60',60)
    finish(state,'s3-best-n60',1900,sla=False);watch.advance_load_refinement(state)
    assert submitted[-1]==('s3-midpoint',58)
    finish(state,'s3-midpoint',2220);watch.advance_load_refinement(state)
    assert submitted[-1]==('s3-best-load-repeat',58)
    finish(state,'s3-best-load-repeat',2222);assert not watch.advance_load_refinement(state)
    watch.advance_load_refinement(state);assert len(submitted)==6

    state=fresh();watch.advance_load_refinement(state)
    finish(state,'s3-control-n52',2080);finish(state,'s3-best-n54',1900,sla=False)
    watch.advance_load_refinement(state);assert submitted[-1]==('s3-midpoint',53)
    assert not any(n>=56 for _,n in submitted)
    finish(state,'s3-midpoint',2110);assert not watch.advance_load_refinement(state)
    assert not any(name=='s3-best-load-repeat' for name,_ in submitted)

    state=fresh();external[0]=4;assert watch.advance_load_refinement(state);assert not submitted

    state=fresh();watch.advance_load_refinement(state)
    finish(state,'s3-control-n52',2080);finish(state,'s3-best-n54',2150)
    next(e for e in state['entries'] if e['id']=='s3-best-n54')['attempts'][0]['output_baseline_comparison']['research_eligible']=False
    watch.advance_load_refinement(state);assert not any(n>=56 for _,n in submitted)

    state=fresh();watch.advance_load_refinement(state)
    finish(state,'s3-control-n52',2080);finish(state,'s3-best-n54',2150);watch.advance_load_refinement(state)
    finish(state,'s3-best-n56',2180);watch.advance_load_refinement(state)
    finish(state,'s3-best-n60',1900,sla=False,errors=1);watch.advance_load_refinement(state)
    assert not any(name=='s3-midpoint' for name,_ in submitted)

report=dict(passed=True,actual_sbatch_calls=0,staged_54_56_60=True,
            failed_sla_refines_below_boundary=True,queue_cap_enforced=True,
            output_regression_blocks_higher_load=True,request_errors_not_a_latency_boundary=True,
            repeat_requires_two_percent_gain=True,at_most_six_jobs=True,no_duplicates=True)
(ROOT/'serving-tuning-03/controller-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
