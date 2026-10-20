"""Stage a pinned public draft cache with verified bytes; never capture weights in Git."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import time
import urllib.request

O = Path(__file__).resolve().parent
R = O.parent
REPO = 'nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507'
REVISION = 'ff0f0c0999f6c86b21dfd2f5803eebc4ac712224'
expected_sha = 'bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86'
expected_size = 1145943008
assert json.loads((O / 'interface-checks.json').read_text())['state'] == 'CPU_HEADER_CONFIG_POINTER_CHECKS_PASS_GPU_INTEGRATION_UNVERIFIED'
cache = R / 'hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09'
cache.mkdir(parents=True, exist_ok=True)
metadata_url = f'https://huggingface.co/api/models/{REPO}/tree/{REVISION}'
with urllib.request.urlopen(metadata_url, timeout=25) as response:
    tree = json.load(response)
entry = next(item for item in tree if item['path'] == 'model.safetensors')
assert entry['size'] == entry['lfs']['size'] == expected_size
assert entry['lfs']['oid'] == expected_sha
assert expected_size < 1536 * 1024**2
(O / 'draft-file-metadata.json').write_text(json.dumps(dict(
    repository=REPO, revision=REVISION, source_url=metadata_url, entry=entry), indent=2) + '\n')
destination = cache / 'model.safetensors'
started = time.monotonic()
reused = destination.exists()
digest = hashlib.sha256()
received = 0
if reused:
    with destination.open('rb') as stream:
        while chunk := stream.read(4 * 1024**2):
            digest.update(chunk)
            received += len(chunk)
else:
    partial = destination.with_suffix('.part')
    assert not partial.exists(), 'Partial staging exists; inspect before another download'
    stable_url = f'https://huggingface.co/{REPO}/resolve/{REVISION}/model.safetensors'
    with urllib.request.urlopen(stable_url, timeout=30) as response, partial.open('xb') as stream:
        assert response.status == 200, 'Full download requires HTTP 200'
        while chunk := response.read(4 * 1024**2):
            received += len(chunk)
            assert received <= expected_size, 'Oversized response'
            assert time.monotonic() - started < 300, 'Staging deadline'
            digest.update(chunk)
            stream.write(chunk)
    assert received == expected_size and digest.hexdigest() == expected_sha, 'Incomplete or mismatched draft; preserve partial for diagnosis'
    partial.replace(destination)
assert received == expected_size and digest.hexdigest() == expected_sha
original = R / 'deepinfer-review-20261020/source/draft/config.json'
shutil.copy2(original, cache / 'publisher-config.json')
shutil.copy2(O / 'derived-draft-config.json', cache / 'config.json')
shutil.copy2(R / 'deepinfer-review-20261020/source/draft/README.md', cache / 'README.md')
result = dict(staged_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              repository=REPO, revision=REVISION, cache_path=str(cache), reused=reused,
              bytes=received, sha256=digest.hexdigest(), elapsed_s=time.monotonic() - started,
              lfs_digest_verified=True, tensor_payload_downloaded=True,
              draft_config_changes=['architectures: LlamaForCausalLM -> LlamaForCausalLMEagle3'],
              config_sha256=hashlib.sha256((cache / 'config.json').read_bytes()).hexdigest(),
              target_model_changed=False, gpu_used=False, loaded_with_sglang=False,
              storage='Disposable public-model cache outside selected Git captures; recover from pinned public revision and verify SHA256. No weight bytes in Git or research artifact store.',
              license='CC BY 4.0, publisher card retained for attribution',
              recovery_url=f'https://huggingface.co/{REPO}/resolve/{REVISION}/model.safetensors')
(O / 'staged-draft.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ['bytes', 'sha256', 'elapsed_s', 'lfs_digest_verified', 'gpu_used']}))
