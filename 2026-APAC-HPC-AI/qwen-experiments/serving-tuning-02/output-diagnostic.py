"""Unranked output checks on unmodified monolithic model deployments."""
import argparse
import ast
import concurrent.futures
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path


def suite(path):
    tree = ast.parse(path.read_text())
    return next(ast.literal_eval(n.value) for n in tree.body
                if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'cases' for t in n.targets))


def request(host, case):
    name, prompt, expected = case
    row = dict(endpoint=host, name=name, prompt=prompt, expected=expected)
    start = time.monotonic()
    try:
        body = dict(model='qwen', messages=[dict(role='user', content=prompt)],
                    max_tokens=64, temperature=0.0, stream=False)
        req = urllib.request.Request('http://' + host + '/v1/chat/completions',
                                     json.dumps(body).encode(), {'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=60) as handle:
            response = json.load(handle)
        content = response['choices'][0]['message']['content']
        text = re.sub(r'^```(?:json)?\s*|\s*```$', '', content.strip(), flags=re.I).strip()
        if isinstance(expected, (dict, list)):
            try:
                passed = json.loads(text) == expected
            except ValueError:
                passed = False
        else:
            passed = text.strip('"\'` .\n').lower() == expected
        row.update(response=response, text=content, passed=passed)
    except Exception as error:
        row.update(passed=False, error=str(error))
    row['elapsed_s'] = time.monotonic() - start
    return row


def long_cases():
    # Actual input token counts are retained from the API; this is not AIPerf.
    filler = 'The river flows through the quiet valley. ' * 220
    rows = []
    for seed in range(4):
        values = [hashlib.sha256(f'output-diagnostic-{seed}-{key}'.encode()).hexdigest()[:12]
                  for key in ('a', 'b', 'c')]
        context = f'LABEL_A={values[0]}\n{filler}\nLABEL_B={values[1]}\n{filler}\nLABEL_C={values[2]}\n'
        for i, key in enumerate(('A', 'B', 'C')):
            rows.append((f'long-retrieval-{seed}-{key}',
                         context + f'Return only the exact value assigned to LABEL_{key}.', values[i]))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoints', nargs='+', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke-source', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    cases = suite(args.smoke_source)
    rows = []
    journal = args.output / 'output-diagnostic.jsonl'
    if journal.exists():
        raise RuntimeError('Refusing to overwrite previous output responses')
    with journal.open('x') as handle:
        for phase, workers, workload in (
            ('short-sequential', 1, cases * 2),
            ('short-concurrent', 4, cases * 2),
            ('long-concurrent', 4, long_cases()),
        ):
            for host in args.endpoints:
                with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
                    for row in pool.map(lambda case: request(host, case), workload):
                        row.update(phase=phase, concurrency=workers)
                        rows.append(row)
                        handle.write(json.dumps(row) + '\n')
                        handle.flush()
                print(phase, host, 'complete', flush=True)
    summary = dict(scope='Diagnostic only: same FP8 checkpoint, monolithic deployments, no NIXL transfer. '
                        'Not contest benchmark or organiser accuracy. Numerical/batching differences remain possible.',
                   total=len(rows), passed=sum(r['passed'] for r in rows),
                   errors=sum('error' in r for r in rows),
                   groups=[dict(endpoint=host, phase=phase,
                                total=sum(r['endpoint'] == host and r['phase'] == phase for r in rows),
                                passed=sum(r['passed'] and r['endpoint'] == host and r['phase'] == phase for r in rows))
                           for host in args.endpoints for phase in ('short-sequential', 'short-concurrent', 'long-concurrent')],
                   failed_cases=[{k: r[k] for k in ('endpoint', 'phase', 'name', 'expected', 'text', 'error') if k in r}
                                 for r in rows if not r['passed']])
    (args.output / 'output-diagnostic-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
