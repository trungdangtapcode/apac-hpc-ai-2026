"""CPU-only validation with retained real snapshots and in-memory negative cases."""
import copy, datetime, importlib.util, json, tempfile, hashlib
from pathlib import Path
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments'); O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('review_n54',R/'serving-tuning/review-n54.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
results={}; points={}
for j in ['23778','23839','23780','23859']:
 p=m.point(R,j,52); points[j]=p
 results[j]={k:p[k] for k in ['job','metrics','sealed_files','seal_sha256','output_lengths']}
for a,b in [('23839','23778'),('23859','23780')]:
 results[a]['historical_matched_repeat_comparison']=m.compare_points(R,points[a],[points[b]])
base=R/'runs/23778/confirm/n52/artifacts';d=m.read(base/'profile_export_aiperf.json');mf=m.read(base/'phase_manifest.json')
cases=[]
def check(name,change,expected_error=True):
 a,b=copy.deepcopy(d),copy.deepcopy(mf);change(a,b)
 try:
  v=m.validate_metrics(a,b,52)
  assert not expected_error,(name,'incorrectly accepted')
 except (ValueError, KeyError) as e:
  assert expected_error,(name,e)
 cases.append({'case':name,'pass':True})
check('historical_valid',lambda a,b:None,False)
check('wrong_load',lambda a,b:a['input_config']['phases'][1].update(concurrency=54))
check('wrong_workers',lambda a,b:a['input_config']['runtime'].update(workers=54))
check('short_phase',lambda a,b:b['phases'][1].update(end_ns=b['phases'][1]['start_ns']+119*10**9))
check('cancelled_phase',lambda a,b:b['phases'][1].update(was_cancelled=True))
check('manifest_error',lambda a,b:b['phases'][1].update(error_request_count=1))
check('nonzero_error_metric',lambda a,b:a.update(error_request_count={'avg':1}))
check('missing_error_summary',lambda a,b:a.pop('error_summary'))
check('wrong_seed',lambda a,b:a['input_config']['datasets'][0].update(random_seed=2027))
check('wrong_token_settings',lambda a,b:a['input_config']['endpoint']['extra'].update(max_tokens=201))
check('nan_goodput',lambda a,b:a['goodput'].update(avg=float('nan')))
check('inconsistent_sla',lambda a,b:a['good_request_fraction'].update(avg=.5))
check('inconsistent_goodput',lambda a,b:a['goodput'].update(avg=1))
# A fully measured SLA failure must be represented as a measurement, not deployment failure.
a=copy.deepcopy(d);a['good_request_count']['avg']=int(a['request_count']['avg']*.85);a['good_request_fraction']['avg']=a['good_request_count']['avg']/a['request_count']['avg'];p=mf['phases'][1];a['goodput']['avg']=a['good_request_count']['avg']/((p['end_ns']-p['start_ns'])/1e9)
v=m.validate_metrics(a,mf,52);assert v['sla_pass'] is False;cases.append({'case':'complete_sla_fail_retains_measurement','pass':True})
# Normalize only runtime endpoints, artifact path and load, preserve all other settings.
a=copy.deepcopy(d['input_config']);a['endpoint']['urls']=['http://example.invalid'];a['artifacts']['dir']='/unused'
for p in a['phases']:p['concurrency']=54
a['runtime']['workers']=54
assert m.normalized(a)==m.normalized(d['input_config']);cases.append({'case':'only_intended_protocol_normalization','pass':True})
a['datasets'][0]['random_seed']=2027;assert m.normalized(a)!=m.normalized(d['input_config']);cases.append({'case':'normalization_preserves_seed_drift','pass':True})
for j in ['23924','23934']:
 v=m.review(R,j);assert v['state']=='INCOMPLETE_OR_INVALID_EVIDENCE' and 'No terminal artifact seal' in v['reason'];cases.append({'case':j+'_pending_not_measured','pass':True})
# Small synthetic trees exercise the seal gate without altering or copying real runs.
with tempfile.TemporaryDirectory(prefix='qwen-n54-review-') as tmp:
 root=Path(tmp);run=root/'runs/23924';run.mkdir(parents=True);(root/'serving-tuning').mkdir()
 (root/'serving-tuning/registry.json').write_text(json.dumps({'entries':[{'attempts':[{'job':'23924'}],'payload_sha256':{}}]}))
 f=run/'dummy.txt';f.write_text('evidence');seal={'job':'23924','status_at_seal':{'state':'COMPLETED','exit':'0:0'},'files':[{'path':'runs/23924/dummy.txt','bytes':8,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}]}
 path=run/'artifact-manifest.json';path.write_text(json.dumps(seal));v=m.review(root,'23924');assert 'required evidence unsealed' in v['reason'];cases.append({'case':'unsealed_required_rejected','pass':True})
 f.write_text('corrupt!');v=m.review(root,'23924');assert 'seal mismatch' in v['reason'];cases.append({'case':'corrupted_seal_rejected','pass':True})
 seal['status_at_seal']['state']='RUNNING';path.write_text(json.dumps(seal));v=m.review(root,'23924');assert 'no successful terminal seal' in v['reason'];cases.append({'case':'nonterminal_seal_rejected','pass':True})
result={'validated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'historical_baselines':results,'cpu_cases':cases,'new_gpu_measurement':False,'pending_candidate_runtime_validated':False}
(O/'offline-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'historical_goodtokens_s':{j:p['metrics']['good_tokens_s'] for j,p in points.items()},'cpu_cases_passed':len(cases),'new_gpu_measurement':False},indent=2))
