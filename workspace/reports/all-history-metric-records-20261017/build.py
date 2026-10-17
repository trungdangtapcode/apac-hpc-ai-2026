"""Find observed metric records without mixing short sweeps with full runs."""
import json
import runpy
from pathlib import Path
R = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
O = Path(__file__).resolve().parent
records = {}
counts = {}
for platform, files in [('H200', (R/'runs').glob('*/summary.json')), ('H100', (R/'nscc-pbs/collected').glob('*/*/derived-summary.json'))]:
    rows = []
    seen = set()
    for f in files:
        try:
            summary = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        if not isinstance(summary, list):
            continue
        for p in summary:
            if not isinstance(p, dict) or not p.get('sla_pass') or p.get('errors', 0) or p.get('cancelled_requests', 0):
                continue
            export = Path(p['export'])
            try:
                e = json.loads(export.read_text())
                phases = e['input_config']['phases']
                warmup = next(x for x in phases if x['kind'] == 'warmup')
                measure = next(x for x in phases if x['kind'] == 'profiling')
                if (warmup['duration'], measure['duration'], measure.get('grace_period')) != (60, 120, 30):
                    continue
                prompt = e['input_config']['datasets'][0]['prompts']
                if (prompt['isl']['mean'], prompt['osl']['mean']) != (4000, 200):
                    continue
            except (OSError, ValueError, KeyError, StopIteration):
                continue
            job = f.parent.name if platform == 'H200' else f.parents[1].name
            identity = (job, p['phase'], p['concurrency'])
            if identity in seen:
                continue
            seen.add(identity)
            row = dict(p, job=job, source=str(f), export=str(export))
            rows.append(row)
    counts[platform] = len(rows)
    records[platform] = {}
    for metric, maximize in [('good_output_tokens_s', True), ('ttft_avg_ms', False), ('itl_avg_ms', False), ('good_request_fraction', True)]:
        ranked = sorted(rows, key=lambda x: x[metric], reverse=maximize)
        best = ranked[0][metric]
        records[platform][metric] = dict(value=best, ties=[x for x in ranked if x[metric] == best])
(O/'records.json').write_text(json.dumps(dict(scope='Full 60/120/30 protocol, 4000/200 tokens, reported SLA pass and zero errors/cancellations. Observed historical records, not a fresh runtime/quality audit of every old job.', counts=counts, records=records), indent=2)+'\n')
labels = {
    'good_output_tokens_s': ('Good output throughput ↑', 'good tokens/s', 1),
    'ttft_avg_ms': ('Mean TTFT ↓', 'ms', 1),
    'itl_avg_ms': ('Mean ITL ↓', 'ms/token interval', 1),
    'good_request_fraction': ('Joint SLA pass rate ↑', '%', 100),
}
lines = ['| Platform | Metric | Best observed value | Unit | Job ID | N |',
         '|---|---|---:|---|---|---:|']
for platform, metrics in records.items():
    for metric, record in metrics.items():
        row = record['ties'][0]
        label, unit, scale = labels[metric]
        tie_note = ' ({} tied observations)'.format(len(record['ties'])) if len(record['ties']) > 1 else ''
        lines.append('| {} | {} | {:.3f} | {} | {}{} | {} |'.format(
            platform, label, record['value'] * scale, unit, row['job'], tie_note, row['concurrency']))
template = (O/'REPORT.template.md').read_text()
assert template.count('{{RECORD_TABLE}}') == 1
render_details = runpy.run_path(str(O/'run_details.py'))['render']
report = template.replace('{{RECORD_TABLE}}', '\n'.join(lines)).replace('{{JOB_DETAILS}}', render_details(records))
(O/'REPORT.md').write_text(report)
print('Updated REPORT.md with explicit units, definitions, examples and evidence limits.')
