"""Freeze current-native H200 ports of two measured H100 HPC chunk settings."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import subprocess

D = Path(__file__).resolve().parent
Q = D.parent
P = Q / 'runs/27783/submitted-payload'
subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=P, check=True, stdout=subprocess.DEVNULL)
text = (Q / 'runs/27777/prefill-0.log').read_text()
record = [line.split('server_args=', 1)[1] for line in text.splitlines() if 'server_args=ServerArgs(' in line]
assert len(record) == 1
args = {kw.arg: kw.value for kw in ast.parse(record[0], mode='eval').body.keywords}
graph = {kw.arg: kw.value for kw in args['cuda_graph_config'].keywords}
pg = {kw.arg: ast.literal_eval(kw.value) for kw in graph['prefill'].keywords}
assert pg['max_bs'] == 8192 and pg['backend'] == 'breakable'
records = []
for number, chunk, h100_job in [(114, 6144, 221828), (115, 8192, 222282)]:
    label = f's{number}-h200-hpc-prefill-chunk{chunk}'
    B = Q / 'serving-tuning-11' / label
    shutil.copytree(P, B)
    cfg = json.loads((P / 'config.json').read_text())
    cfg.update(experiment=label, label=label, source_parent_job=27783,
               source_parent='s113-h200-h100-recipe-n64',
               study_arm=f'hpc_prefill_chunk{chunk}', prefill_chunked_prefill_size=chunk,
               prefill_expected_graph_batches=[n for n in pg['bs'] if n <= chunk],
               matched_control_job=27783, incumbent_reference_job=27777,
               h100_recipe_evidence_jobs=[h100_job], performance_or_GPU_acceptance='UNKNOWN',
               matched_pair='HPC-Ops prefill chunk sensitivity versus27783; chunk8192 runner comparison versus27777')
    (B / 'config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    text = (P / 'worker.sh').read_text()
    needle = '--chunked-prefill-size 4096 --moe-runner-backend hpc_ops'
    assert text.count(needle) == 1
    (B / 'worker.sh').write_text(text.replace(needle, f'--chunked-prefill-size {chunk} --moe-runner-backend hpc_ops'))
    text = (P / 'check-fast-runtime.py').read_text()
    needle = "    if expected_pg=='breakable':\n"
    assert text.count(needle) == 1
    text = text.replace(needle, needle + """        if lit(pg,'max_bs',role)!=cfg['prefill_chunked_prefill_size'] or lit(pg,'bs',role)!=cfg['prefill_expected_graph_batches']:
            raise ValueError(f'{role}: native chunk-derived prefill graph maximum/buckets differ')
""")
    (B / 'check-fast-runtime.py').write_text(text)
    text = (P / 'job.sbatch').read_text().replace('s113-h200-h100-recipe-n64', label)
    text = text.replace('#SBATCH -J ap42-s113-h100n64', f'#SBATCH -J ap42-s{number}-hpc{chunk}')
    (B / 'job.sbatch').write_text(text)
    (B / 'README.md').write_bytes((D / 'PLAN.md').read_bytes())
    unchanged = ['topology-job.sh', 'benchmark.sh', 'check-performance.py', 'performance_gates.py',
                 'native-container.sh', 'nixl-conn.py', 'kv_geometry.py', 'validate_kv_geometry.py',
                 'warm-topology.py', 'warmup_semantic.py', 'resource-sampler.py',
                 'expected-input-config.json', 'reference-output-smoke.json']
    for name in unchanged:
        assert (B / name).read_bytes() == (P / name).read_bytes(), name
    for path in B.rglob('*'):
        if path.suffix == '.py':
            ast.parse(path.read_text())
        if path.suffix in ('.sh', '.sbatch'):
            subprocess.run(['bash', '-n', str(path)], check=True)
    files = sorted(p for p in B.rglob('*') if p.is_file() and p.name != 'SHA256SUMS' and '__pycache__' not in p.parts)
    (B / 'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()
        + '  ' + str(p.relative_to(B)) + '\n' for p in files))
    records.append(dict(bundle=str(B.relative_to(Q)), concurrency=64, chunk=chunk,
                        manifest_sha256=hashlib.sha256((B / 'SHA256SUMS').read_bytes()).hexdigest()))
(D / 'preparation.json').write_text(json.dumps(dict(state='PREPARED_NOT_SUBMITTED', bundles=records,
    unchanged_files=unchanged, parent_manifest_sha256=hashlib.sha256((P / 'SHA256SUMS').read_bytes()).hexdigest()), indent=2) + '\n')
print(json.dumps(records, indent=2))
