#!/usr/bin/env python3
"""Replay retained CPU-only fixtures for the fast-default pair; no GPU/network work."""
from __future__ import annotations
import hashlib, importlib.util, json, pathlib, shutil, subprocess, sys, tempfile
ROOT=pathlib.Path('/home/apacsc42/2026-APAC-HPC-AI')
EXP=ROOT/'qwen-experiments'; SERV=EXP/'serving-tuning-10'
S59=SERV/'s59-h200-fast-default-control'; S60=SERV/'s60-h200-fast-default-eagle3'
RUNS=EXP/'runs'; REVIEW=EXP/'research-review-25797-20261024/REVIEW.json'
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def run_runtime(bundle,art,arm,cap):
 p=subprocess.run([sys.executable,str(bundle/'check-fast-runtime.py'),str(art),arm,str(cap)],capture_output=True,text=True)
 if p.returncode: raise RuntimeError(f'fast runtime replay failed: {p.stderr or p.stdout}')
 return json.loads(p.stdout)
def import_module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def expect_fail(bundle,source,mutate,arm,cap,label):
 with tempfile.TemporaryDirectory(prefix='fastpair-cpu-') as td:
  d=pathlib.Path(td)
  for role in ('prefill-0','prefill-1','decode-0'):shutil.copy2(source/f'{role}.log',d/f'{role}.log')
  p=d/mutate[0]; t=p.read_text(); t2=mutate[1](t)
  if t2==t: raise AssertionError(f'{label}: fixture mutation did not apply')
  p.write_text(t2)
  proc=subprocess.run([sys.executable,str(bundle/'check-fast-runtime.py'),str(d),arm,str(cap)],capture_output=True,text=True)
  if proc.returncode==0: raise AssertionError(f'{label}: invalid runtime fixture unexpectedly passed')
  return {'expected_rejection':True,'error':(proc.stderr or proc.stdout).strip().splitlines()[-1]}

# Actual 25863 control full raw AIPerf and response-level gate replay.
expected=json.loads((S59/'expected-input-config.json').read_text())
gates=import_module(S59/'performance_gates.py','fast_perf_gates')
control_art=RUNS/'25863'
raw=gates.check_aiperf(control_art,expected,200)
export=json.loads((control_art/'screen/n64/artifacts/profile_export_aiperf.json').read_text())
raw_metrics={'ttft_avg_ms':export['time_to_first_token']['avg'],'ttft_p95_ms':export['time_to_first_token']['p95'],'itl_avg_ms':export['inter_token_latency']['avg'],'itl_p95_ms':export['inter_token_latency']['p95'],'raw_output_tokens_per_second':export['output_token_throughput']['avg'],'completed_output_tokens':export['output_token_count']['sum']}
smoke=gates.check_smoke(control_art,S59/'reference-output-smoke.json')
retrieval=gates.check_retrieval(control_art)
assert raw['completed']==636 and raw['errors']==raw['cancelled']==0
assert raw['good_request_fraction']>=.90 and smoke['passed']==7 and retrieval['passed']==12
assert abs(raw['good_output_tokens_per_second']-2796.146461353221)<1e-9
# Actual runtimes: 25863 matches prospective P64; candidate 25797 is historical P48 only.
control_runtime=run_runtime(S59,control_art,'control',64)
candidate_art=RUNS/'25797'; candidate_runtime=run_runtime(S60,candidate_art,'candidate',48)
assert control_runtime['state']=='PASS_FAST_RUNTIME' and candidate_runtime['state']=='PASS_FAST_RUNTIME'
assert candidate_runtime['prefill_cap']==48
# Strict negative probes on temporary copies prove runtime flags, KV dtype and MNNVL gates fail closed.
bad_det=expect_fail(S59,candidate_art,('prefill-0.log',lambda t:t.replace('enable_deterministic_inference=False','enable_deterministic_inference=True',1)),'candidate',48,'deterministic mode')
bad_kv=expect_fail(S59,candidate_art,('prefill-0.log',lambda t:t.replace('KV Cache is allocated. dtype: torch.bfloat16','KV Cache is allocated. dtype: torch.float16',1)),'candidate',48,'non-BF16 KV')
bad_mnnvl=expect_fail(S59,candidate_art,('decode-0.log',lambda t:__import__('re').sub(r'^.*FlashInfer AllReduce Fusion enabled and workspace initialized: backend=mnnvl, rank=7, world_size=8.*(?:\n|$)','',t,flags=__import__('re').M)), 'candidate',48,'missing MNNVL rank')
# Candidate binding is intentionally unbound until root reviews actual S59.
proc=subprocess.run([sys.executable,str(S60/'verify-control.py'),'/tmp/fastpair-unbound-control-test.json'],capture_output=True,text=True)
assert proc.returncode!=0 and 'root binding' in (proc.stderr+proc.stdout).lower()
review=json.loads(REVIEW.read_text())
exact={'state':review['state'],'job':review['job'],'token_ids':review['actual_output_token_ids'],
       'runtime_all16':review['runtime_all16'],'geometry_32_receipts':review['geometry_32_receipts'],
       'semantic_PD_paths':review['both_semantic_PD_paths'],'official_accuracy':review['official_accuracy'],
       'comparisons':{r['name']:{'candidate_repeats_equal':r['candidate_a_vs_b']['equal'],
          'candidate_matches_accepted_reference':r['candidate_a_vs_target']['equal'] and r['candidate_b_vs_target']['equal']} for r in review['comparisons']}}
