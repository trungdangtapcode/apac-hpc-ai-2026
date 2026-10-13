"""Freeze the next small wave around the measured winning serving stack."""
import hashlib
import json
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIR = ROOT/'serving-tuning'
SOURCE = ROOT/'runs/22415/submitted'
DIR.mkdir(exist_ok=True)
STATE = DIR/'registry.json'
if STATE.exists():
    raise SystemExit('Tuning wave already exists; refusing to replace frozen history.')

base = json.loads((SOURCE/'config.json').read_text())
source_benchmark = (SOURCE/'benchmark.sh').read_text()
prefix = source_benchmark.split('if [[ ${QWEN_CONFIRM_ONLY:-0} == 1 ]]; then')[0]
tail = '''
for N in ${QWEN_TUNE_NS:-48}; do
  if (( $(date +%s)+240 > ${QWEN_BENCHMARK_DEADLINE:-0} )); then
    echo "FULL_POINT_DEFERRED: insufficient time before N=$N"
    printf '%s\\n' "$N" >>"$ART/deferred-ns.txt"
    continue
  fi
  run_benchmark "$N" confirm 60 120
  if ! python3 - "$ART/summary.json" "$N" <<'GATE'
import json,sys
rows=[r for r in json.load(open(sys.argv[1])) if r['phase']=='confirm' and r['concurrency']==int(sys.argv[2])]
assert len(rows)==1
r=rows[0]
sys.exit(0 if r['sla_pass'] and r['cancelled_requests']==0 and r['errors']==0 and r['requests']>0 else 1)
GATE
  then
    echo "STOP_LOAD_INCREASE: N=$N did not pass the latency/error gate"
    printf '%s\\n' "$N" >"$ART/stop-increase-n.txt"
    break
  fi
done
if [[ ${QWEN_DIAGNOSTIC_PROFILE:-0} == 1 ]]; then
  if (( $(date +%s)+210 < ${QWEN_BENCHMARK_DEADLINE:-0} )); then
    timeout 180 python3 "$QWEN_BUNDLE/profile-serving.py" "${HOST%:8000}" "$ART" >"$ART/diagnostic-profile.log" 2>&1 || {
      echo "DIAGNOSTIC_PROFILE_FAILED: inspect separate log; measured exports remain preserved"
      touch "$ART/diagnostic-profile-failed.txt"
    }
  else
    touch "$ART/diagnostic-profile-deferred.txt"
  fi
fi
'''

trials = [
    ('control-load', [48,52,56], [], False,
     'Repeat N48 and increase N52/N56 using full 60/120/30 measurements; stop raising load after a failed gate.'),
    ('dense-decode-graphs', [48,52,56],
     ['--cuda-graph-max-bs-decode','64','--cuda-graph-bs-decode', *map(str,range(1,65))], False,
     'Decode graphs for every batch 1..64; remove padding to coarse graph sizes. Other workers and model precision unchanged.'),
    ('profile-control', [48], [], True,
     'Independent N48 repeat, then GPU traces under separate 48-request diagnostic traffic; traces never used as performance scores.'),
]
entries = []
for name, ns, decode_flags, profile, purpose in trials:
    bundle = DIR/name
    bundle.mkdir()
    for source in SOURCE.iterdir():
        if source.is_file() and source.name not in ('job.sbatch','SHA256SUMS'):
            shutil.copyfile(source,bundle/source.name)
    shutil.copyfile(ROOT/'profile-serving.py',bundle/'profile-serving.py')
    config = dict(base, phase='confirm', concurrency=ns, experiment=name,
                  control_job='22415', confirm_warmup_s=60, confirm_measure_s=120,
                  decode_extra_flags=decode_flags, diagnostic_profile=profile, purpose=purpose,
                  protocol='Full-duration, closed-loop 4000/200; stop load increase on failed SLA/error gate')
    (bundle/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    (bundle/'benchmark.sh').write_text(prefix+tail)
    if decode_flags:
        worker=(bundle/'worker.sh').read_text()
        declaration='extra=()\nif [[ $role == decode ]]; then\n  extra=('+shlex.join(decode_flags)+')\nfi\n'
        worker=worker.replace('exec python3 -m sglang.launch_server', declaration+'exec python3 -m sglang.launch_server')
        worker=worker.replace('"$@" --host', '"${extra[@]}" "$@" --host')
        (bundle/'worker.sh').write_text(worker)
    # Execute the benchmark payload copied at job start, not a mutable source.
    deployment=(bundle/'topology-job.sh').read_text().replace('QWEN_SWEEP_WARM=10 QWEN_SWEEP_DURATION=20',
       'QWEN_TUNE_NS="${QWEN_TUNE_NS:-48}" QWEN_DIAGNOSTIC_PROFILE="${QWEN_DIAGNOSTIC_PROFILE:-0}" QWEN_BUNDLE="$BUNDLE"')
    (bundle/'topology-job.sh').write_text(deployment)
    patch_sha=config['transport_patch_metadata']['patched_sha256']
    (bundle/'job.sbatch').write_text(f'''#!/bin/bash
#SBATCH -J ap42-tune-{name[:12]}
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --exclusive
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_BUNDLE={shlex.quote(str(bundle))}
export QWEN_PREFILL_EP=1
export QWEN_PAIR_TIMEOUT=480
export QWEN_TUNE_NS={shlex.quote(' '.join(map(str,ns)))}
export QWEN_DIAGNOSTIC_PROFILE={int(profile)}
export QWEN_NIXL_PATCH_SHA256={patch_sha}
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
exec bash "$QWEN_BUNDLE/topology-job.sh"
''')
    for script in ('job.sbatch','topology-job.sh','worker.sh','benchmark.sh'):
        subprocess.run(['bash','-n',str(bundle/script)],check=True)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.iterdir())}
    (bundle/'SHA256SUMS').write_text(''.join(f'{digest}  {filename}\n' for filename,digest in hashes.items()))
    subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
    for p in bundle.iterdir():p.chmod(0o444)
    bundle.chmod(0o555)
    entries.append({'id':name,'bundle':str(bundle),'planned_ns':ns,'purpose':purpose,
                    'state':'PLANNED','attempts':[],'payload_sha256':hashes})
state={'created_utc':datetime.now(timezone.utc).isoformat(),'entries':entries,
       'next_axes':['Prefill chunk 4096/16384 after control','MoE runner after profiler identifies compute cost',
                    'Expert communication after profiler identifies dispatch/collective cost',
                    'FP8 KV with separate quality check','Engine comparison after reproducible current-stack baseline'],
       'promotion_gate':'Repeated full measurements >=90% SLA, no errors/cancellations. No accuracy pass or official score inferred.',
       'benchmark_complete':False}
STATE.write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps({'frozen_trials':[e['id'] for e in entries],'registry':str(STATE)},indent=2))
