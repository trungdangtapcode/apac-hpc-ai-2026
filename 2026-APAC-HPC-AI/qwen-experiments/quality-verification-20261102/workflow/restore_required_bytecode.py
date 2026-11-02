#!/usr/bin/env python3
"""Restore only the exact checksum-required public bytecode files from the reviewed bundle."""
from pathlib import Path
import argparse
import hashlib
import json
import tarfile
S = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--check-only', action='store_true')
a = p.parse_args()
rows = json.loads((S / 'workflow/REQUIRED_BYTECODE.json').read_text())['files']
expected = {r['path']: r for r in rows}
with tarfile.open(S / 'workflow/required-bytecode.tar') as t:
    members = t.getmembers()
    assert len(members) == len(expected) == 16
    assert {m.name for m in members} == set(expected)
    for m in members:
        assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
        data = t.extractfile(m).read()
        row = expected[m.name]
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
        out = S / m.name
        if out.exists():
            assert hashlib.sha256(out.read_bytes()).hexdigest() == row['sha256'], 'Refusing to overwrite different existing file'
        elif a.check_only:
            raise RuntimeError('Missing runtime dependency: ' + m.name)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open('xb') as f:
                f.write(data)
print('Verified 16 exact runtime dependencies; check-only=' + str(a.check_only))
