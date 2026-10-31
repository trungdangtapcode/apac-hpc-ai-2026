"""Reject stale runner/chunk/load assumptions using explicitly synthetic fixtures."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile

D = Path(__file__).resolve().parent
Q = D.parent
prep = json.loads((D / 'preparation.json').read_text())
base = {r: (Q / 'runs/27376' / f'{r}.log').read_text()
        for r in ('prefill-0', 'prefill-1', 'decode-0')}
results = []
for item in prep['bundles']:
    B = Q / item['bundle']
    n = item['concurrency']
    cfg = json.loads((B / 'config.json').read_text())
    assert cfg['concurrency'] == n and cfg['prefill_chunked_prefill_size'] == 4096
    assert cfg['prefill_moe_runner_backend'] == 'hpc_ops'
    assert cfg['decode_attention_backend'] == 'flashinfer' and cfg['arm'] == 'control'
    assert cfg['decode_cuda_graph_batch_sizes'] == list(range(1, 65))
    assert hashlib.sha256((B / 'SHA256SUMS').read_bytes()).hexdigest() == item['manifest_sha256']
    subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=B, check=True,
                   stdout=subprocess.DEVNULL)
    for name in prep['unchanged_files']:
        assert (B / name).read_bytes() == (Q / 'serving-tuning-11/s110-h200-decode-flashinfer-transfer' / name).read_bytes()
    assert f'env QWEN_TUNE_NS={n} ' in (B / 'topology-job.sh').read_text()
    logs = dict(base)
    for role in ('prefill-0', 'prefill-1'):
        assert logs[role].count('chunked_prefill_size=8192,') >= 1
        assert logs[role].count("moe_runner_backend='deep_gemm',") >= 1
        logs[role] = logs[role].replace('chunked_prefill_size=8192,', 'chunked_prefill_size=4096,')
        logs[role] = logs[role].replace("moe_runner_backend='deep_gemm',", "moe_runner_backend='hpc_ops',")
        logs[role] += '\nPREFILL_HPC_OPS_PREFLIGHT_PASSED SYNTHETIC_FIXTURE_ONLY\n'
    cases = [
        ('intended_recipe', {}, True),
        ('wrong_prefill_runner', {'prefill-0': logs['prefill-0'].replace(
            "moe_runner_backend='hpc_ops',", "moe_runner_backend='deep_gemm',")}, False),
        ('wrong_prefill_chunk', {'prefill-1': logs['prefill-1'].replace(
            'chunked_prefill_size=4096,', 'chunked_prefill_size=8192,')}, False),
        ('missing_prefill_preflight', {'prefill-0': logs['prefill-0'].replace(
            'PREFILL_HPC_OPS_PREFLIGHT_PASSED', 'MISSING_PREFLIGHT')}, False),
        ('wrong_decode_backend', {'decode-0': logs['decode-0'].replace(
            "decode_attention_backend='flashinfer',", "decode_attention_backend='fa3',")}, False),
        ('wrong_decode_capacity', {'decode-0': logs['decode-0'].replace(
            'max_running_requests=256,', 'max_running_requests=54,')}, False),
        ('missing_rank_capture', {'decode-0': '\n'.join(line for line in logs['decode-0'].splitlines()
            if not ('TP7 EP7]' in line and 'Capture target decode CUDA graph end.' in line))}, False),
    ]
    with tempfile.TemporaryDirectory(prefix='ap42-h100-recipe-synthetic-fixtures-') as tmp:
        art = Path(tmp)
        for name, changes, expected in cases:
            for role, content in {**logs, **changes}.items():
                (art / f'{role}.log').write_text(content)
            r = subprocess.run([sys.executable, '-B', str(B / 'check-fast-runtime.py'),
                                str(art), 'control', '64'], text=True, capture_output=True)
            assert (r.returncode == 0) is expected, (B.name, name, r.stdout, r.stderr)
            results.append(dict(bundle=B.name, case=name, expected_pass=expected, passed=True))

    spec = importlib.util.spec_from_file_location('recipe_gates', B / 'performance_gates.py')
    gates = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gates)
    expected = json.loads((B / 'expected-input-config.json').read_text())
    assert {p['concurrency'] for p in expected['phases']} == {n}
    assert expected['runtime']['workers'] == n
    with tempfile.TemporaryDirectory(prefix='ap42-h100-recipe-synthetic-client-') as tmp:
        art = Path(tmp)
        (art / 'config.json').write_text(json.dumps(cfg))
        prof = art / f'confirm/n{n}/artifacts'
        prof.mkdir(parents=True)
        row = dict(phase='confirm', concurrency=n, requests=2, errors=0,
                   cancelled_requests=0, sla_pass=True, good_request_fraction=1.0,
                   good_output_tokens_s=400.0)
        (art / 'summary.json').write_text(json.dumps([row]))
        export = dict(input_config=expected, request_count=dict(avg=2),
                      good_request_fraction=dict(avg=1.0),
                      goodput=dict(avg=2.0, unit='requests/sec'),
                      good_request_count=dict(avg=2, unit='requests'))
        request = dict(metadata=dict(benchmark_phase='profiling'), metrics=dict(
            time_to_first_token=dict(value=1000, unit='ms'),
            inter_token_latency=dict(value=15, unit='ms')))
        (prof / 'profile_export.jsonl').write_text((json.dumps(request) + '\n') * 2)
        (prof.parent / 'client.log').write_text(
            'Phase profiling (profiling) complete | completed=2, cancelled=0, errors=0\n')
        for label, bad_export, bad_summary, accepted in [
            ('correct_client_load', False, False, True),
            ('reject_wrong_export_load', True, False, False),
            ('reject_wrong_summary_load', False, True, False),
        ]:
            fixture = json.loads(json.dumps(export))
            summary = dict(row)
            if bad_export:
                fixture['input_config']['phases'][1]['concurrency'] = 64 if n == 54 else 54
            if bad_summary:
                summary['concurrency'] = 64 if n == 54 else 54
            (prof / 'profile_export_aiperf.json').write_text(json.dumps(fixture))
            (art / 'summary.json').write_text(json.dumps([summary]))
            try:
                gates.check_aiperf(art, expected, 200)
                got = True
            except AssertionError:
                got = False
            assert got is accepted, (B.name, label)
            results.append(dict(bundle=B.name, case=label, expected_pass=accepted, passed=True))
(D / 'validation.json').write_text(json.dumps(dict(
    passed=True, fixtures=results,
    scope='CPU fixtures only; all altered runtime/client records are synthetic and not new GPU measurements.'), indent=2) + '\n')
print(f'PASS: {len(results)} recipe/runtime/client-load fixtures')
