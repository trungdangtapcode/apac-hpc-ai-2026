"""Stage the pinned public draft on ASPIRE; retain only recovery metadata locally."""
from pathlib import Path
import json
import shlex
import subprocess

O = Path(__file__).resolve().parent
R = O.parent
cache = R / 'hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09'
configs = {name: (cache / name).read_text() for name in ['publisher-config.json', 'config.json', 'README.md']}
code = '''from pathlib import Path
import datetime,hashlib,json,time,urllib.request
root=Path('/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/drafts/nebius-eagle3-qwen235b-ff0f0c09');root.mkdir(parents=True,exist_ok=True)
expected_size=1145943008;expected_sha='bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86'
dest=root/'model.safetensors';partial=root/'model.safetensors.part';started=time.monotonic();digest=hashlib.sha256();size=0;reused=dest.exists()
if not reused:
 assert not partial.exists(),'Inspect retained partial before retrying staging'
 url='https://huggingface.co/nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507/resolve/ff0f0c0999f6c86b21dfd2f5803eebc4ac712224/model.safetensors'
 with urllib.request.urlopen(url,timeout=30) as response,partial.open('xb') as output:
  assert response.status==200
  while True:
   chunk=response.read(4194304)
   if not chunk:break
   size+=len(chunk);assert size<=expected_size and time.monotonic()-started<240
   digest.update(chunk);output.write(chunk)
 assert size==expected_size and digest.hexdigest()==expected_sha
 partial.replace(dest)
else:
 with dest.open('rb') as stream:
  while True:
   chunk=stream.read(4194304)
   if not chunk:break
   size+=len(chunk);digest.update(chunk)
 assert size==expected_size and digest.hexdigest()==expected_sha
configs=CONFIGS
for name,text in configs.items():
 path=root/name
 if path.exists():assert path.read_text()==text, 'Do not replace different cache metadata'
 else:path.write_text(text)
print(json.dumps(dict(staged_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),path=str(root),bytes=size,sha256=digest.hexdigest(),reused=reused,elapsed_s=time.monotonic()-started,source_revision='ff0f0c0999f6c86b21dfd2f5803eebc4ac712224',gpu_used=False,target_changed=False,storage='Excluded public model cache; Git retains recovery metadata only')))
'''.replace('CONFIGS', repr(configs))
r = subprocess.run(['bash', '/home/apacsc42/workspace/vpn-rootless/vpn.sh', 'ssh-batch',
                    'bash -lc ' + shlex.quote('python3 -c ' + shlex.quote(code))],
                   capture_output=True, timeout=300)
(O / 'staging.stdout').write_bytes(r.stdout)
(O / 'staging.stderr').write_bytes(r.stderr)
assert r.returncode == 0, 'Remote staging failed; no qsub and no automatic retry'
receipt = json.loads(r.stdout)
(O / 'staged-draft.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['sha256'], receipt['bytes'], receipt['elapsed_s'])
