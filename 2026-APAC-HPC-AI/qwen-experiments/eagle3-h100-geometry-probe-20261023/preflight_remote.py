"""Cheap current H100 staging checks, plus full pinned draft hash; no GPU."""
from pathlib import Path
import hashlib,json,subprocess,sys
O=Path(__file__).resolve().parent;P=O/'payload'
record=json.loads((P/'target-staging-record.json').read_text());contract=json.loads((P/'asset-contract.json').read_text())
model=Path(contract['model_path']);assert record['complete'] and record['revision']=='e156cb4efae43fbee1a1ab073f946a1377e6b969'
small=[]
for name,entry in record['verified'].items():
 assert '/' not in name;path=model/name;assert path.is_file() and path.stat().st_size==entry['bytes'],name
 if not name.endswith('.safetensors'):
  assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'],name;small.append(name)
image=contract['images']['sglang-harbor.sqsh'];assert Path(image['path']).stat().st_size==image['bytes']
draft='/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/drafts/nebius-eagle3-qwen235b-ff0f0c09'
verification=subprocess.run([sys.executable,str(P/'verify-draft.py'),draft],capture_output=True,text=True,check=True,timeout=60)
print(json.dumps(dict(passed=True,model_revision=record['revision'],files_size_checked=len(record['verified']),small_files_rehashed=small,serving_image_size_checked=True,draft_full_sha256_passed=True,draft_verifier_output=verification.stdout.strip(),scope='Current staged sizes and small target metadata hashes; pinned full draft hash. Large target weights and serving image not freshly rehashed; runtime source pins also gate initialization. No GPU or native model executed.'),indent=2))
