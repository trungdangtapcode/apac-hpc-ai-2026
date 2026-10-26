#!/usr/bin/env python3
"""Check the TP4 parser against actual R6 metadata records (not a run pass)."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('equal_tp_gate',ROOT/'pd-observer/validate_receipts.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
fixture=ROOT/'fixtures/r6-observed-projection/pd-observer'
paths=sorted(fixture.glob('*/tp-*/metadata.json'))
assert len(paths)==8, len(paths)
result=module.validate(paths)
assert result['receipt_count']==8 and result['cross_role_names_and_widths_match']
assert result['roles']['prefill-0']['rank_ids']==[0,1,2,3]
assert result['roles']['decode-0']['rank_ids']==[0,1,2,3]
assert result['roles']['decode-0']['tp_size']==4
# The fixture rows are actual R6 observations projected from the TP8 D worker;
# this checks parser geometry only and does not claim a TP4 D startup.
print('ACTUAL R6 METADATA PARSER FIXTURE PASS; decode source was TP8, no TP4 runtime claim')
