"""Check model-cache exclusions without invoking the initial snapshot builder."""
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('policy', root / 'tools/build_snapshot.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
blocked = [
    '2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/example/config.json',
    '2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/example/model.safetensors',
    '2026-APAC-HPC-AI/qwen-experiments/assets/model-00001.safetensors',
    'workspace/models/pytorch_model-00001.bin',
    'workspace/models/quantized.gguf',
]
allowed = [
    '2026-APAC-HPC-AI/qwen-experiments/eagle3-preflight-20261020/staged-draft.json',
    '2026-APAC-HPC-AI/qwen-experiments/eagle3-preflight-20261020/draft-safetensors-header.json',
    '2026-APAC-HPC-AI/qwen-experiments/eagle3-preflight-20261020/stage-draft.py',
    'workspace/reports/model-config.json',
]
assert all(policy.policy(path) for path in blocked)
assert all(policy.policy(path) is None for path in allowed)
with tempfile.TemporaryDirectory(prefix='ap42-model-exclusion-') as temporary:
    folder = Path(temporary)
    payload = folder / 'model.safetensors'
    payload.write_bytes(b'Public fixture only, no tensor data')
    archive = folder / 'weights.tar.gz'
    with tarfile.open(archive, 'w:gz') as stream:
        stream.add(payload, arcname='nested/model.safetensors')
    assert 'sensitive_archive_member' in policy.archive_scan(archive)
report = dict(passed=True, model_tensor_bytes_copied=False, blocked_paths=blocked,
              allowed_recovery_metadata=allowed, archive_member_guard_passed=True,
              initial_builder_main_called=False)
destination = root / 'backup/updates/20261020-model-cache-policy'
destination.mkdir(exist_ok=True)
(destination / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print('Model tensor and cache exclusion checks PASS; recovery metadata remains allowed')
