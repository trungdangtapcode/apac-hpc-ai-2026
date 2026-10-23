"""Durable exit evidence around the unchanged native transfer child."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def write_receipt(path, value):
    path = Path(path)
    temp = path.with_name(path.name + '.' + str(os.getpid()) + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


def supervise(command, receipt, rank, deadline, source_sha):
    started = time.time()
    timed_out = False
    child = None
    code = 125
    try:
        if deadline <= started:
            code = 124
            timed_out = True
        else:
            child = subprocess.Popen(command)
            try:
                code = child.wait(timeout=deadline - started)
            except subprocess.TimeoutExpired:
                timed_out = True
                child.kill()
                code = child.wait(timeout=3)
    finally:
        write_receipt(receipt, dict(schema='python-child-exit-v1', rank=rank,
            host=socket.gethostname(), child_returncode=code, timed_out=timed_out,
            started_epoch_s=started, ended_epoch_s=time.time(),
            source_sha256=source_sha, child_fully_waited=(child is not None and child.returncode is not None)))
    return 124 if timed_out else (code if code >= 0 else 128 - code)


def check(art, include_batch=False):
    art = Path(art)
    expected_sha = hashlib.sha256((HERE / 'native_probe.py').read_bytes()).hexdigest()
    for rank in (0, 1):
        py = json.loads((art / f'rank{rank}-python-exit.json').read_text())
        node = json.loads((art / f'rank{rank}-node-exit.json').read_text())
        native = json.loads((art / f'rank{rank}-result.json').read_text())
        if py.get('schema') != 'python-child-exit-v1' or node.get('schema') != 'node-exit-v1':
            raise ValueError('exit receipt schema mismatch')
        if any(row.get('rank') != rank or row.get('host') != native.get('host') for row in (py, node)):
            raise ValueError('exit rank/host does not match native rank result')
        if (type(py.get('child_returncode')) is not int or py['child_returncode'] != 0
                or py.get('timed_out') is not False or py.get('child_fully_waited') is not True
                or py.get('source_sha256') != expected_sha):
            raise ValueError('native Python child did not exit cleanly with bound source')
        for key in ('container_returncode', 'cleanup_returncode', 'final_returncode'):
            if type(node.get(key)) is not int or node[key] != 0:
                raise ValueError('container/node cleanup exit failed: ' + key)
        if node.get('cleanup_deleted') is not True:
            raise ValueError('node private temporary directory cleanup not confirmed')
    if include_batch:
        batch = json.loads((art / 'batch-exit.json').read_text())
        if batch.get('schema') != 'batch-exit-v1' or batch.get('final_returncode') != 0:
            raise ValueError('batch script exit was unsuccessful')
    return dict(status='pass', physical_rank_exits=2, batch_exit_inspected=include_batch,
                scope='Process exit boundaries only; scheduler stageout status reviewed separately')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--art', type=Path, required=True)
    parser.add_argument('--rank', type=int, choices=(0, 1))
    parser.add_argument('--exchange', type=Path)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--include-batch', action='store_true')
    args = parser.parse_args()
    if args.check:
        try:
            result = check(args.art, args.include_batch)
        except Exception as exc:
            result = dict(status='fail', error=str(exc))
        print(json.dumps(result, indent=2))
        return 0 if result['status'] == 'pass' else 1
    if args.rank is None or args.exchange is None:
        parser.error('supervisor requires --rank and --exchange')
    t0 = json.loads((args.exchange / 'component-start.json').read_text())['t0_epoch_s']
    native = HERE / 'native_probe.py'
    return supervise([sys.executable, str(native), '--rank', str(args.rank), '--art', str(args.art),
        '--exchange-dir', str(args.exchange)], args.art / f'rank{args.rank}-python-exit.json',
        args.rank, float(t0) + 500, hashlib.sha256(native.read_bytes()).hexdigest())


if __name__ == '__main__':
    raise SystemExit(main())
