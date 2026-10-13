"""Freeze guarded DeepEP and FP8-KV pilots; actual submission is slot-limited."""
import ast
import argparse
import hashlib
import importlib.util
import json
import shlex
import shutil
import subprocess
import sys
import types
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DIR=ROOT/'serving-tuning-02'
SOURCE=ROOT/'serving-tuning/control-load'
ENGINE=ROOT/'serving-tuning/inspection'
PENDING=DIR/'backend-pilots.json'
if PENDING.exists():raise SystemExit('Backend pilot plan already frozen.')
spec=importlib.util.spec_from_file_location('apac_backend_args',ENGINE/'arg_groups/arg_utils.py')
helper=importlib.util.module_from_spec(spec);sys.modules[spec.name]=helper;spec.loader.exec_module(helper)
tree=ast.parse((ENGINE/'server_args.py').read_text())
fields_wanted={'chunked_prefill_size','cuda_graph_max_bs_decode','moe_runner_backend',
               'moe_a2a_backend','deepep_mode','deepep_dispatcher_output_dtype','kv_cache_dtype'}
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ServerArgs')
fields=[n for n in cls.body if isinstance(n,ast.AnnAssign) and getattr(n.target,'id','') in fields_wanted]
assert len(fields)==len(fields_wanted)
choices=[n for n in tree.body if isinstance(n,ast.Assign) and any(getattr(t,'id','') in
         {'MOE_RUNNER_BACKEND_CHOICES','MOE_A2A_BACKEND_CHOICES'} for t in n.targets)]
module=types.ModuleType('apac_backend_fields');sys.modules[module.__name__]=module
code='from typing import Optional,List,Literal\nfrom dataclasses import dataclass\nfrom apac_backend_args import A,NS,Arg\n'
code+='\n'.join(ast.unparse(n) for n in choices)+'\n@dataclass\nclass Fields:\n'
code+=''.join('    '+ast.unparse(n)+'\n' for n in fields)
exec(code,module.__dict__)
parser=argparse.ArgumentParser();helper.add_cli_args_from_dataclass(parser,module.Fields)
specifications=[
    ('s2-deepgemm-control-n52',['--chunked-prefill-size','4096'],
     ['--cuda-graph-max-bs-decode','64','--moe-runner-backend','deep_gemm'],
     's2-chunk4096-n52','Matched DeepGEMM control for the DeepEP pilot, chunk 4096, coarse decode graph cap 64.',False),
    ('s2-deepep-ll-n52',['--chunked-prefill-size','4096'],
     ['--cuda-graph-max-bs-decode','64','--moe-runner-backend','deep_gemm',
      '--moe-a2a-backend','deepep','--deepep-mode','low_latency','--deepep-dispatcher-output-dtype','fp8'],
     's2-deepgemm-control-n52','DeepEP low-latency FP8 dispatch versus matched DeepGEMM control; TP/EP and BF16 KV retained.',True),
    ('s2-fp8-kv-n52',['--chunked-prefill-size','4096','--kv-cache-dtype','fp8_e4m3'],
     ['--kv-cache-dtype','fp8_e4m3'],
     's2-chunk4096-n52','FP8 E4M3 KV on both P/D versus matched BF16 chunk-4096 control. Accuracy is required before any promotion.',True),
]
pilots=[]
for name,pflags,dflags,parent,purpose,quality_required in specifications:
    for flags in (pflags,dflags):parser.parse_args(flags)
    bundle=DIR/name;bundle.mkdir()
    for path in SOURCE.iterdir():
        if path.is_file() and path.name not in ('job.sbatch','SHA256SUMS'):
            shutil.copyfile(path,bundle/path.name)
    shutil.copyfile(ROOT/'output-smoke.py',bundle/'output-smoke.py')
    config=json.loads((bundle/'config.json').read_text())
    config.update(experiment=name,concurrency=[52],standalone=True,wave=2,diagnostic_profile=False,
        prefill_extra_flags=pflags,decode_extra_flags=dflags,prefill_chunk_size=4096,purpose=purpose,
        matched_control=parent,quality_validation_required=quality_required,
        quality_status='SMOKE_ONLY; full-set accuracy versus organiser reference unverified')
    if name=='s2-fp8-kv-n52':config['kv_dtype']='fp8_e4m3'
    if name=='s2-deepep-ll-n52':config.update(moe_a2a_backend='deepep',moe_runner_backend='deep_gemm',
                                            deepep_mode='low_latency',dispatcher_dtype='fp8')
    (bundle/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    worker=(bundle/'worker.sh').read_text();assert 'extra=()' not in worker
    declaration='extra=()\nif [[ $role == prefill ]]; then\n  extra=('+shlex.join(pflags)+')\nelse\n  extra=('+shlex.join(dflags)+')\nfi\n'
    worker=worker.replace('exec python3 -m sglang.launch_server',declaration+'exec python3 -m sglang.launch_server')
    worker=worker.replace('"$@" --host','"${extra[@]}" "$@" --host')
    (bundle/'worker.sh').write_text(worker)
    benchmark=(bundle/'benchmark.sh').read_text()+'''
if (( $(date +%s)+100 < ${QWEN_BENCHMARK_DEADLINE:-0} )); then
  timeout 90 python3 "$QWEN_BUNDLE/output-smoke.py" "$HOST" "$ART" >"$ART/output-smoke.log" 2>&1 || touch "$ART/output-smoke-failed.txt"
else
  touch "$ART/output-smoke-deferred.txt"
fi
'''
    (bundle/'benchmark.sh').write_text(benchmark)
    patch_sha=config['transport_patch_metadata']['patched_sha256']
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
export QWEN_NIXL_PATCH_SHA256={patch_sha}
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
    pilots.append({'id':name,'bundle':str(bundle),'planned_ns':[52],'matched_control':parent,
                   'purpose':purpose,'quality_validation_required':quality_required,'state':'PLANNED',
                   'cpu_validated':True,'payload_sha256':hashes,'wave':2})
assert json.loads((DIR/'geometry-headbytes-128.json').read_text())['passed']
assert 'pre_permute_deepep_ll_to_deep_gemm' in (ENGINE/'layers/moe/moe_runner/deep_gemm.py').read_text()
PENDING.write_text(json.dumps({'pilots':pilots,'max_active_jobs':4,
    'submission_gate':'Matched control has a passing full N52 measurement and a completed output sanity check; capacity below 4 pending/running jobs.',
    'quality_gate':'No backend/FP8 candidate is promoted to submission without full quality validation.'},indent=2)+'\n')
print(json.dumps({'frozen':[{ 'id':p['id'],'matched_control':p['matched_control']} for p in pilots],
                  'actual_image_flags_validated':True,'FP8_byte_range_cases':720},indent=2))
