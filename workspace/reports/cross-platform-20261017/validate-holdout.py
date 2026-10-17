"""Offline validation against the frozen pre-result forecast; never submits jobs."""
from pathlib import Path
import json,hashlib,importlib.util,datetime
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');O=Path(__file__).resolve().parent

def save(d):
 p=O/'holdout-validation.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(p)

def review():
 frozen=json.loads((O/'pre-registered-prediction.json').read_text());job=frozen['holdout_job'];manifest=R/'runs'/job/'artifact-manifest.json'
 result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job':job,'state':'WAITING_FOR_TERMINAL_SEAL','prediction':frozen['predicted_good_output_tokens_s'],'tolerance_relative':frozen['tolerance_relative'],'accuracy_verified':False,'new_jobs_submitted':False,'no_universal_transfer_claim':True}
 if not manifest.exists():save(result);return result
 signature=hashlib.sha256(manifest.read_bytes()).hexdigest()
 previous=O/'holdout-validation.json'
 if previous.exists():
  p=json.loads(previous.read_text())
  if p.get('reviewed_seal_sha256')==signature and p.get('state') in ['LOCAL_HOLDOUT_SUPPORTED','LOCAL_HOLDOUT_NOT_SUPPORTED','EVIDENCE_INVALID_OR_INCOMPLETE']:
   return p  # Immutable seal already reviewed; preserve original conclusion.
 try:
  for name,digest in frozen['frozen_inputs_sha256'].items():
   if hashlib.sha256((O/name).read_bytes()).hexdigest()!=digest:raise ValueError('Frozen forecast input changed: '+name)
  spec=importlib.util.spec_from_file_location('wave10',R/'serving-tuning-10/review-wave10.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
  p=w.core.point(R,job,50);source=w.core.point(R,'24235',56);w.matched(R,p,source)
  if p['normalized_protocol']!=source['normalized_protocol']:raise ValueError('Normalised client protocol changed')
  long=w.long_check(R/'runs'/job);result['long_diagnostic']=long
  if not p['metrics']['sla_pass'] or long['state']!='PASSED':raise ValueError('SLA or separate long check did not pass')
  log=(R/'runs'/job/'decode-0.log').read_text()
  import re
  ranks=sorted(set(map(int,re.findall(r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3',log))))
  if ranks!=list(range(8)):raise ValueError('Missing eight-rank FlashInfer runtime proof')
  actual=p['metrics']['good_tokens_s'];prediction=result['prediction'];error=(actual-prediction)/prediction;passed=abs(error)<=result['tolerance_relative']
  result.update(state='LOCAL_HOLDOUT_SUPPORTED' if passed else 'LOCAL_HOLDOUT_NOT_SUPPORTED',actual_good_output_tokens_s=actual,signed_error_percent=100*error,absolute_error_percent=100*abs(error),metrics=p['metrics'],point=p,interpretation='One held-out N50 point;2% is an operational threshold,not95%coverage.No validation of otherconfigs/loads/GPUonlycausality.Keepnegativeevidence;do notrefitktohideerror.')
 except (ValueError,KeyError,OSError,TypeError,StopIteration,AssertionError) as e:
  result.update(state='EVIDENCE_INVALID_OR_INCOMPLETE',reason=str(e))
 result['reviewed_seal_sha256']=signature;save(result);return result

if __name__=='__main__':
 d=review();print(json.dumps({k:v for k,v in d.items() if k not in ['point']},ensure_ascii=False))
