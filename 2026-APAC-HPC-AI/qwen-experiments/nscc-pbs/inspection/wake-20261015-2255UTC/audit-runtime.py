"""Read-only runtime/payload audit; captured log prefixes are not final seals."""
import ast
import datetime
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT = Path(__file__).resolve().parent
RUN = ROOT / 'runs/23904'
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
registry = json.loads((ROOT / 'serving-tuning/registry.json').read_text())
entry = next(e for e in registry['entries'] if e['id'] == 's9-mnnvl-flashinfer-n52')
bundle = Path(entry['bundle'])
assert all(sha(bundle / f) == h for f, h in entry['payload_sha256'].items())
assert all(sha(RUN / 'submitted' / f) == h for f, h in entry['payload_sha256'].items())
check = subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=bundle,
                       capture_output=True, text=True, check=True)
(OUT / '23904-bundle-check.txt').write_text(check.stdout)
subprocess.run(['scontrol', 'write', 'batch_script', '23904', str(OUT / '23904-stored.sbatch')],
               capture_output=True, text=True, check=True)
assert (OUT / '23904-stored.sbatch').read_bytes() == (bundle / 'job.sbatch').read_bytes()

def parse_args(text):
    line = next(l.split('server_args=', 1)[1] for l in text.splitlines()
                if 'server_args=ServerArgs(' in l)
    return {k.arg: ast.unparse(k.value) for k in ast.parse(line, mode='eval').body.keywords}

logs = {}
for role in ['prefill-0', 'prefill-1', 'decode-0']:
    source = RUN / (role + '.log')
    captured = OUT / ('23904-runtime-' + source.name)
    captured.write_bytes(source.read_bytes())
    logs[role] = captured.read_text()

comparisons = {}
for job in ['23778', '23839']:
    comparisons[job] = {}
    for role, text in logs.items():
        baseline = parse_args((ROOT / 'runs' / job / (role + '.log')).read_text())
        actual = parse_args(text)
        diffs = {k: [baseline.get(k), actual.get(k)] for k in baseline.keys() | actual.keys()
                 if baseline.get(k) != actual.get(k)}
        allowed = {'random_seed', 'decode_attention_backend'} if role == 'decode-0' else {'random_seed'}
        assert not set(diffs) - allowed, (job, role, diffs)
        comparisons[job][role] = diffs

decode = logs['decode-0']
mnnvl = sorted({int(n) for n in re.findall(r'backend=mnnvl, rank=(\d+), world_size=8', decode)})
attention = sorted({int(n) for n in re.findall(r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3', decode)})
nixl = sorted({int(n) for n in re.findall(r'TP(\d+) EP\d+\] NIXL KVManager initialized with backend: UCX', decode)})
assert mnnvl == attention == nixl == list(range(8))
assert all(parse_args(logs[role])['chunked_prefill_size'] == '4096'
           for role in ['prefill-0', 'prefill-1'])
args = parse_args(decode)
assert args['cuda_graph_bs_decode'] == repr(list(range(1, 65)))
assert args['flashinfer_allreduce_fusion_backend'] == "'mnnvl'"
assert args['decode_attention_backend'] == "'flashinfer'"
assert args['enable_quant_communications'] == 'False'
assert args['kv_cache_dtype'] == "'auto'"  # Same as both validated BF16-KV baselines.
assert all('NIXL_PATCH_VERIFIED 912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f' in t for t in logs.values())
pair = RUN / 'pair-warmup.log'
if pair.exists():
    (OUT / '23904-runtime-pair-warmup.log').write_bytes(pair.read_bytes())
pair_complete = pair.exists() and 'ALL 2 P/D paths initialized' in pair.read_text()

result = dict(reviewed_utc=now(), job='23904', payload_hashes_verified=True,
              stored_slurm_script_matches=True, effective_server_arg_differences=comparisons,
              mnnvl_ranks=mnnvl, flashinfer_decode_ranks=attention, nixl_ucx_ranks=nixl,
              prefill_chunks=[4096, 4096], decode_graph_sizes=list(range(1,65)),
              pair_warmup_complete_at_snapshot=pair_complete,
              engine_seed_note='Unpinned engine random_seed differs across allocations; AIPerf random-seed=2026 is separate. No payload/seed changes made.',
              scope='Runtime initialization only. Captured growing logs are timestamped prefixes, not terminal artifact seals or performance/accuracy evidence.',
              performance_result_claimed=False, accuracy_verified=False,
              snapshots=[dict(path=p.name, bytes=p.stat().st_size, sha256=sha(p))
                         for p in sorted(OUT.glob('23904-runtime-*.log'))])
(OUT / 'runtime-review.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['snapshots', 'effective_server_arg_differences','decode_graph_sizes']},indent=2))
