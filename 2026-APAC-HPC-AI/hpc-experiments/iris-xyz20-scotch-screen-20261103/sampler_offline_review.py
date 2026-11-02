"""Standalone sampler cost-gate, missing-source, size-limit and lifecycle fixtures."""
from pathlib import Path
import json
import tempfile
import time
import sampler

# Exercise preflight cost/missing-source gates and subprocess cleanup on temporary procfs fixtures only.
def make_proc_fixture(root, include_pressure=True, include_required=True):
    root.mkdir(parents=True, exist_ok=True)
    if include_required:
        (root / 'meminfo').write_text('MemAvailable: 100000 kB\nMemFree: 50000 kB\nCached: 20000 kB\nSwapTotal: 0 kB\nSwapFree: 0 kB\nSwapCached: 0 kB\nActive: 40000 kB\nInactive: 10000 kB\nActive(anon): 10000 kB\nInactive(anon): 1000 kB\nActive(file): 30000 kB\nInactive(file): 9000 kB\n')
        (root / 'vmstat').write_text('pgmajfault 12\npswpin 0\npswpout 0\npgscan_kswapd 3\npgsteal_kswapd 2\nnuma_hit 100\nnuma_miss 4\n')
        (root / 'stat').write_text('cpu 1 2 3 4 5 6 7 8 9 10\ncpu0 1 2 3 4 5 6 7 8 9 10\n')
        (root / 'cpuinfo').write_text('processor : 0\ncpu MHz : 2000.000\nprocessor : 1\ncpu MHz : 2100.000\n')
    pressure = root / 'pressure'
    if include_pressure:
        pressure.mkdir(exist_ok=True)
        for name in ('cpu', 'io', 'memory'):
            (pressure / name).write_text('some avg10=0.00 avg60=0.00 avg300=0.00 total=0\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=0\n')
    return root

with tempfile.TemporaryDirectory(prefix='iris-xyz20-sampler-fixtures-') as td:
    base = Path(td)
    proc = make_proc_fixture(base / 'proc')
    probe = sampler.preflight(proc, reads=5, max_read_ms=50.0)
    assert probe['enabled'] and probe['preflight_reads'] == 5
    sample = sampler.collect_sample(proc)
    assert sample['required_components_available']
    assert sample['aggregate_cpu_ticks']['user'] == 1
    assert sample['cpuinfo_frequency'] == {'count': 2, 'minimum_mhz': 2000.0, 'median_mhz': 2050.0, 'maximum_mhz': 2100.0}
    assert sample['vmstat_pages_or_events']['pgmajfault'] == 12
    missing_pressure = make_proc_fixture(base / 'proc-no-pressure', include_pressure=False)
    missing_probe = sampler.preflight(missing_pressure, reads=5, max_read_ms=50.0)
    assert missing_probe['enabled'] and missing_probe['pressure_availability']['io'] is False
    assert sampler.collect_sample(missing_pressure)['pressure']['io']['available'] is False
    missing_required = sampler.preflight(base / 'no-proc', reads=5, max_read_ms=50.0)
    assert not missing_required['enabled'] and missing_required['reads_missing_required_sources']
    slow = sampler.preflight(proc, reader=lambda _: {'collection_ms': 50.1, 'required_components_available': True}, reads=5)
    assert not slow['enabled'] and len(slow['reads_over_cost_gate']) == 5
    missing_pressure_explicit = sampler.collect_sample(missing_pressure)['pressure']
    assert missing_pressure_explicit['io'] == {'available': False, 'missing': 'procfs pressure file not present'}

    output = base / 'samples.jsonl'
    child = sampler.start_sampler(output, proc_root=proc, interval=0.025)
    ready = sampler.wait_for_first_sample(child, output, timeout_seconds=1.0)
    assert ready['available']
    time.sleep(0.10)
    stopped = sampler.stop_sampler(child)
    assert stopped['stopped'] and stopped['returncode'] == 0 and child.poll() == 0
    rows = [json.loads(line) for line in output.read_text().splitlines() if line.strip()]
    assert len(rows) >= 2 and all('collection_ms' in row and 'timestamp_monotonic_seconds' in row for row in rows)
    assert sampler.validate_sample_file(output)['sample_count'] == len(rows)
    too_large = base / 'oversize.jsonl'
    with too_large.open('wb') as stream: stream.truncate(2_000_000)
    try: sampler.validate_sample_file(too_large)
    except ValueError: pass
    else: raise AssertionError('oversized collector sample accepted')

    # Missing procfs sources stay explicit in emitted samples; stop/reap still succeeds.
    output_missing = base / 'missing-sources.jsonl'
    child_missing = sampler.start_sampler(output_missing, proc_root=base / 'no-proc', interval=0.025)
    assert sampler.wait_for_first_sample(child_missing, output_missing, timeout_seconds=1.0)['available']
    stopped_missing = sampler.stop_sampler(child_missing)
    missing_rows = [json.loads(line) for line in output_missing.read_text().splitlines() if line.strip()]
    assert stopped_missing['returncode'] == 0 and not missing_rows[0]['required_components_available']
    assert 'meminfo' in missing_rows[0]['errors']

    # The real solver wrapper must stop and reap its telemetry child when launch raises.
    output_exception = base / 'solver-exception-samples.jsonl'
    child_exception = sampler.start_sampler(output_exception, proc_root=proc, interval=0.025)
    assert sampler.wait_for_first_sample(child_exception, output_exception, timeout_seconds=1.0)['available']
    try: sampler.run_with_sampler(child_exception, [str(base / 'no-such-solver')], timeout=1)
    except FileNotFoundError: pass
    else: raise AssertionError('deliberate solver launch exception was swallowed')
    assert child_exception.poll() == 0

    # A bad output target must terminate with a visible error and be reaped by the parent.
    bad_target = base / 'directory-output'
    bad_target.mkdir()
    child_error = sampler.start_sampler(bad_target, proc_root=proc, interval=0.025)
    child_error.wait(timeout=2.0)
    error_stop = sampler.stop_sampler(child_error)
    assert error_stop['stopped'] and error_stop['returncode'] != 0 and child_error.poll() is not None

print(json.dumps({'passed':True,'scope':'Temporary procfs fixtures only; no real procfs users, scheduler, remote source, or solver outputs were read or changed.',
 'checks':['Five-read 50-ms preflight; >50ms disables sampling','Missing pressure path is explicitly unavailable while required counters remain usable','Missing required procfs sources disable sampler explicitly','Sampler emits timestamped samples and stops/reaps after normal exit','Sampler process is stopped/reaped when solver launcher raises','Sampler process error is visible and reaped','Per-arm JSONL validator enforces the 2MB limit'],
 'observer_interference':'Not estimated by these fixture tests or collection_ms.'},indent=2))
