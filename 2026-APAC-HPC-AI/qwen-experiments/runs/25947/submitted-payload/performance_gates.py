#!/usr/bin/env python3
"""Raw AIPerf and response-level gates for the unranked fast-default pair."""
from __future__ import annotations
import hashlib, json, math, re
from pathlib import Path

def normalize_input_config(config):
    value=json.loads(json.dumps(config))
    assert len(value['endpoint']['urls'])==1
    value['endpoint']['urls']=['DYNAMIC_ALLOCATED_ROUTER']
    value['artifacts']['dir']='DYNAMIC_ARTIFACT_DIRECTORY'
    return value

def check_aiperf(art, expected_input, expected_output_tokens=200):
    art=Path(art)
    summary=json.loads((art/'summary.json').read_text())
    rows=[r for r in summary if r.get('phase')=='screen' and r.get('concurrency')==64]
    assert len(rows)==1, 'one measured N64 point is required'
    metric=rows[0]
    assert metric['requests']>0 and metric['errors']==0 and metric['cancelled_requests']==0
    assert metric['sla_pass'] is True, 'summary SLA floor failed'
    export_path=art/'screen/n64/artifacts/profile_export_aiperf.json'
    assert export_path.is_file(), 'AIPerf export missing'
    export=json.loads(export_path.read_text())
    assert normalize_input_config(export['input_config'])==expected_input, 'AIPerf input config differs from fixed workload'
    request_count=float(export['request_count']['avg'])
    good_fraction=float(export['good_request_fraction']['avg'])
    goodput=float(export['goodput']['avg'])
    assert export['goodput']['unit']=='requests/sec', 'goodput unit must be requests/sec'
    assert all(math.isfinite(x) for x in (request_count,good_fraction,goodput))
    assert request_count>0 and goodput>0 and good_fraction>=0.90
    log=(art/'screen/n64/client.log').read_text(errors='replace')
    matches=re.findall(r'Phase profiling \(profiling\) complete \| completed=([\d,]+), cancelled=([\d,]+), errors=([\d,]+)',log)
    assert len(matches)==1, 'raw AIPerf completed/error/cancelled count missing'
    completed,cancelled,errors=[int(v.replace(',','')) for v in matches[0]]
    assert completed==request_count and cancelled==0 and errors==0
    raw_count=raw_good=0
    raw_path=export_path.parent/'profile_export.jsonl'
    assert raw_path.is_file(), 'raw per-request profile input missing'
    with raw_path.open() as stream:
        for line in stream:
            row=json.loads(line)
            if row['metadata']['benchmark_phase']!='profiling': continue
            metrics=row['metrics']; ttft=metrics['time_to_first_token']; itl=metrics['inter_token_latency']
            assert ttft['unit']==itl['unit']=='ms'
            assert all(math.isfinite(x['value']) and x['value']>=0 for x in (ttft,itl))
            raw_count+=1; raw_good+=int(ttft['value']<=3000 and itl['value']<=20)
    assert raw_count==completed, 'raw profile rows do not retain the full denominator'
    assert math.isclose(raw_good/raw_count,good_fraction,abs_tol=1e-9), 'raw SLA values differ from AIPerf fraction'
    recorded_good=float(export['good_request_count']['avg'])
    assert export['good_request_count']['unit']=='requests' and recorded_good==raw_good, 'good-request count differs from raw SLA rows'
    assert math.isclose(float(metric['good_request_fraction']),good_fraction,abs_tol=1e-9), 'summary fraction differs from raw AIPerf'
    assert math.isclose(float(metric['good_output_tokens_s']),float(expected_output_tokens)*goodput,rel_tol=1e-9), 'summary good-output throughput differs from raw goodput'
    return {'completed':completed,'errors':errors,'cancelled':cancelled,'good_request_fraction':good_fraction,
      'goodput_req_s':goodput,'good_output_tokens_per_second':float(expected_output_tokens)*goodput,
      'goodput_unit':'requests/sec','good_output_throughput_unit':'tokens/sec'}

def _response_text(row):
    response=row.get('response')
    assert isinstance(response,dict), 'raw HTTP response missing'
    choices=response.get('choices')
    assert isinstance(choices,list) and len(choices)==1
    message=choices[0].get('message')
    assert isinstance(message,dict) and isinstance(message.get('content'),str)
    text=message['content']
    assert row.get('text')==text, 'stored parsed text differs from raw response body'
    return text

def _expected_smoke(row):
    expected=row['expected']; text=_response_text(row)
    stripped=re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip(), flags=re.I).strip()
    if isinstance(expected,(dict,list)):
        try: passed=json.loads(stripped)==expected
        except ValueError: passed=False
    else: passed=stripped.strip('"\'` .\n').lower()==expected
    assert row.get('passed') is passed, 'smoke boolean contradicts raw response'
    return passed

def check_smoke(art, reference):
    art=Path(art); smoke=json.loads((art/'output-smoke.json').read_text()); expected=json.loads(reference.read_text())
    assert expected['passed']==7 and expected['total']==8, 'frozen target sanity reference changed'
    expected_rows={r['name']:r for r in expected['cases']}; rows=smoke['cases']
    assert len(rows)==8 and len(expected_rows)==8
    assert {r['name'] for r in rows}==set(expected_rows), 'smoke request names/denominator differ'
    regressions=[]; passed_count=0
    for row in rows:
        baseline=expected_rows[row['name']]
        assert row['prompt']==baseline['prompt'] and row['expected']==baseline['expected']
        assert 'error' not in row
        passed=_expected_smoke(row); passed_count+=int(passed)
        if baseline['passed'] and not passed: regressions.append(row['name'])
    assert smoke['total']==8 and smoke['passed']==passed_count
    assert passed_count>=7 and not regressions
    return {'passed':passed_count,'total':8,'regressions':regressions}

def check_retrieval(art):
    result=json.loads((Path(art)/'long-context-check.json').read_text()); rows=result['cases']
    names={f'retrieval-{i}' for i in range(12)}
    assert result['total']==12 and len(rows)==12 and {r['name'] for r in rows}==names, 'retrieval denominator/names differ'
    passed_count=0
    for row in rows:
        index=int(row['name'].split('-')[1]); expected=str(73160429+index*137)
        assert row['expected']==expected and 'error' not in row
        text=_response_text(row); passed=text.strip(' \t\n\r"\'`.')==expected
        assert row.get('passed') is passed, 'retrieval pass bit contradicts raw response'
        passed_count+=int(passed)
    assert result['errors']==0 and result['passed']==passed_count==12
    return {'passed':12,'total':12,'errors':0}
