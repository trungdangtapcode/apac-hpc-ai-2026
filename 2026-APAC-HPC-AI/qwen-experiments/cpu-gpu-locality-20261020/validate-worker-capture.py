"""CPU-only integration fixtures: owned process tree and namespace GPU PID matching."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

O = Path(__file__).resolve().parent
source = O / 'capture-worker-locality.py'
spec = importlib.util.spec_from_file_location('worker_capture', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.expand('0-2,8,12-13') == {0, 1, 2, 8, 12, 13}
rows = [dict(pid=10, namespace_pids=[100, 10]), dict(pid=20, namespace_pids=[200, 20])]
matches, ambiguous = module.match_gpu_rows(rows, [['100', 'GPU-fixture-A', '12'], ['999', 'GPU-unowned', '1']])
assert len(matches) == 1 and matches[0]['process_pid'] == 10 and ambiguous == 0
matches, ambiguous = module.match_gpu_rows(rows + [dict(pid=30, namespace_pids=[100, 30])], [['100', 'GPU-ambiguous', '12']])
assert matches == [] and ambiguous == 1

with tempfile.TemporaryDirectory(prefix='ap42-locality-fixture-') as temporary:
    root = Path(temporary)
    (root / 'bin').mkdir()
    (root / 'worker-locality').mkdir()
    (root / 'worker-locality/request.json').write_text('{}\n')
    fake = root / 'bin/nvidia-smi'
    fake.write_text('''#!/usr/bin/env python3
import os,sys
if any(x.startswith('--query-compute-apps=') for x in sys.argv):
    print(os.environ['FAKE_GPU_PROCESS_PID']+', GPU-fixture-A, 10')
    print('99999999, GPU-unowned, 10')
else:
    print('7, GPU-fixture-A, 00000000:FF:00.0')
''')
    fake.chmod(0o700)
    sleeper = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'])
    try:
        env = dict(os.environ, PATH=str(root / 'bin') + ':' + os.environ['PATH'],
                   FAKE_GPU_PROCESS_PID=str(sleeper.pid))
        subprocess.run([sys.executable, str(source), '--root', str(os.getpid()),
                        '--role', 'fixture', '--artifact', str(root), '--timeout', '2'],
                       env=env, check=True, timeout=10)
        result = json.loads((root / 'worker-locality/fixture.ready.json').read_text())
        assert result['state'] == 'CAPTURE_COMPLETE', result
        snapshot = result['snapshot']
        assert sleeper.pid in {p['pid'] for p in snapshot['processes']}
        assert result['observer_pid'] not in {p['pid'] for p in snapshot['processes']}
        assert len(snapshot['matched_gpu_processes']) == 1
        assert snapshot['matched_gpu_processes'][0]['process_pid'] == sleeper.pid
        assert snapshot['processes'][0]['thread_mask_counts']
        assert 'GPU-unowned' not in json.dumps(snapshot['matched_gpu_processes'])
        assert snapshot['visible_devices'][0]['nvml_visible_index'] == '7'
        assert snapshot['visible_devices'][0]['local_cpulist'] is None
        assert not snapshot['scored_cpu_demand_collected']
        assert not result['reads_process_environments'] and not result['reads_command_lines']
    finally:
        sleeper.terminate()
        sleeper.wait(timeout=5)
    subprocess.run([sys.executable, str(source), '--root', '99999999', '--role', 'missing-root',
                    '--artifact', str(root), '--timeout', '0'], check=True, timeout=5)
    missing = json.loads((root / 'worker-locality/missing-root.ready.json').read_text())
    assert missing['state'] == 'CAPTURE_INCOMPLETE'

(O / 'worker-capture-validation.json').write_text(json.dumps(dict(
    passed=True, gpu_computation=False,
    checks=['CPU range expansion', 'owned live child discovery', 'observer exclusion',
            'namespace PID translation', 'unowned GPU row exclusion', 'ambiguous PID refusal',
            'thread affinity capture', 'missing locality stays null', 'missing root marked incomplete',
            'no process environment or command-line reads']), indent=2) + '\n')
print('Worker locality CPU fixtures PASS')
