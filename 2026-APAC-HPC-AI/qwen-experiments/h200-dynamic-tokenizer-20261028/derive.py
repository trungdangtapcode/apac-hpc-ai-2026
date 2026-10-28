#!/usr/bin/env python3
"""Freeze one control and two prefill-only native batching interventions."""
import ast,hashlib,json,shutil,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;Q=D.parent;src=Q/'serving-tuning-11/s87-h200-native-r3-chunk8192';probe=int((D/'probe-job.txt').read_text())
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=src,check=True,stdout=subprocess.DEVNULL)
checks=[]
for name,wait in [('s90-h200-tokenizer-off',None),('s91-h200-tokenizer-200us',0.0002),('s92-h200-tokenizer-2ms',0.002)]:
 dst=Q/'serving-tuning-11'/name;shutil.copytree(src,dst);enabled=wait is not None
 cfg=json.loads((src/'config.json').read_text());cfg.update(experiment=name,label=name,source_parent=src.name,study_arm='native_prefill_dynamic_tokenizer',source_failed_jobs=[],matched_pair='R3 same-image N64 control versus prefill-only async dynamic tokenization; decode unchanged.',prefill_dynamic_tokenizer=enabled,prefill_tokenizer_batch_size=32,prefill_tokenizer_batch_timeout=wait if enabled else 0.002,prerequisite_job=probe if enabled else 26764)
 (dst/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
 s=(src/'worker.sh').read_text()
 if enabled:
  old='extra=(--chunked-prefill-size 8192';assert s.count(old)==1
  s=s.replace(old,f'extra=(--enable-dynamic-batch-tokenizer --dynamic-batch-tokenizer-batch-size 32 --dynamic-batch-tokenizer-batch-timeout {wait} --chunked-prefill-size 8192')
 (dst/'worker.sh').write_text(s)
 s=(src/'check-fast-runtime.py').read_text();old='    for key,wanted in common.items():';assert s.count(old)==1
 new='''    common.update(enable_dynamic_batch_tokenizer=cfg['prefill_dynamic_tokenizer'] if role.startswith('prefill') else False,
        dynamic_batch_tokenizer_batch_size=32,
        dynamic_batch_tokenizer_batch_timeout=cfg['prefill_tokenizer_batch_timeout'] if role.startswith('prefill') else 0.002,
        enable_tokenizer_batch_encode=False,skip_tokenizer_init=False)
'''
 s=s.replace(old,new+old);(dst/'check-fast-runtime.py').write_text(s)
 s=(src/'job.sbatch').read_text().replace(src.name,name).replace('#SBATCH -J ap42-s87-r3',f'#SBATCH -J ap42-{name[0:3]}-tok')
 if enabled:
  marker="PREREQ\nexport QWEN_JOB_START_EPOCH";assert marker in s
  proof=f'''PREREQ
python3 - <<'TOKENIZER'
import json
from pathlib import Path
r=json.loads(Path('{Q}/runs/{probe}/tokenizer-proof.json').read_text())
assert r['state']=='EXACT_DYNAMIC_TOKENIZER_IDS_PASS'
assert {{x['wait_seconds'] for x in r['checks']}}=={{0.0002,0.002}}
assert all(x['exact_input_ids']=='PASS' and x['batch_requests']==64 and x['single_request']==1 for x in r['checks'])
TOKENIZER
export QWEN_JOB_START_EPOCH'''
  s=s.replace(marker,proof)
 (dst/'job.sbatch').write_text(s)
 (dst/'TOKENIZER_PARENT.json').write_text(json.dumps({'parent':str(src.relative_to(Q)),'manifest_sha256':hashlib.sha256((src/'SHA256SUMS').read_bytes()).hexdigest(),'deriver':str(Path(__file__).relative_to(Q)),'probe':probe,'enabled':enabled,'timeout_seconds':wait,'intent':'Exact same tokenizer/model semantics; measure hypothetical frontend scheduling benefit, not an asserted CPU bottleneck.'},indent=2)+'\n')
 (dst/'README.md').write_text(f'''# Native prefill tokenizer batching: {name}

This is one full N64 arm in h200-dynamic-tokenizer-20261028. Prefill dynamic tokenization enabled: {enabled}; maximum batch 32; timeout {wait} seconds. Decode tokenization is unchanged. The control is a fresh same-runtime R3 arm. Previous 26766 passed at 3045.501509 good output tokens/s; larger chunks lost. Profiling-envelope decode activity was 100%, prefill 96.4/97.2%, but these values do not prove a CPU or GPU kernel bottleneck. Async tokenization is a new bounded frontend hypothesis, not a repeated losing concurrency or graph trial.

Pinned native TokenizerManager routes single strings through AsyncDynamicbatchTokenizer when enabled, preserving per-request tokenizer kwargs. The batch class runs the same tokenizer in a single background thread; it processes a lone request immediately and groups an already queued burst up to the configured wait/size. Actual string routing through the Rust gateway is not yet instrumented; the option may therefore have negligible effect. Exact concurrent and single input-ID equality is a mandatory CPU-only real-image prerequisite for candidate arms. Actual ServerArgs must show the intended values, never a silently disabled option. No model mathematics, prompt lengths, cache policy or output target changes.

All prior source/runtime/GPU/KV/semantic gates and full 60/120/30, N64, 4000/200, seed2026, joint SLA and local output checks remain. Each full job uses 16 H200/two nodes/17 minutes. No official accuracy or performance gain is claimed. Close the branch if neither candidate achieves a useful same-runtime gain above 1% without material tail regression; independently confirm a useful candidate before promotion.
''')
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in {'.sh','.sbatch'}:subprocess.run(['bash','-n',str(f)],check=True)
 for n in ['benchmark.sh','expected-input-config.json','check-performance.py','performance_gates.py','nixl-conn.py','kv_geometry.py','validate_kv_geometry.py','topology-job.sh','native-container.sh']:
  assert (src/n).read_bytes()==(dst/n).read_bytes(),n
 files=sorted(p for p in dst.iterdir() if p.is_file() and p.name!='SHA256SUMS')
 (dst/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=dst,check=True,stdout=subprocess.DEVNULL)
 checks.append({'bundle':name,'enabled':enabled,'wait_seconds':wait,'syntax':'PASS','retained_protocol_transport_geometry_identity':'PASS','manifest':'PASS'})
(D/'preparation.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks))
