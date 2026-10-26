#!/usr/bin/env python3
"""Fail-closed raw AIPerf, output-smoke and retrieval acceptance for this N24 probe."""
from pathlib import Path
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gates',HERE/'performance_gates.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
stage=sys.argv[1];art=Path(sys.argv[2]);expected=json.loads((HERE/'expected-input-config.json').read_text())
try:
 score=g.check_aiperf(art,expected,200)
 result={'state':'PASS_N24_SCORE_GATES_NOT_OFFICIAL_ACCURACY','score':score,'official_accuracy':'UNKNOWN'}
 if stage=='full':
  smoke=g.check_smoke(art,HERE/'reference-output-smoke.json')
  retrieval=g.check_retrieval(art)
  result={'state':'PASS_LOCAL_N24_NOT_OFFICIAL_ACCURACY','score':score,'smoke':smoke,'retrieval':retrieval,'official_accuracy':'UNKNOWN'}
 elif stage!='score':raise ValueError('stage must be score or full')
 print(json.dumps(result,indent=2))
 raise SystemExit(0)
except Exception as exc:
 print(json.dumps({'state':'FAIL','error':f'{type(exc).__name__}: {exc}','official_accuracy':'UNKNOWN'},indent=2));raise SystemExit(1)
