#!/usr/bin/env bash
set -euo pipefail
TASK_SCRIPTS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TASK_ROOT=$(cd "$TASK_SCRIPTS/.." && pwd)
mkdir -p "$TASK_ROOT/logs/slurm" "$TASK_ROOT/logs/reruns"
for command in sbatch srun scontrol curl python3 sha256sum; do
  command -v "$command" >/dev/null || { echo "Missing prerequisite: $command" >&2; exit 1; }
done
cd "$TASK_SCRIPTS"
sha256sum --check SHA256SUMS
python3 - "$TASK_SCRIPTS" "${1:---check}" <<'PYCHECK'
import hashlib,json,os,sys
from pathlib import Path
root=Path(sys.argv[1]); mode=sys.argv[2]
if mode not in ('--check','--verify-images'):
    raise SystemExit('Usage: bash setup.sh [--check|--verify-images]')
spec=json.loads((root/'environment.json').read_text())
for image in spec['container_images']:
    env=image['override_environment_variable']
    path=Path(os.environ.get(env,image['path']))
    if not path.is_file(): raise SystemExit('Missing provided image: '+str(path))
    if path.stat().st_size!=image['bytes']: raise SystemExit('Image size differs: '+str(path))
    if mode=='--verify-images':
        h=hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
        if h.hexdigest()!=image['sha256']: raise SystemExit('Image SHA256 differs: '+str(path))
    print('IMAGE',path,'OK',flush=True)
model=Path(os.environ.get('TRIPLEU_MODEL_PATH',spec['model']['path']))
for filename,wanted in spec['model']['metadata_sha256'].items():
    if hashlib.sha256((model/filename).read_bytes()).hexdigest()!=wanted:
        raise SystemExit('Model metadata differs: '+filename)
print('MODEL metadata OK; weights reused as staged, not rebuilt or requantised')
print('Offline tokenizer cache and job payload verified')
PYCHECK
echo 'Setup check complete; no model was launched and no Slurm job was submitted.'
