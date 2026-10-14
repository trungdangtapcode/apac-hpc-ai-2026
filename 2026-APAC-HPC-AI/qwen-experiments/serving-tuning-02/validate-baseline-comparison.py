"""Validate the narrow research gate against real baseline artifacts and regressions."""
import copy
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('baseline_watcher',ROOT/'watch-serving-tuning.py')
watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
baseline=ROOT/'runs/23146/output-diagnostic.jsonl'
paths=[ROOT/'runs'/job/'output-smoke.json' for job in ('23128','23129','23130','23131')]
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [baseline,*paths]}
results=[watch.compare_output_baseline(json.loads(p.read_text()),baseline) for p in paths]
assert all(r['research_eligible'] and not r['accuracy_verified'] for r in results)
assert all(r['candidate_passed']==7 and r['known_baseline_failed_cases']==['reverse'] for r in results)
smoke=json.loads(paths[0].read_text())
bad=copy.deepcopy(smoke);bad['cases'][0].update(passed=False,text='43');bad['passed']=6
assert not watch.compare_output_baseline(bad,baseline)['research_eligible']
bad=copy.deepcopy(smoke);bad['cases'][0]['error']='HTTP 500'
assert not watch.compare_output_baseline(bad,baseline)['research_eligible']
bad=copy.deepcopy(smoke);bad['cases'][0]['prompt']='A different question'
assert not watch.compare_output_baseline(bad,baseline)['research_eligible']
bad=copy.deepcopy(smoke);bad['cases'].pop()
assert not watch.compare_output_baseline(bad,baseline)['research_eligible']
with tempfile.TemporaryDirectory(prefix='apac42-baseline-evidence-') as temp:
 path=Path(temp)/'baseline.jsonl';raw=baseline.read_text().splitlines()
 path.write_text('\n'.join(raw[:-1])+'\n')
 assert not watch.compare_output_baseline(smoke,path)['research_eligible']
 rows=[json.loads(line) for line in raw];rows[0]['error']='timeout'
 path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
 assert not watch.compare_output_baseline(smoke,path)['research_eligible']
 rows=[json.loads(line) for line in raw]
 next(r for r in rows if r['name']=='reverse')['passed']=True
 path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
 assert not watch.compare_output_baseline(smoke,path)['research_eligible']
assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [baseline,*paths]}
report=dict(passed=True,scope='Research eligibility only; not organiser accuracy or proof of transport correctness',
            four_real_smoke_failures_preserved=True,raw_files_unchanged=before,
            new_answer_failure_blocks=True,transport_error_blocks=True,prompt_change_blocks=True,
            missing_cases_block=True,incomplete_baseline_blocks=True,inconsistent_baseline_blocks=True)
(ROOT/'serving-tuning-02/baseline-comparison-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
