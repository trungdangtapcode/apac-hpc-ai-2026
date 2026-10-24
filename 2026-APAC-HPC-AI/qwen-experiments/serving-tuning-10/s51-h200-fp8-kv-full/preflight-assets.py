"""Bound target, serving and client image identities before worker startup."""
from pathlib import Path
import json
from asset_identity import verify_asset_identity
root=Path(__file__).resolve().parent
result=verify_asset_identity(root/'asset-verification.json','/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8','/scratch/enroot-images/sglang-harbor.sqsh')
client=json.loads((root/'client-image-identity.json').read_text());stat=Path(client['path']).stat()
assert stat.st_size==client['bytes'] and stat.st_mtime_ns==client['mtime_ns'] and stat.st_ctime_ns==client['ctime_ns'], 'Client image changed after full byte verification'
print(json.dumps(dict(target_and_serving=result,client_image_prechecked_sha256=client['sha256'],client_image_runtime_fingerprint_match=True),indent=2))
