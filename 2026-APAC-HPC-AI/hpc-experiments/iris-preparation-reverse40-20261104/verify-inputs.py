#!/usr/bin/env python3
"""Check the 41 pinned case files and exact permitted decomposition transform."""
import argparse, hashlib, json, pathlib, re
p = argparse.ArgumentParser()
p.add_argument('--source', required=True, type=pathlib.Path)
p.add_argument('--method', required=True, choices=('hierarchical', 'scotch'))
p.add_argument('--pins', required=True, type=pathlib.Path)
p.add_argument('--case', required=True, type=pathlib.Path)
p.add_argument('--observations', required=True, type=pathlib.Path)
a = p.parse_args()
pins = json.loads(a.pins.read_text())['files']
pin_doc = json.loads(a.pins.read_text())
observations = json.loads(a.observations.read_text())['H' if a.method == 'hierarchical' else 'S']
assert len(pins) == 41, f'expected 41 source pins, got {len(pins)}'
# Fixture-only source gates may omit processor trees; runtime caller checks them before copying.
if any(a.source.glob('processor*')):
    assert {p.name for p in a.source.glob('processor*') if p.is_dir()}=={'processor'+str(i) for i in range(56)}
    assert all(not(a.source/('processor'+str(i))).is_symlink() for i in range(56))
for rel, expected in pins.items():
    path = a.source / rel
    if rel == 'Allrun':
        assert not path.exists(), 'unexpected source Allrun'
        pinned_allrun = a.case / 'Allrun'
        assert pinned_allrun.is_file() and hashlib.sha256(pinned_allrun.read_bytes()).hexdigest() == expected, 'retained Allrun pin mismatch'
        continue
    assert path.is_file(), f'missing pinned source input: {rel}'
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if rel != 'system/include/caseDefinition':
        assert actual == expected, f'pinned input drift: {rel}'
case_rel = 'system/include/caseDefinition'
actual_case = (a.source / case_rel).read_bytes()
expected_case = (a.case / f'system/include/caseDefinition.{"H" if a.method == "hierarchical" else "S"}.expected').read_bytes()
expected_hash = pin_doc['verified_ready_case_definition_sha256']['H' if a.method == 'hierarchical' else 'S']
assert hashlib.sha256(expected_case).hexdigest() == expected_hash
assert actual_case == expected_case, 'caseDefinition differs from retained source observation'
ready = (a.source / 'READY').read_text()
assert ready == observations['READY'], 'READY differs from retained native init review'
assert a.method in ready and 'N=56' in ready
assert (a.source / 'system/controlDict.noWrite').is_file()
assert (a.source / 'system/fvSolution.fixedIter').is_file()
assert not (a.source / 'Allrun').exists(), 'unexpected source Allrun'
print(f'PASS: all {len(pins)} source pins and exact {a.method}/56/(7 4 2) transform')
