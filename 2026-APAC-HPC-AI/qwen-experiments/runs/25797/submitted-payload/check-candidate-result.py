#!/usr/bin/env python3
"""Independent head gate for EAGLE3 actual IDs, reference binding, assets and runtime evidence."""
import hashlib, json, os, sys, subprocess
from pathlib import Path
from asset_identity import verify_asset_identity
from draft_identity import verify_post_full_fingerprint
from eagle_observation import observed
ROOT=Path(__file__).resolve().parent
PINNED_REFERENCE_SHA='a3b51d20cd6d67a3f659a5f84e6e787f319fb1e5464e5ddc912cdbdd78824c49'
PINNED_REVIEW_SEAL='563938c2189174218de57ec2f771557766c766b4afafc2ac6af2b2cfc92f3980'
PINNED_REVIEW_JSON_SHA='ebdacaf6bb930075a9811ca1ba2b2a2a1f7ecc0d9a04b1b511e199b0cbb69b35'
result_path=Path(sys.argv[1]); model=Path(sys.argv[2]); art=result_path.parent
reference_path=ROOT/'accepted-h200-reference.json'; review_path=ROOT/'accepted-h200-reference-review.json'
assert hashlib.sha256(reference_path.read_bytes()).hexdigest()==PINNED_REFERENCE_SHA
reference=json.loads(reference_path.read_text()); review=json.loads(review_path.read_text())
assert hashlib.sha256(review_path.read_bytes()).hexdigest()==PINNED_REVIEW_JSON_SHA
assert review.get('state')=='H200_TARGET_REFERENCE_ACCEPTED' and review.get('accepted_reference') is True
assert review.get('reference_sha256')==PINNED_REFERENCE_SHA and review.get('seal_sha256')==PINNED_REVIEW_SEAL
assert reference.get('schema')=='h200-target-reference-v1' and reference.get('passed') is True and reference.get('platform')=='H200'
result=json.loads(result_path.read_text()); corpus=json.loads((ROOT/'prepared-corpus.json').read_text())
assert result.get('schema')=='h200-eagle3-candidate-v1' and result.get('platform')=='H200' and result.get('passed') is True
assert result.get('corpus_sha256')==hashlib.sha256((ROOT/'prepared-corpus.json').read_bytes()).hexdigest()
assert corpus['cases']==reference['cases'] and len(corpus['cases'])==4
assert sum(len(row['observed']['output_ids']) for stage in reference['stages'].values() for row in stage)==1600
assert result['accepted_reference']=={'path':'accepted-h200-reference.json','sha256':PINNED_REFERENCE_SHA,'review_seal_sha256':PINNED_REVIEW_SEAL,'review_json_sha256':PINNED_REVIEW_JSON_SHA,'job':'25585'}
image=os.environ.get('QWEN_IMAGE_PATH'); assert image
asset=verify_asset_identity(ROOT/'asset-verification.json',model,image)
assert result.get('asset_identity')==asset
full_path=art/'draft-full-verification.json'; post_path=art/'draft-post-runtime-fingerprint.json'
draft=Path(os.environ['QWEN_DRAFT_PATH'])
post=verify_post_full_fingerprint(draft,full_path)
assert json.loads(post_path.read_text())==post
record=result.get('draft_identity',{})
assert record.get('full_verification')==json.loads(full_path.read_text()) and record.get('post_runtime_fingerprint')==post
assert record['full_verification']['files'][0]['sha256']=='bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86'
assert record['full_verification']['revision']=='ff0f0c0999f6c86b21dfd2f5803eebc4ac712224'
assert set(result.get('stages',{}))=={'eagle-a','eagle-b'}
assert len(result.get('comparisons',[]))==4
for stage,ref_stage in (('eagle-a','target-a'),('eagle-b','target-b')):
 rows=result['stages'][stage]; refs=reference['stages'][ref_stage]
 assert len(rows)==4
 for case,row,refrow in zip(corpus['cases'],rows,refs):
  assert row['name']==case['name'] and refrow['name']==case['name']
  expected={'input_ids':case['input_ids'],'stream':False,'return_logprob':True,'logprob_start_len':-1,'return_text_in_logprobs':False,
   'sampling_params':{'temperature':0.0,'top_p':1.0,'sampling_seed':2026,'max_new_tokens':200,'ignore_eos':True}}
  assert row['request']==expected and refrow['request']==expected
  assert row['observed']==observed(row['response'],len(case['input_ids']))
  assert row['observed']['output_ids']==refrow['observed']['output_ids']
  assert row['observed']['finish_reason']==refrow['observed']['finish_reason']
for i,case in enumerate(corpus['cases']):
 a,b=result['stages']['eagle-a'][i],result['stages']['eagle-b'][i]
 assert a['request']==b['request']
 assert a['observed']['output_ids']==b['observed']['output_ids'] and a['observed']['finish_reason']==b['observed']['finish_reason']
 c=result['comparisons'][i]
 assert c=={'name':case['name'],'exact_request_equal':True,'candidate_a_b_ids_finish_equal':True,
  'both_candidate_passes_match_accepted_reference_ids_finish':True,'both_passes_have_consistent_native_speculative_counters':True}
assert sum(len(row['observed']['output_ids']) for stage in result['stages'].values() for row in stage)==1600
assert len({row['experiment_id'] for stage in result['stages'].values() for row in stage if 'experiment_id' in row})<=1
run_token=hashlib.sha256(result['experiment_id'].encode()).hexdigest()[:32]
from warmup_semantic import check as check_pair_receipts
pair_receipts=check_pair_receipts(art/'pair-warmup-receipts',art/'endpoints.tsv',run_token)
assert result.get('semantic_pair_receipts')==pair_receipts and pair_receipts['pair_count']==2
runtime=subprocess.run([sys.executable,str(ROOT/'check-runtime.py'),str(art),str(ROOT)],capture_output=True,text=True,check=True)
assert json.loads(runtime.stdout)==json.loads((art/'runtime-readiness.json').read_text())
inspection_input=art/'speculative-metadata-head-input.json'
with inspection_input.open('x') as f: json.dump({'job':result['job'],'token_control':{'stages':result['stages']}},f)
inspection_path=art/'speculative-metadata-head-review.json'
inspection=subprocess.run([sys.executable,str(ROOT/'inspect-speculative-metadata.py'),'--collection',str(inspection_input),'--out',str(inspection_path)],capture_output=True,text=True,check=True)
inspection_record=json.loads(inspection_path.read_text())
assert inspection_record['complete_requests_with_counters']==8 and result.get('speculative_metadata_review')==inspection_record
geometry=subprocess.run([sys.executable,str(ROOT/'validate_kv_geometry.py'),str(art/'kv-geometry'),'--experiment-id',result['experiment_id'],
 '--expected-role','prefill-0=4','--expected-role','prefill-1=4','--expected-role','decode-0=8'],capture_output=True,text=True,check=True)
assert json.loads(geometry.stdout)==json.loads((art/'kv-geometry-validation.json').read_text())
print('H200_EAGLE3_CANDIDATE_ACCEPTED_EXACT_IDS_AND_RUNTIME_RECEIPTS')
