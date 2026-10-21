"""Enforce semantic success independently of remote task-launch exit status."""
import importlib.util,json,sys
from pathlib import Path
O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('tokens',O/'token-control.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=json.loads(Path(sys.argv[1]).read_text());corpus=json.loads((O/'prepared-corpus.json').read_text())
assert r['passed'] and r['cases']==corpus['cases']
assert set(r['stages'])=={'draft-a','draft-b'}
for stage in ['draft-a','draft-b']:
 rows=r['stages'][stage];assert len(rows)==4
 for case,row in zip(corpus['cases'],rows):
  assert row['name']==case['name'] and row['request']['input_ids']==case['input_ids']
  assert m.observed(row['response'],len(case['input_ids']))==row['observed']
for a,b in zip(r['stages']['draft-a'],r['stages']['draft-b']):
 assert a['request']==b['request'] and a['observed']==b['observed']
print('SPECULATIVE_LOCAL_PAIR_GATE_PASSED')

reference=json.loads((O/'target-reference.json').read_text())
assert r['target_identity_sha256']==reference['target_identity_sha256'] and r['platform']==reference['platform']
for a,b in zip(reference['stages']['target-a'],r['stages']['draft-a']):
 assert a['request']==b['request'] and a['observed']==b['observed']
