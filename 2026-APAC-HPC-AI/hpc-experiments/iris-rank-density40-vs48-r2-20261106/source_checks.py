#!/usr/bin/env python3
"""Verify one initialized Scotch source using retained complete manifests."""
import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from seal_tree import inventory

READY_TEMPLATE = 'N={n}\nmethod=scotch\nnHierarchical=unused\nmesh=occDrivAer-65M\nstages=decomposePar restore0Dir renumberMesh potentialFoam applyBoundaryLayer\n'

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(2 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def expected_case_definition(path, ranks):
    text = Path(path).read_text()
    text, a = re.subn(r'(?m)^nCores .*$', 'nCores              %d;' % ranks, text)
    text, b = re.subn(r'(?m)^nHierarchical .*$', 'nHierarchical       (7 4 2);', text)
    text, c = re.subn(r'(?m)^decompositionMethod .*$', 'decompositionMethod scotch;', text)
    text, d = re.subn(r'(?m)(^nHierarchical )', '// Not the scotch cut. Required so decomposeParDict $nHierarchical expands.\n\\1', text)
    if (a, b, c, d) != (1, 1, 1, 1):
        raise ValueError('caseDefinition lacks expected Scotch rank transform')
    return text.encode()

def verify_exact_tree(root, core, supplementary):
    files = dict(core['files'])
    for name, digest in supplementary['files'].items():
        if name in files and files[name] != digest:
            raise ValueError('conflicting source manifests for ' + name)
        files[name] = digest
    links = dict(core.get('symlinks', {}))
    for name, target in supplementary.get('symlinks', {}).items():
        if name in links and links[name] != target:
            raise ValueError('conflicting source symlinks for ' + name)
        links[name] = target
    found_files, found_links, found_dirs = set(), set(), set()
    for base, dirs, names in os.walk(root, topdown=True, followlinks=False):
        here = Path(base)
        for name in list(dirs):
            p = here / name
            rel = p.relative_to(root).as_posix()
            mode = p.lstat().st_mode
            if stat.S_ISLNK(mode):
                found_links.add(rel)
                dirs.remove(name)
            elif stat.S_ISDIR(mode):
                found_dirs.add(rel)
        for name in names:
            p = here / name
            rel = p.relative_to(root).as_posix()
            mode = p.lstat().st_mode
            if stat.S_ISLNK(mode): found_links.add(rel)
            elif stat.S_ISREG(mode): found_files.add(rel)
            else: raise ValueError('unsupported source object: ' + rel)
    if found_files != set(files) or found_links != set(links) or found_dirs != set(supplementary.get('directories', [])):
        raise ValueError('accepted source files, links, or directories differ from complete manifests')
    for name, digest in files.items():
        p = root / name
        if not p.is_file() or p.is_symlink() or sha256(p) != digest:
            raise ValueError('accepted source hash mismatch: ' + name)
    for name, target in links.items():
        p = root / name
        if not p.is_symlink() or p.readlink().as_posix() != target:
            raise ValueError('accepted source symlink mismatch: ' + name)
    actual = inventory(root)
    if actual != core:
        raise ValueError('full core inventory differs from accepted source manifest')
    return len(files), len(found_dirs)

def verify_inputs(source, template, pins_path, ranks):
    pins = json.loads(pins_path.read_text())['files']
    if len(pins) != 41:
        raise ValueError('expected 41 organizer case pins')
    for rel, digest in pins.items():
        original, actual = template / rel, source / rel
        if not original.is_file() or sha256(original) != digest:
            raise ValueError('frozen template pin mismatch: ' + rel)
        if rel == 'Allrun':
            if actual.exists() or actual.is_symlink():
                raise ValueError('unexpected source Allrun')
        elif rel == 'system/include/caseDefinition':
            if not actual.is_file() or actual.is_symlink() or actual.read_bytes() != expected_case_definition(original, ranks):
                raise ValueError('caseDefinition does not match exact Scotch N%d transform' % ranks)
        elif rel == 'system/controlDict':
            if not actual.is_file() or sha256(actual) != sha256(template / 'system/controlDict.noWrite'):
                raise ValueError('controlDict differs from no-write variant')
        elif rel == 'system/fvSolution':
            if not actual.is_file() or sha256(actual) != sha256(template / 'system/fvSolution.fixedIter'):
                raise ValueError('fvSolution differs from fixed-iteration variant')
        elif not actual.is_file() or actual.is_symlink() or sha256(actual) != digest:
            raise ValueError('pinned physics/input mismatch: ' + rel)
    ready = (source / 'READY').read_text()
    if ready != READY_TEMPLATE.format(n=ranks):
        raise ValueError('READY marker does not identify exact N%d Scotch initialization' % ranks)
    return {'passed': True, 'rank_count': ranks, 'pinned_case_files': len(pins),
            'case_definition_sha256': sha256(source / 'system/include/caseDefinition'),
            'ready_sha256': sha256(source / 'READY'),
            'physics_pin_sha256': {n: h for n, h in pins.items() if n != 'system/include/caseDefinition'}}

def verify(source, template, pins, manifest, supplementary, ranks):
    core, extra = json.loads(manifest.read_text()), json.loads(supplementary.read_text())
    if extra.get('source') != str(source):
        raise ValueError('supplementary manifest names a different source')
    files, directories = verify_exact_tree(source, core, extra)
    inputs = verify_inputs(source, template, pins, ranks)
    return {'passed': True, 'source': str(source), 'rank_count': ranks,
            'core_files': len(core['files']), 'supplementary_files': len(extra['files']),
            'complete_files': files, 'directories': directories, 'inputs': inputs}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--template', type=Path, required=True)
    p.add_argument('--pins', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--supplementary', type=Path, required=True)
    p.add_argument('--ranks', type=int, choices=(40, 48), required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    r = verify(a.source, a.template, a.pins, a.manifest, a.supplementary, a.ranks)
    a.output.write_text(json.dumps(r, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'passed': True, 'rank_count': a.ranks, 'complete_files': r['complete_files']}))

if __name__ == '__main__': main()
