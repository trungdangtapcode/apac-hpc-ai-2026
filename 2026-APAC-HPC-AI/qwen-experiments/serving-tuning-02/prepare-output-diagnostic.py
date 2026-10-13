"""Freeze an independent diagnostic; never edits existing experiment bundles."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

DIR = Path(__file__).resolve().parent
ROOT = DIR.parent
SOURCE = DIR / 's2-control-n52'
BUNDLE = DIR / 's2-output-monolithic'
BUNDLE.mkdir()
for name in ('topology-job.sh', 'worker.sh', 'output-smoke.py'):
    shutil.copyfile(SOURCE / name, BUNDLE / name)
shutil.copyfile(DIR / 'output-diagnostic.py', BUNDLE / 'output-diagnostic.py')
shutil.copyfile(ROOT / 'serving-tuning/inspection/disaggregation/nixl/conn.py', BUNDLE / 'nixl-conn.py')
original_sha = hashlib.sha256((BUNDLE / 'nixl-conn.py').read_bytes()).hexdigest()
assert original_sha == '28da79ad06baa8c1b725bc98983ca570f82a73b49439873831505ab7f1eef601'
worker = (BUNDLE / 'worker.sh').read_text()
assert '--disaggregation-mode "$role" --disaggregation-transfer-backend nixl' in worker
worker = worker.replace('--disaggregation-mode "$role" --disaggregation-transfer-backend nixl', '')
(BUNDLE / 'worker.sh').write_text(worker)
# Reuse known GPU placement, process cleanup, readiness and mounts, replacing
# only deployment role arguments and the benchmark/router section.
script = (BUNDLE / 'topology-job.sh').read_text()
script = script.replace('cp "$BUNDLE/benchmark.sh" "$BUNDLE/summarize.py" "$BUNDLE/worker.sh" "$ART/"',
                        'cp "$BUNDLE/worker.sh" "$ART/"')
begin = script.index('  if [[ $role == prefill ]]; then')
end = script.index("  printf '%s\\t%s\\t%s\\n'", begin)
script = script[:begin] + '  if [[ $tp == 4 ]]; then extra=(--ep-size 1); else extra=(--ep-size 8); fi\n' + script[end:]
begin = script.index('srun --overlap', script.index('while read -r name url bootstrap;'))
script = script[:begin] + '''
remaining=$((1020-SECONDS-40))
if ((remaining<120)); then echo "FATAL: insufficient time for output diagnostics" >&2; exit 1; fi
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \\
  --container-image="$SGLANG" --container-mounts="$(mounts diagnostic-client)" \\
  timeout "$remaining" python3 "$BUNDLE/output-diagnostic.py" \\
  --endpoints "${IPS[0]}:30100" "${IPS[0]}:30101" "${IPS[1]}:30200" \\
  --smoke-source "$BUNDLE/output-smoke.py" --output "$ART" >"$ART/output-diagnostic.log" 2>&1
echo "OUTPUT_DIAGNOSTIC_COMPLETE after ${SECONDS}s at $(date -Iseconds)"
'''
(BUNDLE / 'topology-job.sh').write_text(script)
(BUNDLE / 'placement.tsv').write_text((SOURCE / 'placement.tsv').read_text())
config = dict(experiment=BUNDLE.name, purpose='Investigate job 23128 reverse-string anomaly without KV transport',
              scope='UNRANKED diagnostic; not a contest P/D deployment or accuracy gate',
              model='/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8',
              image='/scratch/enroot-images/sglang-harbor.sqsh',
              original_conn_sha256=original_sha, disaggregation=False, gpu_count=16,
              endpoints=[dict(tp=4, ep=1, instances=2), dict(tp=8, ep=8, instances=1)],
              short_cases=8, short_repetitions=4, long_cases=12, expected_requests=132,
              temperature=0, max_tokens=64, kv_dtype='auto')
(BUNDLE / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
(BUNDLE / 'job.sbatch').write_text(f'''#!/bin/bash
#SBATCH -J ap42-output-check
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --exclusive
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_BUNDLE={BUNDLE}
export QWEN_NIXL_PATCH_SHA256={original_sha}
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
exec bash "$QWEN_BUNDLE/topology-job.sh"
''')
for name in ('job.sbatch', 'worker.sh', 'topology-job.sh'):
    subprocess.run(['bash', '-n', str(BUNDLE / name)], check=True)
hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(BUNDLE.iterdir())}
(BUNDLE / 'SHA256SUMS').write_text(''.join(f'{sha}  {name}\n' for name, sha in hashes.items()))
subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=BUNDLE, check=True, capture_output=True)
for path in BUNDLE.iterdir():
    path.chmod(0o444)
BUNDLE.chmod(0o555)
print(json.dumps(dict(bundle=str(BUNDLE), payload_sha256=hashes), indent=2))
