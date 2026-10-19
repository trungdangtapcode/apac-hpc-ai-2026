"""Freeze a prefill-only inference-mode test against the already queued control."""
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
source = PBS / 'h100-hpc-n54-inference-control-49'
name = 'h100-hpc-n54-prefill-inference-51'
dest = PBS / name
assert not dest.exists()
assert json.loads((ROOT / 'research-followup-20261019-1720/221886.pbs111-review.json').read_text())['state'] == 'LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
assert json.loads((ROOT / 'research-followup-20261019-inference-mode/pbs-receipts.json').read_text())[0]['job'] == '221923.pbs111'
shutil.copytree(source, dest)
path = dest / 'benchmark.pbs'
path.write_text(path.read_text().replace(source.name, name))
path = dest / 'worker.sh'
before = path.read_text()
assert before.count('export SGLANG_ENABLE_TORCH_INFERENCE_MODE=0') == 2
after = before.replace('export SGLANG_ENABLE_TORCH_INFERENCE_MODE=0',
                       'export SGLANG_ENABLE_TORCH_INFERENCE_MODE=1', 1)
assert after.replace('export SGLANG_ENABLE_TORCH_INFERENCE_MODE=1',
                      'export SGLANG_ENABLE_TORCH_INFERENCE_MODE=0', 1) == before
path.write_text(after)
config = json.loads((source / 'config.json').read_text())
config.update(experiment=name, source_experiment=source.name, source_job='221886.pbs111',
              control_job='221923.pbs111',
              changed_factor={'kind': 'prefill_dynamic_grad_mode',
                              'prefill_inference_mode': True, 'decode_inference_mode': False},
              purpose='Test prefill-only inference mode against queued explicit-default control; a distinct phase hypothesis from decode-only trial, no predicted gain',
              diagnostic_profile=True, accuracy_verified=False)
(dest / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
for path in dest.iterdir():
    if path.suffix == '.py':
        ast.parse(path.read_text())
    if path.suffix in {'.pbs', '.sh'}:
        subprocess.run(['bash', '-n', str(path)], check=True)
    if path.name not in {'benchmark.pbs', 'worker.sh', 'config.json', 'SHA256SUMS'}:
        assert path.read_bytes() == (source / path.name).read_bytes()
hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted(dest.iterdir()) if p.is_file() and p.name != 'SHA256SUMS'}
(dest / 'SHA256SUMS').write_text(''.join(v + '  ' + k + '\n' for k, v in hashes.items()))
pilot = dict(platform='H100', id=name, bundle=str(dest), planned_ns=[54], minutes=45,
             max_su=1536, state='PREPARED_NOT_SUBMITTED', control_job='221923.pbs111',
             diagnostic_profile=True, payload_sha256=hashes)
(OUT / 'pilots.json').write_text(json.dumps([pilot], indent=2) + '\n')
(OUT / 'validation.json').write_text(json.dumps(dict(
    passed=True, shell_python_syntax_pass=True, workers_differ_only_prefill_inference_mode=True,
    ranked_workload_precision_transport_output_files_byte_identical=True,
    control='221923.pbs111', runtime_and_quality_unverified=True), indent=2) + '\n')
with tarfile.open(OUT / 'pbs-bundles.tar.gz', 'w:gz') as archive:
    archive.add(dest, arcname=name)
print('Prepared one frozen prefill-only candidate; no submission yet.')
