"""Read-only audit of own completed chunk8192 experiment; never submits work."""
import ast
import datetime
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT = Path(__file__).resolve().parent
RUN = ROOT / 'runs/23906'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
registry = json.loads((ROOT / 'serving-tuning/registry.json').read_text())
entry = next(e for e in registry['entries'] if e['id'] == 's9-mnnvl-chunk8192-n52')
bundle = Path(entry['bundle'])
for name, digest in entry['payload_sha256'].items():
    assert sha(bundle / name) == sha(RUN / 'submitted' / name) == digest, name
check = subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=bundle,
                       capture_output=True, text=True, check=True)
(OUT / '23906-bundle-check.txt').write_text(check.stdout)
assert (OUT / '23906-stored.sbatch').read_bytes() == (bundle / 'job.sbatch').read_bytes()

def parse_args(text):
    line = next(l.split('server_args=', 1)[1] for l in text.splitlines()
                if 'server_args=ServerArgs(' in l)
    return {k.arg: ast.unparse(k.value) for k in ast.parse(line, mode='eval').body.keywords}

def graph(text):
    call = ast.parse(text, mode='eval').body
    result = {}
    for part in call.keywords:
        result[part.arg] = {k.arg: ast.literal_eval(k.value) for k in part.value.keywords}
    return result

logs = {}
for role in ['prefill-0', 'prefill-1', 'decode-0']:
    captured = OUT / ('23906-runtime-' + role + '.log')
    captured.write_bytes((RUN / (role + '.log')).read_bytes())
    logs[role] = captured.read_text()
comparisons = {}
for job in ['23778', '23839']:
    submitted = ROOT / 'runs' / job / 'submitted'
    common = [f for f in entry['payload_sha256'] if f not in ['config.json', 'worker.sh', 'job.sbatch']]
    assert len(common) == 11
    assert all(sha(submitted / f) == sha(RUN / 'submitted' / f) for f in common)
    before = (submitted / 'worker.sh').read_text()
    after = (RUN / 'submitted/worker.sh').read_text()
    assert before.replace('--chunked-prefill-size 4096', '--chunked-prefill-size 8192') == after
    (OUT / f'23906-vs-{job}-worker.diff').write_text(''.join(difflib.unified_diff(
        before.splitlines(True), after.splitlines(True), fromfile=job, tofile='23906')))
    comparisons[job] = {}
    for role, log in logs.items():
        baseline = parse_args((ROOT / 'runs' / job / (role + '.log')).read_text())
        actual = parse_args(log)
        delta = {k: [baseline.get(k), actual.get(k)] for k in baseline.keys() | actual.keys()
                 if baseline.get(k) != actual.get(k)}
        allowed = {'random_seed'}
        if role.startswith('prefill'):
            allowed |= {'chunked_prefill_size', 'cuda_graph_config'}
            assert actual['chunked_prefill_size'] == '8192'
            old, new = graph(baseline['cuda_graph_config']), graph(actual['cuda_graph_config'])
            assert old['decode'] == new['decode']
            assert old['prefill']['max_bs'] == 4096 and new['prefill']['max_bs'] == 8192
            assert old['prefill']['bs'] == [n for n in new['prefill']['bs'] if n <= 4096]
            assert new['prefill']['bs'][-1] == 8192
            assert {k:v for k,v in old['prefill'].items() if k not in ['max_bs','bs']} == {
                k:v for k,v in new['prefill'].items() if k not in ['max_bs','bs']}
        assert not set(delta) - allowed, (job, role, delta)
        comparisons[job][role] = delta
decode = logs['decode-0']
args = parse_args(decode)
assert args['cuda_graph_bs_decode'] == repr(list(range(1,65)))
assert args['flashinfer_allreduce_fusion_backend'] == "'mnnvl'"
assert args['decode_attention_backend'] == 'None'
assert args['enable_quant_communications'] == 'False'
assert args['kv_cache_dtype'] == "'auto'"
assert all('NIXL_PATCH_VERIFIED 912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f' in t for t in logs.values())
ranks = lambda pattern: sorted({int(n) for n in re.findall(pattern, decode)})
for name in ['pair-warmup.log', 'connection-warmup.log', 'router.log']:
    if (RUN / name).exists():
        (OUT / ('23906-runtime-' + name)).write_bytes((RUN / name).read_bytes())
pair = OUT / '23906-runtime-pair-warmup.log'
result = dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), job='23906',
    payload_hashes_verified=True, stored_slurm_script_matches=True,
    common_files_identical_per_baseline=11, worker_only_chunk_cli_change=True,
    effective_server_arg_differences=comparisons,
    mnnvl_ranks=ranks(r'backend=mnnvl, rank=(\d+), world_size=8'),
    nixl_ucx_ranks=ranks(r'TP(\d+) EP\d+\] NIXL KVManager initialized with backend: UCX'),
    prefill_chunks=[8192,8192], prefill_graphs={role:graph(parse_args(logs[role])['cuda_graph_config'])
        for role in ['prefill-0','prefill-1']}, decode_graph_sizes=list(range(1,65)),
    pair_warmup_complete_at_snapshot=pair.exists() and 'ALL 2 P/D paths initialized' in pair.read_text(),
    performance_result_claimed=False, accuracy_verified=False,
    scope='Copied terminal logs; final seals independently rehashed by review-chunk8192.py.',
    snapshots=[dict(path=p.name, bytes=p.stat().st_size, sha256=sha(p))
               for p in sorted(OUT.glob('23906-runtime-*.log'))])
(OUT / 'runtime-review.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['effective_server_arg_differences',
    'snapshots','decode_graph_sizes','prefill_graphs']},indent=2))
