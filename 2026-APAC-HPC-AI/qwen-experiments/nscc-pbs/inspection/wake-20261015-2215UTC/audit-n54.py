"""Read-only preflight of the two already-submitted N54 jobs; no GPU or submission."""
import datetime, hashlib, json, re, subprocess
from pathlib import Path

ROOT = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT = Path(__file__).resolve().parent
state = json.loads((ROOT/'serving-tuning/registry.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
results = []
for job, baselines in [('23924', ['23778', '23839']), ('23934', ['23780', '23859'])]:
    entry = next(e for e in state['entries'] if any(a['job'] == job for a in e['attempts']))
    attempt = next(a for a in entry['attempts'] if a['job'] == job)
    bundle = Path(attempt['bundle'])
    hashes = {f: sha(bundle/f) == h for f, h in entry['payload_sha256'].items()}
    assert all(hashes.values())
    seal = subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=bundle, capture_output=True, text=True)
    (OUT/f'{job}-sha256.txt').write_text(seal.stdout+seal.stderr)
    assert seal.returncode == 0
    stored = OUT/f'{job}-stored.sbatch'
    proc = subprocess.run(['scontrol', 'write', 'batch_script', job, str(stored)], capture_output=True, text=True)
    (OUT/f'{job}-scontrol.txt').write_text(proc.stdout+proc.stderr)
    assert proc.returncode == 0 and stored.read_bytes() == (bundle/'job.sbatch').read_bytes()
    matched = []
    for base in baselines:
        source = ROOT/'runs'/base/'submitted'
        common = {f: sha(source/f) == sha(bundle/f) for f in hashes if f not in ['config.json', 'job.sbatch']}
        assert len(common) == 12 and all(common.values())
        ca, cb = read(source/'config.json'), read(bundle/'config.json')
        diff = {k: [ca.get(k), cb.get(k)] for k in ca.keys() | cb.keys() if ca.get(k) != cb.get(k)}
        assert set(diff) == {'experiment', 'purpose', 'concurrency'}
        assert ca['concurrency'] == [52] and cb['concurrency'] == [54]
        def normalized(p):
            text = p.read_text()
            text = re.sub(r'^#SBATCH -J .*$', '#SBATCH -J <name>', text, flags=re.M)
            text = re.sub(r'^export QWEN_BUNDLE=.*$', 'export QWEN_BUNDLE=<bundle>', text, flags=re.M)
            return re.sub(r'^export QWEN_TUNE_NS=\d+$', 'export QWEN_TUNE_NS=<load>', text, flags=re.M)
        assert normalized(source/'job.sbatch') == normalized(bundle/'job.sbatch')
        summary = read(ROOT/'runs'/base/'summary.json')[0]
        matched.append(dict(job=base, identical_operational_files=common, config_differences=diff,
                            good_tokens_s=summary['good_output_tokens_s'],
                            sla_fraction=summary['good_request_fraction'],
                            ttft_ms=summary['ttft_avg_ms'], itl_ms=summary['itl_avg_ms']))
    means = {k: sum(m[k] for m in matched)/2 for k in ['good_tokens_s', 'sla_fraction', 'ttft_ms', 'itl_ms']}
    results.append(dict(job=job, registry_state=attempt['state'], payload_hashes=hashes,
                        frozen_seal_pass=True, stored_script_matches=True, baselines=matched,
                        baseline_means=means, effective_load=54,
                        inherited_metadata_warning='matched_concurrency=52 and older source/control fields are provenance; launcher QWEN_TUNE_NS=54 and config concurrency=[54]. Runtime unverified.'))
result = dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              scope='CPU read-only audit and result interpretation preparation; no benchmark, submission or quality promotion',
              all_checks_pass=True, candidates=results, accuracy_verified=False)
with (OUT/'n54-preflight-review.json').open('x') as f:
    json.dump(result, f, indent=2); f.write('\n')
print(json.dumps({r['job']: r['baseline_means'] for r in results}, indent=2))
