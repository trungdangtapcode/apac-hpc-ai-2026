"""Review ordered one-node method pair without treating a job exit as a score."""
from pathlib import Path
import json,hashlib,re,statistics,math,datetime
r=Path(__file__).resolve().parent;job=json.loads((r/'submission.json').read_text())['stdout'].strip();d=r/'collected'/job;s=d/'runs'/job.split('.')[0]
for relative,digest in json.loads((d/'evidence-sha256.json').read_text()).items():assert hashlib.sha256((d/relative).read_bytes()).hexdigest()==digest
j=json.loads((r/'terminal-accounting.json').read_text())['jobs'][job];assert j['job_state']=='F' and j['Exit_status']==0
assert j['Resource_List']['ncpus']==128 and j['Resource_List']['ngpus']==0
for f in (r/'payload').iterdir():assert f.read_bytes()==(d/f.name).read_bytes(),f.name
assert json.loads((d/'INPUTS_VALIDATED.json').read_text())['passed'] is True
assert 'CPU_HS_PAIR_PASS' in (d/('tu-cpu-HS128.o'+job.split('.')[0])).read_text()
placement=[json.loads(x) for x in (s/'rank-placement.jsonl').read_text().splitlines() if x.strip()];assert sorted(x['rank'] for x in placement)==list(range(128))
assert len(set(x['host'] for x in placement))==1 and all(len(x['affinity'])==1 for x in placement) and len(set(x['affinity'][0] for x in placement))==128
assert 'AMD EPYC 7713' in (s/'environment.log').read_text()
def stage(p):
 t=p.read_text();assert re.search(r'^End\s*$',t,re.M) and 'FOAM FATAL' not in t and 'died from signal' not in t
 assert 'OPENFOAM=2512' in t and 'scalar=64' in t and re.search(r'^nProcs\s*:\s*128\s*$',t,re.M)
 assert re.search(r'Exit status:\s*0\s*$',t,re.M)
 return t
for name in ['renumberMesh','potentialFoam','applyBoundaryLayer']:stage(s/'candidate-init'/(name+'.log'))
results={}
for role,prep in [('control','nscc-cpu-baseline-headerfix-20261021'),('candidate','nscc-cpu-scotch128-20261021')]:
 p=s/role;t=stage(p/'logFiles/simpleFoam.log');steps=[int(x) for x in re.findall(r'^Time = (\d+)\s*$',t,re.M)];assert steps==list(range(1,41))
 dt=[float(x) for x in re.findall(r'Wall-clock time elapsed during the current time step = ([\deE.+-]+)',t)]
 avg=float(re.search(r'Average wall-clock time per time step\s*=\s*([\deE.+-]+)',t)[1]);assert len(dt)==39 and all(math.isfinite(x) and x>0 for x in dt) and abs(statistics.mean(dt)-avg)<1e-10
 wall=[list(map(float,x.split())) for x in (p/'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat').read_text().splitlines() if x.strip() and not x.startswith('#')]
 assert [int(x[0]) for x in wall]==list(range(2,41)) and all(abs(a-b[2])<1e-10 for a,b in zip(dt,wall))
 cd=[list(map(float,x.split())) for x in (p/'postProcessing/forceCoeffsAll/0/coefficient.dat').read_text().splitlines() if x.strip() and not x.startswith('#')]
 assert [int(x[0]) for x in cd]==steps and all(math.isfinite(x) for row in cd for x in row)
 for name,n in [('Ux',15),('Uy',15),('Uz',15),('p',12),('omega',8),('k',8)]:assert [int(x) for x in re.findall(r'Solving for '+name+r',.*?No Iterations (\d+)',t)]==[n]*40
 sem=json.loads((p/'semantic-result.json').read_text());assert sem['passed'] and sem['average_seconds_step']==avg and sem['final_Cd_dimensionless']==cd[-1][1]
 before=json.loads((s/(role+'-before.json')).read_text());after=json.loads((s/(role+'-after.json')).read_text());assert before['files']==after['files']
 src=r.parent/prep/'payload/case/system'
 for f in (p/'system').rglob('*'):
  if f.is_file() and f.name!='controlDict':assert f.read_bytes()==(src/f.relative_to(p/'system')).read_bytes()
 control=(p/'system/controlDict').read_text();assert re.search(r'^startFrom\s+startTime;',control,re.M) and re.search(r'^endTime\s+40;',control,re.M)
 assert [x.strip() for x in re.findall(r'#\{(.*?)#\}',(src/'FOwallClockTimeStatistics').read_text(),re.S)]==[x.strip() for x in re.findall(r'#\{(.*?)#\}',control,re.S)]
 results[role]=dict(method='hierarchical' if role=='control' else 'scotch',steps=40,measured_steps=39,average_seconds_step=avg,median_seconds_step=statistics.median(dt),p95_seconds_step=statistics.quantiles(dt,n=100,method='inclusive')[94],min_seconds_step=min(dt),max_seconds_step=max(dt),final_Cd_dimensionless=cd[-1][1],native_solver_clock_seconds=float(re.findall(r'ClockTime = ([\d.]+) s',t)[-1]),omega_bounding_messages=t.count('bounding omega'),timing_confidence_warning='smaller than the calculated one' in t,initial_fields_unchanged=True)
h,m,sec=map(int,j['resources_used']['walltime'].split(':'));elapsed=h*3600+m*60+sec
ratio=results['control']['average_seconds_step']/results['candidate']['average_seconds_step']
out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),job=job,state='ORDERED_ONE_NODE_METHOD_PAIR_PASS',node=j['exec_host'].split('/')[0],order=['hierarchical','scotch'],results=results,observed_control_over_candidate_step_time_ratio=ratio,observed_candidate_step_time_reduction_percent=100*(1-1/ratio),elapsed_seconds=elapsed,estimated_base_SU=elapsed*128/3600,reported_resources=j['resources_used'],posted_individual_charge='Not individually reported',placement_records=placement,limitations='One ordered pair, no reverse repeat; cache/order/host drift remain. No four-node/150-step score. Partition method can change floating-point order and Cd; do not impose an invented universal accuracy tolerance. Affinity probe is outside solver timing, not solver migration or actual page placement. Hardware bandwidth/cache/MPI counters and power not collected. GNU time wraps PALS launcher.')
(r/'review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='placement_records'},indent=2))
