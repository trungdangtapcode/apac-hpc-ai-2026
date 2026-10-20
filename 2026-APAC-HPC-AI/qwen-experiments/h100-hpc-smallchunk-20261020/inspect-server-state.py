"""Summarise sealed, phase-bounded server gauges without merging metric labels."""
from pathlib import Path
import collections, hashlib, importlib.util, json, math

O = Path(__file__).resolve().parent
R = O.parent
spec = importlib.util.spec_from_file_location('resources', R/'resource-telemetry-20261020/inspect-resources.py')
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
for receipt in json.loads((O/'pbs-receipts.json').read_text()):
    number = receipt['job'].split('.')[0]
    collection = O/('collect-'+number+'.json')
    if not collection.exists():
        continue
    snapshot = Path(json.loads(collection.read_text())['destination'])
    run = snapshot/'runs'/receipt['job']
    seal = json.loads((snapshot/'evidence-sha256.json').read_text())
    def read(path):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == seal[str(path.relative_to(snapshot))]
        return path.read_text()
    manifest = json.loads(read(run/'confirm/n54/artifacts/phase_manifest.json'))
    phases = [p for p in manifest['phases'] if p['phase_kind']=='profiling']
    assert len(phases)==1
    start,end = phases[0]['start_ns'],phases[0]['end_ns']
    roles = {}
    for path in sorted((run/'resource-telemetry').glob('*.jsonl')):
        rows = [json.loads(line) for line in read(path).splitlines()]
        meta = rows[0]
        samples = [x for x in rows if x['kind']=='sample' and start<=x['utc_ns']<=end]
        assert len(samples)>=20
        series = collections.defaultdict(list)
        for sample in samples:
            assert sample['server_http_status']==200
            for line in sample['server_metrics']:
                identity,raw = line.rsplit(' ',1)
                value = float(raw)
                assert math.isfinite(value)
                series[identity].append((sample['utc_ns'],value))
        gauges,counters = {},{}
        for identity,values in series.items():
            name = identity.split('{')[0]
            if name.endswith(('_sum','_count','_total')):
                counters[identity] = dict(samples=len(values),first=values[0][1],last=values[-1][1],
                                          change_between_samples=values[-1][1]-values[0][1])
            else:
                gauges[identity] = metrics.distribution([v for t,v in values])
        roles[meta['role']] = dict(host=meta['host'],scored_samples=len(samples),
            gauges=gauges,counter_intervals=counters,
            inflight_state='NOT_COLLECTED: current sampler whitelist does not include an inflight gauge')
    result = dict(job=receipt['job'],phase=phases[0],roles=roles,
        limitations=['Epoch phase alignment assumes host clocks agree; skew is not independently calibrated.',
                     'Five-second gauge samples can miss short queue/inflight transitions.',
                     'Keep full labels separate; gauges are not summed across ranks or roles.',
                     'Counter changes between interior samples omit both phase edges and are not contest request counts.',
                     'Token occupancy, sampled VRAM and GPU activity describe different quantities.'])
    out = O/(receipt['job']+'-server-state.json')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(receipt['job'],{role:len(x['gauges']) for role,x in roles.items()})
