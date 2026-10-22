"""Independent integrity and native-work review for sealed shared CPU density runs."""
from pathlib import Path, PurePosixPath
import datetime, hashlib, json, math, re, statistics, tarfile

ROOT = Path(__file__).resolve().parent
COLLECTED = ROOT / "collected"
BASELINE = ROOT.parent / "nscc-cpu-baseline-headerfix-20261021" / "payload" / "case"
PRIOR = ROOT.parent / "shared-cpu-intake-20261022"
EXPECTED_CELLS = 65_334_765
NEW = {
 "25921831.pbs101": ("1n-hierarchical-25921831",1,40,"hierarchical"),
 "25921832.pbs101": ("1n-scotch-25921832",1,40,"scotch"),
 "25921833.pbs101": ("1n-scotch-25921833",1,40,"scotch"),
 "25921809.pbs101": ("2n-hierarchical-25921809",2,80,"hierarchical"),
 "25921820.pbs101": ("2n-scotch-25921820",2,80,"scotch"),
 "25921822.pbs101": ("2n-scotch-25921822",2,80,"scotch"),
}
STAGES=("10_decomposePar","20_renumberMesh","30_potentialFoam","40_applyBoundaryLayer")
def require(ok,msg):
 if not ok: raise AssertionError(msg)
def digest(data): return hashlib.sha256(data).hexdigest()
def jread(p): return json.loads(p.read_text())
def secs(v):
 h,m,s=map(int,v.split(':')); return 3600*h+60*m+s
def rows(text): return [x.split() for x in text.splitlines() if x.strip() and not x.lstrip().startswith('#')]
def qtile(a,p):
 a=sorted(a); x=(len(a)-1)*p; lo=math.floor(x); hi=math.ceil(x); f=x-lo
 return a[lo]*(1-f)+a[hi]*f
def normalize(rel,b):
 t=b.decode()
 if rel in ('controlDict','controlDict.noWrite'): t=re.sub(r'(?m)^(\s*endTime\s+)[^;]+;',r'\g<1><ALLOWED_END_TIME>;',t)
 if rel=='include/caseDefinition':
  for k in ('nCores','decompositionMethod','nHierarchical'):
   t=re.sub(r'(?m)^(\s*'+k+r'\s+)[^;]+;',r'\g<1><ALLOWED_'+k.upper()+'>;',t)
 return t.encode()
def source_check(root,files):
 for prefix,base in (("system/",BASELINE/"system"),("0.orig/",BASELINE/"0.orig"),("constant/",BASELINE/"constant")):
  candidate={n[len(root+prefix):]:b for n,b in files.items() if n.startswith(root+prefix)}
  expected={str(p.relative_to(base)):p.read_bytes() for p in base.rglob('*') if p.is_file()}
  require(set(candidate)==set(expected),f"{root}: {prefix} file set differs from accepted official payload")
  for rel,b in expected.items():
   lhs,rhs=(normalize(rel,candidate[rel]),normalize(rel,b)) if prefix=='system/' else (candidate[rel],b)
   require(lhs==rhs,f"{root}: unexpected source difference {prefix+rel}")
def stage_metrics(text):
 m=re.search(r'Finished decomposition in ([0-9.eE+-]+) s',text)
 if m: return float(m.group(1))
 m=re.search(r'ClockTime\s*=\s*([0-9.eE+-]+) s',text)
 return float(m.group(1)) if m else None
def read_source_flags(files):
 paths=[n for n in files if n.endswith('/run_occ_common.sh')]
 require(len(paths)==1,'expected one retained run_occ_common.sh')
 b=files[paths[0]]; t=b.decode(errors='replace')
 flags={k:re.findall(r'(?m)^\s*export\s+'+k+r'=(.*)$',t) for k in ('FI_OFI_RXM_USE_SRX','OMP_NUM_THREADS')}
 return {"archive_member":paths[0],"sha256":digest(b),"runtime_flags":flags,"frozen_submission_proof":False}
