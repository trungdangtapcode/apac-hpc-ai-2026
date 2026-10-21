"""Adversarial semantic-guard tests using reference-derived fixtures, not inference."""
from pathlib import Path
import ast,copy,hashlib,json,subprocess,tempfile,importlib.util
O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('tokens',O/'token-control.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ref=json.loads((O/'target-reference.json').read_text());base=copy.deepcopy(ref)
base['stages']={'draft-a':base['stages']['target-a'],'draft-b':base['stages']['target-b']}
base['passed']=True
outcomes=[]
with tempfile.TemporaryDirectory(prefix='eagle3-guard-') as temporary:
 p=Path(temporary)/'fixture.json'
 for case in ['valid_reference_fixture','same_text_different_ids','missing_first_id','changed_prompt','changed_finish','missing_response','changed_identity','changed_platform','false_pass']:
  value=copy.deepcopy(base)
  if case=='same_text_different_ids':
   for stage in ['draft-a','draft-b']:
    row=value['stages'][stage][0];row['response']['meta_info']['output_token_logprobs'][0][1]=(row['response']['meta_info']['output_token_logprobs'][0][1]+1)%151936
    row['observed']=m.observed(row['response'],len(row['request']['input_ids']))
  if case=='missing_first_id':value['stages']['draft-a'][0]['response']['meta_info']['output_token_logprobs'].pop(0)
  if case=='changed_prompt':value['stages']['draft-a'][0]['request']['input_ids'][0]=1
  if case=='changed_finish':value['stages']['draft-a'][0]['response']['meta_info']['finish_reason']={'type':'abort'}
  if case=='missing_response':value['stages']['draft-a'].pop()
  if case=='changed_identity':value['target_identity_sha256']='0'*64
  if case=='changed_platform':value['platform']='H200'
  if case=='false_pass':value['passed']=False
  p.write_text(json.dumps(value));r=subprocess.run(['python3',str(O/'check-token-result.py'),str(p)],capture_output=True,text=True)
  expected=case=='valid_reference_fixture';assert (r.returncode==0)==expected,(case,r.stderr)
  outcomes.append(dict(case=case,accepted=r.returncode==0,expected=expected))
for p in O.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in list(O.glob('*.sh'))+[O/'benchmark.pbs']:subprocess.run(['bash','-n',str(p)],check=True)
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=O,check=True,capture_output=True)
(O/'semantic-validation.json').write_text(json.dumps(dict(passed=True,cases=outcomes,scope='Reference-derived CPU fixtures only; no speculative inference or performance result'),indent=2)+'\n')
print('Semantic guard PASS:',len(outcomes),'reference-derived fixtures; no inference')
