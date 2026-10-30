#!/usr/bin/env python3
"""Replay actual harness gates with explicitly synthetic sparse runtime changes."""
from pathlib import Path
import copy,datetime,hashlib,importlib.util,json,subprocess,sys,tempfile
D=Path(__file__).resolve().parent;Q=D.parent;B=Q/'serving-tuning-11/s107-h200-sparse-graph-control';P=Q/'runs/27376'
spec=importlib.util.spec_from_file_location('sparse_gate',D/'check_sparse_graph_startup.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
cfg=json.loads((B/'config.json').read_text());warm=json.loads((P/'pair-warmup-context.json').read_text())
results=[]
with tempfile.TemporaryDirectory(prefix='ap42-s107-full-fixture-') as temp:
 a=Path(temp)/'27376';a.mkdir()
 for p in P.iterdir():
  if p.name in ['config.json','launch-context.json','runtime-readiness.json','sparse-graph-startup-gate.json','compile-receipts'] or p.name.endswith('.log'):continue
  (a/p.name).symlink_to(p,target_is_directory=p.is_dir())
 logs={role:(P/f'{role}.log').read_text() for role in ('prefill-0','prefill-1','decode-0')}
 old=str(list(range(1,65)));new=str(list(gate.GRAPH_BUCKETS))
 assert old in logs['decode-0'] and 'torch_compile_max_bs=32,' in logs['decode-0']
 logs['decode-0']=logs['decode-0'].replace(old,new).replace('torch_compile_max_bs=32,','torch_compile_max_bs=56,')
 logs['decode-0']='SPARSE_GRAPH_SOURCE_VERIFIED\n'+logs['decode-0']
 # Other log files remain exact original bytes.
 for p in P.glob('*.log'):
  (a/p.name).write_text(logs.get(p.stem,p.read_text()))
 (a/'config.json').write_text(json.dumps(cfg))
 context=json.loads((P/'launch-context.json').read_text())
 context['bundle_config_sha256']=hashlib.sha256((B/'config.json').read_bytes()).hexdigest()
 (a/'launch-context.json').write_text(json.dumps(context))
 def fast(want=True):
  p=subprocess.run([sys.executable,'-B',str(B/'check-fast-runtime.py'),str(a),'control','64'],capture_output=True,text=True)
  assert (p.returncode==0)==want,(p.stdout,p.stderr)
  return json.loads(p.stdout) if want else None
 runtime=fast();results.append('actual_fast_gate_accepts_synthetic_sparse_control')
 (a/'runtime-readiness.json').write_text(json.dumps(runtime))
 (a/'compile-receipts').mkdir()
 for rank in range(8):
  p=a/'compile-receipts'/f'rank-{rank}-pid-{1000+rank}.json'
  record={'schema':'native-qwen-torch-compile-startup-observer-v1','state':'RUNNING',
    'receipt_path':str(p),'job_id':'27376','experiment_id':warm['experiment_id'],'role':'decode-0',
    'rank':rank,'world_size':8,'distributed_initialized_at_hook':True,
    'native_source_sha256':gate.EXPECTED_NATIVE_SHA256,'module_source_sha256':gate.EXPECTED_NATIVE_SHA256,
    'updated_unix':3,'observer_disabled_unix':2,'observer_disabled_after_capture_shapes':list(gate.GRAPH_BUCKETS),
    'shapes':{str(s):{'compile_enabled_argument_seen':False,'successful_cuda_graph_captures':1} for s in gate.GRAPH_BUCKETS}}
  p.write_text(json.dumps(record))
 sparse=gate.check(a/'compile-receipts',a/'decode-0.log','control',B/'config.json','27376',warm['experiment_id'],'decode-0')
 assert sparse['ready_for_aiperf'],sparse
 (a/'sparse-graph-startup-gate.json').write_text(json.dumps(sparse))
 def performance(want=True):
  r=subprocess.run([sys.executable,'-B',str(B/'check-performance.py'),str(a)],capture_output=True,text=True)
  assert (r.returncode==0)==want,(r.stdout,r.stderr)
  return r
 performance();results.append('complete_independent_gate_replays_sparse_receipts_and_native_raw_control')
 for name,role,old,new in [
  ('reject_dense_runtime_list','decode-0',str(list(gate.GRAPH_BUCKETS)),str(list(range(1,65)))),
  ('reject_compile_enabled','decode-0','enable_torch_compile=False,','enable_torch_compile=True,'),
  ('reject_wrong_compile_cap','decode-0','torch_compile_max_bs=56,','torch_compile_max_bs=54,'),
  ('reject_physical_KV_disable','prefill-0','prefill_only_disable_kv_cache=False,','prefill_only_disable_kv_cache=True,'),
  ('reject_wrong_prefill_cache','prefill-1','impl=RadixCache ','impl=ChunkCache '),
  ('reject_missing_cache_source_guard','prefill-0','CACHE_LIFECYCLE_SOURCE_VERIFIED','CACHE_SOURCE_MISSING')]:
  assert old in logs[role],name
  (a/f'{role}.log').write_text(logs[role].replace(old,new));fast(False)
  (a/f'{role}.log').write_text(logs[role]);results.append(name)
 receipt=next((a/'compile-receipts').glob('rank-0-*'));original=receipt.read_text()
 for name,change in [
  ('reject_stale_job',lambda r:r.update(job_id='old')),
  ('reject_wrong_role',lambda r:r.update(role='prefill-0')),
  ('reject_missing_bucket56',lambda r:r['shapes'].pop('56')),
  ('reject_observer_still_active',lambda r:r.pop('observer_disabled_unix')),
  ('reject_source_mismatch',lambda r:r.update(native_source_sha256='0'*64))]:
  r=json.loads(original);change(r);receipt.write_text(json.dumps(r));performance(False)
  receipt.write_text(original);results.append(name)
 performance()
out={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'PASS_OFFLINE_COMPLETE_PIPELINE_FIXTURES',
 'fixtures':results,'count':len(results),'actual_GPU_or_Torch_runtime':False,
 'scope':'Native control27376 raw output is reused read-only, with explicitly synthetic sparse flags and rank receipts. This validates checker wiring, not actual S107 inference/capture/output/performance.'}
(D/'PIPELINE_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
