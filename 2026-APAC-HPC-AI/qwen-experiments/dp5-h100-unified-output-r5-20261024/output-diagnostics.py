#!/usr/bin/env python3
"""Independently summarize raw HTTP responses without imposing a quality gate."""
import json,re,sys
from pathlib import Path
b=Path(__file__).resolve().parent; out=Path(sys.argv[1])
smoke=json.loads((out/'output-smoke.json').read_text())
retrieval=json.loads((out/'long-context-check.json').read_text())
reference=json.loads((b/'reference-output-smoke.json').read_text())
assert smoke.get('total')==8 and len(smoke.get('cases',[]))==8
assert len({r['name'] for r in smoke['cases']})==8
assert reference.get('passed')==7 and reference.get('total')==8
assert retrieval.get('total')==12 and len(retrieval.get('cases',[]))==12
assert {r['name'] for r in retrieval['cases']}=={f'retrieval-{i}' for i in range(12)}
expected={r['name']:r for r in reference['cases']}
smoke_pass=0; smoke_errors=0; regressions=[]
for row in smoke['cases']:
    assert row['name'] in expected and row['prompt']==expected[row['name']]['prompt'] and row['expected']==expected[row['name']]['expected']
    if 'error' in row:
        smoke_errors+=1; continue
    response=row.get('response'); assert isinstance(response,dict)
    text=response['choices'][0]['message']['content']; assert row.get('text')==text
    stripped=re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip(), flags=re.I).strip()
    exp=row['expected']
    if isinstance(exp,(dict,list)):
        try: passed=json.loads(stripped)==exp
        except ValueError: passed=False
    else: passed=stripped.strip('"\'` .\n').lower()==exp
    if expected[row["name"]]["passed"] and not passed: regressions.append(row["name"])
    smoke_pass+=int(passed)
retrieval_pass=0; retrieval_errors=0
for row in retrieval['cases']:
    i=int(row['name'].rsplit('-',1)[1]); assert row['expected']==str(73160429+i*137)
    if 'error' in row:
        retrieval_errors+=1; continue
    response=row.get('response'); assert isinstance(response,dict)
    text=response['choices'][0]['message']['content']; assert row.get('text')==text
    retrieval_pass+=int(text.strip(' \t\n\r"\'`.')==row['expected'])
local_pass=smoke_pass>=7 and retrieval_pass==12 and smoke_errors==retrieval_errors==0 and not regressions
result={'state':'PASS_LOCAL_OUTPUT_SCREEN' if local_pass else 'FAIL_LOCAL_OUTPUT_SCREEN','smoke':{'observed_passed':smoke_pass,'total':8,'reference_floor':7,'floor_met':smoke_pass>=7,'errors':smoke_errors},'retrieval':{'observed_passed':retrieval_pass,'total':12,'errors':retrieval_errors},'new_smoke_regressions':regressions,'local_screen_passed':local_pass,'exact_response_threshold_used_for_readiness':False,'readiness_independent':True,'official_quality_status':'UNKNOWN','scored_load':False,'throughput_claim':False}
(out/'output-diagnostics.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,sort_keys=True))

raise SystemExit(0 if local_pass else 1)
