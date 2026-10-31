"""Port H100 both-HPC-Ops/chunk4096 serving choices into the frozen H200 harness."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import subprocess

D = Path(__file__).resolve().parent
Q = D.parent
P = Q / 'serving-tuning-11/s110-h200-decode-flashinfer-transfer'
subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=P, check=True,
               stdout=subprocess.DEVNULL)
records = []
for number, n in [(112, 54), (113, 64)]:
    label = f's{number}-h200-h100-recipe-n{n}'
    B = Q / 'serving-tuning-11' / label
    shutil.copytree(P, B)
    cfg = json.loads((P / 'config.json').read_text())
    cfg.update(experiment=label, label=label, source_parent_job=27777,
               source_parent=P.name, study_arm=f'h100_serving_recipe_n{n}',
               concurrency=n, prefill_moe_runner_backend='hpc_ops',
               prefill_chunked_prefill_size=4096,
               client_protocol=f'N{n} full60/120/30 then smoke/retrieval; official quality unknown',
               matched_pair='H100 serving recipe N54 versus N64; N64 compared with H200 incumbent as a coupled recipe',
               matched_control_job=27777, h100_recipe_evidence_jobs=[222048, 225227],
               performance_or_GPU_acceptance='UNKNOWN')
    cfg['performance_gate'] = cfg['performance_gate'].replace('N64', f'N{n}')
    (B / 'config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    text = (P / 'worker.sh').read_text()
    needle = 'extra=(--chunked-prefill-size 8192 --moe-runner-backend deep_gemm --cuda-graph-backend-prefill breakable)'
    assert text.count(needle) == 1
    text = text.replace(needle, 'extra=(--chunked-prefill-size 4096 --moe-runner-backend hpc_ops --cuda-graph-backend-prefill breakable)')
    # Check actual module availability on prefill as well as the inherited decode check.
    needle = 'if [[ $role == prefill ]]; then\n'
    assert text.count(needle) == 1
    text = text.replace(needle, needle + '''  python3 - <<'PREFILL_HPC_CHECK'
import torch, hpc
assert torch.cuda.get_device_capability()[0] == 9, 'Hopper GPU required'
assert hasattr(hpc, 'fuse_moe_blockwise'), 'Missing HPC-Ops FP8 kernel'
print('PREFILL_HPC_OPS_PREFLIGHT_PASSED', torch.cuda.get_device_name(), flush=True)
PREFILL_HPC_CHECK
''')
    (B / 'worker.sh').write_text(text)
    text = (P / 'check-fast-runtime.py').read_text()
    needle = "moe_runner_backend='deep_gemm',flashinfer_allreduce_fusion_backend='auto'"
    assert text.count(needle) == 1
    text = text.replace(needle, "moe_runner_backend=cfg['prefill_moe_runner_backend'],flashinfer_allreduce_fusion_backend='auto'")
    needle = '    for key,wanted in common.items():'
    assert text.count(needle) == 1
    text = text.replace(needle, '''    marker = 'PREFILL_HPC_OPS_PREFLIGHT_PASSED' if role.startswith('prefill') else 'HPC_OPS_PREFLIGHT_PASSED'
    if marker not in text: raise ValueError(f'{role}: actual HPC-Ops module/device preflight missing')
''' + needle)
    (B / 'check-fast-runtime.py').write_text(text)
    text = (P / 'topology-job.sh').read_text()
    assert text.count('env QWEN_TUNE_NS=64 ') == 1
    text = text.replace('env QWEN_TUNE_NS=64 ', f'env QWEN_TUNE_NS={n} ')
    text = text.replace('no N64 performance-client budget remains', f'no N{n} performance-client budget remains')
    (B / 'topology-job.sh').write_text(text)
    expected = json.loads((P / 'expected-input-config.json').read_text())
    for phase in expected['phases']:
        phase['concurrency'] = n
    expected['runtime']['workers'] = n
    (B / 'expected-input-config.json').write_text(json.dumps(expected, indent=2) + '\n')
    text = (P / 'job.sbatch').read_text().replace(P.name, label)
    text = text.replace('#SBATCH -J ap42-s110-flashinfer', f'#SBATCH -J ap42-s{number}-h100n{n}')
    (B / 'job.sbatch').write_text(text)
    (B / 'README.md').write_bytes((D / 'PLAN.md').read_bytes())
    unchanged = ['check-performance.py', 'benchmark.sh', 'performance_gates.py',
                 'native-container.sh', 'nixl-conn.py', 'kv_geometry.py',
                 'validate_kv_geometry.py', 'warm-topology.py', 'warmup_semantic.py',
                 'resource-sampler.py', 'reference-output-smoke.json']
    for name in unchanged:
        assert (B / name).read_bytes() == (P / name).read_bytes(), name
    for path in B.rglob('*'):
        if path.suffix == '.py':
            ast.parse(path.read_text())
        if path.suffix in ('.sh', '.sbatch'):
            subprocess.run(['bash', '-n', str(path)], check=True)
    files = sorted(p for p in B.rglob('*') if p.is_file()
                   and '__pycache__' not in p.parts and p.name != 'SHA256SUMS')
    (B / 'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()
        + '  ' + str(p.relative_to(B)) + '\n' for p in files))
    records.append(dict(bundle=str(B.relative_to(Q)), concurrency=n,
                        manifest_sha256=hashlib.sha256((B / 'SHA256SUMS').read_bytes()).hexdigest()))
(D / 'preparation.json').write_text(json.dumps(dict(
    state='PREPARED_NOT_SUBMITTED', bundles=records, unchanged_files=unchanged,
    parent_manifest_sha256=hashlib.sha256((P / 'SHA256SUMS').read_bytes()).hexdigest()), indent=2) + '\n')
print(json.dumps(records, indent=2))
