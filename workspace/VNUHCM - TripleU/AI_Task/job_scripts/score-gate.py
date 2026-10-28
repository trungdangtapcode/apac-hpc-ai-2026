"""Reject missing, incomplete or inconsistent AIPerf results after a replay.

This local performance gate does not certify organiser full-set accuracy.
"""
import json
import math
import re
import sys
from pathlib import Path
from artifact_paths import resolve_artifacts

root = Path(sys.argv[1])
n = int(sys.argv[2])
run = root / 'official' / ('n' + str(n))
art = run / 'artifacts'
try:
    export_path, requests_path = resolve_artifacts(art)
    export = json.loads(export_path.read_text())
    text = (run / 'client.log').read_text()
    log = art / 'logs/aiperf.log'
    if log.exists():
        text += '\n' + log.read_text()
    phases = re.findall(
        r'Phase profiling \(profiling\) complete \| completed=([\d,]+), cancelled=([\d,]+), errors=([\d,]+)', text)
    assert phases, 'Missing completed scored phase'
    completed, cancelled, errors = map(lambda x: int(x.replace(',', '')), phases[-1])
    assert completed > 0 and cancelled == errors == 0, 'Incomplete or failed requests'
    assert not export.get('was_cancelled') and not export.get('error_summary'), 'Export reports failure'
    count = good = bad = 0
    with requests_path.open() as stream:
        for line in stream:
            row = json.loads(line)
            meta = row['metadata']
            if meta.get('phase_kind', meta.get('benchmark_phase')) != 'profiling':
                continue
            count += 1
            failed = bool(meta.get('was_cancelled') or meta.get('context_overflow_skip')
                          or row.get('error') or row.get('errors'))
            bad += failed
            metrics = row.get('metrics', {})
            ttft = metrics.get('time_to_first_token', {}).get('value')
            itl = metrics.get('inter_token_latency', {}).get('value')
            assert failed or (isinstance(ttft, (float, int)) and math.isfinite(ttft)
                              and isinstance(itl, (float, int)) and math.isfinite(itl)), 'Missing latency'
            good += not failed and 0 <= ttft <= 3000 and 0 <= itl <= 20
    assert count == completed and bad == 0, 'Raw/export phase count mismatch or request failure'
    assert export['request_count']['avg'] == count
    assert export['good_request_count']['avg'] == good
    fraction = good / count
    assert fraction >= .90, 'Joint SLA below 90%'
    assert abs(export['good_request_fraction']['avg'] - fraction) < 1e-10
    goodput = export['goodput']['avg']
    assert math.isfinite(goodput) and goodput > 0
    result = dict(passed=True, concurrency=n, requests=count, good_requests=good,
                  errors=errors, cancelled=cancelled, good_request_fraction=fraction,
                  good_output_tokens_s=goodput * 200, score_source='exported goodput.avg * 200',
                  official_accuracy_verified=False)
except (OSError, ValueError, KeyError, AssertionError, TypeError) as error:
    result = dict(passed=False, reason=str(error), official_accuracy_verified=False)
print(json.dumps(result, indent=2))
sys.exit(0 if result['passed'] else 1)
