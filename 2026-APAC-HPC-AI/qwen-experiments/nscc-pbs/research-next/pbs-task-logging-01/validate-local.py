"""Exercise descriptor/exit/signal behavior and the PBS shim using CPU stubs."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    args = parser.parse_args()
    args.evidence.mkdir(parents=True, exist_ok=False)
    root = args.evidence.resolve()
    checks = []

    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
        assert value, name

    wrapper = HERE / 'pbs-task-log.sh'
    prefix = root / 'direct'

    def run(command):
        return subprocess.run(['bash', str(wrapper), str(prefix), *command],
                              capture_output=True, text=True, timeout=10)

    payload = 'literal spaces ; $HOME `false` "quotes"'
    p = run(['python3', '-c',
             'import json,sys;print(json.dumps(sys.argv[1:]));print("STDERR_SENTINEL",file=sys.stderr)',
             payload])
    logs = list(root.glob('direct.*.log'))
    text = logs[0].read_text()
    check('stdout_and_stderr_captured_with_literal_arguments',
          p.returncode == 0 and not p.stdout and not p.stderr
          and json.dumps([payload]) in text and 'STDERR_SENTINEL' in text)
    check('private_log_mode', logs[0].stat().st_mode & 0o777 == 0o600)
    p = run(['bash', '-c', 'echo FAILURE_SENTINEL >&2; exit 23'])
    check('child_exit23_preserved', p.returncode == 23)
    check('same_prefix_keeps_both_logs', len(list(root.glob('direct.*.log'))) == 2
          and logs[0].read_text() == text)
    p = subprocess.run(['bash', str(wrapper), str(root / 'missing' / 'log'),
                        'bash', '-c', 'echo should-not-run'],
                       capture_output=True, text=True, timeout=10)
    check('log_creation_failure_blocks_execution', p.returncode != 0
          and 'should-not-run' not in p.stdout)
    p = subprocess.run(['bash', str(wrapper), 'relative', 'true'],
                       capture_output=True, text=True, timeout=10)
    check('relative_log_prefix_rejected', p.returncode == 2)
    expected_umask = subprocess.check_output(['bash', '-c', 'umask'], text=True).strip()
    p = run(['bash', '-c', 'umask'])
    check('child_umask_preserved', p.returncode == 0 and any(
        line.strip() == expected_umask
        for path in root.glob('direct.*.log') for line in path.read_text().splitlines()))
    ready = root / 'signal-ready'
    with (root / 'signal-parent.stdout').open('w') as out:
        p = subprocess.Popen(['bash', str(wrapper), str(root / 'signal'),
                              'python3', '-c',
                              'import pathlib,sys,time;pathlib.Path(sys.argv[1]).touch();time.sleep(10)',
                              str(ready)], stdout=out, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 3
            while not ready.exists() and p.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
            assert ready.exists(), 'Signal fixture did not start'
            p.send_signal(signal.SIGTERM)
            check('exec_keeps_signal_semantics', p.wait(timeout=3) == -signal.SIGTERM)
        finally:
            if p.poll() is None:
                p.kill()
                p.wait()

    # Stub pbsdsh emits a spool marker then executes the task locally. The
    # container stub only records arguments: no scheduler, container or GPU.
    bundle = root / 'bundle with spaces'
    bundle.mkdir()
    for name in ('pbs-shim.sh', 'pbs-task-log.sh'):
        shutil.copy2(HERE / name, bundle / name)
    (bundle / 'placement.tsv').write_text(
        'prefill-0\t0\t4\t30100\t9000\nprefill-1\t0\t4\t30101\t9001\ndecode-0\t1\t8\t30200\t0\n')
    (bundle / 'pbs-container.sh').write_text(
        '#!/bin/bash\nexec python3 -c \'import json,sys;print("CONTAINER_STUB",json.dumps(sys.argv[1:]))\' "$@"\n')
    stub = root / 'pbsdsh'
    stub.write_text('#!/bin/bash\nset -eu\n[[ $1 == -n && $3 == -- ]]\nshift 3\necho PBS_SPOOL_SENTINEL\nexec "$@"\n')
    stub.chmod(0o700)
    nodefile = root / 'nodefile'
    nodefile.write_text('node0\nnode1\n')
    task_dir = root / 'runs' / 'fixture.pbs0'
    task_dir.mkdir(parents=True)
    env = dict(os.environ, QWEN_BUNDLE=str(bundle), PBS_NODEFILE=str(nodefile),
               SLURM_SUBMIT_DIR=str(root), PBS_JOBID='fixture.pbs0')
    env.pop('APAC_PBS_DRY_RUN', None)
    for role, host, gpu, cpus, offset in [
        ('prefill-0', 'node0', 4, 32, 0), ('prefill-1', 'node0', 4, 32, 4),
        ('decode-0', 'node1', 8, 64, 0), ('aux', 'node0', 0, 4, 0),
    ]:
        command = ['bash', '/fixture/worker.sh', role, '30100', '/fixture/model', str(gpu), payload]
        script = ('source "$QWEN_BUNDLE/pbs-shim.sh"\n'
                  'pbsdsh() { "$STUB_PBSDHS" "$@"; }\n'
                  'srun -w "$1" --gres=gpu:"$2" --cpus-per-task="$3" '
                  '--container-image=/fixture/image --container-mounts=/fixture:/fixture "${@:4}"\n')
        p = subprocess.run(['bash', '-c', script, 'fixture', host, str(gpu), str(cpus), *command],
                           env=dict(env, STUB_PBSDHS=str(stub)), capture_output=True, text=True, timeout=10)
        task_logs = list(task_dir.glob('task-' + role + '-node*.*.log'))
        body = task_logs[0].read_text() if len(task_logs) == 1 else ''
        line = next((s for s in body.splitlines() if s.startswith('CONTAINER_STUB ')), '')
        recorded = json.loads(line.removeprefix('CONTAINER_STUB ')) if line else []
        check('shim_task_logging_' + role,
              p.returncode == 0 and p.stdout == 'PBS_SPOOL_SENTINEL\n' and not p.stderr
              and 'PBS_SPOOL_SENTINEL' not in body and 'TASK_LOG_START ' in body
              and recorded[:5] == ['/fixture/image', '/fixture:/fixture', str(offset), str(gpu), str(cpus)]
              and recorded[6:] == command)
    result = {'scope': 'CPU only, stub pbsdsh/container; not live PBS or runtime rank proof',
              'checks': checks, 'passed': len(checks), 'total': len(checks)}
    (root / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
