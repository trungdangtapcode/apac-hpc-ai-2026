"""Inspect retained organiser solver/partition evidence, never label it our run."""
import csv,hashlib,json,math,re,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'upstream-20261021/sources'
OUT=ROOT/'reference-analysis-20261021'
NUM=r'[-+\d.eE]+'
def extract(pattern,text,convert=float,required=True):
    m=re.search(pattern,text,re.M)
    if not m:
        if required:raise ValueError('Missing field: '+pattern)
        return None
    return convert(m[1])
def quantile(values,q):
    vals=sorted(values);index=(len(vals)-1)*q;lower=int(index);upper=min(lower+1,len(vals)-1)
    return vals[lower]+(vals[upper]-vals[lower])*(index-lower)
def parse_solver(path):
    text=path.read_text();steps=[int(x) for x in re.findall(r'^Time = (\d+)\s*$',text,re.M)]
    assert steps and steps==list(range(1,steps[-1]+1)), 'Incomplete or repeated solver steps'
    assert re.search(r'^End\s*$',text,re.M),'Missing solver completion'
    average=extract(r'Average wall-clock time per time step\s*=\s*('+NUM+')',text)
    count=extract(r'Number of measured time steps\s*=\s*(\d+)',text,int)
    values=[float(x) for x in re.findall(r'Wall-clock time elapsed during the current time step = ('+NUM+r') s',text)]
    assert count==len(values)==steps[-1]-1
    assert all(math.isfinite(v) and v>0 for v in values)
    assert abs(statistics.mean(values)-average)<1e-10
    return dict(average_s_step=average,steps=steps[-1],measured_steps=count,
                step_p50_s=statistics.median(values),step_p95_s=quantile(values,.95),step_max_s=max(values),
                first_20_measured_steps_s=statistics.mean(values[:20]),
                ranks=extract(r'^nProcs\s*:\s*(\d+)',text,int),
                ieee_double='scalar=64' in text,solver_end=True,signal7='signal 7' in text,
                unexpected_fatal='FOAM FATAL' in text or bool(re.search(r'Floating point exception \(core dumped\)|died from signal 8', text)))
def parse_cd(path,steps):
    lines=path.read_text().splitlines();header=next(x for x in lines if x.startswith('# Time'))
    columns=header.lstrip('#').split();index=columns.index('Cd')
    rows=[x.split() for x in lines if x.strip() and not x.startswith('#')]
    assert len(rows)==steps and [float(r[0]) for r in rows]==list(range(1,steps+1))
    cd=float(rows[-1][index]);assert math.isfinite(cd)
    return cd
def parse_partition(path,ranks):
    text=path.read_text();parts={};edges={}
    for rank,body in re.findall(r'^Processor (\d+)\s*\n(.*?)(?=^Processor \d+\s*$|\Z)',text,re.M|re.S):
        rank=int(rank)
        cells=extract(r'^\s+Number of cells = (\d+)',body,int,False)
        if cells is None:continue
        assert rank not in parts
        parts[rank]=dict(cells=cells,faces=extract(r'^\s+Number of processor faces = (\d+)',body,int),
                        patches=extract(r'^\s+Number of processor patches = (\d+)',body,int))
        for peer,faces in re.findall(r'Number of faces shared with processor (\d+) = (\d+)',body):edges[rank,int(peer)]=int(faces)
    assert set(parts)==set(range(ranks))
    assert sum(r['cells'] for r in parts.values())==65334765
    assert all(edges.get((b,a))==n for (a,b),n in edges.items()),'Nonreciprocal partition interface'
    faces=extract(r'^Number of processor faces = (\d+)',text,int)
    assert sum(edges.values())==2*faces
    mean_cells=65334765/ranks
    return dict(cells_total=65334765,cell_max_above_mean_pct=(max(r['cells'] for r in parts.values())/mean_cells-1)*100,
                unique_partition_faces=faces,max_processor_faces=max(r['faces'] for r in parts.values()),
                max_processor_neighbors=max(r['patches'] for r in parts.values()),
                mean_processor_neighbors=statistics.mean(r['patches'] for r in parts.values()),
                network_cut_faces=None,network_cut_reason='Actual rank-to-host map not supplied; global rank interfaces do not prove cross-node traffic.')
