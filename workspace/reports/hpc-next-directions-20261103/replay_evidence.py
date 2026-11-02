"""Recompute retained endpoint-counter evidence; never infer solver-time attribution."""
from pathlib import Path
import hashlib,json,re,statistics
R=Path(__file__).resolve().parents[3]/'2026-APAC-HPC-AI/hpc-experiments'
# The active source tree and archive both preserve this home-relative layout.
if not R.is_dir():
    raise RuntimeError('Place this report alongside the captured 2026-APAC-HPC-AI tree')
rows=[];pins={}
def read(p):
    raw=p.read_bytes();pins[str(p.relative_to(R))]=hashlib.sha256(raw).hexdigest();return raw.decode()
def counters(text):
    return {s.split()[0].rstrip(':'):int(s.split()[1]) for s in text.splitlines() if len(s.split())>=2 and s.split()[1].isdigit()}
for name,job in [('iris-own-zyx40-20261102','2294640'),('iris-xzy40-20261102','2294643'),('iris-xzy52-reverse-20261102','2294644')]:
    p=R/name/('completed-'+job);review=json.loads(read(p/'REVIEW.json'));assert review['passed']
    for arm in review['arms']:
        d=p/'collected/runs'/job/'arms'/arm['arm'];before=json.loads(read(d/'solver-before-node-snapshot.json'));after=json.loads(read(d/'solver-after-node-snapshot.json'))
        vm=[counters(x['vmstat']) for x in (before,after)];mem=[counters(x['meminfo']) for x in (before,after)];resource=read(d/'resource-time.log')
        def value(label):
            match=re.search(r'^\s*'+re.escape(label)+r':\s*(\S+)',resource,re.M);return float(match[1]) if match else None
        row={'job_id':job,'arm':arm['arm'],'mean_s_step':arm['mean_s_step'],'node_delta':{k:vm[1][k]-vm[0][k] for k in ['pgmajfault','numa_miss','pswpin','pswpout'] if all(k in v for v in vm)},'MemAvailable_GiB_endpoints':[v['MemAvailable']/1024**2 for v in mem],'SwapTotal_kB_endpoints':[v['SwapTotal'] for v in mem],'memory_PSI_collected':all('pressure/memory' in v for v in (before,after)),'GNU_major_faults':value('Major (requiring I/O) page faults'),'GNU_filesystem_inputs_raw':value('File system inputs'),'GNU_user_seconds':value('User time (seconds)'),'GNU_system_seconds':value('System time (seconds)'),'snapshot_MHz_medians':[statistics.median(float(x) for x in re.findall(r'^cpu MHz\s*:\s*([\d.]+)',v['cpuinfo'],re.M)) for v in (before,after)]}
        rows.append(row)
output={'scope':'Whole-node before/after snapshots and process-tree resource counters; no within-solver time series, attribution or causal claim. Raw GNU input counts are not labeled bytes.','rows':rows,'source_sha256':pins}
(Path(__file__).parent/'EVIDENCE.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({'replayed_arms':len(rows),'hashed_sources':len(pins),'memory_PSI_available_arms':sum(r['memory_PSI_collected'] for r in rows)}))
