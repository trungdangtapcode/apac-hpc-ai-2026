"""Offline fixtures for label grouping and exact xzy source transforms."""
from pathlib import Path
import json
import shutil
import tempfile

from case_checks import source_check
from native_output import review_native_output
from run import ARMS, MANIFESTS, SOURCES, comparison_metrics, method_key, solver_launch

E = Path(__file__).resolve().parent
PARENT40 = E.parent / 'iris-xzy40-20261102/completed-2294643/collected/runs/2294643/arms/B1-our-xzy'
try:
    review_native_output(PARENT40)
except AssertionError as exc:
    assert 'steps 1..52' in str(exc), str(exc)
else:
    raise AssertionError('52-step parser accepted a 40-step parent log')
assert ARMS == ['A1-scotch', 'B1-our-xzy', 'B2-our-xzy', 'A2-scotch']
assert [method_key(label) for label in ARMS] == ['scotch', 'xzy', 'xzy', 'scotch']
assert MANIFESTS['xzy'].name == 'accepted-xzy-source-manifest.json'
assert SOURCES['xzy'].name == 'order-xzy'
assert solver_launch('B1-our-xzy') == solver_launch('A1-scotch')
assert solver_launch('B1-our-xzy')[-2:] == ['simpleFoam', '-parallel']

# Use unequal ABBA values so index-based grouping would return the wrong answer.
rows = [
    {'arm': 'A1-scotch', 'mean_s_step': 20.0},
    {'arm': 'B1-our-xzy', 'mean_s_step': 10.0},
    {'arm': 'B2-our-xzy', 'mean_s_step': 11.0},
    {'arm': 'A2-scotch', 'mean_s_step': 21.0},
]
metrics = comparison_metrics(rows)
assert abs(metrics['xzy_vs_scotch_percent'] - (100 * (21 / 41 - 1))) < 1e-12
assert metrics['first_adjacent_B1_xzy_vs_A1_scotch_percent'] == -50.0
assert abs(metrics['reverse_adjacent_B2_xzy_vs_A2_scotch_percent'] - (100 * (11 / 21 - 1))) < 1e-12
assert abs(metrics['control_repeat_A2_vs_A1_percent'] - 5.0) < 1e-12
assert abs(metrics['candidate_repeat_B2_vs_B1_percent'] - 10.0) < 1e-12

# Build a minimal source tree from the pinned physical inputs and allowed decomposition edits.
with tempfile.TemporaryDirectory(prefix='iris-xzy-source-fixture-') as tmp:
    root = Path(tmp) / 'source'
    for relative in json.loads((E / 'source-pins.json').read_text())['files']:
        if relative == 'Allrun':
            continue
        source_file = E / 'payload-case' / relative
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = source_file.read_bytes()
        if relative == 'system/include/caseDefinition':
            raw = (E / 'payload-case/system/include/caseDefinition.H.expected').read_bytes()
        elif relative == 'system/decomposeParDict':
            import re
            text, count = re.subn(r'(?m)^([ \t]+order[ \t]+)xyz;', r'\g<1>xzy;', raw.decode())
            assert count == 1
            raw = text.encode()
        target.write_bytes(raw)
    (root / 'READY').write_text(json.loads((E / 'source-observations.json').read_text())['H']['READY'])
    result = source_check(root, 'xzy')
    assert result == {'passed': True, 'pinned_input_files': 41, 'order': 'xzy', 'factors': [7, 4, 2]}
    wrong_order = root / 'system/decomposeParDict'
    wrong_order.write_bytes((E / 'payload-case/system/decomposeParDict').read_bytes())
    try:
        source_check(root, 'xzy')
    except AssertionError:
        pass
    else:
        raise AssertionError('source checker accepted the wrong hierarchy order')

print('PASS: 52-step rejection of parent-40 evidence, ABBA grouping, common launch, and exact xzy source pins')