def review(job,meta,files):
 dirname,nodes,end,method=NEW[job]; root=f'runs/{dirname}/'; item=meta['jobs'][job]
 require(item['job_state']=='F' and item['Exit_status']==0,f'{job}: PBS metadata not F/0')
 rl=item['Resource_List']; ru=item['resources_used']; ranks=int(rl['mpiprocs']); cpus=int(rl['ncpus']); ncpus_used=int(ru['ncpus'])
 require(int(rl['nodect'])==nodes and ranks%nodes==0 and cpus==128*nodes and ncpus_used==cpus,f'{job}: node/rank/allocated CPU mismatch')
 def get(p):
  k=root+p; require(k in files,f'{job}: missing {k}'); return files[k]
 log_names=[p for p in files if p.startswith(root+'logFiles/50_simpleFoam.')]
 require(len(log_names)==1,f'{job}: expected one solver log')
 solver=files[log_names[0]].decode(errors='replace')
 stage_map={x:root+'logFiles/'+x+'.log' for x in STAGES}; stage_map['50_simpleFoam']=log_names[0]
 stageinfo={}; stage_text={}
 for label,path in stage_map.items():
  require(path in files,f'{job}: missing stage log {path}')
  t=files[path].decode(errors='replace'); stage_text[label]=t
  ended=bool(re.search(r'^End\s*$',t,re.M)); fat=len(re.findall(r'FOAM FATAL|FATAL ERROR',t,re.I))
  require(ended and fat==0,f'{job}: {label} no End or native fatal')
  stageinfo[label]={"end_marker":ended,"native_fatal_count":fat,"error_markers":len(re.findall(r'^ERROR:',t,re.M)),"warning_count":len(re.findall(r'FOAM Warning|MPICH WARNING',t)),"tail":[x for x in t.splitlines() if x.strip()][-5:]}
 require('OPENFOAM=2512' in solver and 'scalar=64' in solver and re.search(r'Arch\s*:\s*"LSB;label=32;scalar=64"',solver),f'{job}: OpenFOAM build/precision evidence mismatch')
 require(re.search(rf'(?m)^nProcs\s*:\s*{ranks}\s*$',solver),f'{job}: solver nProcs mismatch')
 require([int(x) for x in re.findall(r'^SIMPLE: no convergence criteria found\. Calculations will run for (\d+) steps\.',solver,re.M)]==[end],f'{job}: endpoint declaration mismatch')
 times=[int(x) for x in re.findall(r'^Time = (\d+)\s*$',solver,re.M)]; require(times==list(range(1,end+1)),f'{job}: incomplete solver Time sequence')
 cd=get('system/controlDict').decode(); em=re.search(r'(?m)^\s*endTime\s+(\d+)\s*;',cd); require(em and int(em.group(1))==end,f'{job}: controlDict endpoint mismatch')
 cdef=get('system/include/caseDefinition').decode()
 def scalar(k):
  m=re.search(r'(?m)^\s*'+k+r'\s+([^;]+);',cdef); require(m,f'{job}: missing {k}'); return m.group(1).split('//')[0].strip()
 c_ranks=int(scalar('nCores')); c_method=scalar('decompositionMethod'); shape=[int(x) for x in re.findall(r'\d+',scalar('nHierarchical'))]
 require((ranks,c_ranks,c_method)==(ranks,ranks,method),f'{job}: caseDefinition rank/method mismatch')
 decomp=stage_text['10_decomposePar']; dm=re.search(r'Decomposition method\s+(\w+)\s+\[(\d+)\]',decomp); require(dm and dm.group(1)==method and int(dm.group(2))==ranks,f'{job}: native decomposition identity mismatch')
 cells=[int(x) for x in re.findall(r'^    Number of cells\s*=\s*(\d+)',decomp,re.M)]; require(len(cells)==ranks and sum(cells)==EXPECTED_CELLS,f'{job}: partition records/cell total mismatch')
 # Exact work history from solverInfo.
 si=rows(get('postProcessing/solverInfo/0/solverInfo.dat').decode()); header=None; rec=[]
 for line in get('postProcessing/solverInfo/0/solverInfo.dat').decode().splitlines():
  s=line.strip()
  if s.startswith('#') and 'Ux_iters' in s: header=s.lstrip('#').split()
  elif s and not s.startswith('#') and header and len(s.split())==len(header): rec.append(dict(zip(header,s.split())))
 require(header and [int(float(r['Time'])) for r in rec]==list(range(1,end+1)),f'{job}: solverInfo rows missing')
 work={'Ux_iters':15,'Uy_iters':15,'Uz_iters':15,'p_iters':12,'omega_iters':8,'k_iters':8}
 require(all(all(int(float(r[k]))==v for r in rec) for k,v in work.items()),f'{job}: fixed iteration work mismatch')
 wr=rows(get('postProcessing/wallClockTimeStatistics/0/wallClockTime.dat').decode()); wct=[[float(x) for x in r] for r in wr]
 require(len(wct)==end-1 and [int(r[0]) for r in wct]==list(range(2,end+1)),f'{job}: WCT indices mismatch')
 samples=[]; current=None
 for line in solver.splitlines():
  m=re.match(r'^Time = (\d+)\s*$',line)
  if m: current=int(m.group(1))
  m=re.match(r'^Wall-clock time elapsed during the current time step = ([0-9.eE+-]+) s\s*$',line)
  if m: require(current is not None,f'{job}: unindexed step sample'); samples.append((current,float(m.group(1))))
 values=[r[2] for r in wct]
 require(len(samples)==len(values) and [x[0] for x in samples]==[int(r[0]) for r in wct],f'{job}: solver/WCT rows differ')
 diffs=[abs(x[1]-r[2]) for x,r in zip(samples,wct)]
 require(all(math.isfinite(x) and x>0 for x in values+[v for _,v in samples]) and max(diffs)<=1e-9,f'{job}: timestep values invalid or solver/WCT differ')
 avg=statistics.mean(values); am=re.search(r'Average wall-clock time per time step\s*=\s*([0-9.eE+-]+)',solver); mm=re.search(r'Number of measured time steps\s*=\s*(\d+)',solver)
 require(am and mm and int(mm.group(1))==len(values) and math.isclose(float(am.group(1)),avg,rel_tol=1e-10,abs_tol=1e-10),f'{job}: aggregate timing mismatch')
 p95=qtile(values,.95); q1,q3=qtile(values,.25),qtile(values,.75); fences=[q1-1.5*(q3-q1),q3+1.5*(q3-q1)]
 out=[{'time':int(wct[i][0]),'seconds':v} for i,v in enumerate(values) if v<fences[0] or v>fences[1]]; mi=max(range(len(values)),key=values.__getitem__)
 fr=[[float(x) for x in r] for r in rows(get('postProcessing/forceCoeffsAll/0/coefficient.dat').decode())]
 require(len(fr)==end and [int(r[0]) for r in fr]==list(range(1,end+1)) and all(math.isfinite(x) for r in fr for x in r),f'{job}: force data invalid')
 source_check(root,files)
 elapsed=secs(ru['walltime']); cput=secs(ru['cput']); util=cput/(elapsed*cpus)*100; rate=float(rl['queue_charge_rate'])
 stage_secs={k:stage_metrics(stage_text[k]) for k in STAGES}; require(all(v is not None and math.isfinite(v) for v in stage_secs.values()),f'{job}: missing stage elapsed value')
 partial_prep_timer_sum=sum(stage_secs.values())
 min_match=re.search(r'Minimum number of measured time steps for 2% error at 95% confidence level\s*=\s*(\d+)',solver)
 require(min_match,f'{job}: missing native minimum sample recommendation')
 min_samples=int(min_match.group(1))
 confidence_warning=bool(re.search(r'Number of time steps of the current run is smaller than the calculated one by the statistical analysis',solver,re.I))
 omega=[float(x) for x in re.findall(r'bounding omega, min:\s*([-+0-9.eE]+)',solver)]
 return {'job':job,'run_directory':dirname,'method':method,'nodes':nodes,'per_node_mpi_ranks':ranks//nodes,'total_mpi_ranks':ranks,'allocated_cpus':cpus,'endpoint':end,'steps':end,'stage_logs':stageinfo,'source_case_comparison':{'all_system_matches_after_allowed_normalization':True,'initial_0_orig_constant_match_exactly':True,'allowed_changes':['nCores','endTime','decompositionMethod','nHierarchical'],'hierarchical_factors':shape},'partition':{'method':method,'records':len(cells),'total_cells':sum(cells),'min_cells_per_rank':min(cells),'max_cells_per_rank':max(cells),'mean_cells_per_rank':statistics.mean(cells),'max_excess_fraction':max(cells)/statistics.mean(cells)-1},'native_simplefoam':{'average_step_seconds':avg,'p95_seconds':p95,'max_seconds':values[mi],'max_time':int(wct[mi][0]),'min_seconds':min(values),'median_seconds':statistics.median(values),'sample_stddev_seconds':statistics.pstdev(values),'step_time_samples':[{'time':int(r[0]),'solver_log_elapsed_seconds':s[1],'wallClockTime_dat_seconds':r[2],'absolute_difference_seconds':d} for r,s,d in zip(wct,samples,diffs)],'iqr_fences_seconds':fences,'iqr_outliers':out,'wct_measured_steps':len(values),'native_minimum_sample_count_for_reported_2pct_95pct_target':min_samples,'native_sample_count_below_reported_minimum':len(values)<min_samples,'native_sample_confidence_warning_present':confidence_warning,'final_time':times[-1],'fixed_iterations_per_step':work,'tail':solver.splitlines()[-10:]},'force_coefficients':{'rows':len(fr),'final_Cd':fr[-1][1],'min_Cd':min(r[1] for r in fr),'max_Cd':max(r[1] for r in fr),'all_values_finite':True},'pbs':{'state':item['job_state'],'exit_status':item['Exit_status'],'queue':item['queue'],'exec_host':item['exec_host'],'requested_mpiprocs':ranks,'requested_ncpus':int(rl['ncpus']),'used_ncpus':cpus,'walltime':ru['walltime'],'walltime_seconds':elapsed,'cput':ru['cput'],'cput_seconds':cput,'cpupercent_last_sample':ru['cpupercent'],'whole_allocation_cpu_utilization_percent':util,'mem':ru['mem'],'vmem':ru['vmem'],'queue_charge_rate':rate,'estimated_SU':elapsed*cpus*rate/3600,'posted_charge':None},'partial_preparation_timer_sum_seconds':partial_prep_timer_sum,'partial_preparation_timer_components_seconds':stage_secs,'partial_preparation_timer_definition':'decomposePar algorithm duration plus renumberMesh, potentialFoam, and applyBoundaryLayer ClockTime values; excludes decomposePar processor-mesh/field transfer and write, read/I/O, and unattributed time','omega_negative_minimum_seen':min(omega) if omega else None,'omega_diagnostic_only':True}

def load_sealed(path):
 c=path/'collected'; local=jread(c/'evidence-sha256.json')
 for rel,h in local.items(): require((c/rel).is_file() and digest((c/rel).read_bytes())==h,f'{path.name}: local seal mismatch {rel}')
 rm=jread(c/'remote-file-sha256.json'); archive_path=c/'raw-text-evidence.tar.gz'
 with tarfile.open(archive_path,'r:gz') as tar:
  ms=tar.getmembers(); require(all(x.isfile() for x in ms),'non-file archive member')
  names=[x.name for x in ms]; require(len(names)==len(set(names)),'duplicate archive path')
  require(all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names),'unsafe archive path')
  require(set(names)==set(rm)|{'remote-file-sha256.json'},'archive/remote manifest member mismatch')
  files={m.name:tar.extractfile(m).read() for m in ms}
 require(files['remote-file-sha256.json']==(c/'remote-file-sha256.json').read_bytes(),'embedded remote manifest mismatch')
 for n,h in rm.items(): require(digest(files[n])==h,f'{path.name}: remote hash mismatch {n}')
 return jread(c/'collection.json'),files,len(local),len(rm)

