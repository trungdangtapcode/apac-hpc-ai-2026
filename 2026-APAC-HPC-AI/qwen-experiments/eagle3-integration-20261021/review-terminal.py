"""Review the failed real reference, including retained telemetry and limits."""
from pathlib import Path
import collections,hashlib,json,re
O=Path(__file__).resolve().parent;r=json.loads((O/'collection.json').read_text());D=Path(r['destination']);run=D/'runs'/r['job'];seal=json.loads((D/'evidence-sha256.json').read_text())
def read(p):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==seal[str(p.relative_to(D))]
    return p.read_text(errors='replace')
roles={};uuids=set()
for p in (run/'resource-telemetry').glob('*.jsonl'):
    rows=[json.loads(line) for line in read(p).splitlines()];meta=rows[0];samples=[x for x in rows if x['kind']=='sample']
    ids={g['uuid'] for x in samples for g in x.get('gpus',[])}
    assert not ids & uuids;uuids|=ids
    gauges=collections.defaultdict(list)
    for x in samples:
        for line in x.get('server_metrics',[]):
            key,value=line.rsplit(' ',1)
            if any(t in key for t in ['num_running_reqs','num_queue_reqs','token_usage']):gauges[key].append(float(value))
    roles[meta['role']]=dict(host=meta['host'],samples=len(samples),gpu_uuids=sorted(ids),
        gpu_status_counts=dict(collections.Counter(x.get('gpu_status','MISSING') for x in samples)),
        server_status_counts=dict(collections.Counter(str(x.get('server_http_status',x.get('server_metrics_status','MISSING'))) for x in samples)),
        sampled_max_vram_mib=max((float(g['memory.used']) for x in samples for g in x.get('gpus',[]) if g.get('memory.used','').replace('.','',1).isdigit()),default=None),
        startup_gauges={k:dict(samples=len(v),minimum=min(v),maximum=max(v),last=v[-1]) for k,v in gauges.items()})
locality=json.loads(read(run/'worker-locality-request.log'))
logs={p.name:read(p) for p in run.glob('task-*.log')}
client=read(run/'token-control.log')
account=read(D/'pbs-accounting.txt');h,m,s=map(int,re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)',account).groups());seconds=3600*h+60*m+s
out=dict(job=r['job'],terminal_exit_status=r['exit_status'],token_reference_passed=False,
         failure='BatchEncoding retained as input_ids is not JSON serializable; diagnostic requests/result serialization fail',
         task_status_limit='Client traceback with PBS exit zero; require actual result artifact gates, never scheduler exit alone',
         allocated_walltime_seconds=seconds,estimated_charge_su=16*128*seconds/3600,
         hardware_role_samples=roles,unique_gpu_uuids=len(uuids),locality=locality,
         pd_warmup_observations=[line for name,text in logs.items() for line in text.splitlines() if 'ALL 2 P/D paths initialized' in line or re.search(r'prefill-\d/decode-\d OK',line)],
         limitations=['No scored phase, token diagnostic result, latency/error fraction or greedy reference exists.',
                      'Samples cover startup/warmup/client failure, not steady benchmark utilization.',
                      'Node CPU/network are shared and not used to infer role saturation; scored per-thread CPU demand and memory placement remain uncollected.',
                      'Hardware time series and available server gauges inspected; no heavy profiles requested.',
                      'Native profile-stop HTTP issue is not retested by this unprofiled diagnostic.'])
assert 'BatchEncoding is not JSON serializable' in client
assert locality['all_roles_mapping_complete'] and len(uuids)==16
(O/'terminal-inspection.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(job=r['job'],walltime_seconds=seconds,estimated_su=out['estimated_charge_su'],roles={k:v['samples'] for k,v in roles.items()},unique_uuids=len(uuids))))
