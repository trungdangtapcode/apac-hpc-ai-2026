"""Validate the 150-step native solver chain and every 149-step timing sample."""
from pathlib import Path
import argparse,json,math,re,statistics,tarfile

def linear(a,p):
 a=sorted(a);x=(len(a)-1)*p;lo=math.floor(x);hi=math.ceil(x);f=x-lo
 return a[lo]*(1-f)+a[hi]*f
def source(case,rel):
 p=case/rel
 assert p.is_file(),str(p)
 return p.read_text(errors='replace')
def archive_member(tf,prefix,suffix,unique=False):
 names=[n for n in tf.getnames() if n.startswith(prefix) and n.endswith(suffix)]
 if unique: assert len(names)==1,(prefix,suffix,names)
 assert names,names
 return tf.extractfile(names[0]).read().decode(errors='replace')
def validate(log,si,wct,force,expected_ranks=512):
 assert 'OPENFOAM=2512' in log and 'version=v2512' in log
 assert 'Arch   : "LSB;label=32;scalar=64"' in log
 assert re.search(rf'(?m)^nProcs\s*:\s*{expected_ranks}\s*$',log)
 hosts=re.findall(r'^\s*\((\S+)\s+(\d+)\)\s*$',log[log.find('Hosts  :'):log.find('Pstream initialized with:')],re.M)
 assert len(hosts)==4 and len({h for h,_ in hosts})==4 and all(int(n)==128 for _,n in hosts),hosts
 pm=re.search(r'node communication\s*:\s*on \[type=host\] \((\d+) ranks, (\d+) nodes\)',log)
 assert pm and int(pm.group(1))==512 and int(pm.group(2))==4
 assert re.search(r'^End\s*$',log,re.M) and not re.search(r'FOAM FATAL|FATAL ERROR|MPI_ABORT|died from signal|terminated by signal',log,re.I)
 steps=[int(x) for x in re.findall(r'^Time = (\d+)\s*$',log,re.M)];assert steps==list(range(1,151)),(len(steps),steps[-5:])
 for field,niter in [('Ux',15),('Uy',15),('Uz',15),('p',12),('omega',8),('k',8)]:
  got=[int(x) for x in re.findall(r'Solving for '+field+r',.*?No Iterations\s+(\d+)',log)]
  assert got==[niter]*150,(field,len(got),sorted(set(got)))
 header=None;sirows=[]
 for line in si.splitlines():
  text=line.strip()
  if text.startswith('#') and 'Ux_iters' in text: header=text.lstrip('#').split()
  elif text and not text.startswith('#') and header and len(text.split())==len(header): sirows.append(dict(zip(header,text.split())))
 assert header and [int(float(x['Time'])) for x in sirows]==list(range(1,151)),('solverInfo rows',len(sirows))
 expected_iters={'Ux_iters':15,'Uy_iters':15,'Uz_iters':15,'p_iters':12,'omega_iters':8,'k_iters':8}
 assert all(all(int(float(x[k]))==v for k,v in expected_iters.items()) for x in sirows),'solverInfo fixed iteration history mismatch'
 timed=[];current=None
 for line in log.splitlines():
  m=re.match(r'^Time = (\d+)\s*$',line)
  if m:current=int(m.group(1))
  m=re.match(r'^Wall-clock time elapsed during the current time step\s*=\s*([\deE.+-]+)\s*s\s*$',line)
  if m:timed.append((current,float(m.group(1))))
 assert [i for i,_ in timed]==list(range(2,151)),('solver WCT indices',len(timed))
 timer=[]
 for line in wct.splitlines():
  if line.strip() and not line.lstrip().startswith('#'):
   q=[float(x) for x in line.split()];assert len(q)==3,q;timer.append(q)
 assert [int(x[0]) for x in timer]==list(range(2,151)),('function indices',len(timer))
 native=[x for _,x in timed];function=[x[2] for x in timer]
 assert all(math.isfinite(x) and x>0 for x in native+function)
 checks=[abs(a-b) for a,b in zip(native,function)];tol=max(1e-9,max(function)*1e-10)
 assert max(checks)<=tol,('time samples differ',max(checks),tol)
 accum=0.;accdiff=[]
 for row in timer:
  accum+=row[2];accdiff.append(abs(row[1]-accum))
 assert max(accdiff)<=max(1e-8,accum*1e-10),('accumulated time mismatch',max(accdiff))
 avgm=re.search(r'Average wall-clock time per time step\s*=\s*([\deE.+-]+)',log)
 nsm=re.search(r'Number of measured time steps\s*=\s*(\d+)',log)
 assert avgm and nsm and int(nsm.group(1))==149
 avg=float(avgm.group(1));mean=statistics.mean(function);assert math.isclose(avg,mean,rel_tol=1e-10,abs_tol=1e-10),(avg,mean)
 rows=[]
 for line in force.splitlines():
  if line.strip() and not line.lstrip().startswith('#'):
   row=[float(x) for x in line.split()];rows.append(row)
 assert len(rows)==150 and [int(x[0]) for x in rows]==steps and all(math.isfinite(v) for row in rows for v in row)
 vals=function;q1=linear(vals,.25);q3=linear(vals,.75);fences=[q1-1.5*(q3-q1),q3+1.5*(q3-q1)]
 outliers=[{'time':int(timer[i][0]),'seconds':v} for i,v in enumerate(vals) if v<fences[0] or v>fences[1]]
 top=sorted(({'time':int(timer[i][0]),'seconds':v} for i,v in enumerate(vals)),key=lambda x:x['seconds'],reverse=True)[:5]
 p95=linear(vals,.95);med=statistics.median(vals);mx=max(vals);mi=vals.index(mx);sumv=sum(vals)
 mm=re.search(r'Minimum number of measured time steps for 2% error at 95% confidence level\s*=\s*(\d+)',log)
 assert mm,'native minimum sample recommendation absent'
 warning=bool(re.search(r'Number of time steps of the current run is smaller than the calculated one by the statistical analysis',log,re.I))
 warning_lines=[x.strip() for x in log.splitlines() if 'Number of time steps of the current run is smaller than the calculated one by the statistical analysis' in x]
 return {'passed':True,'steps':150,'timed_samples':149,'time_indices':[2,150],'average_seconds_step_native':avg,'recomputed_sample_mean_seconds':mean,'median_seconds_step':med,'mean_median_ratio':avg/med,'p95_seconds_linear_interpolation':p95,'max_seconds_step':mx,'max_time':int(timer[mi][0]),'top_five_steps_descending':top,'largest_step_sum_share':mx/sumv,'largest_step_mean_contribution_seconds':mx/149,'largest_step_mean_contribution_percent':100*mx/sumv,'iqr_q1_seconds':q1,'iqr_q3_seconds':q3,'iqr_fences_seconds':fences,'iqr_outliers':outliers,'all_samples_preserved':True,'solver_vs_time_function_max_abs_difference_seconds':max(checks),'time_function_accumulated_max_abs_difference_seconds':max(accdiff),'timing_samples':[{'time':int(timer[i][0]),'solver_log_seconds':native[i],'time_function_seconds':function[i],'absolute_difference_seconds':checks[i]} for i in range(149)],'force_rows':len(rows),'final_Cd':rows[-1][1],'Cd_range':[min(x[1] for x in rows),max(x[1] for x in rows)],'native_minimum_sample_count_for_2pct_95pct_target':int(mm.group(1)),'native_warning_below_recommended_count':warning,'native_warning_text_present':warning,'native_short_sample_warning_lines':warning_lines,'native_confidence_note':'Native recommendation is an internal time-series diagnostic, not an independent confidence interval.'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('case',nargs='?');ap.add_argument('--archive');ap.add_argument('--prefix',default='');ap.add_argument('--output');a=ap.parse_args()
 if a.archive:
  with tarfile.open(a.archive,'r:gz') as tf:
   p=a.prefix.rstrip('/')+'/'
   simple=[n for n in tf.getnames() if n.startswith(p) and '/logFiles/50_simpleFoam.' in n]
   if len(simple)!=1:
    simple=[n for n in tf.getnames() if n.startswith(p) and n.endswith('/logFiles/simpleFoam.log')]
   assert len(simple)==1,(p,simple)
   log=tf.extractfile(simple[0]).read().decode(errors='replace')
   names=[n for n in tf.getnames() if n.startswith(p+'postProcessing/solverInfo/0/solverInfo.dat')];assert len(names)==1
   si=tf.extractfile(names[0]).read().decode(errors='replace')
   wct=archive_member(tf,p,'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat',True)
   force=archive_member(tf,p,'postProcessing/forceCoeffsAll/0/coefficient.dat',True)
 else:
  c=Path(a.case).resolve();log=source(c,'logFiles/simpleFoam.log');si=source(c,'postProcessing/solverInfo/0/solverInfo.dat');wct=source(c,'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat');force=source(c,'postProcessing/forceCoeffsAll/0/coefficient.dat')
 r=validate(log,si,wct,force);txt=json.dumps(r,indent=2)+'\n'
 if a.output:Path(a.output).write_text(txt)
 print(txt)
if __name__=='__main__':main()
