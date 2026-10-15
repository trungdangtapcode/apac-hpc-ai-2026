"""Run on the NSCC login node before qsub; missing assets must not burn SU."""
import hashlib
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parent
contract=json.loads((root/'asset-contract.json').read_text());missing=[]
for name,asset in contract['images'].items():
    path=Path(asset['path'])
    if not path.is_file() or path.stat().st_size!=asset['bytes']:missing.append(str(path)+' (missing or wrong size)')
    elif asset.get('sha256'):
        digest=hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(8*1024*1024),b''):digest.update(block)
        if digest.hexdigest()!=asset['sha256']:missing.append(str(path)+' (SHA256 mismatch)')
# The downloader renames a shard before hashing it. Nonzero size alone must not
# permit allocation while verification is incomplete or after a corrupt download.
metadata=json.loads((root/'inspection/official-model-metadata.json').read_text())
status_path=root/'model-transfer-status.json'
status=json.loads(status_path.read_text()) if status_path.is_file() else {}
if status.get('revision')!=metadata['sha'] or not status.get('complete') or status.get('errors'):
    missing.append('official model staging manifest is absent, incomplete, or failed')
for entry in metadata['siblings']:
    name=entry['rfilename']
    if '/' in name or name=='.gitattributes':continue
    path=Path(contract['model_path'])/name
    verified=status.get('verified',{}).get(name,{})
    expected_sha=entry.get('lfs',{}).get('sha256')
    if not path.is_file() or path.stat().st_size!=entry['size']:
        missing.append(str(path)+' (missing or wrong official size)')
    elif verified.get('bytes')!=entry['size'] or not verified.get('sha256') or (expected_sha and verified.get('sha256')!=expected_sha):
        missing.append(str(path)+' (official staging verification missing or mismatched)')
model=Path(contract['model_path']);config=model/'config.json';index=model/'model.safetensors.index.json'
if not config.is_file():missing.append(str(config))
elif hashlib.sha256(json.dumps(json.loads(config.read_text()),sort_keys=True).encode()).hexdigest()!=contract['model_config_canonical_sha256']:
    missing.append(str(config)+' (differs from official checkpoint config used on Firmus)')
if not index.is_file():missing.append(str(index))
else:
    for name in sorted(set(json.loads(index.read_text())['weight_map'].values())):
        path=model/name
        if not path.is_file() or path.stat().st_size==0:missing.append(str(path))
cache=Path(contract['tokenizer_cache'])/'models--Qwen--Qwen3-235B-A22B-Instruct-2507'
ref=cache/'refs/main'
if not ref.is_file():missing.append(str(ref))
else:
    revision=ref.read_text().strip()
    if len(revision)!=40 or any(c not in '0123456789abcdef' for c in revision):missing.append(str(ref)+' (invalid revision)')
    elif not (cache/'snapshots'/revision/'tokenizer.json').is_file():missing.append(str(cache/'snapshots'/revision/'tokenizer.json'))
result=dict(ready=not missing,scope='Official-size and completed-staging checks plus image SHA256; no runtime/performance/accuracy claim',missing=missing)
print(json.dumps(result,indent=2));sys.exit(0 if result['ready'] else 2)
