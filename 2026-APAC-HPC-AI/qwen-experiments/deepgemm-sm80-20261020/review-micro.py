"""Review a sealed eight-rank kernel screen, excluding its unranked preflight."""
from pathlib import Path
import csv, gzip, hashlib, json, math, statistics, sys

O = Path(__file__).resolve().parent
collection = json.loads(Path(sys.argv[1]).read_text())
assert collection['terminal'] and collection['payload_hashes_passed']
assert collection['exit_status'] == 0, 'Setup/runtime failure is not an accepted screen'
snapshot = Path(collection['destination'])
seal = json.loads((snapshot/'evidence-sha256.json').read_text())
for name, digest in seal.items():
    assert hashlib.sha256((snapshot/name).read_bytes()).hexdigest() == digest
run = snapshot/'runs'/collection['job']
config_bytes = (run/'submitted/config.json').read_bytes()
config = json.loads(config_bytes)
config_sha = hashlib.sha256(config_bytes).hexdigest()
preflight = json.loads((run/'micro/preflight/rank-0.json').read_text())
assert preflight['completed'] and preflight['input_integrity_passed'] and len(preflight['cases']) == 4
assert preflight['config_sha256'] != config_sha
expected = {(shape['name'], m, backend)
            for shape in config['shapes'] for m in config['batch_tokens']
            for backend in config['backends']}
assert len(expected) == 20
cases = {}
rank_reviews = []
for rank in range(8):
    report = json.loads((run/f'micro/rank-{rank}.json').read_text())
    assert report['rank'] == rank and report['completed'] and report['input_integrity_passed'] and report['default_sms_restored']
    assert report['source_sha256'] == config['fp8_utils_sha256']
    assert report['config_sha256'] == config_sha and not report['model_loaded']
    assert len(report['cases']) == 20
    observed = set()
    for c in report['cases']:
        key = (c['role_shape'], c['m'], c['backend'])
        assert c['configured_sms'] == int(c['backend'].split('_')[1])
        assert key not in observed and key in expected
        observed.add(key)
        shape = next(s for s in config['shapes'] if s['name'] == c['role_shape'])
        assert (c['n'],c['k']) == (shape['n'],shape['k'])
        assert math.isfinite(c['relative_rmse']) and 0 <= c['relative_rmse'] <= config['max_relative_rmse']
        assert math.isfinite(c['vs_deepgemm_relative_rmse']) and 0 <= c['vs_deepgemm_relative_rmse'] <= config['max_between_backend_relative_rmse']
        assert len(c['samples_us']) == config['samples'] == 9
        assert all(math.isfinite(x) and x>0 for x in c['samples_us'])
        assert math.isclose(c['median_us'], statistics.median(c['samples_us']), rel_tol=1e-10)
        cases[(rank,)+key] = c
    assert observed == expected
    rank_reviews.append(dict(rank=rank,cases=20,completed=True,input_integrity=True))
with (run/'micro/gpu-before.csv').open() as f:
    gpu_rows = [{k.strip():v.strip() for k,v in row.items()} for row in csv.DictReader(f)]
assert {int(row['index']) for row in gpu_rows} == set(range(8))
assert len({row['uuid'] for row in gpu_rows}) == 8
comparisons = []
for shape,m,backend in sorted(expected):
    if backend == 'sms_132': continue
    baseline = [cases[(rank,shape,m,'sms_132')]['median_us'] for rank in range(8)]
    candidate = [cases[(rank,shape,m,backend)]['median_us'] for rank in range(8)]
    reductions = [100*(1-c/b) for b,c in zip(baseline,candidate)]
    comparisons.append(dict(shape=shape,m=m,backend=backend,deepgemm_median_us=statistics.median(baseline),
                            candidate_median_us=statistics.median(candidate),
                            median_paired_latency_reduction_pct=statistics.median(reductions),
                            positive_ranks=sum(x>0 for x in reductions),
                            paired_reductions_pct=reductions))
traces = []
for p in sorted((run/'micro').glob('*.trace.json.gz')):
    with gzip.open(p,'rt') as f: trace = json.load(f)
    totals = {}
    for event in trace['traceEvents']:
        if event.get('cat') == 'kernel' and event.get('ph') == 'X':
            totals[event['name']] = totals.get(event['name'],0)+event['dur']
    assert totals, 'A requested trace must contain GPU kernel events'
    requested = int(p.name.split('sms_')[1].split('.')[0])
    assert any('sm90_fp8_gemm' in name and ', '+str(requested)+'u, (deep_gemm::GemmType)' in name for name in totals), 'Native SM parameter must match requested scheduler setting'
    traces.append(dict(file=p.name,kernel_duration_sum_us=sum(totals.values()),
                       leading_kernels=sorted(totals.items(),key=lambda x:-x[1])[:8]))
assert len(traces) == 4
result = dict(job=collection['job'],state='ISOLATED_KERNEL_NUMERICAL_TIMING_PASS',
              rank_reviews=rank_reviews,full_cases=160,unranked_preflight_cases=4,
              gpu_uuid_mapping_verified=True,comparisons=comparisons,traces=traces,
              model_loaded=False,accuracy_verified=False,
              limits='Synthetic TP8 decode projection helpers only; eight hardware repetitions are not independent model jobs. Kernel times are not serving goodput or official accuracy. No end-to-end extrapolation.')
decisions={}
for backend in ['sms_80']:
    points=[c for c in comparisons if c['backend']==backend and c['m'] in [48,54,60,64]]
    diagnostic=[c for c in comparisons if c['backend']==backend and c['m']==32]
    assert len(points)==8 and len(diagnostic)==2
    decisions[backend]=all(c['median_paired_latency_reduction_pct']>=5 and c['positive_ranks']>=6 for c in points) and all(c['median_paired_latency_reduction_pct']>=-5 for c in diagnostic)
result['candidate_eligible_for_model_planning']=decisions
result['limitations_added']='Native scheduler budget only. Compilation is warmed before timing. Micro gains omit potential model integration CPU overhead and do not justify changing global serving state without inspecting other callers.'
out = O/(collection['job']+'-review.json')
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(job=collection['job'],state=result['state'],full_cases=160,traces=len(traces),review=str(out)),indent=2))