assert exact['state']=='FAILED_PREDECLARED_EXACT_TOKEN_DIAGNOSTIC' and exact['token_ids']==1600
obj={'schema':'fast-default-pair-cpu-fixtures-v1','scope':'CPU-only replay of retained actual artifacts and negative parser probes; no H200 run or matched new experiment.',
 'control_job_25863':{'runtime':control_runtime,'raw_performance_replay':raw,'raw_latency_and_volume':raw_metrics,'smoke':smoke,'retrieval':retrieval,
   'source_artifact_sha256':{f:sha(control_art/f) for f in ['prefill-0.log','prefill-1.log','decode-0.log','summary.json','screen/n64/artifacts/profile_export_aiperf.json','screen/n64/artifacts/profile_export.jsonl','output-smoke.json','long-context-check.json']}},
 'historical_candidate_job_25797':{'runtime':candidate_runtime,'cap_note':'P cap 48 is the actual historical log state; override is used only to replay parser behavior and is not evidence for prospective P cap 64.','exact_ID_review':exact,'source_log_sha256':{f:sha(candidate_art/f'{f}.log') for f in ['prefill-0','prefill-1','decode-0']}},
 'negative_runtime_fixtures':{'deterministic_true_rejected':bad_det,'non_bf16_kv_rejected':bad_kv,'missing_native_mnnvl_rank_rejected':bad_mnnvl},
 'candidate_binding':{'state':'UNBOUND_FAIL_CLOSED','expected_exit_nonzero':True},
 'raw_metric_units':{'goodput_req_s':'requests/sec','good_output_tokens_per_second':'tokens/sec','TTFT_and_ITL':'milliseconds; raw AIPerf profile fixture retained at actual run path'}}
(ROOT/'qwen-experiments/eagle3-fastpath-performance-20261024/cpu-fixtures.json').write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
print(json.dumps({'state':'PASS_CPU_FIXTURES','goodput_req_s':raw['goodput_req_s'],'good_output_tokens_per_second':raw['good_output_tokens_per_second'],'good_request_fraction':raw['good_request_fraction'],'control_smoke':smoke['passed'],'control_retrieval':retrieval['passed'],'candidate_exact_ID_state':exact['state'],'candidate_fixture_Pcap':48,'new_matched_run':False},indent=2))
