from pathlib import Path
import importlib.util,copy,json,hashlib
O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('token_equivalence',O/'token-equivalence.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
a={'stage':'target-a','platform':'H200','passed':True,'target_manifest_sha256':'a'*64,'requests':m.requests(),'responses':[{'name':r['name'],'response':{'choices':[{'index':0,'finish_reason':'length','prompt_token_ids':[1,2],'token_ids':[3,4],'message':{'content':'same decoded text'}}]}} for r in m.requests()]}
b=copy.deepcopy(a);b['stage']='target-b';assert m.compare(a,b)['passed']
rows=[{'case':'Identical actual IDs with matched inputs','passed':True}]
def check(name,mutate,raises=True):
 c=copy.deepcopy(b);mutate(c)
 try:result=m.compare(a,c);passed=not raises and not result['passed']
 except (ValueError,KeyError):passed=raises
 assert passed,name
 rows.append({'case':name,'passed':passed})
check('Same decoded text, different generated IDs',lambda c:c['responses'][0]['response']['choices'][0].update(token_ids=[3,5]),False)
check('Different prompt IDs',lambda c:c['responses'][0]['response']['choices'][0].update(prompt_token_ids=[2,1]),False)
check('Shorter output with matching prefix',lambda c:c['responses'][0]['response']['choices'][0].update(token_ids=[3]),False)
check('Changed finish reason',lambda c:c['responses'][0]['response']['choices'][0].update(finish_reason='stop'),False)
check('Text-only gateway response',lambda c:c['responses'][0]['response']['choices'][0].pop('token_ids'))
check('Boolean is not a token ID',lambda c:c['responses'][0]['response']['choices'][0].update(token_ids=[True]))
check('Out-of-vocabulary ID',lambda c:c['responses'][0]['response']['choices'][0].update(token_ids=[151936]))
check('Missing response',lambda c:c['responses'].pop())
check('Changed request seed',lambda c:c['requests'][0]['body'].update(seed=1))
check('Different platform',lambda c:c.update(platform='H100'))
check('Different target manifest',lambda c:c.update(target_manifest_sha256='b'*64))
check('Failed capability capture',lambda c:c.update(passed=False))
result={'scope':'Synthetic adversarial CPU fixtures for the diagnostic comparator; no live gateway, model or GPU result','passed':True,'cases':rows,'script_sha256':hashlib.sha256((O/'token-equivalence.py').read_bytes()).hexdigest()}
(O/'token-equivalence-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(len(rows),'passed')