rows=[]
for prefix,platform in [('4.2-gadi-logs','Gadi normalsr'),('4.3-aspire2a-logs','ASPIRE-2A CPU')]:
    for folder in sorted((SOURCE/prefix).iterdir()):
        logs=list(folder.glob('50_simpleFoam*.log'))
        if not logs:continue
        assert len(logs)==1
        row=parse_solver(logs[0]);row.update(platform=platform,reference=folder.name,
                source_log=str(logs[0].relative_to(ROOT)),source_sha256=hashlib.sha256(logs[0].read_bytes()).hexdigest(),
                cd=parse_cd(folder/'coefficient.dat',row['steps']),cd_sha256=hashlib.sha256((folder/'coefficient.dat').read_bytes()).hexdigest(),
                source_owner='organisers',our_measurement=False,official_protocol_steps=row['steps']=={1:40,2:80,4:150}[row['ranks']//(104 if prefix=='4.2-gadi-logs' else 128)])
        decomp=folder/'10_decomposePar.log'
        if decomp.exists():row['partition']=parse_partition(decomp,row['ranks'])
        assert row['official_protocol_steps'] and row['ieee_double'] and not row['unexpected_fatal']
        rows.append(row)
OUT.mkdir(exist_ok=True)
(OUT/'reference-results.json').write_text(json.dumps(rows,indent=2)+'\n')
columns=['platform','reference','ranks','steps','average_s_step','cd','step_p95_s','step_max_s','signal7','source_log']
with (OUT/'reference-results.csv').open('w') as stream:
    writer=csv.DictWriter(stream,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
lines=['# Recomputed public reference observations','',
       'These are organiser measurements, not our jobs. Reported Average matches all per-step samples; the first solver step is excluded by the case timer. Columns have seconds/step, seconds and dimensionless Cd units.','',
       '| Platform | Reference | Ranks | Steps | Average (s/step) | Cd | Max step (s) | Signal 7 in solver log |',
       '|---|---|---:|---:|---:|---:|---:|---|']
for r in rows:lines.append('| {} | {} | {} | {} | {:.6f} | {:.9f} | {:.3f} | {} |'.format(r['platform'],r['reference'],r['ranks'],r['steps'],r['average_s_step'],r['cd'],r['step_max_s'],'yes, after End' if r['signal7'] else 'not found'))
lines+=['','## Partition evidence on four-node full chains','',
        '| Platform | Reference | Maximum cells above mean (%) | Unique partition faces | Maximum neighbor count | Maximum processor faces |',
        '|---|---|---:|---:|---:|---:|']
for r in rows:
    p=r.get('partition')
    if p and r['steps']==150:lines.append('| {} | {} | {:.3f} | {} | {} | {} |'.format(r['platform'],r['reference'],p['cell_max_above_mean_pct'],p['unique_partition_faces'],p['max_processor_neighbors'],p['max_processor_faces']))
lines+=['','All raw partition interfaces are reciprocal and their face sum matches the reported unique interface count. Rank-to-node mapping is not independently available, so these counts are not measured network traffic.','',
        'A completed solver with a teardown signal is retained as such, not relabelled as a clean end-to-end job. Future runs should use the documented MPI remedy, check every exit code and inspect semantic artifacts. Do not ignore arbitrary errors because End appears.','']
(OUT/'RESULTS.md').write_text('\n'.join(lines))
# Validate known public results and a failure-sensitive parser, rather than mirroring implementation.
expected={('ASPIRE-2A CPU','scotch-4node'):3.575991440657719,('Gadi normalsr','scotch-4node'):2.126}
for key,value in expected.items():assert abs(next(r['average_s_step'] for r in rows if (r['platform'],r['reference'])==key)-value)<.00051
(OUT/'validation.json').write_text(json.dumps(dict(passed=True,parsed_reference_runs=len(rows),all_measured_step_means_agree=True,all_present_partition_faces_and_cell_totals_checked=True,source='pinned organiser logs',gpu_or_cpu_jobs_submitted=0),indent=2)+'\n')
print(json.dumps(dict(reference_runs=len(rows),output=str(OUT))))
