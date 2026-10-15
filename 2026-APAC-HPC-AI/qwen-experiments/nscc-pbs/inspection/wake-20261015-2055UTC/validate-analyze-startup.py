"""Offline fixtures and preserved own-child samples; no compute or GPU execution."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('analysis', ROOT / 'analyze-startup.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
meta = {'kind': 'metadata', 'clock_ticks': 100, 'interval_s': 15,
        'job': 'SYNTHETIC_OFFLINE_FIXTURE', 'hostname': 'fixture'}


def process(pid, start, cpu, read=None):
    result = {'pid': pid, 'start_ticks': start, 'cpu_ticks': cpu}
    if read is not None:
        result['read_bytes'] = read
    return result


def encode(records):
    return b''.join((json.dumps(row) + '\n').encode() for row in records)


samples = [meta,
    {'monotonic_s': 10, 'checked_utc': 'fixture0', 'processes': [
        process(10, 1, 100, 1000), process(11, 1, 0, 0)]},
    {'monotonic_s': 25, 'checked_utc': 'fixture1', 'processes': [
        process(10, 1, 3100, 1600), process(11, 2, 9000, 999999),
        process(12, 1, 8000)]},
    {'monotonic_s': 55, 'checked_utc': 'fixture2', 'processes': [
        process(10, 1, 3200, 1500), process(12, 1, 8100)]},
    {'monotonic_s': 70, 'checked_utc': 'fixture3', 'processes': []},
]
result = module.analyze(encode(samples) + b'{"partial":')
a, b, c = result['intervals']
assert a['observed_cpu_cores'] == 2
assert a['observed_read_bytes_s'] == 40
assert (a['matched_processes'], a['new_identities'], a['disappeared_identities']) == (1, 2, 1)
assert b['sample_gap'] and len(b['counter_resets']) == 1
assert b['observed_counter_deltas']['read_bytes'] is None
assert c['observed_cpu_cores'] is None and c['disappeared_identities'] == 2
assert result['ignored_incomplete_tail']
rejections = 0
for data in [b'{}\n', encode(samples[:2] + [samples[1]]),
             encode([dict(meta, clock_ticks=0)]), encode([dict(meta, clock_ticks=float('nan'))]),
             encode(samples[:1]) + b'{bad}\n',
             encode(samples[:1] + [dict(samples[1], processes=[process(10, 1, 0)] * 2)])]:
    try:
        module.analyze(data)
    except (ValueError, KeyError):
        rejections += 1
assert rejections == 6
# Old validation saved raw samples without sampler metadata. This envelope
# labels its provenance explicitly; it is not NSCC or a benchmark measurement.
old = json.loads((ROOT / 'inspection/wake-20261015-2020UTC/startup-sampler-validation.json').read_text())
envelope = dict(meta, clock_ticks=os.sysconf('SC_CLK_TCK'),
                job='LOCAL_CPU_VALIDATION_ONLY', hostname='local-validation',
                provenance='Metadata constructed now for preserved own-child CPU validation samples')
local_input = HERE / 'preserved-own-child-samples.jsonl'
local_input.write_bytes(encode([envelope, *old['raw_samples']]))
local_result = module.analyze(local_input.read_bytes())
assert local_result['intervals'][0]['observed_counter_deltas']['wchar'] == 4194309
assert local_result['intervals'][0]['observed_counter_deltas']['write_bytes'] == 0
out = HERE / 'preserved-own-child-analysis.json'
cli = subprocess.run([sys.executable, str(ROOT / 'analyze-startup.py'), str(local_input),
                      '--out', str(out)], capture_output=True, text=True)
assert cli.returncode == 0, cli.stderr
before = out.read_bytes()
repeat = subprocess.run([sys.executable, str(ROOT / 'analyze-startup.py'), str(local_input),
                         '--out', str(out)], capture_output=True, text=True)
assert repeat.returncode != 0 and out.read_bytes() == before
report = {'passed': True, 'gpu_executed': False, 'nscc_runtime_validated': False,
          'pid_reuse_excluded': True, 'missing_counters_stay_null': True,
          'counter_reset_and_gap_flagged': True, 'partial_live_tail_ignored': True,
          'invalid_input_rejections': rejections, 'cli_no_overwrite_verified': True,
          'preserved_own_child_wchar_delta': 4194309, 'preserved_own_child_write_bytes_delta': 0,
          'scope': 'Offline fixtures and preserved local CPU own-child samples only'}
(HERE / 'analyzer-validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
