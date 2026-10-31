"""Reject incorrect phase activation receipts without pretending host Torch exists."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

D = Path(__file__).resolve().parent
Q = D.parent
prep = json.loads((D / 'preparation.json').read_text())
base = {role: (Q / f'runs/27777/{role}.log').read_text()
        for role in ('prefill-0', 'prefill-1', 'decode-0')}
results = []
for row in prep['bundles']:
    B = Q / row['bundle']
    cfg = json.loads((B / 'config.json').read_text())
    assert cfg['concurrency'] == 64 and cfg['arm'] == 'control'
    assert hashlib.sha256((B / 'SHA256SUMS').read_bytes()).hexdigest() == row['manifest_sha256']
    subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=B, check=True, stdout=subprocess.DEVNULL)
    for name in prep['unchanged_files']:
        assert (B / name).read_bytes() == (Q / 'runs/27777/submitted-payload' / name).read_bytes()
    logs = {}
    for role in base:
        wanted = cfg['phase_inference_mode']['prefill' if role.startswith('prefill') else 'decode']
        logs[role] = base[role] + f'\nDYNAMIC_GRAD_MODE_PREFLIGHT_PASSED inference_mode={wanted}\n'
    cases = [
        ('intended_phase_receipts', {}, True),
        ('missing_decode_receipt', {'decode-0': base['decode-0']}, False),
        ('wrong_decode_mode', {'decode-0': logs['decode-0'].replace(
            f"inference_mode={row['decode_inference_mode']}", f"inference_mode={not row['decode_inference_mode']}")}, False),
        ('wrong_prefill_mode', {'prefill-0': logs['prefill-0'].replace(
            f"inference_mode={row['prefill_inference_mode']}", f"inference_mode={not row['prefill_inference_mode']}")}, False),
        ('duplicate_mode_receipt', {'prefill-1': logs['prefill-1'] +
            f"DYNAMIC_GRAD_MODE_PREFLIGHT_PASSED inference_mode={row['prefill_inference_mode']}\n"}, False),
        ('unrelated_decode_backend', {'decode-0': logs['decode-0'].replace(
            "decode_attention_backend='flashinfer',", "decode_attention_backend='fa3',")}, False),
        ('missing_rank_graph', {'decode-0': '\n'.join(line for line in logs['decode-0'].splitlines()
            if not ('TP7 EP7]' in line and 'Capture target decode CUDA graph end.' in line))}, False),
    ]
    with tempfile.TemporaryDirectory(prefix='ap42-phase-mode-synthetic-fixtures-') as tmp:
        A = Path(tmp)
        for name, edits, accepted in cases:
            for role, text in {**logs, **edits}.items():
                (A / f'{role}.log').write_text(text)
            r = subprocess.run([sys.executable, '-B', str(B / 'check-fast-runtime.py'), str(A), 'control', '64'],
                               text=True, capture_output=True)
            assert (r.returncode == 0) is accepted, (B.name, name, r.stdout, r.stderr)
            results.append(dict(bundle=B.name, case=name, expected_pass=accepted, passed=True))
workers = [(Q / row['bundle'] / 'worker.sh').read_text() for row in prep['bundles']]
normalised = []
for text in workers:
    for value in ('0', '1'):
        text = text.replace('export SGLANG_ENABLE_TORCH_INFERENCE_MODE=' + value,
                            'export SGLANG_ENABLE_TORCH_INFERENCE_MODE=PHASE_VALUE')
    normalised.append(text)
assert len(set(normalised)) == 1, 'Worker difference is not phase selection only'
(D / 'validation.json').write_text(json.dumps(dict(passed=True, fixtures=results,
    workers_differ_only_phase_flags=True, host_native_torch_execution='NOT_AVAILABLE_NOT_CLAIMED',
    real_provider_GPU_acceptance='UNKNOWN_UNTIL_ALLOCATED_NATIVE_PREFLIGHT',
    scope='CPU synthetic gate tests and source/worker/workload checks, not native Torch or serving proof.'), indent=2) + '\n')
print(f'PASS: {len(results)} phase/backend/graph gate fixtures; workers differ only phase flags')
