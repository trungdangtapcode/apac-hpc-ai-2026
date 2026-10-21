"""CPU tokenizer API/corpus gate inside the actual image; no target weights/inference."""
import argparse,hashlib,inspect,json,os
from pathlib import Path
from datetime import datetime,timezone
from token_ids import token_ids
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
result=dict(created_utc=datetime.now(timezone.utc).isoformat(),job=os.environ.get('PBS_JOBID'),passed=False,cases=[],gpu_operations=False,target_weights_loaded=False,inference_executed=False)
try:
 import transformers
 from transformers import AutoTokenizer
 expected=json.loads((Path(__file__).parent/'target-staging-record.json').read_text())
 assert expected['complete'] and not expected.get('errors')
 current={}
 for name,entry in expected['verified'].items():
  if name.endswith('.safetensors'):continue
  f=a.model/name;assert f.is_file() and f.stat().st_size==entry['bytes'],name
  digest=hashlib.sha256(f.read_bytes()).hexdigest();assert digest==entry['sha256'],name
  current[name]=digest
 result['target_revision']=expected['revision'];result['small_file_sha256']=current
 tokenizer=AutoTokenizer.from_pretrained(a.model,local_files_only=True,trust_remote_code=False)
 source=Path(inspect.getfile(tokenizer.__class__))
 result['runtime']=dict(transformers_version=transformers.__version__,tokenizer_class=type(tokenizer).__name__,class_source=str(source),class_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
 prompts=[('arithmetic','Compute 37 * 19. Explain the calculation briefly.'),('code','Write a Python function that reverses a list without mutating it.'),('unicode','Explain the relationship between “throughput” and “latency”.')]
 result['template_return_types']=[]
 for name,text in prompts:
  raw=tokenizer.apply_chat_template([dict(role='user',content=text)],tokenize=True,return_dict=False,return_tensors=None,add_generation_prompt=True,enable_thinking=False)
  ids=token_ids(raw)
  result['template_return_types'].append(dict(name=name,type=type(raw).__name__))
  result['cases'].append(dict(name=name,input_ids=ids))
 marker='AP42_UNIQUE_CONTEXT_MARKER'
 rendered=tokenizer.apply_chat_template([dict(role='user',content=marker)],tokenize=False,add_generation_prompt=True,enable_thinking=False)
 assert isinstance(rendered,str) and rendered.count(marker)==1
 before,after=rendered.split(marker)
 prefix=token_ids(tokenizer.encode(before,add_special_tokens=False));suffix=token_ids(tokenizer.encode(after,add_special_tokens=False))
 content=token_ids(tokenizer.encode(('A serving queue holds requests waiting for available compute. Explain the difference between waiting and processing. '*500),add_special_tokens=False))
 long_ids=prefix+content[:4000-len(prefix)-len(suffix)]+suffix;assert len(long_ids)==4000
 result['cases'].append(dict(name='long4000',input_ids=token_ids(long_ids)))
 assert len(result['cases'])==4
 json.dumps(result) # Fail before success if any retained object is not serializable.
 result['passed']=True
except Exception as error:
 result['failure']=dict(type=type(error).__name__,message=str(error))
a.out.write_text(json.dumps(result,indent=2)+'\n')
raise SystemExit(0 if result['passed'] else 1)
