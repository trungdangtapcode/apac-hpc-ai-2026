"""Synthetic gate fixtures derived from real log syntax, never new measurements."""
from pathlib import Path
import importlib.util,json,shutil,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SOURCE=ROOT/'runs/25487'
REF=ROOT/'runs/25585'

def load(path):
 spec=importlib.util.spec_from_file_location('head_screen_fixture',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def fixture(root,policy):
 proposal=next(p for p in (HERE/'proposals').iterdir() if ('disabled' in p.name)==(policy=='disabled'))
 sys.path.insert(0,str(proposal));m=load(proposal/'check-screen.py')
 art=root/policy;art.mkdir();shutil.copyfile(proposal/'config.json',art/'config.json')
 for role in ['prefill-0','prefill-1','decode-0']:
  text=(SOURCE/(role+'.log')).read_text(errors='replace').replace("dtype='auto'","dtype='bfloat16'")
  if role.startswith('prefill'):
   text=text.replace('max_running_requests=None','max_running_requests=64').replace('max_running_requests=4096','max_running_requests=64')
  if policy=='disabled':
   text=text.replace('cuda_graph_backend_prefill=None',"cuda_graph_backend_prefill='disabled'").replace("prefill=PhaseConfig(backend='breakable'","prefill=PhaseConfig(backend='disabled'")
   if role.startswith('prefill'):text='\n'.join(line for line in text.splitlines() if 'Capture target prefill CUDA graph' not in line)+'\n'
  (art/(role+'.log')).write_text(text)
 for name in ['endpoints.tsv','pair-warmup-context.json']:
  shutil.copyfile(REF/name,art/name)
 shutil.copytree(REF/'pair-warmup-receipts',art/'pair-warmup-receipts')
 for name in ['output-smoke.json','long-context-check.json']:shutil.copyfile(SOURCE/name,art/name)
 run=art/'screen/n64';exp=run/'artifacts';exp.mkdir(parents=True)
 example=json.loads((SOURCE/'confirm/n64/artifacts/profile_export_aiperf.json').read_text())
 example['input_config']=json.loads((proposal/'expected-input-config.json').read_text());example['input_config']['endpoint']['urls']=['http://fixture:8000'];example['input_config']['artifacts']['dir']=str(exp)
 example['goodput']['avg']=.05;example['good_request_fraction']['avg']=1.0;example['request_count']['avg']=2
 (exp/'profile_export_aiperf.json').write_text(json.dumps(example))
 rows=[]
 for line in (SOURCE/'confirm/n64/artifacts/profile_export.jsonl').open():
  row=json.loads(line)
  if row['metadata']['benchmark_phase']=='profiling':
   rows.append(row)
   if len(rows)==2:break
 assert all(x['metrics']['time_to_first_token']['value']<=3000 and x['metrics']['inter_token_latency']['value']<=20 for x in rows)
 (exp/'profile_export.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))
 (run/'client.log').write_text('Phase profiling (profiling) complete | completed=2, cancelled=0, errors=0 | synthetic fixture\n')
 return art,m

with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp)
 for policy in ['auto','disabled']:
  art,m=fixture(root,policy);assert m.validate(art)['status']=='pass'
  exp=art/'screen/n64/artifacts/profile_export_aiperf.json';original=exp.read_text();v=json.loads(original);v['input_config']['phases'][1]['duration']=120;exp.write_text(json.dumps(v))
  try:m.validate(art)
  except AssertionError as e:assert 'protocol differs' in str(e)
  else:raise AssertionError('wrong duration accepted')
  exp.write_text(original)
  raw=exp.parent/'profile_export.jsonl';original=raw.read_text();rows=[json.loads(x) for x in original.splitlines()];rows[0]['metrics']['inter_token_latency']['value']=25;raw.write_text(''.join(json.dumps(x)+'\n' for x in rows))
  try:m.validate(art)
  except AssertionError as e:assert 'raw SLA' in str(e)
  else:raise AssertionError('wrong SLA count accepted')
  raw.write_text(original)
  p=art/'output-smoke.json';original=p.read_text();v=json.loads(original);v['cases'][0]['response']['choices'][0]['message']['content']='wrong';v['cases'][0]['text']='wrong';v['cases'][0]['passed']=False;p.write_text(json.dumps(v))
  try:m.validate(art)
  except AssertionError as e:assert 'regressions' in str(e)
  else:raise AssertionError('new output failure accepted')
  p.write_text(original)
  (art/'decode-0.log').write_text((art/'decode-0.log').read_text().replace('Capture target decode CUDA graph end.','no graph receipt'))
  try:m.validate(art)
  except AssertionError as e:assert 'capture receipts missing' in str(e)
  else:raise AssertionError('missing decode graph capture accepted')
print('PASS: two synthetic full head fixtures; each rejects wrong duration, raw SLA mismatch, output regression and missing graph receipts')
