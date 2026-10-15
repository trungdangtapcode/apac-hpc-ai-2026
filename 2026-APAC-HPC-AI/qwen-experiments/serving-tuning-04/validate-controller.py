"""Check queue sharing and duplicate prevention without submitting real jobs."""
import copy
import importlib.util
import json
import tempfile
import types
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prefill_watcher',ROOT/'watch-serving-tuning.py')
watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
original=json.loads((ROOT/'serving-tuning-04/prefill-pilots.json').read_text())
for pilot in original['pilots']:
    pilot['state']='PLANNED';pilot.pop('job',None)
calls=[];watch.subprocess=types.SimpleNamespace(run=lambda *a,**k:None)
watch.command=lambda args:calls.append(args) or str(95000+len(calls))
watch.account_active_jobs=lambda state:2+sum(e['state']=='ACTIVE' for e in state['entries'])
row=dict(concurrency=52,requests=100,errors=0,cancelled_requests=0,good_output_tokens_s=2079,sla_pass=True)
source=dict(id='s2-repeat-best',state='MEASURED',attempts=[dict(job='94000',state='COMPLETED',measurements=[row],output_smoke=dict(passed=7,total=8),output_baseline_comparison=dict(research_eligible=True))])
with tempfile.TemporaryDirectory(prefix='apac42-prefill-scheduler-') as temp:
    directory=Path(temp);(directory/'serving-tuning-04').mkdir();path=directory/'serving-tuning-04/prefill-pilots.json'
    validation=path.with_name('cpu-validation.json');watch.ROOT=directory;watch.STATE=directory/'registry.json'
    path.write_text(json.dumps(copy.deepcopy(original)));state=dict(entries=[copy.deepcopy(source)])
    assert not watch.advance_prefill_pilots(state) and not calls
    validation.write_text(json.dumps(dict(passed=True)))
    assert watch.advance_prefill_pilots(state) and len(calls)==2
    assert watch.advance_prefill_pilots(state) and len(calls)==2
    for e in state['entries'][1:]:e['state']='MEASURED'
    assert not watch.advance_prefill_pilots(state) and len(calls)==2
    calls.clear();path.write_text(json.dumps(copy.deepcopy(original)))
    watch.account_active_jobs=lambda state:4;state=dict(entries=[copy.deepcopy(source)])
    assert watch.advance_prefill_pilots(state) and not calls
    watch.account_active_jobs=lambda state:0;state['entries'][0]['attempts'][0]['output_baseline_comparison']['research_eligible']=False
    assert not watch.advance_prefill_pilots(state) and not calls
report=dict(passed=True,actual_sbatch_calls=0,shared_queue_cap_four=True,cpu_validation_required=True,
            no_duplicate_submission=True,invalid_source_blocks=True,at_most_two_pilots=True)
(ROOT/'serving-tuning-04/controller-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
