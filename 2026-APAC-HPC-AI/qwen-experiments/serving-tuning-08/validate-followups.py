"""Do not spend repeat/high-load slots unless the matched evidence justifies them."""
import copy
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('backend_followups',ROOT/'watch-serving-tuning.py')
watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
original=json.loads((ROOT/'serving-tuning-08/followup-plan.json').read_text());calls=[];external=[0]
# Reset mutable production state for independent queue-decision fixtures.
original['candidates']=original['candidates'][:2]
for c in original['candidates']:
 for step in (c['repeat'],c['higher_load']):
  step['state']='UNDECIDED';step.pop('job',None);step.pop('reason',None)
watch.account_active_jobs=lambda state:external[0]+sum(e['state']=='ACTIVE' for e in state['entries'])
def measured(name,rate,itl=18.8,valid=True):
 row=dict(concurrency=52,requests=100,errors=0,cancelled_requests=0,good_output_tokens_s=rate,sla_pass=True,good_request_fraction=.98,itl_avg_ms=itl)
 return dict(id=name,state='MEASURED',measurements=[row],attempts=[dict(job='98500',state='COMPLETED',measurements=[row],output_smoke=dict(passed=7,total=8),output_baseline_comparison=dict(research_eligible=valid))])
def fake_submit(state,name,source,ns,purpose,**kwargs):
 assert kwargs['wave']==8;calls.append((name,ns[0]));state['entries'].append(dict(id=name,state='ACTIVE',measurements=[],attempts=[dict(job=str(99000+len(calls)),state='SUBMITTED',measurements=[])]))
watch.submit_followup=fake_submit
with tempfile.TemporaryDirectory(prefix='apac42-backend-followups-') as temp:
 directory=Path(temp);(directory/'serving-tuning-08').mkdir();path=directory/'serving-tuning-08/followup-plan.json';watch.ROOT=directory
 def fresh():
  calls.clear();external[0]=0;path.write_text(json.dumps(copy.deepcopy(original)))
  return dict(entries=[measured('s6-rr-profile-n52',2410),measured('s8-rr-dpa8-deepep-n52',2500)])
 state=fresh();assert watch.advance_backend_followups(state,wave=8)
 assert calls==[('s8-dpa8-repeat-n52',52)]
 state['entries'][-1]=measured('s8-dpa8-repeat-n52',2505)
 assert watch.advance_backend_followups(state,wave=8) and calls[-1]==('s8-dpa8-n54',54)
 state['entries'][-1]=measured('s8-dpa8-n54',2510)
 assert not watch.advance_backend_followups(state,wave=8)
 watch.advance_backend_followups(state,wave=8);assert len(calls)==2

 state=fresh();watch.advance_backend_followups(state,wave=8);state['entries'][-1]=measured('s8-dpa8-repeat-n52',2505,itl=19.5)
 assert not watch.advance_backend_followups(state,wave=8) and len(calls)==1
 state=fresh();external[0]=original['max_active_jobs'];assert watch.advance_backend_followups(state,wave=8) and not calls
 state=fresh();state['entries'][1]=measured('s8-rr-dpa8-deepep-n52',2500,valid=False)
 assert not watch.advance_backend_followups(state,wave=8) and not calls
 state=fresh();state['entries'][0]=measured('s6-rr-profile-n52',2520)
 assert not watch.advance_backend_followups(state,wave=8) and not calls, 'A slower fresh control must not manufacture a gain'
report=dict(passed=True,actual_sbatch_calls=0,matched_and_original_controls_required=True,
            two_percent_gain_required=True,independent_repeat_before_higher_load=True,itl_margin_required=True,
            output_evidence_required=True,configured_queue_cap=True,no_duplicates=True)
(ROOT/'serving-tuning-08/followup-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
