import hashlib,importlib.util,json
from pathlib import Path
root=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01')
out=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0530UTC')
spec=importlib.util.spec_from_file_location('capture',root/'capture-native-tokens.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=root/'token-suite-v1'
suite=json.loads((p/'suite.json').read_bytes())
m.preflight(suite,Path('/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8/tokenizer.json').read_bytes(),'http://127.0.0.1:30000/generate')
rows=json.loads((p/'prompts.json').read_text()); cases=suite['cases']
assert len(cases)==14 and len(rows)==14
assert len({x['case_id'] for x in cases})==14
assert all(x['request']['input_ids']==cases[0]['request']['input_ids'] for x in cases[:5])
assert [x['request']['sampling_params']['max_new_tokens'] for x in cases[:5]]==[1,3,4,5,200]
assert all(len(c['request']['input_ids'])==r['input_tokens_including_chat_template'] for c,r in zip(cases,rows))
assert all(hashlib.sha256((p/name).read_bytes()).hexdigest()==sha for sha,name in (x.split() for x in (p/'SHA256SUMS').read_text().splitlines()))
assert all(r['target_input_tokens']-40<=r['input_tokens_including_chat_template']<=r['target_input_tokens'] for r in rows if 'target_input_tokens' in r)
report={'state':'OFFLINE_SUITE_PREFLIGHT_PASS_NO_HTTP_MODEL_GPU','case_count':len(cases),'case_input_tokens':{r['case_id']:r['input_tokens_including_chat_template'] for r in rows},'max_input_plus_cap':max(len(x['request']['input_ids'])+x['request']['sampling_params']['max_new_tokens'] for x in cases),'same_prompt_boundary_caps':[1,3,4,5,200],'seal_verified':True,'capture_preflight_passed':True,'http_contacted':False,'model_executed':False,'eos_observed':False,'versions':json.loads((p/'provenance.json').read_text())['versions'],'script_sha256':hashlib.sha256((root/'prepare-token-suite.py').read_bytes()).hexdigest()}
(out/'suite-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
