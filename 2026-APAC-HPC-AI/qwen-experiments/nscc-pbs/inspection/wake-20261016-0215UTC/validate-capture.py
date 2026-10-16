"""Loopback mock only. No actual Qwen/model/GPU requests."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BRANCH=ROOT/'nscc-pbs/research-next/eagle3-01'
spec=importlib.util.spec_from_file_location('capture',BRANCH/'capture-native-tokens.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fixture=json.loads((ROOT/'nscc-pbs/inspection/wake-20261016-0205UTC/synthetic-control.json').read_text())
tokenizer=b'SYNTHETIC TOKENIZER ONLY\n'
(OUT/'synthetic-tokenizer.txt').write_bytes(tokenizer)
suite={k:fixture[k] for k in ('schema','target_revision','tokenizer_sha256')}
suite['tokenizer_sha256']=hashlib.sha256(tokenizer).hexdigest()
suite['cases']=[{k:fixture['cases'][0][k] for k in ('case_id','request')}]
response=fixture['cases'][0]['response']
mode={'name':'valid'};requests=[]
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  raw=self.rfile.read(int(self.headers['Content-Length']));requests.append(raw)
  r=copy.deepcopy(response);name=mode['name']
  if name=='count':r['meta_info']['completion_tokens']=99
  if name=='prompt':r['prompt_token_ids']=[999]
  if name=='difference':r['output_ids']=[31,33]
  if name=='tail':r['output_ids']=[31,32,33];r['meta_info']['completion_tokens']=3
  if name=='abort':r['meta_info']['finish_reason']={'type':'abort'}
  if name=='eos':r['output_ids']=[151645];r['meta_info'].update(completion_tokens=1,finish_reason={'type':'stop','matched':151645})
  body=json.dumps(r).encode()
  if name=='malformed':body=b'{broken'
  if name=='duplicate':body=b'{"output_ids": [1], "output_ids": [2]}'
  if name=='nan':body=b'{"bad":NaN}'
  status=500 if name=='http500' else 302 if name=='redirect' else 200
  self.send_response(status);self.send_header('Content-Type','application/json')
  if name=='redirect':self.send_header('Location','http://127.0.0.1:1/generate')
  if name=='partial':
   self.send_header('Content-Length',str(len(body)+100));self.end_headers();self.wfile.write(body[:10]);self.wfile.flush();self.close_connection=True;return
  self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
server=HTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
endpoint=f'http://127.0.0.1:{server.server_port}/generate'
results=[]
def check(name,fn):
 try:fn();results.append({'name':name,'pass':True})
 except Exception as e:results.append({'name':name,'pass':False,'error':repr(e)})
def run(name,valid=True):
 mode['name']=name;p=OUT/f'suite-{name}.json';p.write_text(json.dumps(suite));d=OUT/f'mock-{name}'
 before=len(requests)
 try:
  m.capture(p,OUT/'synthetic-tokenizer.txt',endpoint,d,2)
 except (ValueError,OSError,m.http.client.HTTPException):
  assert not valid
 else:assert valid
 assert len(requests)==before+1
 assert (d/'000-request.json').read_bytes()==requests[-1]
 assert (d/'000-response.bin').exists()
 assert (d/'capture.json').exists()==valid
 assert (d/('status.json' if valid else 'failure.json')).exists()
 if name=='partial':assert (d/'000-response.bin').read_bytes()==json.dumps(response).encode()[:10]
 if valid:m.review.validate(json.loads((d/'capture.json').read_bytes()))
for name in ('valid','difference','eos'):check('http-'+name,lambda n=name:run(n))
for name in ('count','prompt','tail','abort','malformed','duplicate','nan','http500','redirect','partial'):
 check('http-reject-'+name,lambda n=name:run(n,False))

def compare():
 a=json.loads((OUT/'mock-valid/capture.json').read_text())
 b=json.loads((OUT/'mock-difference/capture.json').read_text())
 assert m.review.compare(a,a)['state']=='CAPTURED_CASES_MATCH'
 assert m.review.compare(a,b)['state']=='CAPTURED_CASES_DIFFER'
 assert m.review.compare(a,b)['cases'][0]['first_difference_index']==1
check('reviewer-roundtrip-match-and-difference',compare)

def reject_suite(name,modify):
 bad=copy.deepcopy(suite);modify(bad);p=OUT/f'reject-{name}.json';p.write_text(json.dumps(bad));d=OUT/f'reject-{name}'
 before=len(requests)
 try:m.capture(p,OUT/'synthetic-tokenizer.txt',endpoint,d,2)
 except (ValueError,TypeError,KeyError):pass
 else:raise AssertionError('accepted invalid suite')
 assert len(requests)==before and not d.exists()
mods={
 'hash':lambda s:s.update(tokenizer_sha256='a'*64),
 'revision':lambda s:s.update(target_revision='x'),
 'duplicate-case':lambda s:s['cases'].append(copy.deepcopy(s['cases'][0])),
 'stream':lambda s:s['cases'][0]['request'].update(stream=True),
 'sampling':lambda s:s['cases'][0]['request']['sampling_params'].update(temperature=1),
 'nan':lambda s:s['cases'][0]['request']['sampling_params'].update(temperature=float('nan')),
 'bool-token':lambda s:s['cases'][0]['request'].update(input_ids=[True]),
 'context':lambda s:s['cases'][0]['request'].update(input_ids=[1]*8192),
 'cap':lambda s:s['cases'][0]['request']['sampling_params'].update(max_new_tokens=201),
 'grammar':lambda s:s['cases'][0]['request']['sampling_params'].update(json_schema={}),
 'min':lambda s:s['cases'][0]['request']['sampling_params'].update(min_new_tokens=1),
 'missing-ids':lambda s:s['cases'][0]['request'].pop('input_ids'),
}
for name,fn in mods.items():check('preflight-'+name,lambda n=name,f=fn:reject_suite(n,f))

def reject_endpoint(url):
 try:m.preflight(suite,tokenizer,url)
 except ValueError:return
 raise AssertionError('endpoint accepted')
for index,url in enumerate(('http://192.0.2.1:80/generate','http://localhost:80/generate','http://u:p@127.0.0.1:80/generate','http://127.0.0.1:80/generate?q=x','http://127.0.0.1:80/other','http://127.0.0.1/generate','https://127.0.0.1:80/generate')):
 check(f'endpoint-{index}',lambda u=url:reject_endpoint(u))
def no_overwrite():
 before=len(requests);p=OUT/'suite-valid.json';d=OUT/'mock-valid';old=(d/'capture.json').read_bytes()
 try:m.capture(p,OUT/'synthetic-tokenizer.txt',endpoint,d,2)
 except FileExistsError:pass
 else:raise AssertionError('overwrote evidence')
 assert len(requests)==before and (d/'capture.json').read_bytes()==old
check('no-overwrite-or-extra-request',no_overwrite)
server.shutdown();server.server_close();thread.join()
report={'state':'LOOPBACK_SYNTHETIC_HTTP_ONLY_NO_MODEL_GPU','test_count':len(results),'all_pass':all(x['pass'] for x in results),'results':results,'source_sha256':hashlib.sha256((BRANCH/'capture-native-tokens.py').read_bytes()).hexdigest()}
(OUT/'capture-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert report['all_pass']
