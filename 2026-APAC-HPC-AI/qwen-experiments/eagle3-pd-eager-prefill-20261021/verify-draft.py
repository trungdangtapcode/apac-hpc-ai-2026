"""Verify only the pinned public draft; never change official target files."""
import hashlib,json,sys
from pathlib import Path
p=Path(sys.argv[1]);digest=hashlib.sha256()
with (p/'model.safetensors').open('rb') as f:
 while block:=f.read(4194304):digest.update(block)
assert digest.hexdigest()=='bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86'
a=json.loads((p/'config.json').read_text());b=json.loads((p/'publisher-config.json').read_text())
assert {k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}=={'architectures'}
assert a['architectures']==['LlamaForCausalLMEagle3']
print('PINNED_DRAFT_VERIFIED',digest.hexdigest(),flush=True)
