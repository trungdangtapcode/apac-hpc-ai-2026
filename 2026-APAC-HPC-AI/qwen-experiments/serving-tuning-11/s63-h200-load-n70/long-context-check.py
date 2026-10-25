"""Independent synthetic retrieval diagnostic; never an organiser accuracy score."""
import concurrent.futures
import json
from pathlib import Path
import re
import sys
import time
import urllib.request
from transformers import AutoTokenizer

host,outdir=sys.argv[1:]
tokenizer=AutoTokenizer.from_pretrained('Qwen/Qwen3-235B-A22B-Instruct-2507',local_files_only=True)
filler=tokenizer.encode('The archive contains routine weather observations and shipping records. '*1000,add_special_tokens=False)
cases=[]
for index in range(12):
    value=str(73160429+index*137)
    key='archive_key_'+str(index)
    position=[400,1900,3400][index%3]
    before=tokenizer.decode(filler[:position])
    after=tokenizer.decode(filler[:3800-position])
    prompt=f'Record collection {index}.\n{before}\nThe unique value for {key} is {value}.\n{after}\nReturn only the eight-digit value for {key}. No explanation.'
    cases.append(dict(name=f'retrieval-{index}',prompt=prompt,expected=value,input_tokens=len(tokenizer.encode(prompt,add_special_tokens=False))))
def run(case):
    row=dict(case);started=time.monotonic()
    try:
        body={'model':'qwen','messages':[{'role':'user','content':case['prompt']}],
              'max_tokens':64,'temperature':0.0,'stream':False}
        request=urllib.request.Request('http://'+host+'/v1/chat/completions',json.dumps(body).encode(),{'Content-Type':'application/json'})
        with urllib.request.urlopen(request,timeout=60) as response:result=json.load(response)
        answer=result['choices'][0]['message']['content']
        row.update(response=result,text=answer,passed=answer.strip(' \t\n\r\"\'`.')==case['expected'])
    except Exception as exc:row.update(passed=False,error=str(exc))
    row['elapsed_s']=time.monotonic()-started
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(run,cases))
result=dict(scope='12 hand-generated ~3800-token retrieval checks; not full accuracy or formal PD equivalence',
            passed=sum(r['passed'] for r in rows),total=len(rows),errors=sum('error' in r for r in rows),cases=rows)
path=Path(outdir)/'long-context-check.json';path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='cases'}))
raise SystemExit(0 if result['passed']==result['total'] and result['errors']==0 else 1)
