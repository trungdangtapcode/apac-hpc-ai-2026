#!/usr/bin/env python3
"""Verify a frozen Scotch source tree, its supplementary paths, and pinned inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from seal_tree import inventory

READY_TEMPLATE = 'N={n}\nmethod=scotch\nnHierarchical=unused\nmesh=occDrivAer-65M\nstages=decomposePar restore0Dir renumberMesh potentialFoam applyBoundaryLayer\n'

def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def expected_case_definition(path, ranks):
    text = path.read_text()
    text, n1 = re.subn(r'(?m)^nCores .*$', 'nCores              %d;' % ranks, text)
    text, n2 = re.subn(r'(?m)^nHierarchical .*$', 'nHierarchical       (7 4 2);', text)
    text, n3 = re.subn(r'(?m)^decompositionMethod .*$', 'decompositionMethod scotch;', text)
    text, n4 = re.subn(r'(?m)(^nHierarchical )', '// Not the scotch cut. Required so decomposeParDict $nHierarchical expands.\n\\1', text)
    if (n1, n2, n3, n4) != (1, 1, 1, 1):
        raise ValueError('pinned caseDefinition must have one nCores, nHierarchical, and method directive')
    return text.encode()

def verify_exact_tree(root, core, supplementary, core_already_verified=False):
    combined_files = dict(core['files'])
    for name, digest in supplementary['files'].items():
        if name in combined_files and combined_files[name] != digest:
            raise ValueError('conflicting source manifests for ' + name)
        combined_files[name] = digest
    combined_links = dict(core.get('symlinks', {}))
    for name, target in supplementary.get('symlinks', {}).items():
        if name in combined_links and combined_links[name] != target:
            raise ValueError('conflicting symlink manifests for ' + name)
        combined_links[name] = target
    found_files, found_links, found_dirs = set(), set(), set()
    for base, dirs, files in os.walk(root, topdown=True, followlinks=False):
        here = Path(base)
        for name in list(dirs):
            path = here / name
            rel = path.relative_to(root).as_posix()
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                found_links.add(rel)
                dirs.remove(name)
            elif stat.S_ISDIR(mode):
                found_dirs.add(rel)
        for name in files:
            path = here / name
            rel = path.relative_to(root).as_posix()
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                found_links.add(rel)
            elif stat.S_ISREG(mode):
                found_files.add(rel)
            else:
                raise ValueError('unsupported filesystem object: ' + rel)
    if found_files != set(combined_files) or found_links != set(combined_links) or found_dirs != set(supplementary.get('directories', [])):
        raise ValueError('accepted source tree paths differ from the frozen manifests')
    for name, target in combined_links.items():
        if os.readlink(root / name) != target:
            raise ValueError('source symlink target differs: ' + name)
    for name, digest in combined_files.items():
        if core_already_verified and name in core['files']:
            continue
        if sha256(root / name) != digest:
            raise ValueError('source file differs from frozen manifest: ' + name)
    return len(combined_files), len(found_dirs)

def verify_inputs(source, template, pins_path, ranks):
    pins = json.loads(pins_path.read_text())['files']
    if len(pins) != 41:
        raise ValueError('expected 41 source pins, got %d' % len(pins))
    for relative, expected in pins.items():
        original = template / relative
        if not original.is_file() or sha256(original) != expected:
            raise ValueError('local source pin mismatch: ' + relative)
        actual = source / relative
        if relative == 'Allrun':
            if actual.exists() or actual.is_symlink():
                raise ValueError('unexpected source Allrun')
        elif relative == 'system/include/caseDefinition':
            if not actual.is_file() or actual.is_symlink() or actual.read_bytes() != expected_case_definition(original, ranks):
                raise ValueError('source caseDefinition differs from exact Scotch N%d transform' % ranks)
        elif relative == 'system/controlDict':
            expected_control = template / 'system/controlDict.noWrite'
            if not actual.is_file() or sha256(actual) != sha256(expected_control):
                raise ValueError('source controlDict differs from frozen no-write variant')
        elif relative == 'system/fvSolution':
            expected_solution = template / 'system/fvSolution.fixedIter'
            if not actual.is_file() or sha256(actual) != sha256(expected_solution):
                raise ValueError('source fvSolution differs from frozen fixed-iteration variant')
        elif not actual.is_file() or actual.is_symlink() or sha256(actual) != expected:
            raise ValueError('source input differs from pinned case input: ' + relative)
    ready = (source / 'READY').read_text()
    expected_ready = READY_TEMPLATE.format(n=ranks)
    if ready != expected_ready:
        raise ValueError('source READY does not match reviewed N%d Scotch initialization' % ranks)
    return {'passed': True, 'rank_count': ranks, 'pinned_case_files': len(pins),
            'case_definition_sha256': sha256(source / 'system/include/caseDefinition'),
            'ready_sha256': sha256(source / 'READY'), 'ready_text': ready,
            'physics_pin_sha256': {name: digest for name, digest in pins.items() if name != 'system/include/caseDefinition'}}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--template', type=Path, required=True)
    ap.add_argument('--pins', type=Path, required=True)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--supplementary', type=Path, required=True)
    ap.add_argument('--ranks', type=int, choices=(48, 56), required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    core = json.loads(args.manifest.read_text())
    extra = json.loads(args.supplementary.read_text())
    if extra.get('source') != str(args.source):
        raise ValueError('supplementary manifest points at a different source root')
    manifest_n = int(re.search(r'(?m)^N=(48|56)$', (args.source / 'READY').read_text())[1])
    if manifest_n != args.ranks:
        raise ValueError('source READY rank count differs from selected partition')
    if inventory(args.source) != core:
        raise ValueError('full accepted core source manifest differs')
    files, directories = verify_exact_tree(args.source, core, extra, core_already_verified=True)
    inputs = verify_inputs(args.source, args.template, args.pins, args.ranks)
    result = {'passed': True, 'source': str(args.source), 'rank_count': args.ranks,
              'core_files': len(core['files']), 'supplementary_files': len(extra['files']),
              'full_files': files, 'directories': directories, 'inputs': inputs,
              'actual_source_observation': {'ready_text': inputs['ready_text'],
                  'ready_sha256': inputs['ready_sha256'],
                  'case_definition_sha256': inputs['case_definition_sha256'],
                  'inspection': 'Read directly from accepted initialized source after full manifest validation.'}}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'passed': True, 'rank_count': args.ranks, 'full_files': files}))

if __name__ == '__main__':
    main()
