"""Unranked gateway token-ID diagnostics for a future allocated correctness pilot.

Capture each stage separately after readiness, outside scoring. Compare two
target-only captures before comparing a draft capture. This never substitutes
retokenized text for actual generated IDs and never retries an HTTP request.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.request

VOCAB_SIZE = 151936
PROMPTS = [
    ('arithmetic', 'Compute 37 * 19. Explain the calculation briefly.'),
    ('code', 'Write a Python function that reverses a list without mutating it.'),
    ('explanation', 'Explain why a queue can increase latency under heavy load.'),
    ('unicode', 'Explain the relationship between “throughput” and “latency”.'),
]


def requests():
    return [dict(name=name, body=dict(
        model='qwen', messages=[dict(role='user', content=prompt)],
        temperature=0.0, top_p=1.0, seed=2026, max_tokens=200,
        stream=False, logprobs=False, return_token_ids=True,
        return_prompt_token_ids=True)) for name, prompt in PROMPTS]


def ids(value):
    if not isinstance(value, list) or not value:
        raise ValueError('Actual nonempty token IDs are required; text is insufficient')
    if any(type(token) is not int or not 0 <= token < VOCAB_SIZE for token in value):
        raise ValueError('Invalid target-vocabulary token ID')
    return value


def choice(response):
    choices = response.get('choices')
    if not isinstance(choices, list) or len(choices) != 1:
        raise ValueError('Exactly one complete choice is required')
    row = choices[0]
    if row.get('index') != 0 or row.get('finish_reason') not in ('stop', 'length'):
        raise ValueError('Missing or unsuccessful completion finish reason')
    return dict(prompt_ids=ids(row.get('prompt_token_ids')),
                output_ids=ids(row.get('token_ids')),
                finish_reason=row['finish_reason'])


def compare(reference, candidate):
    expected = requests()
    rows = []
    if reference.get('stage') != 'target-a' or candidate.get('stage') not in ('target-b', 'draft'):
        raise ValueError('Use target-a as the reference; first establish target-b stability')
    if not reference.get('passed') or not candidate.get('passed'):
        raise ValueError('Both captures must pass the token-ID capability gate')
    if reference.get('requests') != expected or candidate.get('requests') != expected:
        raise ValueError('Request corpus or greedy settings changed')
    if reference.get('target_manifest_sha256') != candidate.get('target_manifest_sha256'):
        raise ValueError('Target identity manifest changed')
    if reference.get('platform') != candidate.get('platform'):
        raise ValueError('Cross-platform token comparison is not a matched control')
    if len(reference.get('responses', [])) != len(expected) or len(candidate.get('responses', [])) != len(expected):
        raise ValueError('Missing or additional responses')
    for request, before, after in zip(expected, reference['responses'], candidate['responses']):
        if before.get('name') != request['name'] or after.get('name') != request['name']:
            raise ValueError('Response order or request identity changed')
        a, b = choice(before['response']), choice(after['response'])
        prompt_equal = a['prompt_ids'] == b['prompt_ids']
        output_equal = a['output_ids'] == b['output_ids']
        finish_equal = a['finish_reason'] == b['finish_reason']
        mismatch = next((i for i, pair in enumerate(zip(a['output_ids'], b['output_ids']))
                         if pair[0] != pair[1]), None)
        if mismatch is None and not output_equal:
            mismatch = min(len(a['output_ids']), len(b['output_ids']))
        rows.append(dict(name=request['name'], prompt_equal=prompt_equal,
                         output_equal=output_equal, finish_equal=finish_equal,
                         first_output_mismatch=mismatch,
                         reference_tokens=len(a['output_ids']),
                         candidate_tokens=len(b['output_ids']),
                         passed=prompt_equal and output_equal and finish_equal))
    return dict(passed=all(row['passed'] for row in rows), cases=rows,
                scope='Four unranked generic greedy requests; not official accuracy or a performance score')


def write_new(path, data):
    with Path(path).open('x') as stream:
        json.dump(data, stream, indent=2, ensure_ascii=True)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    capture = sub.add_parser('capture')
    capture.add_argument('--endpoint', required=True, help='Allocated gateway URL, e.g. http://node:8000')
    capture.add_argument('--stage', required=True, choices=['target-a', 'target-b', 'draft'])
    capture.add_argument('--platform', required=True, choices=['H100', 'H200'])
    capture.add_argument('--target-manifest', type=Path, required=True)
    capture.add_argument('--out', type=Path, required=True)
    comparison = sub.add_parser('compare')
    comparison.add_argument('--reference', type=Path, required=True)
    comparison.add_argument('--candidate', type=Path, required=True)
    comparison.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'compare':
        result = compare(json.loads(args.reference.read_text()), json.loads(args.candidate.read_text()))
        write_new(args.out, result)
        raise SystemExit(0 if result['passed'] else 1)
    if args.out.exists():
        parser.error('Output exists; preserve the earlier capture')
    if not args.endpoint.startswith('http://') or '@' in args.endpoint or '?' in args.endpoint:
        parser.error('Use an allocated internal HTTP gateway without authentication material')
    data = dict(created_utc=datetime.now(timezone.utc).isoformat(), stage=args.stage,
                platform=args.platform,
                target_manifest_sha256=hashlib.sha256(args.target_manifest.read_bytes()).hexdigest(),
                requests=requests(), responses=[], passed=False)
    try:
        for case in data['requests']:
            started = time.monotonic()
            req = urllib.request.Request(args.endpoint.rstrip('/') + '/v1/chat/completions',
                                         json.dumps(case['body']).encode(),
                                         {'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=90) as response:
                raw = response.read(2 * 1024 * 1024 + 1)
                if len(raw) > 2 * 1024 * 1024:
                    raise ValueError('Oversized diagnostic response')
                result = json.loads(raw)
            # Retain the raw parsed response even if IDs are absent.
            data['responses'].append(dict(name=case['name'], response=result,
                                          elapsed_s=time.monotonic() - started))
            choice(result)
        data['passed'] = True
    except Exception as error:
        # No retry. Preserve partial responses for the capability/integration review.
        data['failure'] = dict(type=type(error).__name__, message=str(error))
    write_new(args.out, data)
    raise SystemExit(0 if data['passed'] else 1)


if __name__ == '__main__':
    main()
