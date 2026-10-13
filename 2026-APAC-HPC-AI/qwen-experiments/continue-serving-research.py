"""Freeze standalone controls and scheduling candidates for the second wave."""
import hashlib
import json
import shlex
import shutil
import subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DIR=ROOT/'serving-tuning-02'
STATE=ROOT/'serving-tuning/registry.json'
SOURCE=ROOT/'serving-tuning/control-load'
DIR.mkdir(exist_ok=True)
state=json.loads(STATE.read_text())
assert not state['active'], 'Do not race an active controller while extending its registry'
if any(e['id'].startswith('s2-') for e in state['entries']):
    raise SystemExit('Second wave already prepared; refusing to overwrite history.')
trials=[
    ('s2-control-n52',[],[], 'Standalone N52 control with the old chunk 8192; measure cold deployment reproducibility.'),
    ('s2-chunk4096-n52',['--chunked-prefill-size','4096'],[], 'Standalone N52 confirmation of the current best chunk 4096.'),
    ('s2-chunk4096-dense-n52',['--chunked-prefill-size','4096'],
     ['--cuda-graph-max-bs-decode','64','--cuda-graph-bs-decode',*map(str,range(1,65))],
     'Combine the independently measured chunk 4096 and dense decode graphs; compare with chunk-only at the same N52.'),
    ('s2-chunk16384-n52',['--chunked-prefill-size','16384'],[],
     'Larger prefill chunk 16384 versus 8192/4096; test batching throughput against TTFT and startup time.'),
]
for name,pflags,dflags,purpose in trials:
    bundle=DIR/name;bundle.mkdir()
    for path in SOURCE.iterdir():
        if path.is_file() and path.name not in ('job.sbatch','SHA256SUMS'):
            shutil.copyfile(path,bundle/path.name)
    shutil.copyfile(ROOT/'output-smoke.py',bundle/'output-smoke.py')
    config=json.loads((bundle/'config.json').read_text())
    config.update(experiment=name,concurrency=[52],phase='confirm',diagnostic_profile=False,
                  prefill_extra_flags=pflags,decode_extra_flags=dflags,purpose=purpose,
                  wave=2,quality_status='SMOKE_ONLY; organiser full-set accuracy unverified',
                  standalone=True,prefill_chunk_size=int(pflags[1]) if pflags else 8192)
    (bundle/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    worker=(bundle/'worker.sh').read_text()
    assert 'extra=()' not in worker
    declaration='extra=()\nif [[ $role == prefill ]]; then\n  extra=('+shlex.join(pflags)+')\nelse\n  extra=('+shlex.join(dflags)+')\nfi\n'
    worker=worker.replace('exec python3 -m sglang.launch_server',declaration+'exec python3 -m sglang.launch_server')
    worker=worker.replace('"$@" --host','"${extra[@]}" "$@" --host')
    (bundle/'worker.sh').write_text(worker)
    benchmark=(bundle/'benchmark.sh').read_text()
    benchmark+='''
if (( $(date +%s)+100 < ${QWEN_BENCHMARK_DEADLINE:-0} )); then
  timeout 90 python3 "$QWEN_BUNDLE/output-smoke.py" "$HOST" "$ART" >"$ART/output-smoke.log" 2>&1 || touch "$ART/output-smoke-failed.txt"
else
  touch "$ART/output-smoke-deferred.txt"
fi
'''
    (bundle/'benchmark.sh').write_text(benchmark)
    sha=config['transport_patch_metadata']['patched_sha256']
    (bundle/'job.sbatch').write_text(f'''#!/bin/bash
#SBATCH -J ap42-{name[:19]}
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
export QWEN_TUNE_NS=52
export QWEN_DIAGNOSTIC_PROFILE=0
export QWEN_NIXL_PATCH_SHA256={sha}
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
exec bash "$QWEN_BUNDLE/topology-job.sh"
''')
    for script in ('job.sbatch','worker.sh','topology-job.sh','benchmark.sh'):
        subprocess.run(['bash','-n',str(bundle/script)],check=True)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.iterdir())}
    (bundle/'SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name,digest in hashes.items()))
    subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
    for p in bundle.iterdir():p.chmod(0o444)
    bundle.chmod(0o555)
    state['entries'].append({'id':name,'bundle':str(bundle),'planned_ns':[52],'purpose':purpose,
      'state':'PLANNED','attempts':[],'payload_sha256':hashes,'measurements':[],
      'missing_ns':[52],'benchmark_complete':False,'profile_complete':None,'traces':[],'wave':2})
    print('FROZEN',name)
state.update(benchmark_complete=False,active=False,updated_utc=datetime.now(timezone.utc).isoformat())
temporary=STATE.with_suffix('.json.tmp');temporary.write_text(json.dumps(state,indent=2)+'\n');temporary.replace(STATE)
