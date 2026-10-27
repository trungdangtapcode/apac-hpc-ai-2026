"""Verify the complete 50-step horizon without promoting an unmatched speedup."""
from pathlib import Path
import hashlib,json,math,re,statistics,sys,tarfile,tempfile
E=Path(__file__).resolve().parent;B=E.parent;sys.path.insert(0,str(B))
from native_output import review_native_output
meta=json.loads((E/'collection.json').read_text());arc=E/'raw-evidence.tar.gz'
assert hashlib.sha256(arc.read_bytes()).hexdigest()==meta['archive_sha256']
with tarfile.open(arc) as tar:
 members=tar.getmembers();assert all(m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts for m in members)
 data={m.name:tar.extractfile(m).read() for m in members}
assert len(members)==len(data) and set(data)==set(meta['files'])
for name,raw in data.items():assert len(raw)==meta['files'][name]['bytes'] and hashlib.sha256(raw).hexdigest()==meta['files'][name]['sha256']
assert meta['remote_runtime_hashes']==json.loads((B/'payload-sha256.json').read_text())['files']
account=[x.split('|') for x in meta['accounting'].splitlines()[1:]]
job=next(x for x in account if x[0]=='2294148');assert job[1:6]==['COMPLETED','0:0','1224','56','iris009']
r='runs/2294148/';prefix='cases/zyx/'
for name,raw in data.items():
 if name.startswith(r) and name.endswith('.status.json'):assert json.loads(raw)['returncode']==0
assert not data['kit/runs/2294148.err'] and b'SINGLE_ZYX_50STEP_HORIZON_EXTENSION_PASS' in data['kit/runs/2294148.out']
result=json.loads(data[r+'result.json']);assert result['passed'] and result['comparison'] is False and result['scored_result'] is False and result['order']==['zyx']
row=result['arms_by_order']['zyx'];assert set(result['arms_by_order'])=={'zyx'} and row['steps']==50 and row['intervals']==49
assert data[prefix+'source-before.json']==data[prefix+'copy-check.json']==data[prefix+'source-after.json']
seal=json.loads(data[prefix+'source-before.json']);assert len(seal['symlinks'])==1
assert all('processor'+str(i)+'/0/'+f in seal['files'] for i in range(56) for f in ['U','p','k','omega','nut','nuTilda'])
assert json.loads(data[r+'zyx-source.json'])=={'passed':True,'pinned_input_files':41,'order':'zyx','factors':[7,4,2]}
with tempfile.TemporaryDirectory() as temp:
 root=Path(temp)
 for name,raw in data.items():
  p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 arm=root/'cases/zyx';assert json.loads((arm/'return-code.json').read_text())['returncode']==0
 log,times,cd,counts=review_native_output(arm)
 assert times==row['timings_seconds'] and counts==row['fixed_iterations'] and cd==row['Cd_by_step'] and cd[-1][1]==row['final_Cd']
 assert abs(statistics.mean(times)-row['mean_seconds_per_step'])<1e-10
 assert abs(statistics.median(times)-row['median_seconds_per_step'])<1e-10
 assert abs(statistics.quantiles(times,n=100,method='inclusive')[94]-row['p95_seconds_per_step'])<1e-10
 assert max(times)==row['maximum_seconds_per_step']
 assert row['timing_by_step_seconds']=={str(i):x for i,x in zip(range(2,51),times)}
 for key,segment in [('steps_2_to_30',times[:29]),('steps_31_to_50',times[29:])]:
  stated=row['descriptive_timing_segments'][key];assert stated['samples']==len(segment) and abs(stated['mean_seconds']-statistics.mean(segment))<1e-10 and abs(stated['median_seconds']-statistics.median(segment))<1e-10
 assert re.search(r'(?m)^startFrom\s+startTime;', (arm/'system/controlDict').read_text())
 assert re.search(r'(?m)^endTime\s+50;', (arm/'system/controlDict').read_text())
 assert (arm/'system/fvSolution').read_bytes()==(B/'payload-case/system/fvSolution.fixedIter').read_bytes()
 affinity=[json.loads((arm/'affinity'/('rank-%02d.json'%i)).read_text()) for i in range(56)]
 assert [x['rank'] for x in affinity]==list(range(56)) and len({x['host'] for x in affinity})==1
 assert all(len(x['affinity_cpus'])==1 for x in affinity) and len({tuple(x['affinity_cpus']) for x in affinity})==56
 std=statistics.pstdev(times);formula=(1.96*std/(0.02*statistics.mean(times)))**2
 native_min=int(re.search(r'Minimum number of measured time steps[^\n]*=\s*(\d+)',log)[1]);assert native_min==row['native_minimum_samples']==math.floor(formula+0.5)
 resource=(arm/'resource-time.log').read_text();stderr=(arm/'solver.stderr').read_text()
 assert not re.search(r'FOAM FATAL|FOAM ERROR|MPI_ABORT|died from signal|core dumped',stderr,re.I)
 if stderr.strip():assert 'libwallClockTimeStatistics_' in stderr and 'cannot open shared object file' in stderr and 'wmake libso' in log
 diagnostics={}
 for label in ['User time (seconds)','System time (seconds)','Percent of CPU this job got','Maximum resident set size (kbytes)','Major (requiring I/O) page faults','Minor (reclaiming a frame) page faults','File system inputs','File system outputs','Swaps']:
  diagnostics[label]=next(line.split(':',1)[1].strip() for line in resource.splitlines() if line.strip().startswith(label+':'))
 snaps={phase:json.loads((arm/('solver-'+phase+'-node-snapshot.json')).read_text()) for phase in ['before','after']}
 assert snaps['after']['time_ns']>snaps['before']['time_ns'] and all(v['collection_elapsed_ms']>=0 for v in snaps.values())
 node_vm={phase:{k:int(v) for k,v in (line.split() for line in snap['vmstat'].splitlines())} for phase,snap in snaps.items() if 'vmstat' in snap}
 vm_deltas={k:node_vm['after'][k]-node_vm['before'][k] for k in ['pgfault','pgmajfault','pswpin','pswpout']} if len(node_vm)==2 else None
 bounding=len(re.findall(r'bounding omega',log))
 # Compare the same first 30 Cd rows with the preceding zyx arm, not with another final step.
 prior=B.parent/'iris-order56-reverse30-20261026/completed-2294132/raw-evidence.tar.gz'
 with tarfile.open(prior) as tar:raw=tar.extractfile('cases/zyx/postProcessing/forceCoeffsAll/0/coefficient.dat').read().decode()
 old_cd=[list(map(float,line.split())) for line in raw.splitlines() if line.strip() and not line.lstrip().startswith('#')]
 assert cd[:30]==old_cd
