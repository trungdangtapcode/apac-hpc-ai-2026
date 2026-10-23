#!/usr/bin/env python3
"""Cheaply recheck draft device/inode/size/time identity against full-hash evidence."""
import json, sys
from pathlib import Path

def fp(path):
 s=path.stat(); return {k:getattr(s,k) for k in ('st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns')}
root=Path(__file__).resolve().parent
draft=Path(sys.argv[1]).resolve(strict=True)
full=json.loads(Path(sys.argv[2]).read_text())
assert full.get('state')=='PASS' and full.get('revision')=='ff0f0c0999f6c86b21dfd2f5803eebc4ac712224'
expected={Path(row['path']).name:row for row in full['files']}
assert set(expected)=={'model.safetensors','config.json','publisher-config.json'}
for name,row in expected.items():
 p=draft/name
 assert fp(p)==row['fingerprint'], f'draft fingerprint changed: {name}'
 if name!='model.safetensors':
  import hashlib
  assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'], f'draft config hash changed: {name}'
assert expected['model.safetensors']['sha256']=='bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86'
print(json.dumps({'state':'PASS','draft_path':str(draft),'files':{k:v['fingerprint'] for k,v in expected.items()},'weight_full_hash_source':'pre-worker full verifier'}))
