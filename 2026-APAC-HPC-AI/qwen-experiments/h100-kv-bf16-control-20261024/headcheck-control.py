"""Independently reject incomplete short-policy load, warmup and quality evidence."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def normalize_input_config(config):
    value = json.loads(json.dumps(config))
    assert len(value['endpoint']['urls']) == 1
    value['endpoint']['urls'] = ['DYNAMIC_ALLOCATED_ROUTER']
    value['artifacts']['dir'] = 'DYNAMIC_ARTIFACT_DIRECTORY'
    return value


def validate(art):
    art = Path(art)
    config = json.loads((HERE / 'config.json').read_text())
    assert json.loads((art / 'config.json').read_text()) == config, 'actual config differs'
    expected_kv = config['kv_dtype']
    kv_proofs = []
    spec = importlib.util.spec_from_file_location('capacity_parser', HERE / 'audit-capacity.py')
    parser = importlib.util.module_from_spec(spec); spec.loader.exec_module(parser)
    for role, tp, ep in [('prefill-0',4,1),('prefill-1',4,1),('decode-0',8,8)]:
        r = subprocess.run([sys.executable,str(HERE/'check-kv-ranks.py'),str(art/(role+'.log')),role,'--expected',expected_kv],capture_output=True,text=True)
        assert r.returncode == 0, r.stderr
        lines = [x for x in (art/(role+'.log')).read_text(errors='replace').splitlines() if 'server_args=ServerArgs(' in x]
        assert lines, 'Missing resolved server arguments'
        for line in lines:
            values = {k:parser._value_for(line,k) for k in ['dtype','kv_cache_dtype','tp_size','ep_size','moe_runner_backend']}
            assert values == dict(dtype='bfloat16',kv_cache_dtype='auto',tp_size=tp,ep_size=ep,moe_runner_backend='hpc_ops'), values
        kv_proofs.append({'role':role,'rank_count':tp,'logical_cache_dtype':'torch.bfloat16','resolved_args':values})
    forbidden = ['deferred-ns.txt', 'stop-increase-n.txt', 'output-smoke-failed.txt',
        'output-smoke-deferred.txt', 'long-context-check-failed.txt', 'long-context-check-deferred.txt']
    assert not any((art / name).exists() for name in forbidden), 'missing/failed measurement or quality gate'
    exports = list(art.glob('confirm/n54/artifacts/profile_export_aiperf.json'))
    assert len(exports) == 1, 'one short N64 export required'
    export = json.loads(exports[0].read_text())
    expected_input = json.loads((HERE / 'expected-input-config.json').read_text())
    assert normalize_input_config(export['input_config']) == expected_input, 'actual AIPerf workload/protocol differs'
    goodput = export['goodput']['avg']
    fraction = export['good_request_fraction']['avg']
    count = export['request_count']['avg']
    assert math.isfinite(goodput) and goodput > 0 and 0.9 <= fraction <= 1 and count > 0
    log = (art / 'confirm/n54/client.log').read_text(errors='replace')
    matches = re.findall(r'Phase profiling \(profiling\) complete \| completed=([\d,]+), cancelled=([\d,]+), errors=([\d,]+)', log)
    assert len(matches) == 1, 'complete profiling error/cancellation receipt required'
    completed, cancelled, errors = [int(x.replace(',', '')) for x in matches[0]]
    assert completed == count and cancelled == errors == 0, 'profiling requests failed or counts differ'
    raw_count = 0
    raw_good = 0
    for line in (exports[0].parent / 'profile_export.jsonl').open():
        row = json.loads(line)
        if row['metadata']['benchmark_phase'] != 'profiling':
            continue
        metrics = row['metrics']
        ttft, itl = metrics['time_to_first_token'], metrics['inter_token_latency']
        assert ttft['unit'] == itl['unit'] == 'ms'
        assert all(math.isfinite(x['value']) and x['value'] >= 0 for x in (ttft, itl))
        raw_count += 1
        raw_good += int(ttft['value'] <= 3000 and itl['value'] <= 20)
    assert raw_count == count and math.isclose(raw_good / raw_count, fraction, abs_tol=1e-9), 'raw SLA fraction/count differs'
    smoke = json.loads((art / 'output-smoke.json').read_text())
    reference = json.loads((HERE / 'reference-output-smoke.json').read_text())
    expected = {row['name']: row for row in reference['cases']}
    rows = smoke['cases']
    assert len(rows) == len(expected) == 8 and {row['name'] for row in rows} == set(expected)
    regressions = []
    for row in rows:
        baseline = expected[row['name']]
        assert row['prompt'] == baseline['prompt'] and row['expected'] == baseline['expected']
        assert 'error' not in row, 'smoke request error'
        text = row['response']['choices'][0]['message']['content']
        assert text == row['text']
        stripped = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip(), flags=re.I).strip()
        if isinstance(row['expected'], (dict, list)):
            try:
                passed = json.loads(stripped) == row['expected']
            except ValueError:
                passed = False
        else:
            passed = stripped.strip('"\'` .\n').lower() == row['expected']
        assert row['passed'] is passed, 'smoke result contradicts raw response'
        if baseline['passed'] and not passed:
            regressions.append(row['name'])
    actual_smoke_passed = sum(bool(row['passed']) for row in rows)
    assert reference['passed'] == 7 and reference['total'] == 8, 'frozen known-smoke reference changed'
    assert actual_smoke_passed >= 7, 'the 7/8 known-smoke floor regressed'
    assert not regressions, 'new output regressions: ' + str(regressions)
    long = json.loads((art / 'long-context-check.json').read_text())
    assert long['total'] == long['passed'] == len(long['cases']) == 12 and long['errors'] == 0
    assert len({row['name'] for row in long['cases']}) == 12
    for row in long['cases']:
        index = int(row['name'].split('-')[1])
        assert 0 <= index < 12 and row['expected'] == str(73160429 + index * 137)
        assert 'error' not in row and row['passed'] is True
        text = row['response']['choices'][0]['message']['content']
        assert text == row['text'] and text.strip(' \t\n\r"\'`.') == row['expected']
    return dict(status='pass', scope='Fresh full-protocol H100 BF16 cache control',
        graph_policy='native baseline', concurrency=54, completed_requests=completed,
        request_errors=errors, cancellations=cancelled, good_request_fraction=fraction,
        good_output_tokens_s=goodput * 200, pair_receipts_not_independently_replayed=True, new_smoke_regressions=regressions,
        long_checks_passed=12, kv_dtype=expected_kv, kv_runtime_proofs=kv_proofs,
        backend_scale_status='uncalibrated default 1.0 inferred from source and checkpoint metadata; per-layer backend values are not logged',
        quality_status='UNKNOWN; exploratory unranked screen only',
        official_accuracy_verified=False, speedup_claim=False)


if __name__ == '__main__':
    try:
        result = validate(sys.argv[1])
    except Exception as error:
        result = dict(status='fail', error=str(error))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'pass' else 1)
