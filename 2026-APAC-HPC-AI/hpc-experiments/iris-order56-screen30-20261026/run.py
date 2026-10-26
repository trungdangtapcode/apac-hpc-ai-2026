"""Matched 30-step xyz/zyx screen; preserve both initialized source cases."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,time,statistics,socket
from case_checks import source_check
from native_output import review_native_output
KIT=Path(__file__).resolve().parent;WORK=KIT.parent;RUN=None
SOURCE=Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-order-init-20261026T133526Z/initialized')
DEADLINE=time.monotonic()+2580

def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def bounded(label,args,cwd,cap):
 left=int(DEADLINE-time.monotonic())-60;assert left>0,'deadline before '+label
 with (RUN/(label+'.log')).open('w') as f:p=subprocess.run(['timeout','--signal=TERM','--kill-after=10s',str(min(cap,left))+'s',*args],cwd=str(cwd),stdout=f,stderr=subprocess.STDOUT,timeout=min(cap,left)+20)
 save(RUN/(label+'.status.json'),{'returncode':p.returncode});assert p.returncode==0,(label,p.returncode)

def main():
 global RUN
 RUN=WORK/'runs'/os.environ['SLURM_JOB_ID'];RUN.mkdir(parents=True,exist_ok=False)
 bounded('kit-before',['sha256sum','-c','payload-sha256.txt'],KIT,30)
 results=[]
 for order in ['xyz','zyx']:
  assert int(DEADLINE-time.monotonic())>1170
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
  left=int(DEADLINE-time.monotonic());assert left>=1170
  with (dest/'simpleFoam.log').open('w') as out, (dest/'solver.stderr').open('w') as err:
   p=subprocess.run(['/usr/bin/time','-v','-o',str(dest/'resource-time.log'),'timeout','--signal=TERM','--kill-after=15s','1050s','mpirun','-np','56','--','simpleFoam','-parallel'],cwd=str(dest),stdout=out,stderr=err,timeout=1070)
  save(dest/'return-code.json',{'returncode':p.returncode});assert p.returncode==0,(order,p.returncode)
  log,timing,cd,counts=review_native_output(dest)
  assert not re.search(r'FOAM FATAL|MPI_ABORT|died from signal|core dumped',(dest/'solver.stderr').read_text(),re.I)
  bounded(order+'-source-after',['python3',str(KIT/'tree-manifest.py'),str(src),str(dest),str(dest/'source-after.json'),'--source-only','--compare-source-snapshot'],KIT,180)
  confidence=re.search(r'Minimum number of measured time steps[^\n]*=\s*(\d+)',log)
  row={'order':order,'steps':30,'intervals':29,'mean_seconds_per_step':statistics.mean(timing),'median_seconds_per_step':statistics.median(timing),'p95_seconds_per_step':statistics.quantiles(timing,n=100,method='inclusive')[94],'maximum_seconds_per_step':max(timing),'final_Cd':cd[-1][1],'fixed_iterations':counts,'native_minimum_samples':int(confidence[1]) if confidence else None,'confidence_warning_present':'smaller than the calculated one' in log,'timings_seconds':timing}
  results.append(row);save(RUN/'partial-results.json',{'arms':results})
 bounded('kit-after',['sha256sum','-c','payload-sha256.txt'],KIT,30)
 save(RUN/'comparison.json',{'passed':True,'arms':results,'order':['xyz','zyx'],'candidate_time_change_percent':100*(results[1]['mean_seconds_per_step']/results[0]['mean_seconds_per_step']-1),'hostname':socket.getfqdn(),'scored_result':False,'limits':['Short matched30-step screen, not a full150-step result','One fixed-order pair leaves temporal and thermal drift unresolved','No memory bandwidth or kernel telemetry collected']})
 print('MATCHED_XYZ_ZYX_30STEP_SCREEN_PASS')
if __name__=='__main__':main()
