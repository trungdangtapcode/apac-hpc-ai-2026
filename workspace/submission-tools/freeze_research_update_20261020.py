"""Freeze retained research numbers and their source hashes for the 20 October talk."""
from pathlib import Path
import datetime,hashlib,json
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');W=Path('/home/apacsc42/workspace');O=W/'submission-review/research-update-2026-10-20';OLD=W/'submission-review/research-update-2026-10-17'
d=json.loads((OLD/'presentation-data.json').read_text());d['snapshot_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();d['latest']={'h200':{},'h100':{}}
def source(p):
 p=Path(p);d['sources'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
for j,f in [('24724','research-followup-20261019-0600'),('24736','research-followup-20261020-0028'),('24737','research-followup-20261020-0028'),('24738','research-followup-20261020-0028'),('24819','research-followup-20261020-0028'),('24912','research-followup-20261020-h200-load'),('24913','research-followup-20261020-0132'),('24914','research-followup-20261020-0132'),('24915','research-followup-20261020-0218')]:
 review=source(R/f/(j+'-review.json'));assert review['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS';d['latest']['h200'][j]=review
 summary=source(R/'runs'/j/'summary.json');d['h200'][j]=summary
 for row in summary:source(Path(row['export']))
for j in ['222027','222028']:
 review=source(R/'research-followup-20261020-0132'/(j+'.pbs111-review.json'));assert review['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS';d['latest']['h100'][j]=review
 inspect=source(R/'research-followup-20261020-0132'/(j+'.pbs111-inspection.json'));d['latest']['h100'][j]['extended']=inspect
for p in [R/'research-followup-20261020-0132/RESULTS.md',R/'research-followup-20261020-recv2/RESULTS.md',R/'resource-telemetry-20261020/source-validation.json',R/'research-followup-20261020-0028/H200_PROFILE.md',R/'research-followup-20261020-collective-graph/RESULTS.md',R/'research-followup-20261020-collective-pdl/RESULTS.md',R/'status-review-20261019-1755/CORRECTION.md']:
 d['sources'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
# Reuse the existing full-protocol scan implementation without rewriting its old report.
script=(W/'reports/all-history-metric-records-20261017/build.py').read_text().split("(O/'records.json').write_text",1)[0];namespace={'__file__':str(O/'scan.py')};exec(compile(script,'retained-full-protocol-scan','exec'),namespace)
d['historical_records']={'scope':'Full 60/120/30 and 4000/200 retained observations with reported SLA pass/zero errors. Not a fresh runtime/quality audit of every historical record.','counts':namespace['counts'],'records':namespace['records']}
for metrics in namespace['records'].values():
 for record in metrics.values():
  for row in record['ties']:
   source(Path(row['source']));source(Path(row['export']))
raw=R/'runs/24915/confirm/n62/artifacts/profile_export.jsonl';d['sources'][str(raw)]=hashlib.sha256(raw.read_bytes()).hexdigest();counts={'requests':0,'good':0,'ttft_breaches':0,'itl_breaches':0}
for line in raw.read_text().splitlines():
 row=json.loads(line)
 if row['metadata'].get('phase_kind',row['metadata'].get('benchmark_phase'))!='profiling':continue
 assert not row['metadata']['was_cancelled'] and not row.get('error') and not row.get('errors')
 ttft=row['metrics']['time_to_first_token']['value'];itl=row['metrics']['inter_token_latency']['value'];counts['requests']+=1;counts['good']+=ttft<=3000 and itl<=20;counts['ttft_breaches']+=ttft>3000;counts['itl_breaches']+=itl>20
assert counts=={'requests':1884,'good':1860,'ttft_breaches':24,'itl_breaches':0},counts
d['raw_latest_sla']=counts
(O/'presentation-data.json').write_text(json.dumps(d,indent=2)+'\n');(O/'historical-records-at-build.json').write_text(json.dumps(d['historical_records'],indent=2)+'\n')
for f in ['background-manifest.json','drawing-helpers.py']:(O/f).write_bytes((OLD/f).read_bytes())
print(json.dumps({'snapshot_utc':d['snapshot_utc'],'sources':len(d['sources']),'raw_sla':counts,'historical_counts':namespace['counts'],'records':{p:{k:[v['value'],v['ties'][0]['job'],v['ties'][0]['concurrency']] for k,v in metrics.items()} for p,metrics in namespace['records'].items()}},indent=2))
