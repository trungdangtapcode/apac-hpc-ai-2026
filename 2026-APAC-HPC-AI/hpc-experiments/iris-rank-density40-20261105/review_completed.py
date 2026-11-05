"""Replay full native rank-density evidence and retain diagnostic limits."""
from pathlib import Path
import hashlib,json,math,re,statistics,sys
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E))
from native_output import review_native_output
from run import compare_same_partition
from helpers import runtime_identity_equal
O=E/'completed-2294916';D=O/'collected';R=D/'runs/2294916';c=json.loads((O/'collection.json').read_text())
for name,row in c['files'].items():
 raw=(D/name).read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name
assert c['scheduler']['State']=='COMPLETED' and c['scheduler']['ExitCode']=='0:0' and c['scheduler']['ElapsedRaw']=='5297' and c['scheduler']['AllocCPUS']=='56'
pins=json.loads((E/'deployment.json').read_text())['files'];assert c['frozen_runtime_hashes']==pins
for phase in ['before','after']:
 assert set((R/('payload-'+phase+'.log')).read_text().splitlines())=={n+': OK' for n in pins}
for n,count in [(48,896),(56,1040)]:
 pair=[json.loads((R/(f'source-{phase}-{n}.json' if phase=='after' else f'source-observation-{n}.json')).read_text()) for phase in ['before','after']]
 assert all(x['passed'] and x['rank_count']==n and x['core_files']==count and x['supplementary_files']==13 for x in pair)
 assert pair[0]==pair[1]
assert runtime_identity_equal(json.loads((R/'runtime-before.json').read_text()),json.loads((R/'runtime-after.json').read_text()))
comp=json.loads((R/'comparison.json').read_text());rows=[];force={};telemetry={}
for label,n in [('A1-scotch56',56),('B1-scotch48',48),('B2-scotch48',48),('A2-scotch56',56)]:
 a=R/'arms'/label;log,times,forces,work=review_native_output(a,n);force[label]=forces
 expected=next(x for x in comp['arms'] if x['arm']==label);assert times==expected['timings_seconds'];assert forces==expected['force_coefficients_by_step']
 assert json.loads((a/'return-code.json').read_text())['returncode']==0
 prep=json.loads((R/(label+'-preparation.json')).read_text());masks={int(k):set(v) for k,v in prep['cpu_affinity_masks'].items()};assert set(masks)==set(range(n)) and all(masks.values())
 assert all(not v&w for k,v in masks.items() for j,w in masks.items() if j>k)
 assert prep['passed'] and prep['no_source_inode_reuse'] and prep['rank_count']==n
 assert json.loads((a/'postsolve-fields.json').read_text())==json.loads((R/(f'source-fields-{n}.json')).read_text())
 assert json.loads((a/'solver-binding-review.json').read_text())['passed']
 resource=(a/'resource-time.log').read_text();assert 'Exit status: 0' in resource
 stats={key:float(re.search(pattern,resource).group(1)) for key,pattern in {'user_CPU_seconds':r'User time \(seconds\):\s*([\d.]+)','system_CPU_seconds':r'System time \(seconds\):\s*([\d.]+)','CPU_percent':r'Percent of CPU this job got:\s*([\d.]+)%','process_peak_RSS_KiB':r'Maximum resident set size \(kbytes\):\s*(\d+)'}.items()}
 samples=[json.loads(x) for x in (a/'telemetry-samples.jsonl').read_text().splitlines()];status=json.loads((a/'telemetry-status.json').read_text());assert len(samples)==status['sample_count'] and all(x['required_components_available'] for x in samples)
 telemetry[label]={'sample_count':len(samples),'sample_read_max_ms':max(x['collection_ms'] for x in samples),'minimum_node_MemAvailable_GiB':min(x['meminfo_kb']['MemAvailable'] for x in samples)/1024**2,'median_reported_CPU_frequency_MHz':statistics.median(x['cpuinfo_frequency']['median_mhz'] for x in samples),'pressure_available_any':any(any(v.get('available') for v in x['pressure'].values()) for x in samples),'resources':stats,'warnings':['Initial dynamic-code library lookup misses appear before normal compilation and successful completion; not established runtime failure.'] if 'cannot open shared object' in (a/'solver.stderr').read_text() else []}
 ordered=sorted(times);rows.append({'arm':label,'ranks':n,'steps':40,'intervals':39,'mean_s_step':statistics.mean(times),'median_s_step':statistics.median(times),'p95_s_step_nearest_rank':ordered[math.ceil(.95*len(times))-1],'maximum_s_step':max(times),'final_Cd':forces[-1][1]})
for labels in [('A1-scotch56','A2-scotch56'),('B1-scotch48','B2-scotch48')]:assert compare_same_partition(force[labels[0]],force[labels[1]])['passed']
a1,b1,b2,a2=[x['mean_s_step'] for x in rows];mean56=(a1+a2)/2;mean48=(b1+b2)/2;change=100*(mean48/mean56-1)
assert abs(change-comp['scotch48_vs_scotch56_percent'])<1e-10
review={'passed':True,'measurement_valid':True,'job_id':'2294916','scheduler':c['scheduler'],'arms':rows,'scotch56_mean_s_step':mean56,'scotch48_mean_s_step':mean48,'candidate_time_change_percent':change,'adjacent_time_changes_percent':[100*(b1/a1-1),100*(b2/a2-1)],'repeat_drift_percent':{'56':100*(a2/a1-1),'48':100*(b2/b1-1)},'telemetry_inspected':telemetry,'verified_files':len(c['files']),'actual_allocated_CPU_hours':5297*56/3600,'cost_SU':None,'assessment':'Both complete adjacent contrasts favor48 ranks in this allocation; promising matched signal, not independently confirmed or a winner against teammate/BTC. Reverse-order same-horizon confirmation is justified.','limits':['One forty-step allocation; candidate repeat drift and effect-size variation remain substantial.','Rank count and required partition change together; no isolated communication, memory or frequency cause established.','Python rank masks are pre-MPI_Init and solver binding reports are separate; no per-process bandwidth or solver-thread residency collected.','Whole-node phase samples include startup/exit; frequency reports are not hardware-cycle profiles.','Pressure telemetry unavailable; GNU time RSS is not summed MPI/node memory.','Different decompositions change intermediate Cd; Basic native fixed-work/source gates passed, no universal cross-partition Cd tolerance invented.','Not official full simulation, cross-platform comparison or scored contest result.']}
(O/'REVIEW.json').write_text(json.dumps(review,indent=2)+'\n');print(json.dumps({k:v for k,v in review.items() if k!='telemetry_inspected'},indent=2))
