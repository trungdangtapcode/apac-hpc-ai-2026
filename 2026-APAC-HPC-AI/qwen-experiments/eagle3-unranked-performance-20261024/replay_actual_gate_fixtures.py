#!/usr/bin/env python3
"""Replay readiness and client gates against retained actuals without combining them as one run."""
from __future__ import annotations
import hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
Q=ROOT
B=ROOT/'serving-tuning-10/s56-h200-eagle3-perf-candidate'
RUN25862=ROOT/'runs/25862'
RUN25920=ROOT/'runs/25920'
REV=json.loads((ROOT/'research-review-25862-20261024/REVIEW.json').read_text())
BIND=json.loads((Path(__file__).with_name('ACTUAL_GATE_REPLAY_BINDING.json')).read_text())
for group, rows in BIND['jobs'].items():
    for name, item in rows.items():
        p=Path(item['path'])
        assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'], f'actual replay source changed: {group}/{name}'

def run_json(args):
    result=subprocess.run([sys.executable,*map(str,args)],capture_output=True,text=True)
    if result.returncode:
        raise RuntimeError(f"fixture checker failed: {' '.join(map(str,args))}\n{result.stdout}\n{result.stderr}")
    return json.loads(result.stdout)

# Replay S49 actual runtime, draft identity, geometry and semantic receipts from job 25862.
runtime=run_json([B/'check-deterministic-runtime.py',RUN25862,'--eagle'])
assert runtime['state']=='PASS'
draft=run_json([B/'headcheck-worker-drafts.py',RUN25862,RUN25862/'draft-full-verification.json'])
assert draft['state']=='PASS'
geometry=run_json([B/'validate_kv_geometry.py',RUN25862/'kv-geometry','--experiment-id',REV['experiment_id'],'--expected-role','prefill-0=4','--expected-role','prefill-1=4','--expected-role','decode-0=8'])
assert geometry['passed'] is True and geometry['observed_prefill_mha_signature']['kv_regions_per_rank']==190
warm=json.loads((RUN25862/'pair-warmup-context.json').read_text())
spec=importlib.util.spec_from_file_location('warm_semantic',B/'warmup_semantic.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
semantic=module.check(RUN25862/'pair-warmup-receipts',RUN25862/'endpoints.tsv',hashlib.sha256(warm['experiment_id'].encode()).hexdigest()[:32])
assert semantic['pair_count']==2

# Replay raw N=64 input/SLA rows and raw smoke/retrieval response gates from separate actual job 25920.
S55=ROOT/'serving-tuning-10/s55-h200-eagle3-perf-control'
gate_spec=importlib.util.spec_from_file_location('performance_gates',S55/'performance_gates.py')
gates=importlib.util.module_from_spec(gate_spec); gate_spec.loader.exec_module(gates)
expected=json.loads((S55/'expected-input-config.json').read_text())
profile=gates.check_aiperf(RUN25920,expected)
smoke=gates.check_smoke(RUN25920,S55/'reference-output-smoke.json')
retrieval=gates.check_retrieval(RUN25920)
assert profile['request_errors']==0 and profile['cancellations']==0 and smoke['passed']>=7 and retrieval['passed']==12
# Explicitly describe this as separate gate fixtures, never as a combined run or performance comparison.
print(json.dumps({'state':'ACTUAL_GATE_FIXTURE_REPLAY_PASS','fixture_jobs_separate':['25862','25920'],
    '25862_gates':['deterministic_runtime','draft_worker_identity','native_geometry_190','semantic_pd_2'],
    '25920_gates':['raw_profile_input_and_SLA','raw_smoke_responses_7_of_8','raw_retrieval_responses_12'],
    'single_run_evidence':False,'performance_claim':False,'quality_claim':False},indent=2))
