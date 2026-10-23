"""Offline native evidence review for the sealed four-node OpenFOAM collection."""
from pathlib import Path, PurePosixPath
import datetime, hashlib, json, math, re, statistics, tarfile

ROOT = Path(__file__).resolve().parent
COLLECTED = ROOT / 'collected'
BASELINE = ROOT.parent / 'nscc-cpu-baseline-headerfix-20261021' / 'payload' / 'case'
EXPECTED_CELLS = 65_334_765
JOBS = {
 '25921488.pbs101': ('4n-scotch-25921488','scotch',128,512,512),
 '25921517.pbs101': ('4n-scotch-25921517','scotch',64,256,256),
 '25921518.pbs101': ('4n-scotch-25921518','scotch',96,384,384),
 '25921692.pbs101': ('4n-hierarchical-25921692','hierarchical',128,512,512),
 '25921905.pbs101': ('4n-hierarchical-25921905','hierarchical',96,384,512),
 '25921906.pbs101': ('4n-hierarchical-25921906','hierarchical',64,256,512),
}
STAGES=('10_decomposePar','20_renumberMesh','30_potentialFoam','40_applyBoundaryLayer')
def need(x,msg):
 if not x: raise AssertionError(msg)
def sha(b): return hashlib.sha256(b).hexdigest()
def readj(p): return json.loads(p.read_text())
def rows(t): return [x.split() for x in t.splitlines() if x.strip() and not x.lstrip().startswith('#')]
def qt(a,p):
 a=sorted(a); x=(len(a)-1)*p; lo=math.floor(x); hi=math.ceil(x); f=x-lo
 return a[lo]*(1-f)+a[hi]*f
def norm(rel,b):
 t=b.decode()
 if rel in ('controlDict','controlDict.noWrite'): t=re.sub(r'(?m)^(\s*endTime\s+)[^;]+;',r'\g<1><ALLOWED_END_TIME>;',t)
 if rel=='include/caseDefinition':
  for k in ('nCores','decompositionMethod','nHierarchical'):
   t=re.sub(r'(?m)^(\s*'+k+r'\s+)[^;]+;',r'\g<1><ALLOWED_'+k.upper()+'>;',t)
 return t.encode()
def check_source(root,files):
 for prefix,base in [('system/',BASELINE/'system'),('0.orig/',BASELINE/'0.orig'),('constant/',BASELINE/'constant')]:
  got={n[len(root+prefix):]:b for n,b in files.items() if n.startswith(root+prefix)}
  exp={str(p.relative_to(base)):p.read_bytes() for p in base.rglob('*') if p.is_file()}
  need(set(got)==set(exp),f'{root}: {prefix} file set mismatch')
  for k,b in exp.items(): need((norm(k,got[k])==norm(k,b)) if prefix=='system/' else got[k]==b,f'{root}: unexpected source delta {prefix+k}')
def stage_metric(t):
 m=re.search(r'Finished decomposition in ([0-9.eE+-]+) s',t)
 if m:return float(m.group(1))
 m=re.search(r'ClockTime\s*=\s*([0-9.eE+-]+) s',t); return float(m.group(1)) if m else None
