"""Reverse-order 30-step zyx/xyz screen; preserve both initialized source cases."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,time,statistics,socket,datetime
from case_checks import source_check
from native_output import review_native_output
KIT=Path(__file__).resolve().parent;WORK=KIT.parent;RUN=None
SOURCE=Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-order-init-20261026T133526Z/initialized')
DEADLINE=time.monotonic()+2580
ARM_ORDER=("zyx", "xyz")
SOLVER_CAP=1150
ARM_START_RESERVE=1270

def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def select_arms_by_order(rows):
    by_order={row['order']:row for row in rows}
    assert len(by_order)==len(rows)==2 and set(by_order)=={'zyx','xyz'},'expected exactly one zyx and one xyz arm'
    return by_order['zyx'],by_order['xyz']
def node_snapshot(label,dest):
    # Metadata-only whole-node counters; no cache controls or sysctl changes.
    started=time.monotonic_ns()
    root=Path('/proc'); snap={'label':label,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'time_ns':time.time_ns(),'scope':'whole-node procfs counters; not per-process hardware bandwidth'}
    for name in ('meminfo','vmstat','pressure/memory'):
        p=root/name
        try:snap[name]=p.read_text()
        except Exception as exc:snap[name+'_error']={'type':type(exc).__name__,'message':str(exc)}
    snap['collection_elapsed_ms']=(time.monotonic_ns()-started)/1e6
    save(dest/(label+'-node-snapshot.json'),snap)
def bounded(label,args,cwd,cap):
 left=int(DEADLINE-time.monotonic())-60;assert left>0,'deadline before '+label
 with (RUN/(label+'.log')).open('w') as f:p=subprocess.run(['timeout','--signal=TERM','--kill-after=10s',str(min(cap,left))+'s',*args],cwd=str(cwd),stdout=f,stderr=subprocess.STDOUT,timeout=min(cap,left)+20)
 save(RUN/(label+'.status.json'),{'returncode':p.returncode});assert p.returncode==0,(label,p.returncode)

def main():
 global RUN
 RUN=WORK/'runs'/os.environ['SLURM_JOB_ID'];RUN.mkdir(parents=True,exist_ok=False)
 bounded('kit-before',['sha256sum','-c','payload-sha256.txt'],KIT,30)
 results=[]
 for order in ARM_ORDER:
  remaining=int(DEADLINE-time.monotonic())
  assert remaining>=ARM_START_RESERVE,('insufficient shared deadline before '+order,remaining)
  src=SOURCE/('order-'+order);assert (src/'READY').is_file();save(RUN/(order+'-source.json'),source_check(src,order))
  dest=WORK/'cases'/order;assert not dest.exists();dest.mkdir(parents=True)
  bounded(order+'-source-before',['python3',str(KIT/'tree-manifest.py'),str(src),str(dest),str(dest/'source-before.json'),'--source-only'],KIT,180)
  bounded(order+'-clone',['python3','-c','import shutil,sys;shutil.copytree(sys.argv[1],sys.argv[2],symlinks=True,dirs_exist_ok=True,ignore=shutil.ignore_patterns("source-before.json","source-after-copy.json","source-after-init.json"))',str(src),str(dest)],KIT,300)
  bounded(order+'-clone-check',['python3',str(KIT/'tree-manifest.py'),str(src),str(dest),str(dest/'copy-check.json'),'--compare-copy'],KIT,180)
  text=(dest/'system/controlDict.noWrite').read_text()
  for key,value in [('startFrom','startTime'),('endTime','30')]:
   text,count=re.subn(r'(?m)^'+key+r'[ \t]+[^;\n]+;[^\n]*$',key+' '+value+';',text);assert count==1
  (dest/'system/controlDict').write_text(text);shutil.copyfile(dest/'system/fvSolution.fixedIter',dest/'system/fvSolution')
  bounded(order+'-affinity',['mpirun','-np','56','--','python3',str(KIT/'affinity-probe.py'),'worker',str(dest/'affinity')],dest,60)
  bounded(order+'-affinity-check',['python3',str(KIT/'affinity-probe.py'),'validate',str(dest/'affinity')],dest,30)
  remaining=int(DEADLINE-time.monotonic())
  assert remaining>=ARM_START_RESERVE,('insufficient shared deadline immediately before '+order+' solver',remaining)
  node_snapshot('solver-before',dest)
  with (dest/'simpleFoam.log').open('w') as out, (dest/'solver.stderr').open('w') as err:
   p=subprocess.run(['/usr/bin/time','-v','-o',str(dest/'resource-time.log'),'timeout','--signal=TERM','--kill-after=15s',str(SOLVER_CAP)+'s','mpirun','-np','56','--','simpleFoam','-parallel'],cwd=str(dest),stdout=out,stderr=err,timeout=SOLVER_CAP+20)
  node_snapshot('solver-after',dest)
  save(dest/'return-code.json',{'returncode':p.returncode});assert p.returncode==0,(order,p.returncode)
  log,timing,cd,counts=review_native_output(dest)
  assert not re.search(r'FOAM FATAL|MPI_ABORT|died from signal|core dumped',(dest/'solver.stderr').read_text(),re.I)
  bounded(order+'-source-after',['python3',str(KIT/'tree-manifest.py'),str(src),str(dest),str(dest/'source-after.json'),'--source-only','--compare-source-snapshot'],KIT,180)
  confidence=re.search(r'Minimum number of measured time steps[^\n]*=\s*(\d+)',log)
  row={'order':order,'steps':30,'intervals':29,'mean_seconds_per_step':statistics.mean(timing),'median_seconds_per_step':statistics.median(timing),'p95_seconds_per_step':statistics.quantiles(timing,n=100,method='inclusive')[94],'maximum_seconds_per_step':max(timing),'final_Cd':cd[-1][1],'fixed_iterations':counts,'native_minimum_samples':int(confidence[1]) if confidence else None,'confidence_warning_present':'smaller than the calculated one' in log,'timings_seconds':timing}
  results.append(row);save(RUN/'partial-results.json',{'arms':results})
 bounded('kit-after',['sha256sum','-c','payload-sha256.txt'],KIT,30)
 zyx,xyz=select_arms_by_order(results)
 save(RUN/'comparison.json',{'passed':True,'arms':results,'order':list(ARM_ORDER),'arms_by_order':{row['order']:row for row in results},'candidate_time_change_percent':100*(zyx['mean_seconds_per_step']/xyz['mean_seconds_per_step']-1),'hostname':socket.getfqdn(),'scored_result':False,'limits':['Short matched 30-step screen, not a full 150-step result','One reverse-order pair leaves temporal and thermal drift unresolved','No memory bandwidth or kernel telemetry collected; procfs snapshots are whole-node counters, not per-process attribution']})
 print('MATCHED_XYZ_ZYX_30STEP_SCREEN_PASS')
if __name__=='__main__':main()
