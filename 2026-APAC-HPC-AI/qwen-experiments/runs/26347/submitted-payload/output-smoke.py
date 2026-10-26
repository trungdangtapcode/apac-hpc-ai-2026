"""Small output sanity checks, separate from benchmark and organiser accuracy."""
import concurrent.futures
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

host, directory = sys.argv[1:]
cases = [
    ('addition', 'What is 17 + 25? Answer with only the integer.', '42'),
    ('multiplication', 'What is 99 multiplied by 7? Answer with only the integer.', '693'),
    ('capital', 'What is the capital of Japan? Answer with only the city name.', 'tokyo'),
    ('reverse', 'Reverse the ASCII string cluster. Answer with only the reversed string.', 'retsulc'),
    ('sort', 'Sort these integers in ascending order: 9, 3, 7. Return only a JSON array.', [3,7,9]),
    ('sequence', 'Complete the arithmetic sequence: 5, 10, 15, ?. Answer with only the integer.', '20'),
    ('classification', 'Is a cat a mammal? Answer with only yes or no.', 'yes'),
    ('json', 'Return exactly a JSON object whose only key is ok and whose value is true.', {'ok':True}),
]

def run(case):
    name, prompt, expected = case
    started=time.monotonic()
    row={'name':name,'prompt':prompt,'expected':expected}
    try:
        body={'model':'qwen','messages':[{'role':'user','content':prompt}],
              'max_tokens':64,'temperature':0.0,'stream':False}
        request=urllib.request.Request('http://'+host+'/v1/chat/completions',
                json.dumps(body).encode(),{'Content-Type':'application/json'})
        with urllib.request.urlopen(request,timeout=60) as response:
            result=json.load(response)
        text=result['choices'][0]['message']['content']
        stripped=re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip(), flags=re.I).strip()
        if isinstance(expected,(dict,list)):
            try:passed=json.loads(stripped)==expected
            except ValueError:passed=False
        else:passed=stripped.strip('"\'` .\n').lower()==expected
        row.update(response=result,text=text,passed=passed)
    except Exception as error:
        row.update(passed=False,error=str(error))
    row['elapsed_s']=time.monotonic()-started
    return row

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    rows=list(pool.map(run,cases))
out=Path(directory)/'output-smoke.json'
out.write_text(json.dumps({'scope':'Eight hand-written output sanity cases; not MMLU-Pro, GPQA or the organiser accuracy gate',
                          'passed':sum(r['passed'] for r in rows),'total':len(rows),'cases':rows},indent=2)+'\n')
print(json.dumps({'passed':sum(r['passed'] for r in rows),'total':len(rows),'output':str(out)}))
