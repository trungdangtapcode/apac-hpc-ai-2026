"""Unranked real PD token-observation and repeat-stability control."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.request

VOCAB = 151936


def observed(response, expected_prompt_tokens):
    meta = response['meta_info']
    count = meta.get('completion_tokens')
    rows = meta.get('output_token_logprobs')
    if type(count) is not int or count != 200 or not isinstance(rows, list) or len(rows) != count:
        raise ValueError('Require all 200 actual output IDs, including the first token')
    if meta.get('prompt_tokens') != expected_prompt_tokens:
        raise ValueError('Prompt length changed')
    if any(not isinstance(r, list) or len(r) != 3 or type(r[1]) is not int or not 0 <= r[1] < VOCAB for r in rows):
        raise ValueError('Missing/invalid actual target-vocabulary IDs')
    finish = meta.get('finish_reason')
    if not isinstance(finish, dict) or finish.get('type') != 'length':
        raise ValueError('Unexpected or missing finish reason')
    return dict(output_ids=[r[1] for r in rows], finish_reason=finish)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('gateway')
    parser.add_argument('model', type=Path)
    parser.add_argument('artifact', type=Path)
    args = parser.parse_args()
    O = args.artifact
    output = O/'token-control.json'
    assert not output.exists(), 'Never overwrite a diagnostic capture'
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), passed=False,
                  platform='H100', scope='Real target-only PD /generate observation and repeat stability; no ranked score or organiser accuracy',
                  stages={}, cases=[])
    try:
        expected = json.loads((Path(__file__).parent/'target-staging-record.json').read_text())
        assert expected['complete'] and not expected.get('errors')
        identity = dict(revision=expected['revision'], verified_staging=expected['verified'], current_files={},
                        limit='Large weight files checked for current size against retained complete SHA256 staging record; not rehashed during this allocation')
        for name, entry in expected['verified'].items():
            if '/' in name:
                raise ValueError('Unexpected staging member')
            p = args.model/name
            assert p.is_file() and p.stat().st_size == entry['bytes'], name
            current = dict(bytes=p.stat().st_size)
            if not name.endswith('.safetensors'):
                current['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
                assert current['sha256'] == entry['sha256'], name
            identity['current_files'][name] = current
        (O/'target-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
        result['target_identity_sha256'] = hashlib.sha256((O/'target-identity.json').read_bytes()).hexdigest()
        corpus=json.loads((Path(__file__).parent/'prepared-corpus.json').read_text())
        assert corpus['passed'] and corpus['target_revision']==expected['revision']
        assert corpus['small_file_sha256']=={n:v['sha256'] for n,v in expected['verified'].items() if not n.endswith('.safetensors')}
        result['cases']=corpus['cases']
        assert len(result['cases'])==4
        for case in result['cases']:
            ids=case['input_ids']
            assert isinstance(ids,list) and ids and all(type(t) is int and 0<=t<VOCAB for t in ids)
        assert len(next(c['input_ids'] for c in result['cases'] if c['name']=='long4000'))==4000
        json.dumps(result)
        started_all=time.monotonic()
        for stage in ['target-a','target-b']:
            result['stages'][stage]=[]
            for case in result['cases']:
                if time.monotonic()-started_all>210:
                    raise TimeoutError('Total diagnostic deadline exhausted')
                body=dict(input_ids=case['input_ids'],stream=False,return_logprob=True,
                          logprob_start_len=-1,return_text_in_logprobs=False,
                          sampling_params=dict(temperature=0.0,top_p=1.0,sampling_seed=2026,
                                               max_new_tokens=200,ignore_eos=True))
                request=urllib.request.Request('http://'+args.gateway+'/generate',json.dumps(body).encode(),{'Content-Type':'application/json'})
                started=time.monotonic()
                with urllib.request.urlopen(request,timeout=60) as response:
                    raw=response.read(2*1024*1024+1)
                    assert len(raw)<=2*1024*1024
                    payload=json.loads(raw)
                row=dict(name=case['name'],request=body,response=payload,elapsed_s=time.monotonic()-started)
                result['stages'][stage].append(row)
                output.write_text(json.dumps(result,indent=2)+'\n')
                row['observed']=observed(payload,len(case['input_ids']))
        comparisons=[]
        for a,b in zip(result['stages']['target-a'],result['stages']['target-b'],strict=True):
            equal=a['request']==b['request'] and a['observed']==b['observed']
            comparisons.append(dict(name=a['name'],exact_ids_and_finish_equal=equal))
        result['comparisons']=comparisons
        assert all(c['exact_ids_and_finish_equal'] for c in comparisons), 'Target repeat differs'
        result['passed']=True
    except Exception as error:
        result['failure']=dict(type=type(error).__name__,message=str(error))
    output.write_text(json.dumps(result,indent=2)+'\n')
    raise SystemExit(0 if result['passed'] else 1)


if __name__=='__main__':
    main()
