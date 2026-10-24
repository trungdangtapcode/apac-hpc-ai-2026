#!/usr/bin/env python3
"""Capture two exact-ID EAGLE3 passes and compare them with accepted H200 target IDs."""
from datetime import datetime, timezone
import hashlib, json, os, sys, time, urllib.request, subprocess
from pathlib import Path
from eagle_observation import observed
from asset_identity import verify_asset_identity
from draft_identity import verify_post_full_fingerprint
from warmup_semantic import check as check_pair_receipts
ROOT=Path(__file__).resolve().parent

def main():
    if len(sys.argv)!=4: raise SystemExit('usage: candidate-control.py HOST:PORT TARGET_MODEL ARTIFACT_DIR')
    gateway,model,art=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3])
    out=art/'eagle3-candidate.json'
    if out.exists(): raise FileExistsError(f'refusing to overwrite {out}')
    binding=json.loads((ROOT/'target-reference-binding.json').read_text())
    if binding.get('state')!='S46_TARGET_ACCEPTED': raise ValueError('candidate is blocked until root binds the actual reviewed S46 receipt')
    ref_path=(ROOT/binding['target_reference_file']).resolve(strict=True); review_path=(ROOT/binding['target_review_path']).resolve(strict=True)
    if ROOT not in ref_path.parents or ROOT not in review_path.parents: raise ValueError('bound reference/review must be retained inside candidate bundle')
    reference=json.loads(ref_path.read_text()); ref_hash=hashlib.sha256(ref_path.read_bytes()).hexdigest(); review_hash=hashlib.sha256(review_path.read_bytes()).hexdigest()
    ref_review=json.loads(review_path.read_text())
    if ref_hash!=binding['target_reference_sha256'] or review_hash!=binding['target_review_json_sha256'] or ref_review.get('seal_sha256')!=binding['target_review_seal_sha256'] or str(ref_review.get('job'))!=str(binding['target_job']): raise ValueError('S46 target receipt binding hash/seal mismatch')
    assert ref_review['state']=='H200_DETERMINISTIC_TARGET_REFERENCE_ACCEPTED' and ref_review['accepted_reference'] is True
    assert ref_review['reference_sha256']==ref_hash and reference['passed'] is True and reference['platform']=='H200'
    draft=Path(os.environ['QWEN_DRAFT_PATH'])
    full_path=art/'draft-full-verification.json'
    post_path=art/'draft-post-runtime-fingerprint.json'
    post=verify_post_full_fingerprint(draft,full_path)
    with post_path.open('x') as f: json.dump(post,f,indent=2); f.write('\n')
    image=os.environ.get('QWEN_IMAGE_PATH'); assert image
    target_identity=verify_asset_identity(ROOT/'asset-verification.json',model,image)
    corpus=json.loads((ROOT/'prepared-corpus.json').read_text())
    assert corpus['cases']==reference['cases']
    result={'schema':'h200-eagle3-candidate-v1','platform':'H200','created_utc':datetime.now(timezone.utc).isoformat(),
      'experiment_id':os.environ['QWEN_EXPERIMENT_ID'],'job':os.environ.get('SLURM_JOB_ID','cpu-fixture'),'passed':False,'scope':'EAGLE3 exact-ID correctness diagnostic only; no score or speedup claim',
      'corpus_sha256':hashlib.sha256((ROOT/'prepared-corpus.json').read_bytes()).hexdigest(),
      'accepted_reference':{'path':binding['target_reference_file'],'sha256':ref_hash,'review_seal_sha256':ref_review['seal_sha256'],'review_json_sha256':review_hash,'job':str(ref_review['job'])},
      'asset_identity':{},'draft_identity':{},'semantic_pair_receipts':{},'stages':{},'comparisons':[]}
    try:
      result['asset_identity']=target_identity
      run_token=hashlib.sha256(result['experiment_id'].encode()).hexdigest()[:32]
      result['semantic_pair_receipts']=check_pair_receipts(art/'pair-warmup-receipts',art/'endpoints.tsv',run_token)
      if result['semantic_pair_receipts']['pair_count']!=2: raise ValueError('both semantic P/D warmup receipts required')
      result['draft_identity']={'full_verification':json.loads(full_path.read_text()),'post_runtime_fingerprint':post}
      deadline=float(os.environ['QWEN_CLIENT_DEADLINE_EPOCH'])
      for stage in ('eagle-a','eagle-b'):
        result['stages'][stage]=[]
        for case in corpus['cases']:
          if time.time()>=deadline: raise TimeoutError('absolute EAGLE3 exact-token deadline exhausted')
          body={'input_ids':case['input_ids'],'stream':False,'return_logprob':True,'logprob_start_len':-1,'return_text_in_logprobs':False,
            'sampling_params':{'temperature':0.0,'top_p':1.0,'sampling_seed':2026,'max_new_tokens':200,'ignore_eos':True}}
          req=urllib.request.Request('http://'+gateway+'/generate',json.dumps(body).encode(),{'Content-Type':'application/json'})
          started=time.monotonic(); timeout=max(.1,min(45.,deadline-time.time()))
          with urllib.request.urlopen(req,timeout=timeout) as response:
            if response.status!=200: raise ValueError(f'/generate HTTP {response.status}')
            raw=response.read(2*1024*1024+1)
          if len(raw)>2*1024*1024: raise ValueError('response exceeded 2 MiB bound')
          payload=json.loads(raw); row={'name':case['name'],'request':body,'response':payload,'elapsed_s':time.monotonic()-started}
          row['observed']=observed(payload,len(case['input_ids']))
          result['stages'][stage].append(row); out.write_text(json.dumps(result,indent=2)+'\n')
      for idx,case in enumerate(corpus['cases']):
        a,b=(result['stages'][stage][idx] for stage in ('eagle-a','eagle-b'))
        ra,rb=(reference['stages'][stage][idx] for stage in ('target-a','target-b'))
        same_request=a['request']==b['request']==ra['request']==rb['request']
        repeat=(a['observed']['output_ids']==b['observed']['output_ids'] and a['observed']['finish_reason']==b['observed']['finish_reason'])
        matches_reference=(a['observed']['output_ids']==b['observed']['output_ids']==ra['observed']['output_ids']==rb['observed']['output_ids'] and
                           a['observed']['finish_reason']==b['observed']['finish_reason']==ra['observed']['finish_reason']==rb['observed']['finish_reason'])
        result['comparisons'].append({'name':case['name'],'exact_request_equal':same_request,'candidate_a_b_ids_finish_equal':repeat,
          'both_candidate_passes_match_accepted_reference_ids_finish':matches_reference,
          'both_passes_have_consistent_native_speculative_counters':a['observed']['speculative']['verification_observed'] and b['observed']['speculative']['verification_observed']})
      result['passed']=len(result['comparisons'])==4 and all(all(v for k,v in row.items() if k!='name') for row in result['comparisons'])
      if not result['passed']: raise ValueError('candidate/reference exact-ID or speculative metadata comparison failed')
      inspection_input=art/'speculative-metadata-input.json'
      with inspection_input.open('x') as f: json.dump({'job':result['job'],'token_control':{'stages':result['stages']}},f)
      inspection=subprocess.run([sys.executable,str(ROOT/'inspect-speculative-metadata.py'),'--collection',str(inspection_input),'--out',str(art/'speculative-metadata-review.json')],capture_output=True,text=True,check=True)
      inspection_record=json.loads((art/'speculative-metadata-review.json').read_text())
      if inspection_record['complete_requests_with_counters']!=8: raise ValueError('native speculative metadata inspection incomplete')
      result['speculative_metadata_review']=inspection_record
    except Exception as e:
      result['passed']=False; result['failure']={'type':type(e).__name__,'message':str(e)}
    out.write_text(json.dumps(result,indent=2)+'\n')
    raise SystemExit(0 if result['passed'] else 1)
if __name__=='__main__': main()
