"""Freeze matched H200 decode-attention arms from reviewed control 27376."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import subprocess

D = Path(__file__).resolve().parent
Q = D.parent
P = Q / 'runs/27376/submitted-payload'
subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=P, check=True,
               stdout=subprocess.DEVNULL)
records = []
for number, backend in [(110, 'flashinfer'), (111, 'fa3')]:
    label = f's{number}-h200-decode-{backend}-transfer'
    B = Q / 'serving-tuning-11' / label
    shutil.copytree(P, B)
    cfg = json.loads((P / 'config.json').read_text())
    cfg.update(experiment=label, label=label, source_parent_job=27376,
               source_parent='s103-h200-cold-cache-control',
               study_arm='fresh_control' if backend == 'flashinfer' else 'fa3_decode',
               decode_attention_backend=backend,
               matched_pair='H200 FlashInfer versus FA3 decode; one serving factor changed',
               performance_or_GPU_acceptance='UNKNOWN', matched_control_job=None)
    (B / 'config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    text = (P / 'worker.sh').read_text()
    needle = '--decode-attention-backend flashinfer --moe-runner-backend hpc_ops'
    assert text.count(needle) == 1
    text = text.replace(needle, f'--decode-attention-backend {backend} --moe-runner-backend hpc_ops')
    (B / 'worker.sh').write_text(text)
    text = (P / 'check-fast-runtime.py').read_text()
    needle = "decode_attention_backend='flashinfer',flashinfer_allreduce_fusion_backend='mnnvl'"
    assert text.count(needle) == 1
    text = text.replace(needle, "decode_attention_backend=cfg['decode_attention_backend'],flashinfer_allreduce_fusion_backend='mnnvl'")
    needle = "'actual_cache_class':expected_cache"
    assert text.count(needle) == 1
    text = text.replace(needle, "'resolved_decode_attention_backend':common.get('decode_attention_backend'),'actual_cache_class':expected_cache")
    (B / 'check-fast-runtime.py').write_text(text)
    text = (P / 'job.sbatch').read_text().replace('s103-h200-cold-cache-control', label)
    text = text.replace('#SBATCH -J ap42-s103-ctrl', f'#SBATCH -J ap42-s{number}-{backend}')
    (B / 'job.sbatch').write_text(text)
    (B / 'README.md').write_bytes((D / 'PLAN.md').read_bytes())
    unchanged = ['topology-job.sh', 'check-performance.py', 'benchmark.sh',
                 'performance_gates.py', 'native-container.sh', 'nixl-conn.py',
                 'kv_geometry.py', 'validate_kv_geometry.py', 'warm-topology.py',
                 'warmup_semantic.py', 'resource-sampler.py',
                 'expected-input-config.json', 'reference-output-smoke.json']
    for name in unchanged:
        assert (B / name).read_bytes() == (P / name).read_bytes(), name
    for path in B.rglob('*'):
        if path.suffix == '.py':
            ast.parse(path.read_text())
        if path.suffix in ('.sh', '.sbatch'):
            subprocess.run(['bash', '-n', str(path)], check=True)
    files = sorted(p for p in B.rglob('*') if p.is_file()
                   and '__pycache__' not in p.parts and p.name != 'SHA256SUMS')
    (B / 'SHA256SUMS').write_text(''.join(
        hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + str(p.relative_to(B)) + '\n'
        for p in files))
    records.append(dict(bundle=str(B.relative_to(Q)), backend=backend,
                        manifest_sha256=hashlib.sha256((B / 'SHA256SUMS').read_bytes()).hexdigest()))
(D / 'preparation.json').write_text(json.dumps(dict(
    state='PREPARED_NOT_SUBMITTED', bundles=records,
    parent_manifest_sha256=hashlib.sha256((P / 'SHA256SUMS').read_bytes()).hexdigest(),
    unchanged_files=unchanged), indent=2) + '\n')
print(json.dumps(records, indent=2))
