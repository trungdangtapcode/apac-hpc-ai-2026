"""Exit supervisor and independent gate fixtures; no GPU or model allocation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import sys
import tempfile
import time

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('exit_boundaries', here / 'exit-boundaries.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)

with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    for code in (0, 17):
        receipt = root / f'exit{code}.json'
        assert e.supervise([sys.executable, '-c', f'raise SystemExit({code})'], receipt, 0,
                           time.time() + 10, 'fixture') == code
        row = json.loads(receipt.read_text())
        assert row['child_returncode'] == code and row['child_fully_waited']
    receipt = root / 'timeout.json'
    assert e.supervise([sys.executable, '-c', 'import time; time.sleep(5)'], receipt,
                       0, time.time() + 0.1, 'fixture') == 124
    assert json.loads(receipt.read_text())['timed_out'] is True
    source = hashlib.sha256((here / 'native_probe.py').read_bytes()).hexdigest()
    for rank in (0, 1):
        host = f'fixture-host-{rank}'
        e.write_receipt(root / f'rank{rank}-result.json', dict(host=host))
        e.write_receipt(root / f'rank{rank}-python-exit.json', dict(schema='python-child-exit-v1',
            rank=rank, host=host, child_returncode=0, timed_out=False, child_fully_waited=True,
            source_sha256=source))
        e.write_receipt(root / f'rank{rank}-node-exit.json', dict(schema='node-exit-v1',
            rank=rank, host=host, container_returncode=0, cleanup_returncode=0,
            final_returncode=0, cleanup_deleted=True))
    e.write_receipt(root / 'batch-exit.json', dict(schema='batch-exit-v1', final_returncode=0))
    assert e.check(root, include_batch=True)['status'] == 'pass'
    node = root / 'rank1-node-exit.json'
    clean = json.loads(node.read_text())
    for field, value in [('container_returncode', 1), ('cleanup_returncode', 1),
                         ('rank', 0), ('host', 'wrong'), ('cleanup_deleted', False)]:
        e.write_receipt(node, dict(clean, **{field: value}))
        try:
            e.check(root)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid exit evidence accepted: ' + field)
    node.unlink()
    try:
        e.check(root)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError('missing node receipt accepted')
print('PASS: supervisor exit0/exit17/timeout; valid exit gates; five malformed and missing receipt rejections')
