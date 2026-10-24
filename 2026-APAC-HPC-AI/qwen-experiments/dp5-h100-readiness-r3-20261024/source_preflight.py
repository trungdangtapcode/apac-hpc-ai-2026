"""Rehash pinned runtime source without importing SGLang or Torch."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent
rows=json.loads((B/'SOURCE_PROVENANCE.json').read_text())['additional_source_files']
verified=[]
for key,digest in rows.items():
 path=Path('/'+(key[len('torch/'):] if key.startswith('torch/') else key))
 actual=hashlib.sha256(path.read_bytes()).hexdigest()
 assert actual==digest, f'Pinned runtime source changed: {path}'
 verified.append(str(path))
print(json.dumps({'status':'PASS_PINNED_RUNTIME_SOURCES','files':verified,'gpu_import':False}))
