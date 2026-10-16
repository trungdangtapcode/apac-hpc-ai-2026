#!/usr/bin/env python3
"""Sequential native-token capture from an explicitly selected loopback /generate.

No model launch, tokenizer transformation, authentication, retry or scheduler action.
"""
import argparse
import hashlib
import http.client
import importlib.util
import ipaddress
import json
import math
import os
from pathlib import Path
import time
from urllib.parse import urlsplit

spec = importlib.util.spec_from_file_location('token_review', Path(__file__).with_name('review-token-pairs.py'))
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    def reject(value):
        raise ValueError('non-finite JSON number: ' + value)
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError('duplicate JSON key: ' + key)
            obj[key] = value
        return obj
    return json.loads(raw, parse_constant=reject, object_pairs_hook=unique)


def write_new(path, raw):
    with path.open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def preflight(suite, tokenizer_raw, endpoint):
    review.require(isinstance(suite, dict) and suite.get('schema') == 1, 'unsupported suite')
    review.require(suite.get('target_revision') == review.TARGET_REVISION, 'target revision mismatch')
    review.require(suite.get('tokenizer_sha256') == sha(tokenizer_raw), 'local tokenizer hash mismatch')
    url = urlsplit(endpoint)
    review.require(url.scheme == 'http' and url.path == '/generate' and
                   not url.query and not url.fragment and url.username is None and
                   url.password is None, 'use http://LOOPBACK:PORT/generate without auth/query')
    review.require(url.hostname is not None and ipaddress.ip_address(url.hostname).is_loopback,
                   'only numeric loopback endpoint is supported; establish an authorized forward separately')
    review.require(url.port is not None and 1 <= url.port <= 65535, 'explicit valid port required')
    cases = suite.get('cases')
    review.require(isinstance(cases, list) and 1 <= len(cases) <= 64, 'require 1..64 cases')
    seen = set()
    for case in cases:
        review.require(isinstance(case, dict) and set(case) == {'case_id', 'request'}, 'suite case fields')
        name = case['case_id']
        review.require(isinstance(name, str) and name and name not in seen, 'duplicate/missing case ID')
        seen.add(name)
        req = case['request']
        review.require(isinstance(req, dict) and set(req) ==
                       {'input_ids', 'sampling_params', 'stream', 'return_prompt_token_ids'}, 'request fields')
        review.token_ids(req['input_ids'], name)
        review.require(req['stream'] is False and req['return_prompt_token_ids'] is True, 'capture options')
        params = req['sampling_params']
        expected = set(review.NEUTRAL) | {'max_new_tokens', 'min_new_tokens', 'ignore_eos',
                                         'skip_special_tokens', 'no_stop_trim'}
        review.require(isinstance(params, dict) and set(params) == expected, 'initial sampling fields')
        review.require(all(type(params[k]) in (int, float) and params[k] == v
                           for k, v in review.NEUTRAL.items()), 'require neutral greedy settings')
        review.require(type(params['max_new_tokens']) is int and 1 <= params['max_new_tokens'] <= 200,
                       'initial capture cap must be 1..200')
        review.require(type(params['min_new_tokens']) is int and params['min_new_tokens'] == 0,
                       'initial capture min_new_tokens must be zero')
        review.require(params['ignore_eos'] is False and params['skip_special_tokens'] is True and
                       params['no_stop_trim'] is False, 'initial capture EOS/text options')
        review.require(len(req['input_ids']) + params['max_new_tokens'] <= 8192, 'context8192 budget exceeded')
    return url


def capture(suite_path, tokenizer_path, endpoint, outdir, timeout=120):
    review.require(math.isfinite(timeout) and 0 < timeout <= 300, 'timeout must be in (0,300]')
    suite_raw, tokenizer_raw = suite_path.read_bytes(), tokenizer_path.read_bytes()
    suite = decode(suite_raw)
    url = preflight(suite, tokenizer_raw, endpoint)
    # Reserve evidence location only after all requests have passed preflight.
    outdir.mkdir(parents=False, exist_ok=False)
    write_new(outdir/'suite.json', suite_raw)
    write_new(outdir/'provenance.json', encoded({
        'state': 'CAPTURE_ONLY_RUNTIME_NOT_ATTESTED', 'endpoint': endpoint,
        'suite_sha256': sha(suite_raw), 'tokenizer_sha256': sha(tokenizer_raw),
        'target_revision': suite['target_revision'], 'sequential': True,
        'retries': 0, 'model_validation': False,
        'limits': 'Source declarations require separate image, target, tokenizer, args and simulation audit.'}))
    result = {k: suite[k] for k in ('schema', 'target_revision', 'tokenizer_sha256')}
    result['cases'] = []
    try:
        with (outdir/'journal.jsonl').open('x') as journal:
            for index, case in enumerate(suite['cases']):
                prefix = f'{index:03d}'
                request_raw = encoded(case['request'])
                write_new(outdir/(prefix+'-request.json'), request_raw)
                conn = http.client.HTTPConnection(url.hostname, url.port, timeout=timeout)
                started = time.monotonic()
                try:
                    conn.request('POST', '/generate', body=request_raw,
                                 headers={'Content-Type': 'application/json'})
                    response = conn.getresponse()
                    status = response.status
                    with (outdir/(prefix+'-response.bin')).open('xb') as raw_output:
                        try:
                            while True:
                                chunk = response.read1(65536)
                                if not chunk:
                                    break
                                raw_output.write(chunk)
                                raw_output.flush()
                        finally:
                            os.fsync(raw_output.fileno())
                    remaining = response.length
                    body = (outdir/(prefix+'-response.bin')).read_bytes()
                finally:
                    conn.close()
                row = {'case_id': case['case_id'], 'index': index, 'http_status': status,
                       'request_sha256': sha(request_raw), 'response_sha256': sha(body),
                       'elapsed_seconds_diagnostic_only': time.monotonic()-started}
                journal.write(json.dumps(row, allow_nan=False)+'\n')
                journal.flush()
                os.fsync(journal.fileno())
                review.require(remaining in (None, 0), 'incomplete HTTP Content-Length; preserve raw body')
                review.require(status == 200, 'HTTP status '+str(status)+'; no retry/redirect')
                parsed = decode(body)
                single = {**result, 'cases': [{**case, 'response': parsed}]}
                review.validate(single)
                result['cases'].append(single['cases'][0])
        review.validate(result)
        write_new(outdir/'capture.json', encoded(result))
        state = {'state': 'CAPTURE_COMPLETE_NOT_ACCURACY_CERTIFIED', 'case_count': len(result['cases'])}
        write_new(outdir/'status.json', encoded(state))
        return state
    except Exception as exc:
        write_new(outdir/'failure.json', encoded({'state': 'INCOMPLETE_OR_INVALID_CAPTURE',
                  'completed_cases': len(result['cases']), 'error_type': type(exc).__name__,
                  'reason': str(exc)}))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', required=True, type=Path)
    parser.add_argument('--tokenizer', required=True, type=Path)
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--outdir', required=True, type=Path)
    parser.add_argument('--timeout', type=float, default=120)
    args = parser.parse_args()
    try:
        state = capture(args.suite, args.tokenizer, args.endpoint, args.outdir, args.timeout)
    except (ValueError, OSError, TypeError, KeyError, http.client.HTTPException) as exc:
        print('CAPTURE_FAILED: '+str(exc))
        return 2
    print(state['state'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
