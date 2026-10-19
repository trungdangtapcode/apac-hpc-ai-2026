"""Freeze a matched decode inference-mode comparison without changing scoring."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PBS = ROOT / 'nscc-pbs'
SOURCE = PBS / 'h100-hpc-n54-cpu-gpu-profile-48'
review = json.loads((ROOT / 'research-followup-20261019-1720/221886.pbs111-review.json').read_text())
assert review['state'] == 'LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
source_root = ROOT / 'research-followup-20261019-1720/host-runtime-source'
source_files = {
    '/sgl-workspace/sglang/python/sglang/srt/utils/common.py': None,
    '/sgl-workspace/sglang/python/sglang/srt/managers/scheduler.py': None,
}
for path in source_files:
    source_files[path] = hashlib.sha256((source_root / path.lstrip('/')).read_bytes()).hexdigest()

pilots = []
for name, enabled in [('h100-hpc-n54-inference-control-49', False),
                      ('h100-hpc-n54-decode-inference-50', True)]:
    dest = PBS / name
    assert not dest.exists(), 'Never overwrite a frozen payload'
    shutil.copytree(SOURCE, dest)
    job = dest / 'benchmark.pbs'
    job.write_text(job.read_text().replace(SOURCE.name, name))
    worker = dest / 'worker.sh'
    code = worker.read_text()
    preflight = '''# Set before importing the server's DynamicGradMode decorator.
export SGLANG_ENABLE_TORCH_INFERENCE_MODE=0
if [[ $role == decode ]]; then
  export SGLANG_ENABLE_TORCH_INFERENCE_MODE=DECODE_MODE
fi
python3 - <<'MODECHECK'
import hashlib, os, torch
from pathlib import Path
from sglang.srt.utils.common import DynamicGradMode, _ENABLE_TORCH_INFERENCE_MODE
expected_sources = SOURCE_HASHES
for filename, expected_hash in expected_sources.items():
    assert hashlib.sha256(Path(filename).read_bytes()).hexdigest() == expected_hash
expected = os.environ['SGLANG_ENABLE_TORCH_INFERENCE_MODE'] == '1'
assert _ENABLE_TORCH_INFERENCE_MODE == expected
assert not torch.is_inference_mode_enabled()
with DynamicGradMode():
    assert torch.is_inference_mode_enabled() == expected
    assert not torch.is_grad_enabled()
print('DYNAMIC_GRAD_MODE_PREFLIGHT_PASSED', 'inference_mode=' + str(expected), flush=True)
MODECHECK
'''.replace('DECODE_MODE', '1' if enabled else '0').replace('SOURCE_HASHES', repr(source_files))
    anchor = 'exec python3 -m sglang.launch_server'
    assert code.count(anchor) == 1
    worker.write_text(code.replace(anchor, preflight + anchor, 1))
    config = json.loads((SOURCE / 'config.json').read_text())
    config.update(experiment=name, source_experiment=SOURCE.name,
                  source_job='221886.pbs111', control_job='MATCHED_CONTROL_49_PENDING',
                  diagnostic_profile=True, accuracy_verified=False,
                  changed_factor={'kind': 'decode_dynamic_grad_mode',
                                  'prefill_inference_mode': False,
                                  'decode_inference_mode': enabled},
                  purpose='Matched explicit-default control' if not enabled else
                          'Test decode-only inference mode to reduce view tracking and version counter overhead; no predicted gain')
    (dest / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
    for path in dest.iterdir():
        if path.suffix == '.py':
            ast.parse(path.read_text())
        if path.suffix in {'.sh', '.pbs'}:
            subprocess.run(['bash', '-n', str(path)], check=True)
        if path.name not in {'benchmark.pbs', 'worker.sh', 'config.json', 'SHA256SUMS'}:
            assert path.read_bytes() == (SOURCE / path.name).read_bytes()
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(dest.iterdir()) if p.is_file() and p.name != 'SHA256SUMS'}
    (dest / 'SHA256SUMS').write_text(''.join(v + '  ' + k + '\n' for k, v in hashes.items()))
    pilots.append(dict(platform='H100', id=name, bundle=str(dest), planned_ns=[54],
                       minutes=45, max_su=1536, state='PREPARED_NOT_SUBMITTED',
                       diagnostic_profile=True, payload_sha256=hashes))

first = Path(pilots[0]['bundle'])
second = Path(pilots[1]['bundle'])
a = (first / 'worker.sh').read_text()
b = (second / 'worker.sh').read_text()
assert b.replace('export SGLANG_ENABLE_TORCH_INFERENCE_MODE=1',
                 'export SGLANG_ENABLE_TORCH_INFERENCE_MODE=0', 1) == a
assert a.count('export SGLANG_ENABLE_TORCH_INFERENCE_MODE=0') == 2
(OUT / 'pilots.json').write_text(json.dumps(pilots, indent=2) + '\n')
(OUT / 'validation.json').write_text(json.dumps(dict(
    passed=True, shell_and_python_syntax_pass=True,
    matched_workers_differ_only_decode_mode=True,
    scoring_precision_transport_output_files_unchanged=True,
    pinned_runtime_preflight_source_hashes=source_files,
    runtime_activation_not_yet_verified=True), indent=2) + '\n')
with tarfile.open(OUT / 'pbs-bundles.tar.gz', 'w:gz') as archive:
    for pilot in pilots:
        archive.add(pilot['bundle'], arcname=pilot['id'])
print('Two frozen matched N54 trials prepared; no submission or reservation yet.')
