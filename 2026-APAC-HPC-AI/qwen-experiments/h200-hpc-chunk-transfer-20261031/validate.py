"""Exercise native chunk/graph guards with synthetic altered historical logs."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys
import tempfile

D = Path(__file__).resolve().parent
Q = D.parent
prep = json.loads((D / 'preparation.json').read_text())
base = {r: (Q / f'runs/27783/{r}.log').read_text() for r in ('prefill-0', 'prefill-1', 'decode-0')}

def change(text, chunk, batches, wrong_max=False, wrong_buckets=False):
    lines = text.splitlines()
    indices = [i for i, line in enumerate(lines) if 'server_args=ServerArgs(' in line]
    assert len(indices) == 1
    i = indices[0]
    prefix, payload = lines[i].split('server_args=', 1)
    root = ast.parse(payload, mode='eval').body
    args = {kw.arg: kw for kw in root.keywords}
    args['chunked_prefill_size'].value = ast.Constant(chunk)
    graph = {kw.arg: kw.value for kw in args['cuda_graph_config'].value.keywords}
    pg = {kw.arg: kw for kw in graph['prefill'].keywords}
    pg['max_bs'].value = ast.Constant(4096 if wrong_max else chunk)
    pg['bs'].value = ast.parse(repr(batches[:-1] if wrong_buckets else batches), mode='eval').body
    lines[i] = prefix + 'server_args=' + ast.unparse(ast.fix_missing_locations(root))
    return '\n'.join(lines) + '\n'

results = []
for row in prep['bundles']:
    B = Q / row['bundle']
    cfg = json.loads((B / 'config.json').read_text())
    assert cfg['concurrency'] == 64 and cfg['prefill_moe_runner_backend'] == 'hpc_ops'
    assert cfg['decode_attention_backend'] == 'flashinfer' and cfg['decode_cuda_graph_batch_sizes'] == list(range(1, 65))
    assert cfg['prefill_expected_graph_batches'][-1] == row['chunk']
    assert hashlib.sha256((B / 'SHA256SUMS').read_bytes()).hexdigest() == row['manifest_sha256']
    subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=B, check=True, stdout=subprocess.DEVNULL)
    logs = dict(base)
    for role in ('prefill-0', 'prefill-1'):
        logs[role] = change(logs[role], row['chunk'], cfg['prefill_expected_graph_batches'])
    cases = [
        ('intended_chunk_and_graph', {}, True),
        ('wrong_chunk', {'prefill-0': logs['prefill-0'].replace(f"chunked_prefill_size={row['chunk']},", 'chunked_prefill_size=4096,')}, False),
        ('wrong_graph_max', {'prefill-0': change(base['prefill-0'], row['chunk'], cfg['prefill_expected_graph_batches'], wrong_max=True)}, False),
        ('missing_graph_bucket', {'prefill-1': change(base['prefill-1'], row['chunk'], cfg['prefill_expected_graph_batches'], wrong_buckets=True)}, False),
        ('wrong_runner', {'prefill-0': logs['prefill-0'].replace("moe_runner_backend='hpc_ops',", "moe_runner_backend='deep_gemm',")}, False),
        ('missing_prefill_module_receipt', {'prefill-0': logs['prefill-0'].replace('PREFILL_HPC_OPS_PREFLIGHT_PASSED', 'MISSING_PREFLIGHT')}, False),
        ('wrong_decode_attention', {'decode-0': logs['decode-0'].replace("decode_attention_backend='flashinfer',", "decode_attention_backend='fa3',")}, False),
        ('wrong_decode_capacity', {'decode-0': logs['decode-0'].replace('max_running_requests=256,', 'max_running_requests=64,')}, False),
    ]
    with tempfile.TemporaryDirectory(prefix='ap42-hpc-chunk-synthetic-fixtures-') as tmp:
        A = Path(tmp)
        for name, edits, wanted in cases:
            for role, text in {**logs, **edits}.items():
                (A / f'{role}.log').write_text(text)
            run = subprocess.run([sys.executable, '-B', str(B / 'check-fast-runtime.py'), str(A), 'control', '64'], text=True, capture_output=True)
            assert (run.returncode == 0) is wanted, (B.name, name, run.stdout, run.stderr)
            results.append(dict(bundle=B.name, case=name, expected_pass=wanted, passed=True))
(D / 'validation.json').write_text(json.dumps(dict(passed=True, fixtures=results,
    scope='CPU fixtures only. Historical logs altered synthetically, never new GPU evidence. Full client/output/source gates remain unchanged.'), indent=2) + '\n')
print(f'PASS: {len(results)} native chunk/graph/backend rejection fixtures')
