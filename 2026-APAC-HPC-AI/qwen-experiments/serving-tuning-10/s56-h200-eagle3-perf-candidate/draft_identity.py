"""Verify the full pre-worker draft receipt and cheap post-runtime fingerprint."""
import json
from pathlib import Path

def fingerprint(path):
 s=path.stat(); return {k:getattr(s,k) for k in ('st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns')}
def verify_post_full_fingerprint(draft, full_path):
 full=json.loads(Path(full_path).read_text())
 if full.get('state')!='PASS' or full.get('revision')!='ff0f0c0999f6c86b21dfd2f5803eebc4ac712224': raise ValueError('missing or wrong full draft verification')
 expected={Path(row['path']).name:row for row in full['files']}
 if set(expected)!={'model.safetensors','config.json','publisher-config.json'}: raise ValueError('full draft file inventory mismatch')
 files={}
 for name,row in expected.items():
  p=Path(draft)/name
  if fingerprint(p)!=row['fingerprint']: raise ValueError(f'draft runtime fingerprint changed: {name}')
  files[name]={'fingerprint':fingerprint(p),'sha256_from_full_check':row['sha256']}
  if name!='model.safetensors':
   import hashlib
   if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']: raise ValueError(f'draft config changed: {name}')
 return {'state':'PASS','files':files,'weight_sha256_source':'full pre-worker verification; not rehashed after runtime'}
