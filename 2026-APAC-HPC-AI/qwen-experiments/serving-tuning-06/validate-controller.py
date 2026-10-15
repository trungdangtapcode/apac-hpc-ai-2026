"""Check eager queue filling, shared limits, and complete per-deployment profiling."""
import copy
import importlib.util
import json
import tempfile
import types
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rr_queue_watcher',ROOT/'watch-serving-tuning.py')
watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
original=json.loads((ROOT/'serving-tuning-06/prepared-pilots.json').read_text())
for pilot in original['pilots']:
    pilot['state']='PLANNED';pilot.pop('job',None)
calls=[];external=[1]
watch.subprocess=types.SimpleNamespace(run=lambda *a,**k:None)
watch.command=lambda args:calls.append(args) or str(98000+len(calls))
watch.account_active_jobs=lambda state:external[0]+sum(e['state']=='ACTIVE' for e in state['entries'])
row=dict(concurrency=52,requests=100,errors=0,cancelled_requests=0,good_output_tokens_s=2398,sla_pass=True)
source=dict(id='s5-rr-repeat-n52',state='MEASURED',attempts=[dict(job='97500',state='COMPLETED',measurements=[row],output_smoke=dict(passed=7,total=8),output_baseline_comparison=dict(research_eligible=True))])
with tempfile.TemporaryDirectory(prefix='apac42-rr-queue-') as temp:
    directory=Path(temp);(directory/'serving-tuning-06').mkdir();path=directory/'serving-tuning-06/prepared-pilots.json'
    path.write_text(json.dumps(copy.deepcopy(original)));path.with_name('cpu-validation.json').write_text(json.dumps(dict(passed=True)))
    watch.ROOT=directory;watch.STATE=directory/'registry.json';state=dict(entries=[copy.deepcopy(source)])
    assert watch.advance_prefill_pilots(state,wave=6) and len(calls)==3
    assert watch.advance_prefill_pilots(state,wave=6) and len(calls)==3
    for e in state['entries'][1:]:e['state']='MEASURED'
    assert not watch.advance_prefill_pilots(state,wave=6)
    calls.clear();external[0]=4;path.write_text(json.dumps(copy.deepcopy(original)));state=dict(entries=[copy.deepcopy(source)])
    assert watch.advance_prefill_pilots(state,wave=6) and not calls

entry=dict(expected_profile_ranks={'prefill-0':4,'prefill-1':4,'decode-0':8},attempts=[dict(job='1'),dict(job='2')])
def traces(job,counts):
    return [dict(trace=f'runs/{job}/diagnostic-profile/{role}/rank{rank}.json.gz',kernels=10)
            for role,count in counts.items() for rank in range(count)]
partial=traces('1',{'prefill-0':4,'prefill-1':4,'decode-0':4})+traces('2',{'decode-0':4})
assert not watch.complete_profile_attempt(entry,partial)
assert watch.complete_profile_attempt(entry,traces('1',entry['expected_profile_ranks']))
bad=traces('1',entry['expected_profile_ranks']);bad[-1]['kernels']=0
assert not watch.complete_profile_attempt(entry,bad)
report=dict(passed=True,actual_sbatch_calls=0,one_waiting_plus_three_prepared_jobs=True,
            queue_cap_four_enforced=True,no_duplicate_jobs=True,complete_sixteen_rank_profile_required=True,
            partial_deployments_not_combined=True,empty_gpu_traces_not_counted=True)
(ROOT/'serving-tuning-06/controller-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
