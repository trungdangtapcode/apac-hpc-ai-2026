"""Derive one H100 placement-observation baseline from the frozen off control."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

O = Path(__file__).resolve().parent
R = O.parent
P = R / 'nscc-pbs'
source = P / 'h100-prefetch-confirm-off-second-77'
bundle = P / 'h100-worker-locality-n54-78'
assert not bundle.exists(), 'Never overwrite an existing payload'
assert json.loads((R / 'cpu-gpu-locality-20261020/worker-capture-validation.json').read_text())['passed']
assert json.loads((R / 'startup-prefetch-confirm-20261020/222419.pbs111-review.json').read_text())['state'] == 'LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=source, capture_output=True, check=True)
shutil.copytree(source, bundle, ignore=shutil.ignore_patterns('__pycache__'))
for filename in ('capture-worker-locality.py', 'request-worker-locality.py'):
    shutil.copy2(R / 'cpu-gpu-locality-20261020' / filename, bundle / filename)
for filename in ('benchmark.pbs', 'benchmark.sh', 'topology-job.sh'):
    path = bundle / filename
    path.write_text(path.read_text().replace(source.name, bundle.name))
worker = (bundle / 'worker.sh').read_text()
anchor = 'extra=()\n'
assert worker.count(anchor) == 1
worker = worker.replace(anchor, '''# Read owned worker masks once before official client warmup; do not change binding.
python3 "$QWEN_BUNDLE/capture-worker-locality.py" --root "$$" --role "$name" \\
  --artifact "$QWEN_ARTDIR" --timeout 900 >"$QWEN_ARTDIR/$name-locality.log" 2>&1 &
echo "WORKER_LOCALITY_OBSERVER pid=$! role=$name root=$$"
''' + anchor)
(bundle / 'worker.sh').write_text(worker)
path = bundle / 'topology-job.sh'
topology = path.read_text()
anchor = 'echo "ALL_PAIRS_WARM after ${SECONDS}s"\n'
assert topology.count(anchor) == 1
topology = topology.replace(anchor, anchor + '''python3 "$BUNDLE/request-worker-locality.py" "$ART" "$BUNDLE/placement.tsv" \\
  >"$ART/worker-locality-request.log" 2>&1
echo "WORKER_LOCALITY_CAPTURE_DONE after ${SECONDS}s"
''')
path.write_text(topology)
config = json.loads((bundle / 'config.json').read_text())
config.update(experiment=bundle.name, source_experiment=source.name,
              purpose='Collect actual full-serving H100 worker affinity before any NUMA binding intervention',
              changed_factor={'worker_locality_capture': 'Read-only before official client'},
              source_job='222420.pbs111', reference_jobs=['222281.pbs111', '222419.pbs111', '222420.pbs111'],
              worker_locality_capture=True, cpu_binding_changed=False, scored_worker_cpu_sampling=False)
(bundle / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
changed = []
allowed = {'config.json', 'benchmark.pbs', 'benchmark.sh', 'topology-job.sh', 'worker.sh',
           'capture-worker-locality.py', 'request-worker-locality.py'}
for path in bundle.iterdir():
    if not path.is_file() or path.name == 'SHA256SUMS':
        continue
    if not (source / path.name).exists() or path.read_bytes() != (source / path.name).read_bytes():
        changed.append(path.name)
        assert path.name in allowed, path
    if path.suffix in ('.sh', '.pbs'):
        subprocess.run(['bash', '-n', str(path)], check=True)
    if path.suffix == '.py':
        ast.parse(path.read_text())
assert worker.split('extra=()\n', 1)[1] == (source / 'worker.sh').read_text().split('extra=()\n', 1)[1]
for filename in ('pbs-container.sh', 'pbs-shim.sh', 'pbs-exec.py', 'placement.tsv', 'nixl-conn.py',
                 'resource-sampler.py', 'profile-serving.py', 'long-context-check.py', 'output-smoke.py',
                 'prefetch-weights.py', 'warm-topology.py', 'client-with-longcheck.sh'):
    assert (bundle / filename).read_bytes() == (source / filename).read_bytes(), filename
assert (bundle / 'benchmark.sh').read_text() == (source / 'benchmark.sh').read_text().replace(source.name, bundle.name)
hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted(bundle.iterdir()) if p.is_file() and p.name != 'SHA256SUMS'}
(bundle / 'SHA256SUMS').write_text(''.join(value + '  ' + name + '\n' for name, value in hashes.items()))
subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=bundle, capture_output=True, check=True)
pilot = dict(id=bundle.name, platform='H100', bundle=str(bundle), planned_ns=[54], max_su=1024,
             minutes=30, payload_sha256=hashes, resource_monitor=True, diagnostic_profile=True,
             scheduler_recv_interval_decode=1, prefill_policy='round_robin', startup_prefetch_mode='off',
             cpu_binding_changed=False, purpose=config['purpose'])
(O / 'pilots.json').write_text(json.dumps([pilot], indent=2) + '\n')
(O / 'validation.json').write_text(json.dumps(dict(passed=True, changed_files=changed,
    model_arguments_unchanged=True, existing_cpu_wrapper_bytes_unchanged=True,
    official_client_bytes_unchanged_except_bundle_labels=True, cpu_binding_changed=False), indent=2) + '\n')
for filename in ('review-pbs.py', 'inspect-pbs.py', 'inspect-server-state.py', 'review-startup.py'):
    shutil.copy2(R / 'startup-prefetch-confirm-20261020' / filename, O / filename)
with tarfile.open(O / 'pbs-bundle.tar.gz', 'w:gz') as archive:
    archive.add(bundle, arcname=bundle.name)
print('Prepared H100 locality baseline:', bundle.name)
