#!/usr/bin/env python3
"""Copy only case system/constant and processor 0 plus constant trees."""
import pathlib, shutil, sys
src, dst = map(pathlib.Path, sys.argv[1:3])
assert dst.is_dir(), f'destination directory must already exist: {dst}'
existing = {p.name for p in dst.iterdir()}
assert existing <= {'source-before.json', 'source-before-hash.log', 'copy.log'}, f'refusing unexpected destination contents: {sorted(existing)}'
for name in ('system', 'constant'):
    shutil.copytree(src / name, dst / name, symlinks=True, dirs_exist_ok=True)
for i in range(56):
    (dst / f'processor{i}').mkdir(exist_ok=True)
    for name in ('0', 'constant'):
        shutil.copytree(src / f'processor{i}' / name, dst / f'processor{i}' / name,
                        symlinks=True, dirs_exist_ok=True)
print('copy complete; no hardlinks requested')
