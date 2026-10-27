"""Replay retained bytes, native work, copy proofs and coordinator statistics."""
from pathlib import Path
import hashlib,json,math,re,statistics,sys,tarfile,tempfile
E=Path(__file__).resolve().parent;B=E.parent;sys.path.insert(0,str(B))
from native_output import review_native_output
meta=json.loads((E/'collection.json').read_text());arc=E/'raw-evidence.tar.gz'
assert hashlib.sha256(arc.read_bytes()).hexdigest()==meta['archive_sha256']
with tarfile.open(arc) as tar:
 members=tar.getmembers();assert all(m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts for m in members)
 data={m.name:tar.extractfile(m).read() for m in members}
assert set(data)==set(meta['files']) and len(data)==len(members)
for name,raw in data.items():assert len(raw)==meta['files'][name]['bytes'] and hashlib.sha256(raw).hexdigest()==meta['files'][name]['sha256']
assert meta['remote_runtime_hashes']==json.loads((B/'payload-sha256.json').read_text())['files']
account=[x.split('|') for x in meta['accounting'].splitlines()[1:]]
job=next(x for x in account if x[0]=='2294132');assert job[1:6]==['COMPLETED','0:0','1870','56','iris001']
r='runs/2294132/'
for name,raw in data.items():
 if name.startswith(r) and name.endswith('.status.json'):assert json.loads(raw)['returncode']==0
assert not data['kit/runs/2294132.err']
assert b'MATCHED_XYZ_ZYX_30STEP_SCREEN_PASS' in data['kit/runs/2294132.out']
comparison=json.loads(data[r+'comparison.json']);assert comparison['passed'] and comparison['order']==['zyx','xyz'] and comparison['scored_result'] is False
arms=[]
with tempfile.TemporaryDirectory() as temp:
 root=Path(temp)
 for name,raw in data.items():
  p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 for order in ['xyz','zyx']:
  a=root/'cases'/order;prefix='cases/'+order+'/'
  assert json.loads((a/'return-code.json').read_text())['returncode']==0
  assert data[prefix+'source-before.json']==data[prefix+'copy-check.json']==data[prefix+'source-after.json']
  seal=json.loads(data[prefix+'source-before.json']);assert len(seal['symlinks'])==1
  assert all('processor'+str(i)+'/0/'+f in seal['files'] for i in range(56) for f in ['U','p','k','omega','nut','nuTilda'])
  assert json.loads(data[r+order+'-source.json'])=={'passed':True,'pinned_input_files':41,'order':order,'factors':[7,4,2]}
  affinity=[json.loads((a/'affinity'/('rank-%02d.json'%i)).read_text()) for i in range(56)]
  assert [x['rank'] for x in affinity]==list(range(56)) and len({x['host'] for x in affinity})==1
  assert all(len(x['affinity_cpus'])==1 for x in affinity)
  assert len({tuple(x['affinity_cpus']) for x in affinity})==56
  log,times,cd,counts=review_native_output(a)
  stderr=(a/'solver.stderr').read_text();assert not re.search(r'FOAM FATAL|FOAM ERROR|MPI_ABORT|died from signal|core dumped',stderr,re.I)
  if stderr.strip():
   assert 'libwallClockTimeStatistics_' in stderr and 'cannot open shared object file' in stderr
   assert 'wmake libso' in log and len(times)==29, 'require successful dynamic compilation and native timing output'
  row=next(x for x in comparison['arms'] if x['order']==order)
  assert times==row['timings_seconds'] and counts==row['fixed_iterations']
  assert abs(statistics.mean(times)-row['mean_seconds_per_step'])<1e-10
  assert abs(statistics.median(times)-row['median_seconds_per_step'])<1e-10
  assert abs(statistics.quantiles(times,n=100,method='inclusive')[94]-row['p95_seconds_per_step'])<1e-10
  assert max(times)==row['maximum_seconds_per_step'] and cd[-1][1]==row['final_Cd']
  recommended=int(re.search(r'Minimum number of measured time steps[^\n]*=\s*(\d+)',log)[1]);assert recommended==row['native_minimum_samples']
  resource=(a/'resource-time.log').read_text()
  row['diagnostics']={}
  for label in ['User time (seconds)','System time (seconds)','Percent of CPU this job got','Maximum resident set size (kbytes)','Major (requiring I/O) page faults','Minor (reclaiming a frame) page faults','File system inputs','File system outputs','Swaps']:
   row['diagnostics'][label]=next(line.split(':',1)[1].strip() for line in resource.splitlines() if line.strip().startswith(label+':'))
  row['stderr_assessment']='Initial missing dynamic wall-clock library; runtime compiles it and native timing output passes' if stderr.strip() else 'empty'
  snapshots={}
  for phase in ['before','after']:
   snap=json.loads((a/('solver-'+phase+'-node-snapshot.json')).read_text());assert snap['label']=='solver-'+phase
   assert snap['collection_elapsed_ms']>=0 and 'utc' in snap and 'time_ns' in snap
   assert all(name in snap or name+'_error' in snap for name in ['meminfo','vmstat','pressure/memory'])
   snapshots[phase]=snap
  assert snapshots['after']['time_ns']>snapshots['before']['time_ns']
  row['node_snapshot_collection_ms']={k:v['collection_elapsed_ms'] for k,v in snapshots.items()}
  vm={k:{key:int(val) for key,val in (line.split() for line in v['vmstat'].splitlines())} for k,v in snapshots.items() if 'vmstat' in v}
  if len(vm)==2:row['whole_node_vm_deltas']={key:vm['after'][key]-vm['before'][key] for key in ['pgfault','pgmajfault','pswpin','pswpout'] if key in vm['after'] and key in vm['before']}
  row['bounding_omega_messages']=len(re.findall(r'bounding omega',log));row['observed_prelaunch_rank_masks']=56
  row['meets_native_sample_recommendation']=len(times)>=recommended
  arms.append(row)
ratio=arms[1]['mean_seconds_per_step']/arms[0]['mean_seconds_per_step'];assert abs(100*(ratio-1)-comparison['candidate_time_change_percent'])<1e-10
result={'passed':True,'job_id':'2294132','terminal_state':'COMPLETED_0_0','verified_files':len(data),'allocation_wall_seconds':1870,'estimated_allocated_CPU_hours':56*1870/3600,'scored_result':False,'arms':arms,'candidate_time_change_percent':100*(ratio-1),'both_meet_native_sample_recommendation':all(x['meets_native_sample_recommendation'] for x in arms),'limits':['Only 30 steps and 29 intervals; reverse xyz recommends111','Fixedorder and first-touch/cache/resource effects unresolved','GNUtime reports observed process-tree statistics; RSS is not summed node residency','Affinity probe is before solver launch, not post-MPI solver-mask verification','No memory-bandwidth, NUMA residency or kernel telemetry','Finite Cd and fixedwork checks are not organizer accuracy approval']}
(E/'review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='arms'},indent=2))
