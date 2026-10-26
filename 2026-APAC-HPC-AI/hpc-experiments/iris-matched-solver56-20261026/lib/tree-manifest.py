#!/usr/bin/env python3
"""Hash copied regular files, inventory symlink targets, and prove isolation."""
import hashlib, json, os, pathlib, stat, sys
src, dst, output = map(pathlib.Path, sys.argv[1:4])
flags = set(sys.argv[4:])

def inventory(root):
    result = {'files': {}, 'symlinks': {}}
    roots = [root / 'system', root / 'constant'] + [root / f'processor{i}' / name for i in range(56) for name in ('0', 'constant')]
    for top in roots:
        if not top.exists() and not top.is_symlink():
            raise AssertionError(f'missing tree: {top}')
        if top.is_symlink():
            result['symlinks'][top.relative_to(root).as_posix()] = os.readlink(top)
            continue
        for base, dirs, names in os.walk(top, followlinks=False):
            b = pathlib.Path(base)
            for name in list(dirs):
                p = b / name
                rel = p.relative_to(root).as_posix()
                if p.is_symlink():
                    result['symlinks'][rel] = os.readlink(p)
                    dirs.remove(name)
            for name in names:
                p = b / name
                rel = p.relative_to(root).as_posix()
                if p.is_symlink():
                    result['symlinks'][rel] = os.readlink(p)
                elif stat.S_ISREG(p.lstat().st_mode):
                    h = hashlib.sha256()
                    with p.open('rb') as f:
                        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
                            h.update(block)
                    result['files'][rel] = h.hexdigest()
    return result

s = inventory(src)
allowed_target='/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam/occDrivAer/polyMesh'
assert all(name=='constant/polyMesh' and str((src/name).resolve())==allowed_target for name in s['symlinks']), 'unexpected runtime symlink'
assert all(('processor'+str(i)+'/0/'+field) in s['files'] for i in range(56) for field in ['U','p','k','omega','nut','nuTilda']), 'initial fields must be regular sealed files'

if '--compare-source-snapshot' in flags:
    before = json.loads((dst / 'source-before.json').read_text())
    assert before == s, 'source changed during solver run'
if '--source-only' not in flags:
    d = inventory(dst)
    assert s == d, 'source and copied case differ (regular file hashes or symlink inventory)'
    source_inodes={( (src/rel).stat().st_dev, (src/rel).stat().st_ino) for rel in s['files']}
    for rel in s['files']:
        statrow=(dst/rel).stat()
        assert (statrow.st_dev,statrow.st_ino) not in source_inodes, f'source inode reused: {rel}'
    if '--compare-copy' in flags:
        before = json.loads((dst / 'source-before.json').read_text())
        assert before == s, 'source changed during copy'
output.write_text(json.dumps(s, sort_keys=True, indent=2) + '\n')
suffix = '; copy matches with no shared inodes' if '--source-only' not in flags else ''
print(f'PASS: {len(s["files"])} source regular files hashed; {len(s["symlinks"])} source symlinks inventoried{suffix}')