review={'passed':True,'job_id':'2294148','verified_files':len(data),'allocation_wall_seconds':1224,'estimated_allocated_CPU_hours':56*1224/3600,'mean_seconds_per_step':statistics.mean(times),'median_seconds_per_step':statistics.median(times),'p95_seconds_per_step':statistics.quantiles(times,n=100,method='inclusive')[94],'maximum_seconds_per_step':max(times),'stddev_seconds':std,'all_timings_seconds':times,'descriptive_segments':row['descriptive_timing_segments'],'late_vs_early_time_change_percent':100*(statistics.mean(times[29:])/statistics.mean(times[:29])-1),'final_Cd_dimensionless':cd[-1][1],'Cd_first_30_rows_exactly_repeat_prior_zyx':True,'native_minimum_samples':native_min,'native_formula_before_rounding':formula,'native_zero_explanation':'The source rounds the estimated sample-count formula to an integer; zero is not zero variance or evidence that no samples are required.','bounding_omega_messages':bounding,'process_tree_diagnostics':diagnostics,'node_snapshot_collection_ms':{k:v['collection_elapsed_ms'] for k,v in snaps.items()},'whole_node_VM_deltas':vm_deltas,'scored_result':False,'matched_50_step_comparison':False,'limits':['One 50-step candidate on iris009; earlier pairs used iris001','No 150-step or matched 50-step xyz control','Finite Cd and fixed iterations do not certify organizer accuracy','Bounding omega warnings retained; no convergence certification','Prelaunch masks do not verify post-MPI solver masks','No hardware bandwidth, NUMA residency or helper-thread sampling']}
(E/'review.json').write_text(json.dumps(review,indent=2)+'\n');print(json.dumps({k:v for k,v in review.items() if k!='all_timings_seconds'},indent=2))
