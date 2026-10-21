"""Reject malformed/ambiguous tokenizer output before any allocated probe."""
from collections import UserDict
from pathlib import Path
import ast,json,subprocess
from token_ids import token_ids
O=Path(__file__).resolve().parent
assert token_ids([1,2])==[1,2]
assert token_ids(UserDict(input_ids=[1,2],attention_mask=[1,1]))==[1,2]
assert json.loads(json.dumps(dict(input_ids=token_ids(UserDict(input_ids=[1,2])))))['input_ids']==[1,2]
rejected=0
for value in [[],[True],[1.0],[-1],[151936],[[1,2]],{},'12',None]:
 try:token_ids(value)
 except (ValueError,KeyError):rejected+=1
 else:raise AssertionError(value)
for p in O.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for name in ['component.pbs','component-entry.sh']:subprocess.run(['bash','-n',str(O/name)],check=True)
(O/'validation.json').write_text(json.dumps(dict(passed=True,malformed_rejections=rejected,scope='Actual-image runtime still unverified; Mapping/list JSON normalization fixtures pass',max_su=128*4/60),indent=2)+'\n')
print('CPU tokenizer normalization PASS',rejected,'rejections')
