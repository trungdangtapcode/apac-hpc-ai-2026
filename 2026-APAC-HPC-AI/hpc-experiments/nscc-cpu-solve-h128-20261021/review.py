"""Review the first full ASPIRE-2A N128 baseline from sealed native evidence."""
from pathlib import Path
import json,hashlib,re,statistics,math,datetime
r=Path(__file__).resolve().parent;d=r/'collected/25905114.pbs101';s=d/'runs/25905114'
for relative,digest in json.loads((d/'evidence-sha256.json').read_text()).items():
    assert hashlib.sha256((d/relative).read_bytes()).hexdigest()==digest
j=json.loads((r/'terminal-accounting.json').read_text())['jobs']['25905114.pbs101']
assert j['job_state']=='F' and j['Exit_status']==0
assert j['Resource_List']['ncpus']==128 and j['Resource_List']['ngpus']==0
assert j['resources_used']['walltime']=='00:12:08'
assert (d/'solve.pbs').read_bytes()==(r/'payload/solve.pbs').read_bytes()
rows=[]
for name,flags in [('renumberMesh','-constant -overwrite -parallel'),('potentialFoam','-initialiseUBCs -parallel'),('applyBoundaryLayer','-ybl 0.0450244 -parallel'),('simpleFoam','-parallel')]:
    t=(s/'logFiles'/(name+'.log')).read_text()
    assert re.search(r'^End\s*$',t,re.M) and 'FOAM FATAL' not in t and 'died from signal' not in t
    assert 'OPENFOAM=2512' in t and 'scalar=64' in t
    assert re.search(r'^nProcs\s*:\s*128\s*$',t,re.M)
    assert name+' '+flags in t and re.search(r'Exit status:\s*0\s*$',t,re.M)
    rows.append({'stage':name,'native_ClockTime_seconds':float(re.findall(r'ClockTime = ([\d.]+) s',t)[-1])})
t=(s/'logFiles/simpleFoam.log').read_text();steps=[int(v) for v in re.findall(r'^Time = (\d+)\s*$',t,re.M)]
assert steps==list(range(1,41))
dt=[float(v) for v in re.findall(r'Wall-clock time elapsed during the current time step = ([\deE.+-]+)',t)]
avg=float(re.search(r'Average wall-clock time per time step\s*=\s*([\deE.+-]+)',t)[1]);assert len(dt)==39 and all(math.isfinite(v) and v>0 for v in dt)
assert abs(statistics.mean(dt)-avg)<1e-10
wall=[list(map(float,x.split())) for x in (s/'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat').read_text().splitlines() if x.strip() and not x.startswith('#')]
assert [int(x[0]) for x in wall]==list(range(2,41)) and all(abs(a-b[2])<1e-10 for a,b in zip(dt,wall))
cd=[list(map(float,x.split())) for x in (s/'postProcessing/forceCoeffsAll/0/coefficient.dat').read_text().splitlines() if x.strip() and not x.startswith('#')]
assert [int(x[0]) for x in cd]==steps and all(math.isfinite(v) for row in cd for v in row)
sem=json.loads((s/'semantic-result.json').read_text());assert sem['passed'] and sem['average_seconds_step']==avg and sem['final_Cd_dimensionless']==cd[-1][1]
prep=r.parent/'nscc-cpu-baseline-headerfix-20261021/payload/case'
for p in (s/'system').rglob('*'):
    if p.is_file() and p.name!='controlDict':assert p.read_bytes()==(prep/'system'/p.relative_to(s/'system')).read_bytes()
control=(s/'system/controlDict').read_text()
assert re.search(r'^startFrom\s+startTime;',control,re.M) and re.search(r'^endTime\s+40;',control,re.M)
source=(prep/'system/FOwallClockTimeStatistics').read_text()
assert [v.strip() for v in re.findall(r'#\{(.*?)#\}',source,re.S)]==[v.strip() for v in re.findall(r'#\{(.*?)#\}',control,re.S)]
iters={}
for field,count in re.findall(r'Solving for (\w+),.*?No Iterations (\d+)',t):
    iters.setdefault(field,{}).setdefault(count,0);iters[field][count]+=1
assert iters=={'Ux':{'15':40},'Uy':{'15':40},'Uz':{'15':40},'p':{'12':40},'omega':{'8':40},'k':{'8':40}}
placement=(s/'rank-placement.log').read_text();ranks=sorted(int(v) for v in re.findall(r'rank=(\d+)\s+host=',placement));assert ranks==list(range(128))
cpus=sorted(int(v) for v in re.findall(r'Cpus_allowed_list:\s*(\d+)\s*$',placement,re.M))
env=(s/'environment.log').read_text();assert 'AMD EPYC 7713' in env and 'NUMA node(s):        8' in env
out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),job='25905114.pbs101',state='ONE_NODE_CPU_BASELINE_PASS',node=j['exec_host'].split('/')[0],ranks=128,nodes=1,method='hierarchical',factors=[16,4,2],steps=40,measured_steps=39,average_seconds_step=avg,median_seconds_step=statistics.median(dt),p95_seconds_step=statistics.quantiles(dt,n=100,method='inclusive')[94],min_seconds_step=min(dt),max_seconds_step=max(dt),final_Cd_dimensionless=cd[-1][1],stages=rows,elapsed_seconds=728,estimated_base_SU=128*728/3600,posted_job_charge='Not individually reported',max_rss_KiB_reported=127675796,max_rss_GiB=127675796/1024**2,total_CPU_time='25:01:24',aggregate_CPU_time_over_allocated_wall_fraction=(25*3600+84)/(128*728),cpu_affinity_single_cpu_values=cpus,rank_ids_seen=ranks,placement_limit='Rank and mask lines are interleaved; union masks and rank set do not reconstruct a reliable per-rank mapping. Probe is separate from solver, not runtime drift telemetry.',iteration_counts=iters,omega_bounding_messages=t.count('bounding omega'),timing_confidence_warning='smaller than the calculated one' in t,score_scope='One-node/40-step CPU baseline, not the four-node/150-step scored result',limitations='No matched candidate or repeated speedup yet. Aggregate cput and RSS do not identify a bandwidth, cache, MPI or NUMA bottleneck; hardware counters/page placement/power not collected. GNU time wraps PALS launcher and its 0% CPU is not solver inactivity.')
(r/'review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['cpu_affinity_single_cpu_values','rank_ids_seen']},indent=2))
