"""Verify frozen token-control payload and reject incomplete actual-ID evidence."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import subprocess

O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('token_control',O/'token-control.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
response={'meta_info':dict(completion_tokens=200,prompt_tokens=4000,
                          output_token_logprobs=[[-.1,i,None] for i in range(200)],
                          finish_reason={'type':'length','length':200})}
assert len(m.observed(response,4000)['output_ids'])==200
rejected=0
for change in ['first_missing','invalid_id','wrong_prompt','wrong_finish','wrong_count','absent_ids']:
    candidate=copy.deepcopy(response);meta=candidate['meta_info']
    if change=='first_missing':meta['output_token_logprobs']=meta['output_token_logprobs'][1:]
    if change=='invalid_id':meta['output_token_logprobs'][0][1]=True
    if change=='wrong_prompt':meta['prompt_tokens']=3999
    if change=='wrong_finish':meta['finish_reason']={'type':'abort'}
    if change=='wrong_count':meta['completion_tokens']=199
    if change=='absent_ids':meta.pop('output_token_logprobs')
    try:m.observed(candidate,4000)
    except (ValueError,KeyError):rejected+=1
    else:raise AssertionError(change)
for path in O.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
for path in list(O.glob('*.sh'))+[O/'benchmark.pbs']:
    subprocess.run(['bash','-n',str(path)],check=True)
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=O,check=True,capture_output=True)
previous=O.parent/'nscc-pbs/h100-cpu-envelope-legacy-n54-79'
for name in ['worker.sh','nixl-conn.py']:
    assert (O/name).read_bytes()==(previous/name).read_bytes(),name
print(json.dumps(dict(passed=True,synthetic_rejections=rejected,frozen_payload_checked=True,
                     scope='CPU diagnostics only; not actual real-ID availability or inference acceptance')))
