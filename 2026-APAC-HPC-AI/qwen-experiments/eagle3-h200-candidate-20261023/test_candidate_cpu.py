"""CPU integration fixtures for the actual EAGLE3 client and independent head gate."""
import hashlib, http.server, json, os, shutil, socketserver, subprocess, sys, tempfile, threading, time, unittest
from pathlib import Path

SOURCE=Path(__file__).resolve().parent/'payload'
REFERENCE=json.loads((SOURCE/'accepted-h200-reference.json').read_text())

class CandidateCPU(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.bundle=self.base/'bundle';self.bundle.mkdir()
  names=['candidate-control.py','check-candidate-result.py','inspect-speculative-metadata.py','eagle_observation.py','token_observation.py','prepared-corpus.json','accepted-h200-reference.json','accepted-h200-reference-review.json','draft_identity.py','asset_identity.py','warmup_semantic.py','check-runtime.py','validate_kv_geometry.py']
  for name in names: shutil.copy2(SOURCE/name,self.bundle/name)
  # Stable fixture versions preserve the identity interfaces while avoiding external cluster paths.
  (self.bundle/'asset_identity.py').write_text('''import hashlib,json,os\nfrom pathlib import Path\ndef verify_asset_identity(manifest_path,model_path,image_path):\n m=json.loads(Path(manifest_path).read_text()); assert m['state']=='PASS'; assert hashlib.sha256(Path(image_path).read_bytes()).hexdigest()==m['image_sha256']; return {'fixture_manifest_sha256':hashlib.sha256(Path(manifest_path).read_bytes()).hexdigest(),'image_sha256':m['image_sha256']}\n''')
  (self.bundle/'draft_identity.py').rename(self.bundle/'draft_identity.py')
  (self.bundle/'draft_identity.py').write_text('''import json,hashlib\nfrom pathlib import Path\ndef verify_post_full_fingerprint(draft,full_path):\n x=json.loads(Path(full_path).read_text()); p=Path(draft)/'model.safetensors'; st=p.stat(); fp={'st_dev':st.st_dev,'st_ino':st.st_ino,'st_size':st.st_size,'st_mtime_ns':st.st_mtime_ns,'st_ctime_ns':st.st_ctime_ns}; assert x['files'][0]['fingerprint']==fp; return {'state':'PASS','fingerprint':fp}\n''')
  self.model=self.base/'model';self.model.mkdir();self.image=self.base/'image.sqsh';self.image.write_bytes(b'fixture-image')
  image_sha=hashlib.sha256(self.image.read_bytes()).hexdigest();(self.bundle/'asset-verification.json').write_text(json.dumps({'state':'PASS','image_sha256':image_sha}))
  self.draft=self.base/'draft';self.draft.mkdir();weight=self.draft/'model.safetensors';weight.write_bytes(b'fixture-draft-bytes');st=weight.stat();fp={'st_dev':st.st_dev,'st_ino':st.st_ino,'st_size':st.st_size,'st_mtime_ns':st.st_mtime_ns,'st_ctime_ns':st.st_ctime_ns}
  self.full={'state':'PASS','revision':'ff0f0c0999f6c86b21dfd2f5803eebc4ac712224','files':[{'path':str(weight),'fingerprint':fp,'sha256':'bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86'}]}
  self.art=self.base/'artifact';self.art.mkdir();(self.art/'draft-full-verification.json').write_text(json.dumps(self.full))
  # Two semantic receipts from both expected pair paths; production checker replays response hashes and inventory.
  endpoints=self.art/'endpoints.tsv';endpoints.write_text('prefill-0\thttp://127.0.0.1:30100\t9000\nprefill-1\thttp://127.0.0.1:30101\t9001\ndecode-0\thttp://127.0.0.1:30200\t0\n')
  from importlib.util import spec_from_file_location,module_from_spec
  spec=spec_from_file_location('warmup_semantic_fixture',SOURCE/'warmup_semantic.py');m=module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
  self.run_token=hashlib.sha256(b'fixture-exp').hexdigest()[:32];receipt_dir=self.art/'pair-warmup-receipts';receipt_dir.mkdir();inv_hash,pairs,rows=m.inventory(endpoints)
  for pair in pairs:
   pid=pair['pair_id']; response={'http_status':200,'body':{'choices':[{'message':{'role':'assistant','content':'hello'}}],'usage':{'prompt_tokens':3,'completion_tokens':2,'total_tokens':5}}}
   (receipt_dir/f'response-{pid}.json').write_text(json.dumps(response,sort_keys=True,separators=(',',':')))
   from warmup_semantic_fixture import validate_response
   evidence=validate_response(response['http_status'],response['body'])
   rec={'schema':'pair-warmup-semantic-v1','pair_id':pid,'prefill':pair['prefill'],'decode':pair['decode'],'run_token':self.run_token,'inventory_sha256':inv_hash,'http_status':200,**evidence,'response_sha256':hashlib.sha256(json.dumps(response,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
   (receipt_dir/f'receipt-{pid}.json').write_text(json.dumps(rec))
  # Runtime logs and complete 16-rank geometry receipts feed the same production head gates.
  draft_path='/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09'
  for role,n in (('prefill-0',4),('prefill-1',4),('decode-0',8)):
   lines=[]
   for rank in range(n):
    lines += [f'[TP{rank} EP{n}] KV Cache is allocated. dtype: torch.bfloat16']*2
    lines += [f'[TP{rank} EP{n}] NIXL KVManager initialized']
    lines += [f"[TP{rank} EP{n}] Disable prefill CUDA graph because cuda_graph_config resolved prefill.backend='disabled'"]*2
   if role.startswith('prefill'): role_args="model_path='/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8', dtype='bfloat16', context_length=8192, mem_fraction_static=0.9, trust_remote_code=True, disaggregation_transfer_backend='nixl', kv_cache_dtype='auto', disaggregation_mode='prefill', tp_size=4, ep_size=1, chunked_prefill_size=8192, moe_runner_backend='deep_gemm', "; graph_args="cuda_graph_config=CudaGraphConfig(decode=PhaseConfig(backend='disabled'), prefill=PhaseConfig(backend='disabled')), "
   else: role_args="model_path='/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8', dtype='bfloat16', context_length=8192, mem_fraction_static=0.9, trust_remote_code=True, disaggregation_transfer_backend='nixl', kv_cache_dtype='auto', disaggregation_mode='decode', tp_size=8, ep_size=8, moe_runner_backend='hpc_ops', decode_attention_backend='flashinfer', flashinfer_allreduce_fusion_backend='mnnvl', "; graph_args="cuda_graph_config=CudaGraphConfig(decode=PhaseConfig(backend='full', max_bs=64, bs=["+', '.join(map(str,range(1,65)))+"], tc_compiler='eager'), prefill=PhaseConfig(backend='disabled')), "
   spec_args=f"speculative_algorithm='EAGLE3', speculative_draft_model_path='{draft_path}', speculative_num_steps=2, speculative_eagle_topk=1, speculative_num_draft_tokens=3, speculative_draft_attention_backend='flashinfer', speculative_draft_model_quantization=None"
   lines += [f'server_args=ServerArgs({role_args}{graph_args}{spec_args})', 'The server is fired up and ready to roll!']
   if role=='decode-0': lines += ['Capture draft decode CUDA graph end','Capture draft extend CUDA graph end']
   (self.art/f'{role}.log').write_text('\n'.join(lines)+'\n')
  gate=subprocess.run([sys.executable,str(self.bundle/'check-runtime.py'),str(self.art),str(self.bundle)],capture_output=True,text=True)
  self.assertEqual(gate.returncode,0,gate.stdout+gate.stderr);(self.art/'runtime-readiness.json').write_text(gate.stdout)
  geo=self.art/'kv-geometry';geo.mkdir();experiment='fixture-exp'
  for role,n in (('prefill-0',4),('prefill-1',4),('decode-0',8)):
   for rank in range(n):
    common={'schema':'h200-kv-registration-geometry-v1','role_name':role,'experiment_id':experiment,'engine_rank':rank,'pp_rank':0,'gpu_rank':rank,'tp_size':n,'page_size_tokens':16,'kv_head_num':8,'total_kv_head_num':64,'kv_layer_ids':[0],'kv_regions':[{'index':0,'region_bytes':4096,'item_bytes':256,'page_stride_bytes':256,'memory_kind':'VRAM','page_count':16,'token_stride_bytes':16}],'aux_region_lengths_bytes':[],'state_region_lengths_bytes':[],'dtype':'not_collected','tensor_strides':'not_collected'}
    for phase,returned in (('before',None),('after',True)):
     record=dict(common,phase=phase,registration_returned=returned);(geo/f'{role}-{rank}-{phase}.json').write_text(json.dumps(record))
  geo_check=subprocess.run([sys.executable,str(self.bundle/'validate_kv_geometry.py'),str(geo),'--experiment-id',experiment,'--expected-role','prefill-0=4','--expected-role','prefill-1=4','--expected-role','decode-0=8'],capture_output=True,text=True)
  self.assertEqual(geo_check.returncode,0,geo_check.stdout+geo_check.stderr);(self.art/'kv-geometry-validation.json').write_text(geo_check.stdout)
  self.server_mode='ok'; self.calls=0
  testcase=self
  class Handler(http.server.BaseHTTPRequestHandler):
   def do_POST(inner):
    body=json.loads(inner.rfile.read(int(inner.headers['Content-Length'])));idx=testcase.calls;testcase.calls+=1
    if testcase.server_mode=='http' and idx==0: inner.send_error(500);return
    stage='target-a';case_idx=idx%4; row=REFERENCE['stages'][stage][case_idx]; response=json.loads(json.dumps(row['response']));meta=response['meta_info']
    if testcase.server_mode=='short': meta['completion_tokens']=199;meta['output_token_logprobs']=meta['output_token_logprobs'][:199]
    if testcase.server_mode=='changed_id' and idx>=4: meta['output_token_logprobs'][0][1]=(meta['output_token_logprobs'][0][1]+1)%151936
    if testcase.server_mode=='changed_finish' and idx==0: meta['finish_reason']={'type':'stop'}
    meta.update({'spec_verify_ct':100,'spec_num_correct_drafts':100,'spec_num_proposed_drafts':200,'spec_accept_rate':0.5,'spec_accept_length':2.0})
    if testcase.server_mode=='missing_counter': meta.pop('spec_verify_ct',None)
    if testcase.server_mode=='bad_counter': meta['spec_accept_rate']=0.9
    raw=json.dumps(response).encode();inner.send_response(200);inner.send_header('Content-Length',str(len(raw)));inner.end_headers();inner.wfile.write(raw)
   def log_message(inner,*args): pass
  class Server(socketserver.ThreadingMixIn,http.server.HTTPServer): daemon_threads=True
  self.server=Server(('127.0.0.1',0),Handler);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
  self.env=dict(os.environ,QWEN_EXPERIMENT_ID='fixture-exp',QWEN_CLIENT_DEADLINE_EPOCH=str(time.time()+40),QWEN_IMAGE_PATH=str(self.image),QWEN_DRAFT_PATH=str(self.draft))
 def tearDown(self): self.server.shutdown();self.server.server_close();self.thread.join(timeout=2);self.tmp.cleanup()
 def run_client(self,mode='ok',art=None):
  self.server_mode=mode;self.calls=0;art=art or self.art
  return subprocess.run([sys.executable,str(self.bundle/'candidate-control.py'),f'127.0.0.1:{self.server.server_port}',str(self.model),str(art)],env=self.env,capture_output=True,text=True,timeout=30)
 def test_execution_paths_are_h200_staged_and_deadlines_share_t0(self):
  files=[SOURCE/name for name in ('topology-job.sh','worker.sh','check-runtime.py','candidate-control.py','check-candidate-result.py','inspect-speculative-metadata.py','config.json')]
  old='/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/drafts/nebius-eagle3-qwen235b-ff0f0c09'
  new='/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09'
  for path in files:
   raw=path.read_text();self.assertNotIn(old,raw,path.name)
   if path.name in ('topology-job.sh','worker.sh','check-runtime.py'): self.assertIn(new,raw,path.name)
  topology=(SOURCE/'topology-job.sh').read_text();self.assertIn('draft_verifier_remaining=$((STARTUP_DEADLINE-$(date +%s)))',topology)
  self.assertIn('timeout --signal=TERM --kill-after=5s "$draft_verifier_remaining"',topology)
 def test_runtime_gate_rejects_malformed_duplicate_and_graph_gap(self):
  path=self.art/'decode-0.log';original=path.read_text()
  cases=[]
  cases.append(('duplicate-record',original+next(line+'\n' for line in original.splitlines() if 'server_args=ServerArgs(' in line)))
  cases.append(('malformed',original.replace('server_args=ServerArgs(', 'server_args=ServerArgs(',1).replace('ServerArgs(', 'ServerArgs(',1).rsplit(')',1)[0]))
  graph_gap=original.replace(', 32,', ',').replace('[1, 2, 3, 4', '[1, 2, 3, 4',1)
  graph_gap=graph_gap.replace('bs=['+', '.join(map(str,range(1,65)))+']', 'bs=['+', '.join(str(i) for i in range(1,65) if i!=32)+']')
  cases.append(('graph-gap',graph_gap))
  for name,content in cases:
   with self.subTest(name=name):
    path.write_text(content)
    result=subprocess.run([sys.executable,str(self.bundle/'check-runtime.py'),str(self.art),str(self.bundle)],capture_output=True,text=True)
    self.assertNotEqual(result.returncode,0,name)
  path.write_text(original)
 def test_actual_client_and_head_gate_use_all_reference_ids(self):
  self.assertEqual(self.run_client().returncode,0)
  result=json.loads((self.art/'eagle3-candidate.json').read_text())
  self.assertEqual(sum(len(r['observed']['output_ids']) for stage in result['stages'].values() for r in stage),1600)
  self.assertEqual([c['output_ids'] for c in [r['observed'] for r in result['stages']['eagle-a']]], [r['observed']['output_ids'] for r in REFERENCE['stages']['target-a']])
  # Production head gate recomputes all observations, counter identities, and reference comparisons.
  checker=subprocess.run([sys.executable,str(self.bundle/'check-candidate-result.py'),str(self.art/'eagle3-candidate.json'),str(self.model)],env=self.env,capture_output=True,text=True,timeout=10)
  self.assertEqual(checker.returncode,0,checker.stdout+checker.stderr)
 def test_client_rejects_incomplete_http_id_finish_and_counter_failures(self):
  for mode in ('short','http','changed_id','changed_finish','missing_counter','bad_counter'):
   with self.subTest(mode=mode):
    art=self.base/f'art-{mode}';art.mkdir()
    # Fresh pair artifacts and full verification are required for every independent attempt.
    shutil.copy2(self.art/'draft-full-verification.json',art/'draft-full-verification.json')
    shutil.copytree(self.art/'pair-warmup-receipts',art/'pair-warmup-receipts')
    shutil.copy2(self.art/'endpoints.tsv',art/'endpoints.tsv')
    for name in ('runtime-readiness.json','kv-geometry-validation.json','prefill-0.log','prefill-1.log','decode-0.log'):
     shutil.copy2(self.art/name,art/name)
    shutil.copytree(self.art/'kv-geometry',art/'kv-geometry')
    result=self.run_client(mode,art)
    self.assertNotEqual(result.returncode,0,mode)
    captured=json.loads((art/'eagle3-candidate.json').read_text())
    self.assertFalse(captured['passed'])
 def test_head_rejects_falsepass_seed_tamper_asset_tamper_and_draft_tamper(self):
  self.assertEqual(self.run_client().returncode,0)
  path=self.art/'eagle3-candidate.json';original=json.loads(path.read_text())
  changes=[]
  changed=json.loads(json.dumps(original));changed['stages']['eagle-a'][0]['request']['sampling_params']['sampling_seed']=2027;changes.append(('seed',changed))
  changed=json.loads(json.dumps(original));changed['stages']['eagle-a'][0]['observed']['output_ids'][0]+=1;changes.append(('id',changed))
  changed=json.loads(json.dumps(original));changed['stages']['eagle-a'][0]['observed']['output_ids'][0]+=1;changes.append(('falsepass_with_invalid_ids',changed))
  for name,mutated in changes:
   with self.subTest(name=name):
    path.write_text(json.dumps(mutated));check=subprocess.run([sys.executable,str(self.bundle/'check-candidate-result.py'),str(path),str(self.model)],env=self.env,capture_output=True,text=True);self.assertNotEqual(check.returncode,0)
  path.write_text(json.dumps(original));refpath=self.bundle/'accepted-h200-reference.json';refraw=refpath.read_bytes();refpath.write_bytes(refraw+b'\n');refcheck=subprocess.run([sys.executable,str(self.bundle/'check-candidate-result.py'),str(path),str(self.model)],env=self.env,capture_output=True,text=True);self.assertNotEqual(refcheck.returncode,0);refpath.write_bytes(refraw);self.image.write_bytes(b'tampered');check=subprocess.run([sys.executable,str(self.bundle/'check-candidate-result.py'),str(path),str(self.model)],env=self.env,capture_output=True,text=True);self.assertNotEqual(check.returncode,0)
  self.image.write_bytes(b'fixture-image');self.draft.joinpath('model.safetensors').write_bytes(b'tampered');check=subprocess.run([sys.executable,str(self.bundle/'check-candidate-result.py'),str(path),str(self.model)],env=self.env,capture_output=True,text=True);self.assertNotEqual(check.returncode,0)

if __name__=='__main__': unittest.main(verbosity=2)
