"""Prepare an equal-budget, serial H100 legacy versus balanced CPU-envelope pair."""
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
source = P / 'h100-worker-locality-n54-78'
assert json.loads((O / 'policy-validation.json').read_text())['passed']
assert json.loads((R / 'worker-locality-h100-20261020/locality-review.json').read_text())['state'] == 'SEALED_FULL_SERVING_AND_WORKER_MAPPING_PASS'
snapshot = Path(json.loads((R / 'worker-locality-h100-20261020/collect-222435.json').read_text())['destination'])
reference = snapshot / 'runs/222435.pbs111/output-smoke.json'
seal = json.loads((snapshot / 'evidence-sha256.json').read_text())
assert hashlib.sha256(reference.read_bytes()).hexdigest() == seal[str(reference.relative_to(snapshot))]
shutil.copy2(reference, O / 'reference-output-smoke.json')
subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=source, capture_output=True, check=True)
pilots = []
for number, mode in [(79, 'legacy'), (80, 'balanced')]:
    name = f'h100-cpu-envelope-{mode}-n54-{number}'
    bundle = P / name
    assert not bundle.exists(), 'Never replace an existing payload'
    shutil.copytree(source, bundle, ignore=shutil.ignore_patterns('__pycache__'))
    for filename in ('worker-cpu-envelope.py', 'check-control.py', 'reference-output-smoke.json'):
        shutil.copy2(O / filename, bundle / filename)
    for filename in ('benchmark.pbs', 'benchmark.sh', 'topology-job.sh'):
        path = bundle / filename
        path.write_text(path.read_text().replace(source.name, name))
    path = bundle / 'benchmark.pbs'
    text = path.read_text().replace('set -euo pipefail\n', 'set -euo pipefail\nexport QWEN_CPU_ENVELOPE_MODE=' + mode + '\n', 1)
    if mode == 'balanced':
        anchor = 'exec bash "$QWEN_BUNDLE/topology-job.sh"'
        assert text.count(anchor) == 1
        text = text.replace(anchor, 'python3 "$QWEN_BUNDLE/check-control.py" "$SLURM_SUBMIT_DIR/runs/${QWEN_CONTROL_JOB:?}"\n' + anchor)
    path.write_text(text)
    path = bundle / 'pbs-container.sh'
    text = path.read_text()
    anchor = 'gpu_list=$(python3'
    assert text.count(anchor) == 1
    insertion = '''# Metadata queries may see the allocation mask; model exec restores the selected task budget.
allocation_cpu_list=$(python3 -c 'import os;print(",".join(map(str,sorted(os.sched_getaffinity(0)))))')
legacy_cpu_list=$cpu_list
if ((count>0)); then cpu_list=$allocation_cpu_list; fi
env_json=$(python3 - "$env_json" "$allocation_cpu_list" "$legacy_cpu_list" "$cpus" "$count" <<'PYCPUENV'
import json,sys
data=json.loads(sys.argv[1]);data.update(QWEN_ALLOCATION_CPU_MASK=sys.argv[2],QWEN_LEGACY_TASK_CPU_MASK=sys.argv[3],QWEN_TASK_CPU_BUDGET=sys.argv[4],QWEN_TASK_GPU_COUNT=sys.argv[5])
print(json.dumps(data))
PYCPUENV
)
'''
    path.write_text(text.replace(anchor, insertion + anchor))
    path = bundle / 'pbs-exec.py'
    text = path.read_text()
    anchor = 'os.execvp(sys.argv[3],sys.argv[3:])'
    assert text.count(anchor) == 1
    path.write_text(text.replace(anchor, '''if int(os.environ.get('QWEN_TASK_GPU_COUNT','0')):
    import importlib.util
    helper=Path(__file__).with_name('worker-cpu-envelope.py')
    specification=importlib.util.spec_from_file_location('cpu_envelope',helper)
    envelope=importlib.util.module_from_spec(specification);specification.loader.exec_module(envelope)
    envelope.apply_envelope(sys.argv[5])
''' + anchor))
    config = json.loads((bundle / 'config.json').read_text())
    config.update(experiment=name, source_experiment=source.name, source_job='222435.pbs111',
                  cpu_envelope_mode=mode, cpu_binding_changed=(mode == 'balanced'),
                  changed_factor={'outer_task_cpu_envelope': mode},
                  purpose='Equal-budget task CPU envelope comparison with native SGLang NUMA behaviour retained')
    (bundle / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
    for filename in ('worker.sh', 'capture-worker-locality.py', 'request-worker-locality.py',
                     'resource-sampler.py', 'profile-serving.py', 'output-smoke.py',
                     'long-context-check.py', 'placement.tsv', 'nixl-conn.py', 'pbs-shim.sh',
                     'client-with-longcheck.sh', 'prefetch-weights.py', 'warm-topology.py'):
        assert (bundle / filename).read_bytes() == (source / filename).read_bytes(), filename
    assert (bundle / 'benchmark.sh').read_text() == (source / 'benchmark.sh').read_text().replace(source.name, name)
    for path in bundle.iterdir():
        if path.suffix in ('.sh', '.pbs'):
            subprocess.run(['bash', '-n', str(path)], check=True)
        if path.suffix == '.py':
            ast.parse(path.read_text())
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(bundle.iterdir()) if path.is_file() and path.name != 'SHA256SUMS'}
    (bundle / 'SHA256SUMS').write_text(''.join(value + '  ' + key + '\n' for key, value in hashes.items()))
    subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=bundle, capture_output=True, check=True)
    pilots.append(dict(id=name, platform='H100', bundle=str(bundle), planned_ns=[54], minutes=30,
                       max_su=1024, paired_role='control' if mode == 'legacy' else 'candidate',
                       cpu_envelope_mode=mode, payload_sha256=hashes, resource_monitor=True,
                       diagnostic_profile=True, scheduler_recv_interval_decode=1,
                       prefill_policy='round_robin', startup_prefetch_mode='off'))
assert (Path(pilots[0]['bundle']) / 'pbs-exec.py').read_bytes() == (Path(pilots[1]['bundle']) / 'pbs-exec.py').read_bytes()
assert (Path(pilots[0]['bundle']) / 'pbs-container.sh').read_bytes() == (Path(pilots[1]['bundle']) / 'pbs-container.sh').read_bytes()
(O / 'pilots.json').write_text(json.dumps(pilots, indent=2) + '\n')
(O / 'validation.json').write_text(json.dumps(dict(passed=True, source_job='222435.pbs111',
    serving_arguments_unchanged=True, benchmark_bytes_unchanged_except_labels=True,
    common_metadata_helper_bytes_identical=True, auxiliary_cpu_bindings_unchanged=True,
    new_cpu_budget_per_task={'prefill': 32, 'decode': 64}), indent=2) + '\n')
with tarfile.open(O / 'pbs-bundles.tar.gz', 'w:gz') as archive:
    for pilot in pilots:
        archive.add(pilot['bundle'], arcname=pilot['id'])
print('Prepared and validated both CPU envelope bundles')