def main():
 meta,files,nlocal,nremote=load_sealed(ROOT)
 require(set(meta['jobs'])==set(NEW),'new collection job set mismatch')
 runs={}
 for j in NEW:
  try: runs[j]=review(j,meta,files)
  except Exception as exc: runs[j]={'job':j,'review_status':'FAIL','error':str(exc)}
 prior,prior_files,plocal,premote=load_sealed(PRIOR)
 control=jread(PRIOR/'review.json')['runs']
 require(set(prior['jobs'])=={'25921487.pbs101','25921492.pbs101'} and set(control)==set(prior['jobs']),'prior control collection mismatch')
 # Reconfirm control native time series from independently sealed logs, retaining source result provenance.
 for job in control:
  ac=prior['jobs'][job]; require(ac['job_state']=='F' and ac['Exit_status']==0,f'{job}: prior PBS metadata not F/0')
  dirname='1n-scotch-25921487' if '25921487' in job else '2n-scotch-25921492'
  key=next(k for k in prior_files if k.startswith('runs/'+dirname+'/logFiles/50_simpleFoam.'))
  text=prior_files[key].decode(errors='replace'); indexed=[]; current=None
  for line in text.splitlines():
   tm=re.match(r'^Time = (\d+)\s*$',line)
   if tm: current=int(tm.group(1))
   dm=re.match(r'^Wall-clock time elapsed during the current time step = ([0-9.eE+-]+) s\s*$',line)
   if dm: indexed.append((current,float(dm.group(1))))
  r=control[job]; t=r['native_simplefoam']; require(len(indexed)==t['wallClockTime_rows'] and all(i is not None and math.isfinite(x) and x>0 for i,x in indexed),'prior control native samples invalid')
  saved=t['step_time_samples']; require([i for i,_ in indexed]==[s['time'] for s in saved],'prior control native time indices mismatch')
  require(max(abs(x-s['wallClockTime_dat_seconds']) for (_,x),s in zip(indexed,saved))<=1e-9,'prior control solver/WCT mismatch')
  min_match=re.search(r'Minimum number of measured time steps for 2% error at 95% confidence level\s*=\s*(\d+)',text); require(min_match,'prior control missing native sample recommendation')
  t['native_minimum_sample_count_for_reported_2pct_95pct_target']=int(min_match.group(1)); t['native_sample_count_below_reported_minimum']=t['wallClockTime_rows']<int(min_match.group(1)); t['native_sample_confidence_warning_present']=bool(re.search(r'Number of time steps of the current run is smaller than the calculated one by the statistical analysis',text,re.I))
  r2={'job':job,'run_directory':('1n-scotch-25921487' if '25921487' in job else '2n-scotch-25921492'),'method':'scotch','nodes':1 if '25921487' in job else 2,'per_node_mpi_ranks':128,'total_mpi_ranks':r['source_case_comparison']['rank'],'allocated_cpus':r['pbs_resources_used']['ncpus'],'endpoint':t['completed_time_steps'],'steps':t['completed_time_steps'],'native_simplefoam':{'average_step_seconds':t['native_average_step_seconds'],'p95_seconds':t['wallClockTime_p95_step_seconds_linear_interpolation'],'max_seconds':t['wallClockTime_max_step_seconds'],'max_time':t['wallClockTime_max_time'],'iqr_outliers':t['wallClockTime_iqr_outlier_samples'],'wct_measured_steps':t['wallClockTime_rows']},'force_coefficients':r['force_coefficients'],'pbs':{'walltime':r['pbs_resources_used']['walltime'],'walltime_seconds':r['pbs_resources_used']['walltime_seconds'],'cput':r['pbs_resources_used']['cput'],'cpupercent_last_sample':r['pbs_resources_used']['cpupercent_last_sample_raw'],'whole_allocation_cpu_utilization_percent':r['pbs_resources_used']['derived_whole_allocation_average_cpu_utilization_percent'],'estimated_SU':r['pbs_resources_used']['estimated_SU'],'exec_host':ac['exec_host']},'partial_preparation_timer_sum_seconds':None,'control_source':'prior independently sealed review; native logs and every referenced hash independently rechecked'}
  # Derive partial preparation timer sum from sealed previous native logs
  dirname=r2['run_directory']; prefix='runs/'+dirname+'/logFiles/'
  stage_values={}
  for st in STAGES:
   txt=prior_files[prefix+st+'.log'].decode(errors='replace'); stage_values[st]=stage_metrics(txt)
  require(all(v is not None for v in stage_values.values()),f'{job}: prior prep timing missing')
  r2['partial_preparation_timer_components_seconds']=stage_values; r2['partial_preparation_timer_sum_seconds']=sum(stage_values.values()); r2['partial_preparation_timer_definition']='decomposePar algorithm duration plus renumberMesh, potentialFoam, and applyBoundaryLayer ClockTime values; excludes decomposePar processor-mesh/field transfer and write, read/I/O, and unattributed time'; r2['native_simplefoam'].update({k:t[k] for k in ('native_minimum_sample_count_for_reported_2pct_95pct_target','native_sample_count_below_reported_minimum','native_sample_confidence_warning_present')})
  runs[job]=r2
 rowsout=[]
 for j,r in runs.items():
  t=r['native_simplefoam']; p=r['pbs']; rowsout.append({'job':j,'nodes':r['nodes'],'method':r['method'],'MPI_ranks_per_node':r['per_node_mpi_ranks'],'MPI_ranks_total':r['total_mpi_ranks'],'allocated_CPUs':r['allocated_cpus'],'endpoint_steps':r['endpoint'],'mean_s':t['average_step_seconds'],'p95_s':t['p95_seconds'],'max_s':t['max_seconds'],'max_Time':t['max_time'],'Cd_endpoint':r['force_coefficients']['final_Cd'],'walltime_s':p['walltime_seconds'],'estimated_SU':p['estimated_SU'],'partial_preparation_timer_sum_s':r['partial_preparation_timer_sum_seconds']})
 require(rowsout,'no native run passed all per-run review gates')
 best=min(rowsout,key=lambda x:x['mean_s']); cheap=min(rowsout,key=lambda x:x['estimated_SU']);
 result={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'CANDIDATE_NATIVE_EVIDENCE_ONLY' if all('review_status' not in r for r in runs.values()) else 'PARTIAL_NATIVE_EVIDENCE_WITH_PER_RUN_FAILURES','collection_integrity':{'new_local_entries':nlocal,'new_remote_entries':nremote,'new_archive_members':len(files),'new_all_seals_pass':True,'control_local_entries':plocal,'control_remote_entries':premote,'control_archive_members':len(prior_files),'control_all_seals_pass':True},'runs':runs,'per_run_gate_failures':{j:r['error'] for j,r in runs.items() if 'review_status' in r},'comparison_rows':rowsout,'metric_leaders':{'lowest_solver_average_step_time':best['job'],'lowest_full_allocation_cost_estimate':cheap['job'],'partial_preparation_timer_sum_is_a_setup_leader':False},'source_flags':read_source_flags(files),'limitations':['Failed per-run gates are retained in the JSON and excluded from comparison rows and metric leaders. All results are cross-allocation and prescribed endpoint observations (40 steps for one node; 80 for two), not a controlled matched-work strong-scaling or stable speedup claim.','New-job PBS resource MPI process requests differ from allocated CPU counts; CPU cost and whole-allocation utilization use allocated ncpus, while partition and solver checks use actual MPI ranks.','Current retained scripts are sealed collection evidence but are not proof of the frozen bytes submitted to PBS; owner and submit provenance remain unverified.','PBS F/exit0 and native End do not establish each native command returned zero: the common helper accepts End and can mask a nonzero command status.','Processor fields, mesh binaries/independent mesh identity, final zero-field seals, environment state, per-rank affinity/physical-core map, hardware telemetry, and posted charge were not collected. exec_host identifies allocated hosts only.','Estimated SU is elapsed walltime × allocated CPUs × queue charge rate / 3600, not a posted/reconciled charge. cpupercent is PBS last sample; derived whole-allocation CPU use is CPUT/(walltime × ncpus).','Native minimum sample recommendations and any emitted short-sample warning are recorded per run. These diagnostics are not formal independent confidence intervals; preserve the prescribed ranked endpoints and per-step variation. No causal bottleneck is inferred.','Partial preparation timer sum combines decomposePar algorithm duration with renumberMesh, potentialFoam, and applyBoundaryLayer ClockTime values. It excludes decomposePar processor-mesh/field transfer and write, read/I/O, and unattributed time, so it is not a full setup/init measure or a setup winner.','Negative omega bounding minima are diagnostics also present in accepted controls; no fields or counters diagnose their cause.']}
 (ROOT/'review.json').write_text(json.dumps(result,indent=2)+'\n')
 md=['# Shared CPU density and decomposition review','', 'This review combines six newly sealed one/two-node jobs with two prior sealed Scotch controls. It reports candidate native evidence and descriptive endpoint comparisons; it does not confer accepted-result status or establish controlled speedup.','', '## Integrity and work checks','',f"All {nlocal} local evidence entries and {nremote} remote-file hashes for the six new runs passed; the raw archive has {len(files)} safe file members. The unchanged two prior Scotch controls were seal-verified and native timing rows rechecked ({plocal} local entries, {premote} remote hashes). All eight PBS records show F/exit 0. Each new run has all five native stage End markers, no FOAM fatal marker, full step endpoints, fixed Ux/Uy/Uz=15, p=12, omega=8, k=8 per-step work, exact solver/WCT time and elapsed matches, finite Cd rows, and matching source inputs after the documented parameter normalizations.",'', 'Allocated CPUs and MPI processes are distinct: one-node jobs reserve 128 CPUs while using 64, 96, or 128 MPI ranks; two-node jobs reserve 256 CPUs while using 128, 192, or 256 ranks. Cell partitions and solver rank checks use MPI ranks; resource cost and utilization use allocated CPUs.','', '| Job | Nodes | Method | MPI ranks/node (total) | Allocated CPUs | Steps | Mean s | p95 s | Max s (Time) | Final Cd | PBS walltime | Estimated SU* | Native minimum samples (warning) | Partial preparation timer sum s |','|---|---:|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---|---:|']
 for x in rowsout:
  initv='—' if x['partial_preparation_timer_sum_s'] is None else f"{x['partial_preparation_timer_sum_s']:.2f}"
  sr=runs[x['job']]['native_simplefoam']; warning='yes' if sr['native_sample_confidence_warning_present'] else 'no'
  md.append(f"| {x['job']} | {x['nodes']} | {x['method']} | {x['MPI_ranks_per_node']} ({x['MPI_ranks_total']}) | {x['allocated_CPUs']} | {x['endpoint_steps']} | {x['mean_s']:.6f} | {x['p95_s']:.6f} | {x['max_s']:.6f} (T{x['max_Time']}) | {x['Cd_endpoint']:.10f} | {x['walltime_s']} s | {x['estimated_SU']:.3f} | {sr['native_minimum_sample_count_for_reported_2pct_95pct_target']} (short-sample warning: {warning}) | {initv} |")
 md += ['',f"The lowest solver Average in this eight-run table is {best['job']} ({best['mean_s']:.6f} s/step). The lowest estimated whole-allocation charge is {cheap['job']} ({cheap['estimated_SU']:.3f} SU estimate). The partial preparation timer sum is descriptive only and is not a fastest setup/init winner. It combines decomposePar algorithm duration with three native ClockTime values and excludes decomposePar processor-mesh/field transfer and write, read/I/O, and unattributed time.",'', 'The p95 uses linear interpolation; maxima and all full time-indexed samples, per-run IQR outliers, Cd ranges, resource records, stage tails, native recommended minimum sample counts, and actual confidence-warning presence are retained in review.json. The logger’s reported minimum is a diagnostic recommendation, not a formal independent confidence interval.','', '## Interpretation and limits','', 'Per-run validation failures, if any, are recorded in review.json and excluded from the comparison table and leaders. These are descriptive endpoint observations across different MPI rank densities and allocations, at prescribed 40-step one-node and 80-step two-node endpoints. Cd endpoints are at different times; the values are not an accuracy comparison. Do not infer stable matched speedup or a causal bottleneck from these runs. The observed lowest solver Average can differ from the cheapest full allocation, because cost includes allocated CPU count and all elapsed preparation and solve time.','', 'PBS `cpupercent` is a last-sample field; whole-allocation average utilization is separately derived as CPUT / (walltime × allocated CPUs). PBS `exec_host` records allocated hosts, but not which physical cores each MPI rank used. Estimated SU is walltime × allocated CPUs × queue charge rate / 3600, not posted charge.','', 'Frozen submission script provenance and owner identity are not established. The collected current common script has a hash and runtime flags in review.json, but may differ from submitted bytes. PBS exit 0 and native End markers do not prove each stage command returned zero because the helper can mask a nonzero native return code. Processor fields, mesh binaries/independent mesh identity, final zero-field seals, runtime environment, rank affinity mapping, hardware telemetry, and posted charge were not collected. Negative omega minima are diagnostic only and also appear in accepted controls; no fields/counters diagnose their cause.','', 'Machine-readable measurements and complete time samples are in [review.json](review.json).']
 (ROOT/'RESULTS.md').write_text('\n'.join(md)+'\n')
 print(json.dumps({'status':result['status'],'leaders':result['metric_leaders'],'new_checks':len(runs),'table_rows':len(rowsout)},indent=2))
if __name__=='__main__': main()
