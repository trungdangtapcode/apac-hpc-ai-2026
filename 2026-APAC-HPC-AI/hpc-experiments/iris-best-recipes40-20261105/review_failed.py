"""Review five completed native arms without certifying the failed six-arm job."""
from pathlib import Path
import hashlib,json,math,re,statistics,sys
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E));from native_output import review_native_output
from run import compare_same_partition
O=E/'completed-2294920';D=O/'collected';R=D/'runs/2294920';c=json.loads((O/'collection.json').read_text())
assert c['scheduler']['State']=='FAILED' and c['scheduler']['ExitCode']=='1:0' and c['scheduler']['ElapsedRaw']=='6575' and c['scheduler']['AllocCPUS']=='56'
for name,meta in c['files'].items():
 raw=(D/name).read_bytes();assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256'],name
pins=json.loads((E/'deployment.json').read_text())['files'];assert c['frozen_runtime_hashes']==pins
assert set((R/'payload-before.log').read_text().splitlines())=={n+': OK' for n in pins}
for n,count in [(48,896),(56,1040)]:
 data=json.loads((R/f'source-observation-{n}.json').read_text());assert data['passed'] and data['core_files']==count and data['supplementary_files']==13
 assert not (R/f'source-after-{n}.json').exists()
assert not (R/'runtime-after.json').exists() and not (R/'comparison.json').exists()
partial=json.loads((R/'partial-results.json').read_text());rows=[];forces={};diagnostics={}
for label,n,handler in [('T1-teammate56',56,'collated'),('O1-original48',48,'uncollated'),('H1-hybrid48',48,'collated'),('H2-hybrid48',48,'collated'),('O2-original48',48,'uncollated')]:
 a=R/'arms'/label;log,timing,force,work=review_native_output(a,n);assert re.search(r'^I/O\s*:\s*'+handler+r'\b',log,re.M);assert json.loads((a/'return-code.json').read_text())['returncode']==0
 expected=next(r for r in partial['arms'] if r['arm']==label);assert timing==expected['timings_seconds'] and force==expected['force_coefficients_by_step'];forces[label]=force
 assert json.loads((a/'postsolve-fields.json').read_text())==json.loads((R/f'source-fields-{n}.json').read_text())
 prep=json.loads((R/(label+'-preparation.json')).read_text());assert prep['passed'] and prep['rank_count']==n and prep['cpu_affinity_nonoverlap']
 samples=[json.loads(line) for line in (a/'telemetry-samples.jsonl').read_text().splitlines()];status=json.loads((a/'telemetry-status.json').read_text());assert len(samples)==status['sample_count'] and all(x['required_components_available'] for x in samples)
 resources=(a/'resource-time.log').read_text();assert 'Exit status: 0' in resources
 diagnostics[label]={'samples':len(samples),'pressure_available_any':any(any(v.get('available') for v in s['pressure'].values()) for s in samples),'process_peak_RSS_KiB':int(re.search(r'Maximum resident set size \(kbytes\):\s*(\d+)',resources).group(1)),'resource_exit':0}
 sorted_t=sorted(timing);rows.append({'arm':label,'ranks':n,'steps':40,'intervals':39,'mean_s_step':statistics.mean(timing),'median_s_step':statistics.median(timing),'p95_s_step':sorted_t[math.ceil(.95*len(timing))-1],'maximum_s_step':max(timing)})
for a,b in [('O1-original48','O2-original48'),('H1-hybrid48','H2-hybrid48'),('O1-original48','H1-hybrid48'),('O2-original48','H2-hybrid48')]:assert compare_same_partition(forces[a],forces[b])['passed']
assert not (R/'arms/T2-teammate56/simpleFoam.log').exists()
failure=json.loads((R/'T2-teammate56-preparation.status.json').read_text());assert failure['returncode']==1
probe=json.loads((O/'RANK_PROBE_REPLAY.json').read_text());assert probe['diagnostically_recovered_records']==56 and probe['original_prefixed_line_parser_count']==55
original=(rows[1]['mean_s_step']+rows[4]['mean_s_step'])/2;hybrid=(rows[2]['mean_s_step']+rows[3]['mean_s_step'])/2
r={'job_id':'2294920','terminal_state':'FAILED','exit_code':'1:0','measurement_valid':False,'complete_six_arm_matrix':False,'partial_native_replays_passed':True,'partial_arms':rows,'diagnostic_only_O48_mean_s_step':original,'diagnostic_only_H48_mean_s_step':hybrid,'diagnostic_only_H48_time_change_vs_O48_percent':100*(hybrid/original-1),'rank_probe_failure':probe,'after_gates_reached':False,'telemetry_and_resources_inspected':diagnostics,'verified_files':len(c['files']),'elapsed_seconds':6575,'allocated_CPUs':56,'actual_allocated_CPU_hours':6575*56/3600,'cost_SU':None,'assessment':'The job is incomplete and invalid as a six-arm benchmark. Five complete native arms are retained diagnostic evidence; both H48 arms lose to neighboring O48 arms, justifying exclusion of unchanged hybrid from the next candidate. No complete teammate repeat or certified ranking exists.','next_decision':'Fix proof transport with exclusive per-rank files; qualify on a bounded MPI-only job. Then test default-mapped48 collated I/O versus O48 and actual T56 controls, retaining40steps/39intervals and absolute seconds primary.','limits':['T2 solver did not run; recovering all56 diagnostic stdout JSON records does not retroactively pass the job.','Source/runtime-after and final repeat gates were not reached; never call them passed.','Pressure data unavailable; no causal bandwidth/page-placement/communication profile collected.','Recorded process peak RSS is not aggregate MPI memory; missing telemetry is not zero.']}
(O/'REVIEW.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['rank_probe_failure','telemetry_and_resources_inspected']},indent=2))
