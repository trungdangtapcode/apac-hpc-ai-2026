"""Inspect actual response speculation counters; never convert acceptance to speedup."""
import argparse,json,math
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--collection',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
r=json.loads(a.collection.read_text());token=r.get('token_control');cases=[]
for stage,rows in (token or {}).get('stages',{}).items():
 for row in rows:
  meta=row['response'].get('meta_info',{});keys=['spec_verify_ct','spec_num_correct_drafts','spec_num_proposed_drafts','spec_accept_rate','spec_accept_length','spec_correct_drafts_histogram']
  values={k:meta[k] for k in keys if k in meta};missing=[k for k in keys[:5] if k not in meta]
  case=dict(stage=stage,name=row['name'],available=values,missing=missing,elapsed_s=row.get('elapsed_s'),native_verification_observed=False)
  if not missing:
   verify=values['spec_verify_ct'];correct=values['spec_num_correct_drafts'];proposed=values['spec_num_proposed_drafts'];completion=meta['completion_tokens']
   valid=type(verify) is int and verify>0 and type(correct) is int and type(proposed) is int and 0<=correct<=proposed and proposed==2*verify
   valid=valid and math.isclose(values['spec_accept_rate'],correct/proposed,rel_tol=1e-6) and math.isclose(values['spec_accept_length'],completion/verify,rel_tol=1e-6)
   case.update(counter_identities_consistent=valid,native_verification_observed=valid)
  cases.append(case)
out=dict(job=r['job'],cases=cases,complete_requests_with_counters=sum(x['native_verification_observed'] for x in cases),
 units=dict(spec_verify_ct='target verification forward calls per request',spec_num_correct_drafts='accepted draft tokens, excluding bonus',spec_num_proposed_drafts='proposed draft tokens',spec_accept_rate='fraction, correct/proposed',spec_accept_length='output tokens per verification forward, including bonus'),
 scope='Actual diagnostic response metadata; no ranked throughput, cold-cache latency or speedup estimate',
 limitations=['Missing fields are not zero or proof of no speculation.','Runtime source/graph/state/precision and exact-ID review remain separate.','N1 elapsed time and acceptance length cannot replace a matched closed-loop score.'])
assert not a.out.exists(),'Preserve previous inspections';a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(job=out['job'],responses=len(cases),with_consistent_counters=out['complete_requests_with_counters'])))
