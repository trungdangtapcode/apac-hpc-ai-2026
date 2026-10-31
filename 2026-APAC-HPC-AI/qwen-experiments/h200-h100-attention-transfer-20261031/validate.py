"""Exercise attention activation gates against explicitly synthetic log fixtures."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

D = Path(__file__).resolve().parent
Q = D.parent
prep = json.loads((D / 'preparation.json').read_text())
base = {role: (Q / 'runs/27376' / f'{role}.log').read_text()
        for role in ('prefill-0', 'prefill-1', 'decode-0')}
results = []
for row in prep['bundles']:
    B = Q / row['bundle']
    backend = row['backend']
    cfg = json.loads((B / 'config.json').read_text())
    assert cfg['arm'] == 'control' and cfg['speculation'] is None
    assert cfg['concurrency'] == 64 and cfg['decode_attention_backend'] == backend
    assert hashlib.sha256((B / 'SHA256SUMS').read_bytes()).hexdigest() == row['manifest_sha256']
    subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=B,
                   check=True, stdout=subprocess.DEVNULL)
    for name in prep['unchanged_files']:
        assert (B / name).read_bytes() == (Q / 'runs/27376/submitted-payload' / name).read_bytes()
    needle = "decode_attention_backend='flashinfer',"
    assert base['decode-0'].count(needle) == 1
    logs = dict(base)
    logs['decode-0'] = logs['decode-0'].replace(needle, f"decode_attention_backend='{backend}',")
    wrong = 'fa3' if backend == 'flashinfer' else 'flashinfer'
    cases = [
        ('intended_backend', {}, True),
        ('wrong_decode_backend', {'decode-0': logs['decode-0'].replace(
            f"decode_attention_backend='{backend}',", f"decode_attention_backend='{wrong}',")}, False),
        ('changed_load_capacity', {'decode-0': logs['decode-0'].replace(
            'max_running_requests=256,', 'max_running_requests=64,')}, False),
        ('changed_KV_dtype', {'decode-0': logs['decode-0'].replace(
            "dtype='bfloat16',", "dtype='float16',")}, False),
        ('wrong_prefill_attention', {'prefill-0': logs['prefill-0'].replace(
            "attention_backend='fa3',", "attention_backend='flashinfer',")}, False),
        ('missing_decode_rank', {'decode-0': '\n'.join(line for line in logs['decode-0'].splitlines()
            if not ('TP7 EP7]' in line and 'Capture target decode CUDA graph end.' in line))}, False),
    ]
    with tempfile.TemporaryDirectory(prefix='ap42-attention-synthetic-fixtures-') as tmp:
        art = Path(tmp)
        for name, changes, expected in cases:
            for role, content in {**logs, **changes}.items():
                (art / f'{role}.log').write_text(content)
            run = subprocess.run([sys.executable, '-B', str(B / 'check-fast-runtime.py'),
                                  str(art), 'control', '64'], text=True, capture_output=True)
            assert (run.returncode == 0) is expected, (B.name, name, run.stdout, run.stderr)
            results.append(dict(bundle=B.name, case=name, expected_pass=expected, passed=True))
configs = [json.loads((Q / row['bundle'] / 'config.json').read_text()) for row in prep['bundles']]
changed = {key for key in configs[0] if configs[0][key] != configs[1][key]}
assert changed == {'experiment', 'label', 'study_arm', 'decode_attention_backend'}, changed
(D / 'validation.json').write_text(json.dumps(dict(
    passed=True, fixtures=results, pair_config_differences=sorted(changed),
    scope='CPU fixture and manifest validation only; altered historical logs are synthetic and never GPU evidence.'),
    indent=2) + '\n')
print(f'PASS: {len(results)} backend/runtime fixtures, preserved workload and pair configuration review')
