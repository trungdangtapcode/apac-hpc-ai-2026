#!/usr/bin/env python3
"""Replay semantic receipts and resolved tokenizer flags for pre-score failures."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,importlib.util,json,subprocess,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;Q=D.parent;reviews=[]
for job in [26849,26851,26853]:
 A=Q/f'runs/{job}';B=A/'submitted-payload';cfg=json.loads((A/'config.json').read_text())
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=B,check=True,stdout=subprocess.DEVNULL)
 assert not list(A.rglob('profile_export_aiperf.json'))
 p=B/'warmup_semantic.py';spec=importlib.util.spec_from_file_location('semantic_'+str(job),p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 token=hashlib.sha256(json.loads((A/'pair-warmup-context.json').read_text())['experiment_id'].encode()).hexdigest()[:32]
 checked=m.check(A/'pair-warmup-receipts',A/'endpoints.tsv',token);assert checked['pair_count']==2
 roles={}
 for role in ['prefill-0','prefill-1','decode-0']:
  text=(A/f'{role}.log').read_text(errors='replace');records=[x.split('server_args=',1)[1] for x in text.splitlines() if 'server_args=ServerArgs(' in x];assert len(records)==1
  node=ast.parse(records[0],mode='eval').body;args={x.arg:x.value for x in node.keywords}
  selected={k:ast.literal_eval(args[k]) for k in ['enable_dynamic_batch_tokenizer','dynamic_batch_tokenizer_batch_size','dynamic_batch_tokenizer_batch_timeout','enable_tokenizer_batch_encode','skip_tokenizer_init']}
  enabled=cfg['prefill_dynamic_tokenizer'] if role.startswith('prefill') else False
  assert selected['enable_dynamic_batch_tokenizer']==enabled
  assert selected['dynamic_batch_tokenizer_batch_size']==32
  assert selected['dynamic_batch_tokenizer_batch_timeout']==(cfg['prefill_tokenizer_batch_timeout'] if role.startswith('prefill') else 0.002)
  telemetry=[]
  for f in (A/'resource-telemetry').glob(role+'-g*.jsonl'):
   telemetry+=[json.loads(x) for x in f.read_text().splitlines() if x]
  samples=[x for x in telemetry if x.get('kind')=='sample'];last=samples[-1] if samples else {}
  roles[role]={'resolved_tokenizer_fields':selected,'selected_transport_errors':[x[:300] for x in text.splitlines() if any(w in x for w in ['KVTransferError','CUDA out of memory','NIXL transport error'])],'traceback_count':text.count('Traceback (most recent call last)'),'startup_warmup_samples':len(samples),'last_sample_gpu_activity_percent':[float(x['utilization.gpu']) for x in last.get('gpus',[])],'last_sample_server_metrics':last.get('server_metrics',[]),'limitations':'No scored request window exists. Startup hardware values do not establish a serving bottleneck.'}
 readiness=json.loads((A/'runtime-readiness.json').read_text());assert readiness['state']=='PASS_FAST_RUNTIME'
 err=(Q/f'runs/{job}.err').read_text();assert 'semantic pair warmup failed status=124' in err
 log=(A/'pair-warmup.log').read_text();assert 'ALL 2 P/D paths semantically initialized' in log
 scheduler=subprocess.check_output(['sacct','-n','-P','-X','-j',str(job),'--format=JobID,State,ExitCode,Elapsed,NodeList'],text=True);assert '|FAILED|1:0|' in scheduler
 reviews.append({'job':job,'terminal_scheduler':scheduler,'classification':'NATIVE_WARMUP_STEP_TIMEOUT_AFTER_VALID_SEMANTIC_RECEIPTS','semantic_replay':checked,'runtime_gate':readiness['state'],'roles':roles,'score':None,'profiling_errors':'NOT_MEASURED','ttft_ms':None,'itl_ms':None,'joint_sla_fraction':None,'local_scoring_output_checks':'NOT_REACHED','root_cause_limit':'The old wrapper had no command-return/removal timestamps. The precise post-semantic delay is unobserved; rootfs cleanup is a hypothesis, not proven culprit.'})
(D/'failure-review.json').write_text(json.dumps({'reviewed_utc':datetime.now(timezone.utc).isoformat(),'runs':reviews},indent=2)+'\n');print('3 terminal failures; all 6 semantic routes independently replay PASS; resolved intended tokenizer flags PASS; no benchmark score')
