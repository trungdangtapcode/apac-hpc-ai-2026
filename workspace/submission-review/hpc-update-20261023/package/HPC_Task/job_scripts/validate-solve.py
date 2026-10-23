"""Check complete fixed-iteration solver output, native timers, and finite force rows."""
from pathlib import Path
import argparse,json,math,re,statistics
p=argparse.ArgumentParser();p.add_argument('case');p.add_argument('--steps',type=int,required=True);p.add_argument('--nodes',type=int,required=True);p.add_argument('--output',required=True);p.add_argument('--log');p.add_argument('--solver-info');p.add_argument('--wall-clock');p.add_argument('--forces');a=p.parse_args();c=Path(a.case);steps=a.steps;ranks=a.nodes*128
log=Path(a.log or c/'logFiles/simpleFoam.log').read_text(errors='replace');si=Path(a.solver_info or c/'postProcessing/solverInfo/0/solverInfo.dat').read_text();wct=Path(a.wall_clock or c/'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat').read_text();force=Path(a.forces or c/'postProcessing/forceCoeffsAll/0/coefficient.dat').read_text()
assert 'OPENFOAM=2512' in log and 'version=v2512' in log and 'Arch   : "LSB;label=32;scalar=64"' in log;assert re.search(rf'(?m)^nProcs\s*:\s*{ranks}\s*$',log);block=log[log.find('Hosts  :'):log.find('Pstream initialized with:')];hosts=re.findall(r'^\s*\((\S+)\s+(\d+)\)\s*$',block,re.M);assert len(hosts)==a.nodes and len(set(h for h,_ in hosts))==a.nodes and all(int(n)==128 for _,n in hosts),hosts
pm=re.search(r'node communication\s*:\s*(?:on|off) \[type=host\] \((\d+) ranks, (\d+) nodes\)',log);assert pm and int(pm.group(1))==ranks and int(pm.group(2))==a.nodes;assert re.search(r'^End\s*$',log,re.M) and not re.search(r'FOAM FATAL|FATAL ERROR|MPI_ABORT|died from signal|terminated by signal',log,re.I)
assert [int(x) for x in re.findall(r'^Time = (\d+)\s*$',log,re.M)]==list(range(1,steps+1))
for field,niter in [('Ux',15),('Uy',15),('Uz',15),('p',12),('omega',8),('k',8)]:
 got=[int(x) for x in re.findall(r'Solving for '+field+r',.*?No Iterations\s+(\d+)',log)];assert got==[niter]*steps,(field,len(got),sorted(set(got)))
header=None;rows=[]
for line in si.splitlines():
 s=line.strip()
 if s.startswith('#') and 'Ux_iters' in s:header=s.lstrip('#').split()
 elif s and not s.startswith('#') and header and len(s.split())==len(header):rows.append(dict(zip(header,s.split())))
assert header and [int(float(x['Time'])) for x in rows]==list(range(1,steps+1)); expected={'Ux_iters':15,'Uy_iters':15,'Uz_iters':15,'p_iters':12,'omega_iters':8,'k_iters':8};assert all(all(int(float(x[k]))==v for k,v in expected.items()) for x in rows)
timed=[];cur=None
for line in log.splitlines():
 m=re.match(r'^Time = (\d+)\s*$',line)
 if m:cur=int(m.group(1))
 m=re.match(r'^Wall-clock time elapsed during the current time step\s*=\s*([\deE.+-]+)\s*s\s*$',line)
 if m:timed.append((cur,float(m.group(1))))
assert [i for i,_ in timed]==list(range(2,steps+1));timer=[]
for line in wct.splitlines():
 if line.strip() and not line.lstrip().startswith('#'):
  q=[float(x) for x in line.split()];assert len(q)==3;timer.append(q)
assert [int(x[0]) for x in timer]==list(range(2,steps+1));native=[x for _,x in timed];func=[x[2] for x in timer];assert all(math.isfinite(x) and x>0 for x in native+func);diff=[abs(x-y) for x,y in zip(native,func)];assert max(diff)<=max(1e-9,max(func)*1e-10)
acc=0.;accdiff=[]
for row in timer:acc+=row[2];accdiff.append(abs(row[1]-acc))
assert max(accdiff)<=max(1e-8,acc*1e-10);avg=re.search(r'Average wall-clock time per time step\s*=\s*([\deE.+-]+)',log);ns=re.search(r'Number of measured time steps\s*=\s*(\d+)',log);assert avg and ns and int(ns.group(1))==steps-1;assert math.isclose(float(avg.group(1)),statistics.mean(func),rel_tol=1e-10,abs_tol=1e-10)
forces=[]
for line in force.splitlines():
 if line.strip() and not line.lstrip().startswith('#'):
  q=[float(x) for x in line.split()];forces.append(q)
assert len(forces)==steps and [int(x[0]) for x in forces]==list(range(1,steps+1)) and all(math.isfinite(v) for row in forces for v in row)
out={'passed':True,'steps':steps,'timed_samples':steps-1,'ranks':ranks,'hosts':hosts,'all_fixed_iteration_counts_match':True,'solver_and_function_timers_match':True,'force_rows':len(forces),'final_Cd':forces[-1][1],'Cd_finite_all_rows':True,'Cd_numeric_passband_used':False,'timing_samples_seconds':[x[2] for x in timer],'limits':'Native output integrity only; this does not supply terminal PBS accounting, independent confidence intervals, or causal attribution.'};Path(a.output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
