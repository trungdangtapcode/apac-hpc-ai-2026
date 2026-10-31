"""Freeze an explicit-default H200 control and two phase inference-mode ports."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import subprocess

D = Path(__file__).resolve().parent
Q = D.parent
P = Q / 'runs/27777/submitted-payload'
subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=P, check=True, stdout=subprocess.DEVNULL)
native = Q / 'research-followup-20261019-1720/host-runtime-source'
source_hashes = {
    '/sgl-workspace/sglang/python/sglang/srt/utils/common.py': 'e1fc22ba7508205a32188dd1cb5b43201973468cb495ae492f8b523d28b3b446',
    '/sgl-workspace/sglang/python/sglang/srt/managers/scheduler.py': '1d4a7683e32f0862cf5b03be33e5ec23f9d112e59546d391e28fa222fcd1619b',
}
for path, digest in source_hashes.items():
    assert hashlib.sha256((native / path.lstrip('/')).read_bytes()).hexdigest() == digest
h100 = (Q / 'nscc-pbs/h100-hpc-n54-decode-inference-50/worker.sh').read_text()
preflight = h100.split("python3 - <<'MODECHECK'", 1)[1].split('\nMODECHECK', 1)[0]
assert repr(source_hashes) in preflight
# Verify restoration explicitly as well as entering the native provider.
needle = "print('DYNAMIC_GRAD_MODE_PREFLIGHT_PASSED'"
assert preflight.count(needle) == 1
preflight = preflight.replace('with DynamicGradMode():', 'original_grad = torch.is_grad_enabled()\nwith DynamicGradMode():')
preflight = preflight.replace(needle, "assert not torch.is_inference_mode_enabled()\nassert torch.is_grad_enabled() == original_grad\n" + needle)
records = []
for number, tag, pmode, dmode, evidence in [
    (116, 'control', False, False, 221923),
    (117, 'decode', False, True, 221924),
    (118, 'prefill', True, False, 221966),
]:
    label = f's{number}-h200-phase-inference-{tag}'
    B = Q / 'serving-tuning-11' / label
    shutil.copytree(P, B)
    cfg = json.loads((P / 'config.json').read_text())
    cfg.update(experiment=label, label=label, source_parent_job=27777,
               source_parent='s110-h200-decode-flashinfer-transfer',
               study_arm=f'phase_inference_{tag}', phase_inference_mode=dict(prefill=pmode, decode=dmode),
               phase_provider_source_hashes=source_hashes, h100_phase_evidence_job=evidence,
               matched_control_bundle='s116-h200-phase-inference-control', matched_control_job=None,
               matched_pair='Explicit-default versus phase-only DynamicGradMode, same current H200 recipe',
               performance_or_GPU_acceptance='UNKNOWN')
    (B / 'config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    text = (P / 'worker.sh').read_text()
    marker = 'exec python3 -m sglang.launch_server'
    assert text.count(marker) == 1
    code = f'''# Select the native provider before importing the server and its decorators.
export SGLANG_ENABLE_TORCH_INFERENCE_MODE={int(pmode)}
if [[ $role == decode ]]; then
  export SGLANG_ENABLE_TORCH_INFERENCE_MODE={int(dmode)}
fi
python3 - <<'MODECHECK'{preflight}
MODECHECK
'''
    (B / 'worker.sh').write_text(text.replace(marker, code + marker))
    text = (P / 'check-fast-runtime.py').read_text()
    marker = '    for key,wanted in common.items():'
    assert text.count(marker) == 1
    text = text.replace(marker, '''    expected_mode=cfg['phase_inference_mode']['prefill' if role.startswith('prefill') else 'decode']
    mode_receipts=re.findall(r'^DYNAMIC_GRAD_MODE_PREFLIGHT_PASSED inference_mode=(True|False)$',text,re.M)
    if mode_receipts!=[str(expected_mode)]:
        raise ValueError(f'{role}: missing, duplicate or incorrect native DynamicGradMode preflight')
''' + marker)
    text = text.replace("'actual_cache_class':expected_cache", "'native_provider_preflight_inference_mode':expected_mode,'actual_cache_class':expected_cache")
    (B / 'check-fast-runtime.py').write_text(text)
    text = (P / 'job.sbatch').read_text().replace('s110-h200-decode-flashinfer-transfer', label)
    text = text.replace('#SBATCH -J ap42-s110-flashinfer', f'#SBATCH -J ap42-s{number}-im-{tag}')
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
    records.append(dict(bundle=str(B.relative_to(Q)), phase=tag, concurrency=64,
                        prefill_inference_mode=pmode, decode_inference_mode=dmode,
                        manifest_sha256=hashlib.sha256((B / 'SHA256SUMS').read_bytes()).hexdigest()))
(D / 'preparation.json').write_text(json.dumps(dict(state='PREPARED_NOT_SUBMITTED', bundles=records,
    unchanged_files=unchanged, native_source_hashes=source_hashes,
    parent_manifest_sha256=hashlib.sha256((P / 'SHA256SUMS').read_bytes()).hexdigest()), indent=2) + '\n')
print(json.dumps(records, indent=2))
