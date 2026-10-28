#!/usr/bin/env python3
"""Verify the pinned AIPerf client image bytes and stable filesystem identity."""
import hashlib, json
from pathlib import Path
identity=json.loads(Path(__file__).with_name('client-image-identity.json').read_text())
p=Path(identity['path']).resolve(strict=True)
assert str(p)==identity['path'], 'client image path is not canonical'
def fingerprint(st):
    return (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
before=p.stat()
assert before.st_size==identity['bytes'], 'client image size differs from pin'
assert before.st_mtime_ns==identity['mtime_ns'] and before.st_ctime_ns==identity['ctime_ns'], 'client image timestamps differ from pin'
h=hashlib.sha256()
with p.open('rb') as f:
    for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
actual=h.hexdigest()
after=p.stat()
assert fingerprint(before)==fingerprint(after), 'client image changed during verification'
assert actual==identity['sha256'], 'client image SHA-256 differs from pin'
print(json.dumps({'state':'PASS','path':str(p),'bytes':after.st_size,'sha256':actual,'stable_stat':True}))
