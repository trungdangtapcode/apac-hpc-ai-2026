"""Offline evidence review of a collect-run.py snapshot; never submits jobs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re


def read(path):
    return json.loads(path.read_text())


def metric(data, name):
    value = data.get(name, {}).get('avg')
    return value if isinstance(value, (float, int)) and math.isfinite(value) else None


def smoke_review(candidate, reference):
    """Require the unchanged suite and no new failures against H100 baseline."""
    if not candidate or not reference:
        return False
    cases, baseline = candidate.get('cases', []), reference.get('cases', [])
    if len(cases) != 8 or len(baseline) != 8:
        return False
    refs = {c['name']: c for c in baseline}
    if len(refs) != 8 or len({c['name'] for c in cases}) != 8:
        return False
    if [c['name'] for c in baseline if c.get('passed') is False] != ['reverse']:
        return False
    for suite in (candidate, reference):
        if suite.get('total') != 8 or suite.get('passed') != sum(c.get('passed') is True for c in suite['cases']):
            return False
        if any(type(c.get('passed')) is not bool or 'error' in c or not isinstance(c.get('text'), str) for c in suite['cases']):
            return False
    for case in cases:
        ref = refs.get(case['name'])
        if not ref or any(case.get(k) != ref.get(k) for k in ('prompt', 'expected')):
            return False
        if ref['passed'] and not case['passed']:
            return False
    return True


def review(snapshot, baseline):
    sealed = read(snapshot / 'evidence-sha256.json')
    mismatches = []
    for relative, expected in sealed.items():
        path = (snapshot / relative).resolve()
        if not path.is_relative_to(snapshot.resolve()) or not path.is_file():
            mismatches.append(relative)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            mismatches.append(relative)
    record = read(snapshot / 'review.json')
    job = record['job']
    if not re.fullmatch(r'\d+\.pbs\d+', job):
        raise ValueError('Unexpected PBS job ID')
    run = snapshot / 'runs' / job
    rows = []
    required = {'review.json', 'pbs-accounting.txt', 'payload-checksums.txt'}
    for export in sorted(run.glob('confirm/n*/artifacts/profile_export_aiperf.json')):
        n = int(export.parents[1].name[1:])
        data = read(export)
        config = data['input_config']
        phases = config.get('phases', [])
        warm = [p for p in phases if p.get('kind') == 'warmup']
        prof = [p for p in phases if p.get('kind') == 'profiling']
        datasets = config.get('datasets', [])
        dataset = datasets[0] if len(datasets) == 1 else {}
        endpoint = config.get('endpoint', {})
        protocol = (
            len(phases) == 2 and len(warm) == len(prof) == 1
            and warm[0].get('duration') == 60 and warm[0].get('concurrency') == n
            and warm[0].get('exclude_from_results') is True
            and prof[0].get('duration') == 120 and prof[0].get('grace_period') == 30
            and prof[0].get('concurrency') == n
            and dataset.get('type') == 'synthetic' and dataset.get('entries') == 12800
            and dataset.get('random_seed') == 2026
            and dataset.get('prompts') == {'isl': {'mean': 4000.0, 'stddev': 0.0},
                                         'osl': {'mean': 200.0, 'stddev': 0.0},
                                         'cache_bust': {'target': 'first_turn_prefix'}}
            and config.get('slos') == {'time_to_first_token': 3000.0, 'inter_token_latency': 20.0}
            and endpoint.get('streaming') is True
            and endpoint.get('extra') == {'min_tokens': 200, 'max_tokens': 200,
                                         'ignore_eos': True, 'temperature': 0.0, 'repetition_penalty': 1.0}
            and data.get('was_cancelled') is False)
        manifest = export.parent / 'phase_manifest.json'
        manifest_rows = read(manifest).get('phases', []) if manifest.exists() else []
        phase_complete = (len(manifest_rows) == 2
                          and {p.get('phase_kind') for p in manifest_rows} == {'warmup', 'profiling'}
                          and all(p.get('was_cancelled') is False and p.get('total_request_count', 0) > 0
                                  and p.get('error_request_count') == 0
                                  and p.get('end_ns', 0) - p.get('start_ns', 0)
                                  >= {'warmup': 60, 'profiling': 120}.get(p.get('phase_kind'), float('inf')) * 1e9
                                  for p in manifest_rows)
                          and all(p.get('total_request_count') == metric(data, 'request_count')
                                  for p in manifest_rows if p.get('phase_kind') == 'profiling'))
        log = export.parent / 'logs/aiperf.log'
        client = export.parents[1] / 'client.log'
        text = '\n'.join(p.read_text(errors='replace') for p in (log, client) if p.exists())
        counts = re.search(r'Phase profiling \(profiling\) complete \| completed=([\d,]+), cancelled=([\d,]+), errors=([\d,]+)', text)
        fraction = metric(data, 'good_request_fraction')
        if fraction is None:
            good, requests, errors = (metric(data, k) for k in ('good_request_count', 'request_count', 'error_request_count'))
            if None not in (good, requests, errors) and requests + errors > 0:
                fraction = good / (requests + errors)
        goodput = metric(data, 'goodput')
        # AIPerf omits this metric on successful runs. Do not assume missing
        # means zero: require the explicit empty error summary plus the
        # independent phase manifest and completed-phase log checked below.
        error_metric_ok = (metric(data, 'error_request_count') == 0
                           or ('error_request_count' not in data and data.get('error_summary') == []))
        passed = bool(protocol and phase_complete and counts
                      and int(counts[1].replace(',', '')) == metric(data, 'request_count')
                      and int(counts[2].replace(',', '')) == int(counts[3].replace(',', '')) == 0
                      and error_metric_ok
                      and fraction is not None and 0.90 <= fraction <= 1.0
                      and goodput is not None and goodput > 0)
        required.update(str(p.relative_to(snapshot)) for p in (export, manifest, log, client) if p.exists())
        rows.append({'concurrency': n, 'protocol_pass': bool(protocol), 'phase_complete': bool(phase_complete),
                     'latency_error_gate_pass': passed, 'sla_fraction': fraction,
                     'good_output_tokens_s': goodput * 200 if goodput is not None else None,
                     'ttft_avg_ms': metric(data, 'time_to_first_token'),
                     'itl_avg_ms': metric(data, 'inter_token_latency')})
    smoke_path = run / 'output-smoke.json'
    if smoke_path.exists():
        required.add(str(smoke_path.relative_to(snapshot)))
    smoke_ok = smoke_review(read(smoke_path) if smoke_path.exists() else None, read(baseline))
    seal_ok = not mismatches and required.issubset(sealed)
    terminal = record.get('pbs_state') == 'F'  # Historical snapshot, never a fresh queue check.
    n32 = [r for r in rows if r['concurrency'] == 32]
    return {'reviewed_utc': datetime.now(timezone.utc).isoformat(), 'snapshot': str(snapshot), 'job': job,
            'baseline_smoke': str(baseline), 'baseline_smoke_sha256': hashlib.sha256(baseline.read_bytes()).hexdigest(),
            'seal_pass': seal_ok, 'seal_mismatches': mismatches, 'unsealed_required': sorted(required - sealed.keys()),
            'snapshot_terminal': terminal, 'exit_status': record.get('exit_status'), 'points': rows,
            'short_nonregression_vs_h100_baseline': smoke_ok,
            'n32_research_evidence_pass': bool(seal_ok and terminal and record.get('payload_checksums_pass') is True
                                             and len(n32) == 1 and n32[0]['latency_error_gate_pass'] and smoke_ok),
            'accuracy_verified': False, 'submission_authorized_by_this_report': False,
            'remaining_gates': 'Fresh own PBS queue, credit, budget reservation under lock, matching payload/runtime review; inspect nonzero exit and long-check failures/deferments before promotion.',
            'scope': 'Offline snapshot evidence only. Higher-load failures do not invalidate a complete passing N32. No new scheduler query, authentication or GPU execution.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--baseline-smoke', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = review(args.snapshot, args.baseline_smoke)
    with args.out.open('x') as output:
        json.dump(result, output, indent=2)
        output.write('\n')
    print(json.dumps({k: result[k] for k in ('job', 'seal_pass', 'n32_research_evidence_pass', 'accuracy_verified')}))


if __name__ == '__main__':
    main()
