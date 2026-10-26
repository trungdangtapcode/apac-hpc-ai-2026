#!/usr/bin/env python3
import hashlib, pathlib, sys
src, dst = map(pathlib.Path, sys.argv[1:])
fields = ('U', 'k', 'nuTilda', 'nut', 'omega', 'p')
items = [(f'processor{i}/0/{name}') for i in range(56) for name in fields]
assert len(items) == 336
for rel in items:
    a, b = src / rel, dst / rel
    assert a.is_file() and b.is_file(), f'missing field: {rel}'
    assert hashlib.sha256(a.read_bytes()).digest() == hashlib.sha256(b.read_bytes()).digest(), f'field hash mismatch: {rel}'
    assert not a.samefile(b), f'hardlink or same inode: {rel}'
print('PASS: 336 initial fields match by SHA-256 and have distinct inodes')
