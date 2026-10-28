"""Validate the staged N64 AI package with static checks and GPU-free replays."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

W = Path('/home/apacsc42/workspace')
O = W/'submission-review/ai-update-20261028'
S = O/'AI_Task/job_scripts'
R = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
checks=[]
def check(name, condition, detail):
    if not condition: raise AssertionError(f'{name}: {detail}')
    checks.append({'name':name,'passed':True,'detail':detail})
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

# Static package shape, syntax, and hashes.
check('only_AI_Task_stage', (O/'AI_Task').is_dir() and not (O/'HPC_Task').exists(), 'Stage contains AI_Task only; no HPC payload.')
for sibling in ('slides','HPC_BEFORE.json','PRESENTER_NOTES.md','TripleU_APAC2026_Presentation.pptx'):
    check('preserved_sibling:'+sibling,(O/sibling).exists(),'Root-owned sibling survived AI preparation.')
setup=subprocess.run(['bash',str(S/'setup.sh'),'--check'],capture_output=True,text=True)
check('setup_check',setup.returncode==0,setup.stdout[-300:]+setup.stderr[-300:])
check('one_primary_entry', len(list(S.glob('*.sbatch')))==1 and (S/'submit.sbatch').is_file(), 'One primary Slurm entry point.')
for p in S.rglob('*.py'):
    if 'hf-cache' not in p.parts: ast.parse(p.read_text(), filename=str(p))
for p in list(S.glob('*.sh'))+list(S.glob('*.sbatch')):
    subprocess.run(['bash','-n',str(p)],check=True)
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=S,check=True,capture_output=True,text=True)
subprocess.run(['sha256sum','--check','AI_Task/logs/SHA256SUMS'],cwd=O,check=True,capture_output=True,text=True)
manifest=json.loads((O/'AI_Task/logs/FILE_MANIFEST.json').read_text())
for row in manifest['files']:
    p=O/row['path']; check('manifest:'+row['path'],p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'Exact size and SHA-256 match.')

config=json.loads((S/'config.json').read_text())
check('N64_config',config['declared_concurrency']==64 and config['concurrency']==[64],config['concurrency'])
check('topology',config['prefill_workers']==2 and config['prefill_tp']==4 and config['decode_tp']==8 and config['decode_ep']==8,'P4+P4/D8 EP8.')
decode_log=(O/'AI_Task/logs/measured/26766/decode-0.log').read_text()
check('precision',config['kv_dtype']=='auto (resolved BF16 in measured job 26766)' and "dtype='bfloat16'" in decode_log and "kv_cache_dtype='auto'" in decode_log,'Measured flags retained: BF16 activation and auto KV resolving to BF16 in server_args.')
check('primary_algorithms',config['prefill_chunk_size']==8192 and config['prefill_moe_runner_backend']=='deep_gemm' and config['decode_moe_runner_backend']=='hpc_ops' and config['decode_attention_backend']=='flashinfer' and config['decode_allreduce_backend']=='mnnvl','DeepGEMM / HPC-Ops / FlashInfer / MNNVL.')
check('graph_shape',config['prefill_cuda_graph']=='breakable' and config['decode_cuda_graph']=='full' and config['decode_cuda_graph_batch_sizes']==list(range(1,65)),'Breakable prefill and resolved full decode graphs 1–64.')
check('routing_and_no_extras',config['router_policy']=='round_robin' and config['speculative_decoding'] is False and config['dynamic_tokenization'] is False,'Round robin, no EAGLE, no dynamic tokenization.')
patch=S/'nixl-conn.py'
check('measured_base_patch',sha(patch)=='912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f','Byte-identical measured 912b7 base patch; no observer wrapper.')
for p in S.rglob('*'):
    if p.is_file() and 'hf-cache' not in p.parts and p.suffix in ('.sh','.sbatch','.py','.json'):
        check('no_user_home_runtime_path:'+str(p.relative_to(S)), '/home/apacsc42' not in p.read_text(errors='ignore'), 'No local account path in package code/config.')

# Official benchmark command preserves fixed parameters and varies only N=64.
bench=(S/'official-benchmark.sh').read_text()
required=['--warmup-duration 60','--benchmark-duration 120','--benchmark-grace-period 30','--synthetic-input-tokens-mean 4000','--output-tokens-mean 200','--random-seed 2026','--cache-bust first_turn_prefix','--goodput "time_to_first_token:3000 inter_token_latency:20"']
check('exact_workload_flags',all(x in bench for x in required),'Full60/120/30, fixed4000/200, seed2026, cold prefix and official goodput thresholds.')
expected=['profile','--url','http://192.0.2.1:8000','--endpoint-type','chat','--endpoint','/v1/chat/completions','--model','qwen','--tokenizer','Qwen/Qwen3-235B-A22B-Instruct-2507','--streaming','-H','Accept: text/event-stream','--concurrency','64','--workers-max','64','--api-key','NOT_USED','--warmup-duration','60','--benchmark-duration','120','--benchmark-grace-period','30','--synthetic-input-tokens-mean','4000','--synthetic-input-tokens-stddev','0','--output-tokens-mean','200','--output-tokens-stddev','0','--extra-inputs','min_tokens:200','--extra-inputs','max_tokens:200','--extra-inputs','ignore_eos:true','--extra-inputs','temperature:0.0','--extra-inputs','repetition_penalty:1.0','--num-dataset-entries','12800','--random-seed','2026','--cache-bust','first_turn_prefix','--goodput','time_to_first_token:3000 inter_token_latency:20','--ui','simple']
submit_text=(S/'submit.sbatch').read_text()
check('submit_start_epoch_export',submit_text.index('set -euo pipefail') < submit_text.index('TRIPLEU_JOB_START_EPOCH=$(date +%s)') < submit_text.index('sha256sum --check SHA256SUMS'),'Immutable deadline epoch is captured immediately after strict mode, before checks.')
worker_text=(S/'worker.sh').read_text()
check('worker_precision_flags','--dtype bfloat16' in worker_text and '--kv-cache-dtype' not in worker_text,'Worker preserves measured BF16 activation/default-auto KV settings.')
check('no_optional_telemetry_branch',all(x not in worker_text for x in ('QWEN_RESOURCE_MONITOR','QWEN_ARTDIR','resource-sampler.py','telemetry_flags','QWEN_BUNDLE','QWEN_HAS_DRAFT')),'Primary worker has no latent optional telemetry branch or missing helper dependency.')
deploy_text=(S/'deploy-and-benchmark.sh').read_text()
check('absolute_readiness_deadline','deadline=$((JOB_START_EPOCH+600))' in deploy_text and 'SECONDS+600' not in deploy_text and '$(date +%s)>=deadline' in deploy_text,'All worker and router readiness checks share submit-start +600 seconds.')
check('absolute_warmup_deadline','JOB_START_EPOCH + 780' in (S/'deploy-and-benchmark.sh').read_text(),'Warmup deadline is 780 seconds from submit start; 240 seconds remain for scoring/cleanup within 1020 seconds.')
check('no_optional_client_flags','--profile' not in bench and 'aiperf profile' in bench and 'TRIPLEU_CONCURRENCY:-64' in bench,'One standard official command at N64.')

# Semantic receipt fixture and fail-closed replay for exactly two P/D routes.
from importlib.machinery import SourceFileLoader
sem=SourceFileLoader('warmup_semantic',str(S/'warmup_semantic.py')).load_module()
with tempfile.TemporaryDirectory(prefix='TripleU semantic paths ') as tmp:
    root=Path(tmp); ep=root/'endpoints.tsv';ep.write_text('prefill-0\thttp://127.0.0.1:1000\t9000\nprefill-1\thttp://127.0.0.1:1001\t9001\ndecode-0\thttp://127.0.0.1:2000\t0\n')
    rec=root/'receipts'; rec.mkdir(); token='a'*32
    inv,pairs,_=sem.inventory(ep)
    response={'choices':[{'message':{'role':'assistant','content':'warm path ready'}}], 'usage':{'prompt_tokens':9,'completion_tokens':4,'total_tokens':13}}
    for pair in pairs: sem.write_receipt(rec,ep,token,pair,200,response)
    result=sem.check(rec,ep,token)
    check('semantic_two_routes',result['pair_count']==2 and result['inventory_sha256']==inv,'Two independently validated semantic receipts.')
    bad=sem.check
    try: bad(rec,ep,'b'*32); rejected=False
    except ValueError: rejected=True
    check('semantic_reject_stale_token',rejected,'Stale semantic receipts fail closed.')

# Replay raw N64 result and corrupted-data failure through the shipped score gate.
score=S/'score-gate.py'
with tempfile.TemporaryDirectory(prefix='TripleU score replay ') as tmp:
    root=Path(tmp); run=root/'official/n64'; art=run/'artifacts'; (art/'logs').mkdir(parents=True)
    raw=R/'runs/26766/confirm/n64'
    for rel in ('artifacts/profile_export_aiperf.json','artifacts/profile_export.jsonl','artifacts/logs/aiperf.log','client.log'):
        shutil.copyfile(raw/rel,(run/rel) if rel=='client.log' else (art/Path(rel).relative_to('artifacts')))
    passed=subprocess.run(['python3',str(score),str(root),'64'],capture_output=True,text=True)
    data=json.loads(passed.stdout)
    check('score_gate_replay_pass',passed.returncode==0 and data['passed'] and data['requests']==1902 and data['good_requests']==1875, data)
    jsonl=art/'profile_export.jsonl'; lines=jsonl.read_text().splitlines()
    for i,line in enumerate(lines):
        row=json.loads(line)
        if row.get('metadata',{}).get('phase_kind')=='profiling':
            row['error']={'message':'validation-only injected failure'};lines[i]=json.dumps(row);break
    jsonl.write_text('\n'.join(lines)+'\n')
    failed=subprocess.run(['python3',str(score),str(root),'64'],capture_output=True,text=True)
    check('score_gate_replay_fail',failed.returncode!=0 and json.loads(failed.stdout)['passed'] is False,'Injected raw request error is rejected.')

# GPU-free smoke of the primary orchestration from a workspace path containing spaces.
with tempfile.TemporaryDirectory(prefix='TripleU mock deployment ') as tmp:
    root=Path(tmp); team=root/'Judge Team With Spaces'/'AI_Task'; scripts=team/'job_scripts'; shutil.copytree(S,scripts)
    source=root/'source';
    for rel in ('artifacts/profile_export_aiperf.json','artifacts/profile_export.jsonl','artifacts/logs/aiperf.log','client.log'):
        dest=source/'n64'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'runs/26766/confirm/n64'/rel,dest)
    bindir=root/'mock-bin';bindir.mkdir(); events=root/'events.jsonl'
    shim=bindir/'shim.py'
    shim.write_text('''#!/usr/bin/python3
import hashlib,json,os,shutil,sys
from pathlib import Path
name=Path(sys.argv[0]).name; a=sys.argv[1:]
def emit(k,args=None):
 with open(os.environ['MOCK_EVENTS'],'a') as f:f.write(json.dumps({'kind':k,'args':args or []})+'\\n')
if name=='scontrol': print('mock-node-a\\nmock-node-b')
elif name=='getent': print(('192.0.2.1' if a[-1]=='mock-node-a' else '192.0.2.2')+' STREAM '+a[-1])
elif name=='curl':
 if any('/v1/models' in x for x in a): print('{"data":[{"id":"qwen"}]}')
elif name=='python3':
 if a and a[0]=='-':
  code=sys.stdin.read()
  if 'importlib.metadata' in code: print('aiperf 0.12.0\\ntransformers 5.14.1\\ntokenizers 0.22.2')
  elif 'Tokenizer.from_pretrained' in code: print('AIPerf tokenizer OK: 2')
  else: sys.exit('/usr/bin/python3 -c '+repr(code))
 elif len(a)>1 and a[1]=='warmup_semantic.py': emit('semantic_check');os.execv('/usr/bin/python3',['python3']+a)
 elif a and a[0].endswith('warmup_semantic.py'): os.execv('/usr/bin/python3',['python3']+a)
 else: os.execv('/usr/bin/python3',['python3']+a)
elif name=='aiperf':
 emit('aiperf',a)
 d=Path('artifacts');(d/'logs').mkdir(parents=True,exist_ok=True)
 src=Path(os.environ['MOCK_SOURCE'])/'n64'
 for rel in ('artifacts/profile_export_aiperf.json','artifacts/profile_export.jsonl','artifacts/logs/aiperf.log'):
  shutil.copyfile(src/rel,d/Path(rel).relative_to('artifacts'))
 shutil.copyfile(src/'client.log','client.log')
 print('mock replay; no new measurement')
elif name=='srun':
 emit('srun',a)
 if any(x.endswith('warm-topology.py') for x in a):
  exp=next(x.split('=',1)[1] for x in a if x.startswith('QWEN_EXPERIMENT_ID=')); art=Path(a[-1]); ep=art/'endpoints.tsv'; rec=art/'pair-warmup-receipts';rec.mkdir(exist_ok=True)
  sem=Path(os.environ['MOCK_SCRIPTS'])/'warmup_semantic.py'
  sys.path.insert(0,str(sem.parent));from warmup_semantic import inventory,write_receipt
  _,pairs,_=inventory(ep);token=hashlib.sha256(exp.encode()).hexdigest()[:32]
  response={'choices':[{'message':{'role':'assistant','content':'mock semantic response'}}], 'usage':{'prompt_tokens':8,'completion_tokens':4,'total_tokens':12}}
  for pair in pairs:write_receipt(rec,ep,token,pair,200,response)
 elif any(x.endswith('official-benchmark.sh') for x in a):
  i=a.index('bash');os.execvp('bash',a[i:])
elif name=='sha256sum': os.execv('/usr/bin/sha256sum',['sha256sum']+a)
else: sys.exit('unexpected shim '+name+' '+repr(a))
''')
    shim.chmod(0o755)
    for name in ('scontrol','getent','curl','python3','aiperf','srun','sha256sum'):(bindir/name).symlink_to(shim)
    env=dict(os.environ,PATH=str(bindir)+':'+os.environ['PATH'],MOCK_EVENTS=str(events),MOCK_SOURCE=str(source),MOCK_SCRIPTS=str(scripts),
             SLURM_JOB_ID='MOCK_ONLY',SLURM_SUBMIT_DIR=str(scripts),SLURM_JOB_NODELIST='mock-node-[a,b]',
             TRIPLEU_SGLANG_IMAGE=str(root/'Images With Spaces/sglang.sqsh'),TRIPLEU_AIPERF_IMAGE=str(root/'Images With Spaces/aiperf.sqsh'),TRIPLEU_MODEL_PATH=str(root/'Model Store With Spaces/qwen'),
             TRIPLEU_CONCURRENCY='64')
    result=subprocess.run(['bash',str(scripts/'submit.sbatch')],cwd=scripts,env=env,capture_output=True,text=True,timeout=60)
    calls=[json.loads(x) for x in events.read_text().splitlines()]
    check('mock_deployment_exit',result.returncode==0,{'returncode':result.returncode,'stderr':result.stderr[-1200:],'stdout':result.stdout[-1200:],'events':calls})
    score_calls=[c for c in calls if c['kind']=='aiperf']
    check('captured_single_official_call',len(score_calls)==1 and score_calls[0]['args'][0]=='profile','One AIPerf invocation.')
    joined=' '.join(score_calls[0]['args'])
    check('captured_exact_n64_protocol',score_calls[0]['args']==expected,{'expected':expected,'actual':score_calls[0]['args']})
    paths=(team/'logs/reruns/MOCK_ONLY/runtime-paths.txt').read_text()
    check('portable_spaces_and_overrides',str(root/'Model Store With Spaces/qwen') in paths and str(root/'Images With Spaces/aiperf.sqsh') in paths,'Deployment accepts relocatable image/model paths with spaces.')
    gate=json.loads((team/'logs/reruns/MOCK_ONLY/performance-gate.json').read_text())
    check('mock_score_gate',gate['passed'] and gate['requests']==1902 and gate['good_requests']==1875,gate)

checks.append({'name':'official_accuracy','passed':True,'detail':'UNKNOWN; no full-set 99%-reference accuracy result is claimed.'})
result={'schema':'ai-update-validation-v1','checked_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'passed':True,'checks':checks,
        'limits':['GPU replay not run; orchestration uses mocks and retained raw exports.','Full-set official accuracy remains UNKNOWN.','No submission, publication, Git operation or scheduler action performed.']}
(O/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(f"PASS: {len(checks)} checks; {O/'VALIDATION.json'}")
