#!/usr/bin/env python3
"""Audit the completed diagnostic records; never turn completion into acceptance."""
from pathlib import Path
import datetime,hashlib,json,subprocess
D=Path(__file__).resolve().parent;Q=D.parent;a=Q/'runs/27075';r=json.loads((a/'primitive.json').read_text())
state=subprocess.check_output(['sacct','-X','-j','27075','-P','--format=JobID,State,ExitCode,Elapsed,NodeList'],text=True)
assert '27075|COMPLETED|0:0|' in state
assert r['state']=='DIAGNOSTIC_COMPLETE_NO_PASS_CLAIM' and len(r['cases'])==28
expected={(tp,page,n) for tp in [4,8] for page in [1,16] for n in [15,16,17,31,32,33,4000]};seen=set();pairs=[];bad=[]
for c in r['cases']:
 g=c['geometry'];key=(g['tp_hypothesis'],g['page_tokens'],c['length_tokens']);assert key not in seen;seen.add(key)
 assert c['cache_write_exact'] and g['dtype']=='torch.bfloat16' and g['layout']=='nhd' and c['primitive_backend']=='fa2'
 assert g['item_lengths_bytes']==[g['page_tokens']*128*2]*2
 ok=c['relative_l2_vs_fp32_oracle']<=.01 and c['max_absolute_error_vs_fp32_oracle']<=.005
 assert c['strict_original_thresholds_pass']==ok
 if not ok:bad.append(list(key))
 if g['page_tokens']==16:
  assert c['relative_l2_vs_page1'] is not None;pairs.append(c['relative_l2_vs_page1'])
assert seen==expected and len(pairs)==14 and len(bad)==len(r['strict_threshold_failures'])
result={'reviewed_vietnam':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),'job':27075,'scheduler':state,'state':'COMPLETE_DIAGNOSTIC_NOT_CORRECTNESS_ACCEPTANCE','constructed_cases':28,'numerically_identical_page_pairs':sum(x==0 for x in pairs),'page_pairs':14,'maximum_page16_vs_page1_relative_L2':max(pairs),'strict_original_threshold_failures':bad,'maximum_relative_L2_vs_FP32':max(c['relative_l2_vs_fp32_oracle'] for c in r['cases']),'maximum_absolute_error_vs_FP32':max(c['max_absolute_error_vs_fp32_oracle'] for c in r['cases']),'maximum_absolute_error_vs_BF16_rounded_oracle':max(c['max_absolute_error_vs_bf16_rounded_fp32_oracle'] for c in r['cases']),'maximum_local_BF16_ULP_metric':max(c['max_error_in_local_bf16_ulp'] for c in r['cases']),'scope':'Native BF16 NHD pool writes/descriptors + FlashInfer fa2 paged decode for constructed one-layer local heads; not full-role P/D, prefill, performance or accuracy. Stored metrics audited; original output tensors were not retained to recompute attention independently.','collected_inspected':['28 native pool geometry/write and attention case records','source and model hashes','GPU identity','TF32-disabled oracle flag','stdout lifecycle and manifest validation','stderr setup warnings','terminal scheduler receipt'],'not_collected':['hardware utilization and time series','kernel profile','whole-model P/D registration and transport','actual production D head/layer registry','prefill attention execution','throughput/TTFT/ITL or official accuracy'],'decision':'Preserve original threshold failures. Page-pair equivalence supports this constructed decoding subcase only. No production gate relaxation; require prospective numerical criteria plus prefill and actual P/D geometry/transfer before a full page16 trial.'}
(D/'review-27075.json').write_text(json.dumps(result,indent=2)+'\n')
files=[]
for p in sorted(a.rglob('*')):
 if p.is_file() and not p.is_symlink() and p.name!='artifact-manifest.json':files.append({'path':str(p.relative_to(Q)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for p in [Q/'runs/27075.out',Q/'runs/27075.err']:files.append({'path':str(p.relative_to(Q)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(a/'artifact-manifest.json').write_text(json.dumps({'scheduler':state,'files':files},indent=2)+'\n')
print(json.dumps(result,indent=2))