def validate(job,meta,files):
 dirname,method,ppn,ranks,reqcpu=JOBS[job]; root=f'runs/{dirname}/'; cfg=meta['jobs'][job]; ncpus=int(cfg['Resource_List']['ncpus']); mpiprocs=int(cfg['Resource_List']['mpiprocs'])
 need(ncpus==reqcpu and mpiprocs==ranks,f'{job}: request snapshot resource mismatch')
 def get(p):
  k=p if p.startswith('runs/') else root+p; need(k in files,f'{job}: missing {k}'); return files[k]
 lognames=[p for p in files if p.startswith(root+'logFiles/50_simpleFoam.')]
 need(len(lognames)==1,f'{job}: expected one simpleFoam log')
 stagetext={}; stageinfo={}
 for name,path in [(s,root+'logFiles/'+s+'.log') for s in STAGES]+[('50_simpleFoam',lognames[0])]:
  t=get(path).decode(errors='replace'); stagetext[name]=t
  end=bool(re.search(r'^End\s*$',t,re.M)); fat=len(re.findall(r'FOAM FATAL|FATAL ERROR',t,re.I))
  mpi_bad=len(re.findall(r'MPI_ABORT|MPI_[A-Z_]*ERROR|signal\s*\d+|terminated by signal|Aborted \(core dumped\)',t,re.I))
  need(end and fat==0 and mpi_bad==0,f'{job}: {name} missing End or has fatal/MPI signal marker')
  warnings=[]
  for wi,wl in enumerate(t.splitlines()):
   if 'FOAM Warning' in wl or 'MPICH WARNING' in wl:
    warnings.append(t.splitlines()[wi:wi+4])
  stageinfo[name]={'end_marker':end,'native_fatal_count':fat,'mpi_or_signal_failure_markers':mpi_bad,'foam_warning_count':len(re.findall(r'FOAM Warning|MPICH WARNING',t)),'warning_context_lines':warnings,'error_lines':[x for x in t.splitlines() if re.match(r'^ERROR:',x)],'tail':[x for x in t.splitlines() if x.strip()][-6:]}
 solver=stagetext['50_simpleFoam']
 need('OPENFOAM=2512' in solver and 'version=v2512' in solver and 'Arch   : "LSB;label=32;scalar=64"' in solver,f'{job}: version/precision labels mismatch')
 need(re.search(rf'(?m)^nProcs\s*:\s*{ranks}\s*$',solver),f'{job}: nProcs mismatch')
 hosts=re.findall(r'^\s*\((\S+)\s+(\d+)\)\s*$',solver[solver.find('Hosts  :'):solver.find('Pstream initialized with:')],re.M)
 host_counts=[{'host':h,'mpi_ranks':int(n)} for h,n in hosts]
 need(len(host_counts)==4 and len({x['host'] for x in host_counts})==4 and all(x['mpi_ranks']==ppn for x in host_counts),f'{job}: expected four native hosts with {ppn} ranks each')
 pm=re.search(r'node communication\s*:\s*on \[type=host\] \((\d+) ranks, (\d+) nodes\)',solver)
 need(pm and int(pm.group(1))==ranks and int(pm.group(2))==4,f'{job}: Pstream rank/node identity mismatch')
 need(not re.search(r'MPI_ABORT|MPI_[A-Z_]*ERROR|signal\s*\d+|terminated by signal|Aborted \(core dumped\)',solver,re.I),f'{job}: MPI/signal failure marker')
 timevals=[int(x) for x in re.findall(r'^Time = (\d+)\s*$',solver,re.M)]
 need(timevals==list(range(1,151)),f'{job}: incomplete intended 150-step sequence')
 control=get('system/controlDict').decode(); em=re.search(r'(?m)^\s*endTime\s+(\d+)\s*;',control); need(em and int(em.group(1))==150,f'{job}: controlDict endTime mismatch')
 cdef=get('system/include/caseDefinition').decode()
 def val(k):
  m=re.search(r'(?m)^\s*'+k+r'\s+([^;]+);',cdef); need(m,f'{job}: missing caseDefinition {k}'); return m.group(1).split('//')[0].strip()
 need(int(val('nCores'))==ranks and val('decompositionMethod')==method,f'{job}: caseDefinition method/ranks mismatch')
 factors=[int(x) for x in re.findall(r'\d+',val('nHierarchical'))]
 decomp=stagetext['10_decomposePar']; dm=re.search(r'Decomposition method\s+(\w+)\s+\[(\d+)\]',decomp); need(dm and dm.group(1)==method and int(dm.group(2))==ranks,f'{job}: native method/rank mismatch')
 cells=[int(x) for x in re.findall(r'^\s+Number of cells\s*=\s*(\d+)',decomp,re.M)]; need(len(cells)==ranks and sum(cells)==EXPECTED_CELLS,f'{job}: decomposed cell count mismatch')
 # Validate exact fixed iterative work for all 149 timed steps.
 si=get('postProcessing/solverInfo/0/solverInfo.dat').decode(); hdr=None; rec=[]
 for line in si.splitlines():
  s=line.strip()
  if s.startswith('#') and 'Ux_iters' in s: hdr=s.lstrip('#').split()
  elif s and not s.startswith('#') and hdr and len(s.split())==len(hdr): rec.append(dict(zip(hdr,s.split())))
 need(hdr and [int(float(r['Time'])) for r in rec]==list(range(1,151)),f'{job}: solverInfo time rows mismatch')
 work={'Ux_iters':15,'Uy_iters':15,'Uz_iters':15,'p_iters':12,'omega_iters':8,'k_iters':8}
 need(all(all(int(float(r[k]))==v for r in rec) for k,v in work.items()),f'{job}: fixed iteration work mismatch')
 wlines=rows(get('postProcessing/wallClockTimeStatistics/0/wallClockTime.dat').decode()); wct=[[float(x) for x in r] for r in wlines]
 need(len(wct)==149 and [int(r[0]) for r in wct]==list(range(2,151)),f'{job}: WCT sample indices mismatch')
 samples=[]; cur=None
 for line in solver.splitlines():
  m=re.match(r'^Time = (\d+)\s*$',line)
  if m: cur=int(m.group(1))
  m=re.match(r'^Wall-clock time elapsed during the current time step = ([0-9.eE+-]+) s\s*$',line)
  if m: samples.append((cur,float(m.group(1))))
 vals=[r[2] for r in wct]; diffs=[abs(a-r[2]) for (_,a),r in zip(samples,wct)]
 need(len(samples)==149 and [i for i,_ in samples]==list(range(2,151)) and max(diffs)<=1e-9 and all(math.isfinite(x) and x>0 for x in vals),f'{job}: solver and WCT samples mismatch/invalid')
 avg=statistics.mean(vals); am=re.search(r'Average wall-clock time per time step\s*=\s*([0-9.eE+-]+)',solver); mm=re.search(r'Number of measured time steps\s*=\s*(\d+)',solver)
 need(am and mm and int(mm.group(1))==149 and math.isclose(float(am.group(1)),avg,rel_tol=1e-10,abs_tol=1e-10),f'{job}: mean cross-check failed')
 p95=qt(vals,.95); q1,q3=qt(vals,.25),qt(vals,.75); fences=[q1-1.5*(q3-q1),q3+1.5*(q3-q1)]; out=[{'time':int(wct[i][0]),'seconds':x} for i,x in enumerate(vals) if x<fences[0] or x>fences[1]]; im=max(range(len(vals)),key=vals.__getitem__)
 top3=sorted(({'time':int(wct[i][0]),'seconds':x} for i,x in enumerate(vals)),key=lambda z:z['seconds'],reverse=True)[:3]
 sample_sum=sum(vals); largest_share=vals[im]/sample_sum
 force=[[float(x) for x in r] for r in rows(get('postProcessing/forceCoeffsAll/0/coefficient.dat').decode())]
 need(len(force)==150 and [int(r[0]) for r in force]==list(range(1,151)) and all(math.isfinite(x) for r in force for x in r),f'{job}: Cd force rows invalid')
 check_source(root,files)
 env=get('logFiles/00_environment.selected.txt').decode(errors='replace')
 env_selected={k:[line for line in env.splitlines() if re.match(r'^\s*(?:export\s+)?'+re.escape(k)+r'=',line)] for k in ('FI_OFI_RXM_USE_SRX','OMP_NUM_THREADS','OMP_PROC_BIND','OMP_PLACES','UCX_TLS','MPIR_CVAR_CH4_OFI_ENABLE_HMEM')}
 stage_sec={k:stage_metric(stagetext[k]) for k in STAGES}; need(all(v is not None and math.isfinite(v) for v in stage_sec.values()),f'{job}: partial initialization timers unavailable')
 minm=re.search(r'Minimum number of measured time steps for 2% error at 95% confidence level\s*=\s*(\d+)',solver); need(minm,f'{job}: missing native confidence recommendation')
 warning=bool(re.search(r'Number of time steps of the current run is smaller than the calculated one by the statistical analysis',solver,re.I))
 return {'job':job,'run_directory':dirname,'method':method,'nodes':4,'per_node_mpi_ranks':ppn,'total_mpi_ranks':ranks,'requested_ncpus':ncpus,'requested_mpiprocs':mpiprocs,'endpoint_steps':150,'timed_steps':149,'native_host_groups':host_counts,'source_case_comparison':{'system_matches_after_allowing_method_rank_hierarchical_factors_endTime':True,'0_orig_constant_match_exactly':True,'allowed_changes':['decompositionMethod','nCores','nHierarchical','endTime'],'hierarchical_factors':factors},'partition':{'records':len(cells),'total_cells':sum(cells),'min_cells_per_rank':min(cells),'max_cells_per_rank':max(cells),'mean_cells_per_rank':statistics.mean(cells),'max_excess_fraction':max(cells)/statistics.mean(cells)-1},'native_stage_logs':stageinfo,'native_simplefoam':{'average_step_seconds':avg,'p95_seconds_linear_interpolation':p95,'max_seconds':vals[im],'max_time':int(wct[im][0]),'min_seconds':min(vals),'median_seconds':statistics.median(vals),'mean_median_ratio':avg/statistics.median(vals),'sample_stddev_population_seconds':statistics.pstdev(vals),'top_three_step_times_descending':top3,'largest_step_sum_share':largest_share,'largest_step_mean_contribution_seconds':vals[im]/len(vals),'largest_step_mean_contribution_percent':100*largest_share,'iqr_fences_seconds':fences,'iqr_outliers':out,'step_time_samples':[{'time':int(wct[i][0]),'solver_log_seconds':samples[i][1],'wallClockTime_dat_seconds':vals[i],'absolute_difference_seconds':diffs[i]} for i in range(149)],'wct_measured_steps':149,'native_minimum_sample_count_for_2pct_95pct_target':int(minm.group(1)),'native_sample_count_below_recommendation':149<int(minm.group(1)),'native_sample_confidence_warning_present':warning,'fixed_iterations_per_step':work,'final_time':timevals[-1],'tail':[x for x in solver.splitlines() if x.strip()][-10:]},'force_coefficients':{'rows':len(force),'final_Cd':force[-1][1],'min_Cd':min(r[1] for r in force),'max_Cd':max(r[1] for r in force),'all_values_finite':True},'requested_resources':{'requested_ncpus':ncpus,'requested_mpiprocs':mpiprocs,'node_count':4,'per_node_cpu_request':int(cfg['Resource_List']['ncpus'])//4,'per_node_mpi_request':ppn},'scheduler':{'historical_job_state_at_snapshot':cfg['historical_job_state_at_snapshot'],'current_final_state':'UnknownJobId','final_exit_status':None,'elapsed':None,'actual_charge':None,'reason':'PBS now returns UnknownJobId; retained collection metadata records only the historical Q snapshot.'},'selected_runtime_environment':{'file':'logFiles/00_environment.selected.txt','sha256':sha(get('logFiles/00_environment.selected.txt')),'selected_lines':env_selected,'complete_whitelisted_file_lines':env.splitlines()},'partial_preparation_timer_components_seconds':stage_sec,'partial_preparation_timer_sum_seconds':sum(stage_sec.values()),'partial_preparation_timer_definition':'decomposePar algorithm timer plus renumberMesh, potentialFoam, and applyBoundaryLayer initialization ClockTime values; partial only, excludes decomposePar transfer/write, I/O and unaccounted setup time.'}
def sealed():
 local=readj(COLLECTED/'evidence-sha256.json')
 for n,h in local.items(): need((COLLECTED/n).is_file() and sha((COLLECTED/n).read_bytes())==h,f'local hash mismatch: {n}')
 remote=readj(COLLECTED/'remote-file-sha256.json'); arc=COLLECTED/'raw-text-evidence.tar.gz'
 with tarfile.open(arc,'r:gz') as t:
  ms=t.getmembers(); names=[m.name for m in ms]
  need(all(m.isfile() for m in ms) and len(names)==len(set(names)),'archive has non-files or duplicate paths')
  need(all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names),'unsafe archive path')
  need(set(names)==set(remote)|{'remote-file-sha256.json'},'archive/remote manifest membership mismatch')
  files={m.name:t.extractfile(m).read() for m in ms}
 need(files['remote-file-sha256.json']==(COLLECTED/'remote-file-sha256.json').read_bytes(),'embedded remote manifest differs')
 for n,h in remote.items(): need(sha(files[n])==h,f'remote hash mismatch: {n}')
 need(set(readj(COLLECTED/'collection.json')['jobs'])==set(JOBS),'collection job set mismatch')
 return readj(COLLECTED/'collection.json'),files,len(local),len(remote)
def main():
 meta,files,nlocal,nremote=sealed(); results={}
 for job in JOBS:
  try: results[job]=validate(job,meta,files)
  except Exception as e: results[job]={'job':job,'review_status':'FAIL','error':str(e)}
 valid=[v for v in results.values() if 'review_status' not in v]
 if not valid: print(json.dumps(results,indent=2)); return
 table=[{'job':r['job'],'method':r['method'],'ranks_per_node':r['per_node_mpi_ranks'],'ranks_total':r['total_mpi_ranks'],'requested_ncpus':r['requested_ncpus'],'mean_s':r['native_simplefoam']['average_step_seconds'],'p95_s':r['native_simplefoam']['p95_seconds_linear_interpolation'],'max_s':r['native_simplefoam']['max_seconds'],'max_Time':r['native_simplefoam']['max_time'],'final_Cd':r['force_coefficients']['final_Cd'],'warning':r['native_simplefoam']['native_sample_confidence_warning_present'],'min_samples_recommended':r['native_simplefoam']['native_minimum_sample_count_for_2pct_95pct_target']} for r in valid]
 leader=min(valid,key=lambda r:r['native_simplefoam']['average_step_seconds'])
 pernode={}
 for ppn in (64,96,128):
  group=[r for r in valid if r['per_node_mpi_ranks']==ppn]
  pernode[str(ppn)]={'lowest_mean_job':min(group,key=lambda r:r['native_simplefoam']['average_step_seconds'])['job'],'lowest_mean_seconds':min(r['native_simplefoam']['average_step_seconds'] for r in group)}
 out={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'CANDIDATE_NATIVE_EVIDENCE_ONLY','scheduler_state':'UnknownJobId for all six; no final scheduler state, exit status, elapsed or charge inferred','integrity':{'local_manifest_entries':nlocal,'remote_manifest_entries':nremote,'raw_archive_members':len(files),'all_hashes_and_archive_membership_pass':True},'runs':results,'per_run_gate_failures':{j:r['error'] for j,r in results.items() if 'review_status' in r},'comparison_rows':table,'lowest_native_average':{'job':leader['job'],'seconds_per_step':leader['native_simplefoam']['average_step_seconds']},'per_node_density_leaders':pernode,'prior_endpoint_context':{'one_node_scotch_128_mpi_ranks_per_node_mean_seconds':13.880988254,'two_node_hierarchical_128_mpi_ranks_per_node_mean_seconds':7.169996913,'two_node_scotch_128_mpi_ranks_per_node_mean_seconds':7.462835189,'note':'Historical reference values provided in the HPC handoff; different allocations and endpoint lengths, context only, not a matched scaling series.'},'interpretation_limits':['The six historical PBS request snapshots were Q. PBS currently returns UnknownJobId. Do not infer successful terminal state, exit 0, actual elapsed time, charge or completion from native logs.','Per-run native source, mesh cell total, solver work and output checks are evidence about retained files. The history-free collection does not include frozen submission proofs, native command return statuses, final zero-field seals or rank affinity; therefore these remain candidate observations, not accepted contest scores.','The preparation timer sum is partial, consisting of the decomposePar algorithm timer plus three initialization ClockTime values. It is not a complete initialization duration or setup winner.','The 149 samples are steps Time 2 through 150; the native recommended counts and short-sample warnings are retained. These are warnings about the sampled time series, not formal confidence intervals.','CPU requests differ from MPI process counts: especially Scotch 64 requests 256 CPUs while hierarchical 64 requests 512 CPUs. Since actual PBS elapsed and accounting are unavailable, no actual cost comparison is possible.','No affinity or physical core placement was retained. Host grouping is parsed from the native OpenFOAM Hosts and Pstream headers.','Hardware counters, memory bandwidth, page residency, MPI wait/traffic, and authoritative final field/mesh identity were not collected. No causal bottleneck is inferred.']}
 (ROOT/'review.json').write_text(json.dumps(out,indent=2)+'\n')
 lines=['# Four-node OpenFOAM native evidence review','','This offline review covers six sealed 150-step runs across Scotch and hierarchical decomposition at 64, 96 and 128 MPI ranks per node. The collection preserves native files, but PBS history is unavailable: PBS returns `UnknownJobId` for all six. The results below are candidate native observations, not accepted scores.','','## Integrity and per-run checks','',f"The {nlocal} local collection entries and {nremote} remote file hashes passed SHA-256 verification; the raw archive contains {len(files)} unique, safe file members. Each run passed source comparison against the accepted baseline (allowing only decomposition method, rank count, hierarchical factors and endTime), native OpenFOAM 2512 / v2512 scalar64 labels, mesh cell total, solver rank count, four distinct native hosts with the expected per-host rank grouping, full 150-step sequence, all five native `End` markers, no fatal or MPI signal marker, fixed iteration work, finite 150-row force coefficients, and all 149 timed samples cross-checked between solver log and wallClockTime data.",'','| Job | Method | MPI ranks/node (total) | Requested CPUs | Mean s/step | p95 s | Max s (Time) | Final Cd | Mean/median | Top three timed steps (Time: seconds) | Largest-step share | Min recommended samples | Short-sample warning |','|---|---|---:|---:|---:|---:|---|---:|---:|---|---:|---:|---|']
 for r in valid:
  t=r['native_simplefoam']; top=', '.join(f"{x['time']}: {x['seconds']:.3f}" for x in t['top_three_step_times_descending']); lines.append(f"| {r['job']} | {r['method']} | {r['per_node_mpi_ranks']} ({r['total_mpi_ranks']}) | {r['requested_ncpus']} | {t['average_step_seconds']:.9f} | {t['p95_seconds_linear_interpolation']:.6f} | {t['max_seconds']:.6f} (T{t['max_time']}) | {r['force_coefficients']['final_Cd']:.10f} | {t['mean_median_ratio']:.3f} | {top} | {t['largest_step_mean_contribution_percent']:.2f}% | {t['native_minimum_sample_count_for_2pct_95pct_target']} | {'yes' if t['native_sample_confidence_warning_present'] else 'no'} |")
 pernode_text=', '.join('{}: {} ({:.9f} s/step)'.format(ppn,v['lowest_mean_job'],v['lowest_mean_seconds']) for ppn,v in pernode.items())
 lines += ['', '## Earlier endpoint context', '', 'Earlier handoff values were 13.880988254 s/step for one-node Scotch at 128 ranks/node, and 7.169996913 / 7.462835189 s/step for two-node hierarchical / Scotch at 128 ranks/node. Those observations used separate allocations and different endpoints; this is context for the research presentation, not a matched scaling curve or causal comparison.', '', f"The lowest native Average is **{leader['job']}** at **{leader['native_simplefoam']['average_step_seconds']:.9f} s/step**. By ranks per node, the observed means favor {pernode_text}. These are descriptive comparisons among separate allocations, without scheduler completion or accounting records.",'','The p95 uses linear interpolation. Mean/median ratios and top-three step lists describe the observed time-series tail. Largest-step share is that step’s portion of the untrimmed 149-sample sum (and of the arithmetic mean); it is a diagnostic only. No step is removed or downweighted from Average. Full time-indexed samples, corrected IQR fences and outliers, Cd ranges, rank-to-host groups, selected runtime flags, stage tails/warnings and per-run checks are retained in [review.json](review.json). The decomposePar algorithm timer plus three initialization `ClockTime` measurements is a **partial** preparation sum; it omits decomposePar transfer/write, I/O and unaccounted setup time, so it is not an initialization-duration estimate or a setup winner.','','## Interpretation limits','','The collection metadata retains the prior PBS snapshot as queued and explicitly has no final state or exit status. Current `UnknownJobId` responses do not establish completion or failure. No final elapsed time or actual charge can be recovered from these logs, and no full-slot billing comparison is made. Requested CPU counts are recorded; Scotch 64 requested 256 CPUs while hierarchical 64 requested 512 despite both using 256 MPI ranks.','','Native `End` markers show the solver logs ended normally, but the history-free collection lacks frozen submission proofs, individual command return codes, final zero-field seals and affinity evidence. Four-host placement is parsed from the solver’s own `Hosts` list and Pstream header, not from a rank-affinity map. These limitations prevent acceptance as scored results. The native sample recommendation exceeds 149 timed steps in each case; emitted short-sample warnings and recommendation counts are preserved, not treated as formal confidence intervals.','','No hardware counters, memory bandwidth, page residency, MPI wait/traffic or authoritative final mesh/field identity were collected. The comparison does not identify a causal bottleneck.']
 (ROOT/'RESULTS.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'status':out['status'],'validated_runs':len(valid),'failures':out['per_run_gate_failures'],'winner':out['lowest_native_average'],'per_node':pernode},indent=2))
if __name__=='__main__': main()
