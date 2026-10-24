#!/usr/bin/env python3
"""CPU-only source contract for the runnable, unsubmitted S55/S56 bundles."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PLAN=Path(__file__).resolve().parent
BUNDLES=ROOT/'serving-tuning-10'
S55=BUNDLES/'s55-h200-eagle3-perf-control'
S56=BUNDLES/'s56-h200-eagle3-perf-candidate'
REVIEW=ROOT/'research-review-25862-20261024/REVIEW.json'
BINDING=PLAN/'SOURCE_BINDING.json'

def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 a=json.loads((S55/'config.json').read_text()); b=json.loads((S56/'config.json').read_text())
 assert a['speculation'] is None
 assert {k:b['speculation'][k] for k in ('algorithm','steps','topk','draft_tokens','draft_attention_backend','draft_dtype','draft_quantization')}=={'algorithm':'EAGLE3','steps':2,'topk':1,'draft_tokens':3,'draft_attention_backend':'flashinfer','draft_dtype':'bfloat16','draft_quantization':'unquant'}
 assert b['speculation']['draft_revision']=='ff0f0c0999f6c86b21dfd2f5803eebc4ac712224'
 assert b['speculation']['draft_weight_sha256']=='bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86'
 assert b['speculation']['draft_bytes']==1145943008
 meta={'experiment','label','source_bundle','arm','speculation'}
 assert {k:v for k,v in a.items() if k not in meta}=={k:v for k,v in b.items() if k not in meta}, 'common controls differ across arms'
 assert a['prefill_max_running_requests']==b['prefill_max_running_requests']==48
 assert a['decode_max_running_requests']==b['decode_max_running_requests']==256
 assert a['prefill_chunked_prefill_size']==b['prefill_chunked_prefill_size']==8192
 assert a['expected_prefill_kv_regions_by_arm']==b['expected_prefill_kv_regions_by_arm']=={'control':188,'candidate':190}
 assert a['decode_cuda_graph_batch_sizes']==list(range(1,65))
 assert a['nixl_conn_wrapper_sha256']==b['nixl_conn_wrapper_sha256']=='45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8'
 assert a['native_nixl_patch_base_sha256']==b['native_nixl_patch_base_sha256']=='912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f'
 assert (a['concurrency'],a['warmup_seconds'],a['measure_seconds'],a['grace_seconds'])==(64,20,40,30)
 assert (a['synthetic_input_tokens_mean'],a['output_tokens_mean'],a['random_seed'])==(4000,200,2026)
 assert a['quality']=='UNKNOWN_NOT_EVALUATED' and a['ranked'] is False and a['official_score_claim'] is False and a['speedup_claim'] is False
 for bundle in (S55,S56):
  inp=json.loads((bundle/'expected-input-config.json').read_text())
  phase={p['name']:p for p in inp['phases']}
  assert phase['warmup']['duration']==20 and phase['warmup']['concurrency']==64
  assert phase['profiling']['duration']==40 and phase['profiling']['grace_period']==30 and phase['profiling']['concurrency']==64
  extra=inp['endpoint']['extra']; assert extra['min_tokens']==extra['max_tokens']==200 and extra['temperature']==0.0 and extra['ignore_eos'] is True
  dataset=inp['datasets'][0]; assert dataset['prompts']['isl']['mean']==4000 and dataset['prompts']['osl']['mean']==200 and dataset['random_seed']==2026
 assert sha(S55/'worker.sh')==sha(S56/'worker.sh'), 'worker argv source must be identical across arms'
 assert sha(S55/'check-client-image.py')==sha(S56/'check-client-image.py')
 assert 'st_mtime_ns' in (S55/'check-client-image.py').read_text() and 'st_ctime_ns' in (S55/'check-client-image.py').read_text()
 for bundle in (S55,S56):
  assert 'QWEN_NIXL_PATCH_SHA256=45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8' in (bundle/'job.sbatch').read_text()
 assert sha(S55/'topology-job.sh')==sha(S56/'topology-job.sh')
 worker=(S55/'worker.sh').read_text()
 assert '--dtype bfloat16 --enable-deterministic-inference' in worker
 for bundle in (S55,S56):
  runtime_src=(bundle/'check-deterministic-runtime.py').read_text()
  assert 'Disable --flashinfer-allreduce-fusion-backend because deterministic inference is enabled.' in runtime_src
  assert 'FlashInfer allreduce fusion is forcibly disabled via --enforce-disable-flashinfer-allreduce-fusion.' in runtime_src
 assert '--speculative-algorithm EAGLE3' in worker and 'if [[ ${QWEN_HAS_DRAFT:-0} == 1 ]]' in worker
 assert worker.count('--speculative-algorithm EAGLE3')==1
 for role,dir in [('S55',S55),('S56',S56)]:
  top=(dir/'topology-job.sh').read_text()
  assert 'T0+1020' in top and 'T0+600' in top and 'T0+960' in top
  assert '--max-running-requests 48' in top and '--max-running-requests 256' in top
  assert 'check-performance.py' in top and 'check-candidate-result.py' not in top and 'check-token-result.py' not in top
  assert 'QWEN_TUNE_NS=64' in top and 'QWEN_GRACE=30' in top
  bench=(dir/'benchmark.sh').read_text()
  assert '--synthetic-input-tokens-mean 4000' in bench and '--output-tokens-mean 200' in bench and '--random-seed 2026' in bench
  assert 'output-smoke.py' in bench and 'long-context-check.py' in bench
 review=json.loads(REVIEW.read_text())
 assert review['job']=='25862' and review['exact_output_gate']['state']=='FAIL'
 assert review['exact_output_gate']['candidate_repeat_stability'] is True
 assert sum(case['output_tokens_per_pass']*2 for case in review['exact_output_gate']['cases'])==1600
 bound=json.loads(BINDING.read_text())
 for key,item in bound.items():
  path=Path(item['path']); assert path.exists() and sha(path)==item['sha256'],f'bound source changed/missing: {key}'
 assert bound['25862_review']['sha256']==sha(REVIEW)
 print('PAIR_WORKER_AND_TOPOLOGY_CONTRACT_PASS')
 print('25862_STRICT_EXACT_ID_GATE_STILL_FAILED_1600_IDS')
 print('UNRANKED_QUALITY_UNKNOWN_NO_SPEEDUP_CLAIM')

if __name__=='__main__': main()
