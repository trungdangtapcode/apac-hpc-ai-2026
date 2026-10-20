"""Derive one immutable H200 observed baseline without changing model computation."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import subprocess

O = Path(__file__).resolve().parent
R = O.parent
source = R / 'serving-tuning-10/s21-dg8192-hpc-n60-control'
bundle = R / 'serving-tuning-10/s22-worker-locality-n60'
assert not bundle.exists(), 'Do not replace an existing or submitted payload'
assert json.loads((R / 'cpu-gpu-locality-20261020/worker-capture-validation.json').read_text())['passed']
assert json.loads((R / 'research-followup-20261020-0530/24927-review.json').read_text())['state'] == 'LOCAL_PROTOCOL_SLA_OUTPUT_PASS'
subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=source, capture_output=True, check=True)
shutil.copytree(source, bundle, ignore=shutil.ignore_patterns('__pycache__'))
for filename in ('capture-worker-locality.py', 'request-worker-locality.py'):
    shutil.copy2(R / 'cpu-gpu-locality-20261020' / filename, bundle / filename)
config = json.loads((bundle / 'config.json').read_text())
config.update(experiment=bundle.name, source_experiment=source.name,
              source_job='24927', reference_jobs=['24927', '24964'],
              purpose='Full-serving CPU/GPU locality capture before any binding intervention',
              changed_factor={'worker_locality_capture': 'Read-only before official client warmup'},
              control_experiment=source.name, fresh_control_job=None,
              worker_locality_capture=True, cpu_binding_changed=False,
              scored_worker_cpu_sampling=False)
(bundle / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
job = (bundle / 'job.sbatch').read_text().replace(source.name, bundle.name)
(bundle / 'job.sbatch').write_text(job)
worker = (bundle / 'worker.sh').read_text()
anchor = 'extra=()\n'
assert worker.count(anchor) == 1
worker = worker.replace(anchor, '''# This observer reads owned process affinity only and exits before scored traffic.
python3 "$QWEN_BUNDLE/capture-worker-locality.py" --root "$$" --role "$name" \\
  --artifact "$QWEN_ARTDIR" --timeout 700 >"$QWEN_ARTDIR/$name-locality.log" 2>&1 &
echo "WORKER_LOCALITY_OBSERVER pid=$! role=$name root=$$"
''' + anchor)
(bundle / 'worker.sh').write_text(worker)
topology = (bundle / 'topology-job.sh').read_text()
anchor = 'echo "ALL_PAIRS_WARM after ${SECONDS}s"\n'
assert topology.count(anchor) == 1
topology = topology.replace(anchor, anchor + '''# No scored traffic is active while worker locality is captured.
python3 "$BUNDLE/request-worker-locality.py" "$ART" "$BUNDLE/placement.tsv" \\
  >"$ART/worker-locality-request.log" 2>&1
echo "WORKER_LOCALITY_CAPTURE_DONE after ${SECONDS}s"
''')
(bundle / 'topology-job.sh').write_text(topology)
allowed = {'SHA256SUMS', 'config.json', 'job.sbatch', 'worker.sh', 'topology-job.sh',
           'capture-worker-locality.py', 'request-worker-locality.py'}
changed = []
for path in bundle.iterdir():
    if not path.is_file() or path.name == 'SHA256SUMS':
        continue
    original = source / path.name
    if not original.exists() or original.read_bytes() != path.read_bytes():
        changed.append(path.name)
        assert path.name in allowed, path
    if path.suffix == '.sh' or path.suffix == '.sbatch':
        subprocess.run(['bash', '-n', str(path)], check=True)
    if path.suffix == '.py':
        ast.parse(path.read_text())
for immutable in ('benchmark.sh', 'resource-sampler.py', 'phase-marker.py', 'nixl-conn.py',
                  'nixl-ondemand.patch', 'profile-serving.py', 'output-smoke.py', 'long-context-check.py',
                  'warm-topology.py', 'placement.tsv'):
    assert (source / immutable).read_bytes() == (bundle / immutable).read_bytes(), immutable
assert worker.split('extra=()\n', 1)[1] == (source / 'worker.sh').read_text().split('extra=()\n', 1)[1]
manifest = ''.join(hashlib.sha256(f.read_bytes()).hexdigest() + '  ' + f.name + '\n'
                   for f in sorted(bundle.iterdir()) if f.is_file() and f.name != 'SHA256SUMS')
(bundle / 'SHA256SUMS').write_text(manifest)
subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=bundle, capture_output=True, check=True)
(O / 'validation.json').write_text(json.dumps(dict(passed=True, changed_files=changed,
    serving_arguments_unchanged=True, benchmark_bytes_unchanged=True,
    cpu_binding_changed=False, all_shell_syntax_passed=True, all_python_ast_passed=True,
    source_bundle=str(source), bundle=str(bundle)), indent=2) + '\n')
pilot = dict(id=bundle.name, platform='H200', bundle=str(bundle), planned_ns=[60],
             purpose=config['purpose'], state='PREPARED', cpu_binding_changed=False,
             reference_jobs=['24927', '24964'], time_limit_minutes=17, gpus=16)
(O / 'pilot.json').write_text(json.dumps(pilot, indent=2) + '\n')
print('Prepared and validated', bundle)
