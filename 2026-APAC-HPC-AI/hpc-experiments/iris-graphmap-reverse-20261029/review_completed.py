"""Replay all four native screen outputs and inspect repeat/time limitations."""
from pathlib import Path
import datetime,hashlib,json,statistics,sys
E=Path(__file__).resolve().parent
sys.path.insert(0,str(E))
from review_short_output import review
JOB=json.loads((E/'submission-receipt.json').read_text())['job_id'];OUT=E/('completed-'+JOB);C=OUT/'collected';R=C/'runs'/JOB
collection=json.loads((OUT/'collection.json').read_text());sched=collection['scheduler']
assert sched['State']=='COMPLETED' and sched['ExitCode']=='0:0' and sched['AllocCPUS']=='56'
for n,row in collection['files'].items():
 raw=(C/n).read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
summary=json.loads((R/'comparison.json').read_text());assert summary['passed'] and not summary['scored_result']
assert json.loads((R/'rankmap-validation.json').read_text())['passed']
assert json.loads((R/'accepted-source-validation.json').read_text())['passed']
assert json.loads((R/'graph-boundary-validation.json').read_text())['passed']
before=json.loads((R/'source-tree-before.json').read_text());after=json.loads((R/'source-tree-after.json').read_text());assert before==after['manifest']
assert before==json.loads((E/'accepted-source-manifest.json').read_text())
runtime_before=json.loads((R/'runtime-before.json').read_text());runtime_after=json.loads((R/'runtime-after.json').read_text());assert runtime_before['tools']==runtime_after['tools'] and runtime_before['libraries']==runtime_after['libraries']
source_seal=json.loads((R/'source-field-seal.json').read_text());by_arm={a['arm']:a for a in summary['arms']};arms={}
for label in [a['arm'] for a in summary['arms']]:
 a=R/'arms'/label;parsed=review(a);saved=by_arm[label]
 assert parsed['timings_seconds']==saved['timings_seconds'] and parsed['Cd_by_step']==saved['Cd_by_step']
 assert len(parsed['timings_seconds'])==13 and len(parsed['Cd_by_step'])==14
 assert json.loads((a/'solver-return-code.json').read_text())['returncode']==0
 assert json.loads((a/'copy-verification.json').read_text())['passed']
 assert json.loads((a/'source-and-control-validation.json').read_text())['steps']==14
 for name in ('initialized-fields-seal.json','post-solver-time0-field-seal.json'):
  assert json.loads((a/name).read_text())['fields']==source_seal['fields']
 log=(a/'simpleFoam.log').read_text();confidence=[x.strip() for x in log.splitlines() if 'Minimum number of measured time steps' in x]
 resource=(a/'resource-time.log').read_text();resources={}
 for key in ('User time (seconds)','System time (seconds)','Percent of CPU this job got','Maximum resident set size (kbytes)','Major (requiring I/O) page faults','Swaps'):
  resources[key]=next((x.strip()[len(key)+1:].strip() for x in resource.splitlines() if x.strip().startswith(key+':')),None)
 arms[label]={'mean_seconds_per_step':parsed['mean_seconds_per_step'],'median_seconds_per_step':parsed['median_seconds_per_step'],'p95_seconds_per_step':parsed['p95_seconds_per_step'],'maximum_seconds_per_step':parsed['maximum_seconds_per_step'],'max_at_step':2+parsed['timings_seconds'].index(max(parsed['timings_seconds'])),'steps':14,'timings':13,'native_sample_recommendation_lines':confidence,'resource_selected':resources,'final_Cd':parsed['Cd_by_step'][-1][1]}
phases=[json.loads(x) for x in (R/'phases.jsonl').read_text().splitlines()];exits=[x for x in phases if x['state']=='exit'];assert exits and all(x['returncode']==0 for x in exits)
a1=arms['A1-default']['mean_seconds_per_step'];a2=arms['A2-default']['mean_seconds_per_step'];b1=arms['B1-graph']['mean_seconds_per_step'];b2=arms['B2-graph']['mean_seconds_per_step']
cd={label:by_arm[label]['Cd_by_step'] for label in by_arm}
record={'passed':True,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':JOB,'scheduler':sched,'all_transfer_hashes_verified':True,'collected_files':len(collection['files']),'all_native_gates_passed':True,'runtime_and_source_stable':True,'scored_result':False,'arm_order':list(arms),'arms':arms,'aggregate_candidate_vs_control_percent':100*((b1+b2)/(a1+a2)-1),'first_adjacent_B1_vs_A1_percent':100*(b1/a1-1),'control_repeat_A2_vs_A1_percent':100*(a2/a1-1),'candidate_repeat_B2_vs_B1_percent':100*(b2/b1-1),'Cd':{'control_repeats_exactly_equal':cd['A1-default']==cd['A2-default'],'candidate_repeats_exactly_equal':cd['B1-graph']==cd['B2-graph'],'all_arms_exactly_equal':all(x==cd['A1-default'] for x in cd.values()),'max_absolute_total_Cd_B1_vs_A1':max(abs(x[1]-y[1]) for x,y in zip(cd['A1-default'],cd['B1-graph'])),'final_total_Cd_B1_vs_A1_percent':100*(cd['B1-graph'][-1][1]/cd['A1-default'][-1][1]-1)},'assessment':'Short reversed screening result requires joint review with parent ABBA, per-arm tails and treatment-position drift before promoting a mapping gain.','limits':['14 steps / 13 correlated timing intervals per arm, one allocation, one ABBA cycle.','CPU frequency, per-rank memory bandwidth, hardware NUMA traffic and actual solver helper-thread affinity were not collected.','GNU time is command-level accounting, not per-rank RSS or bandwidth.','This is not a full 150-step result, NSCC speedup, or official score.'],'next_hypothesis':'Review this BAAB jointly with the parent ABBA; select further measurements only from the qualified result.'}
(OUT/'REVIEW.json').write_text(json.dumps(record,indent=2)+'\n')
(E/'REVIEW.json').write_text(json.dumps({'passed':True,'job_id':JOB,'review_path':str((OUT/'REVIEW.json').relative_to(E)),'review_sha256':hashlib.sha256((OUT/'REVIEW.json').read_bytes()).hexdigest(),'scored_result':False,'assessment':record['assessment']},indent=2)+'\n')
print(json.dumps({k:record[k] for k in ('aggregate_candidate_vs_control_percent','first_adjacent_B1_vs_A1_percent','control_repeat_A2_vs_A1_percent','candidate_repeat_B2_vs_B1_percent','Cd')}))
