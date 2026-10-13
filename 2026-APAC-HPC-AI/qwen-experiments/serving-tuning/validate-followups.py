import ast,copy,importlib.util,json,sys,types,argparse
from pathlib import Path
root=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');engine=root/'serving-tuning/inspection'
spec=importlib.util.spec_from_file_location('apac_arg_utils',engine/'arg_groups/arg_utils.py');helper=importlib.util.module_from_spec(spec);sys.modules[spec.name]=helper;spec.loader.exec_module(helper)
tree=ast.parse((engine/'server_args.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ServerArgs')
fields=[n for n in cls.body if isinstance(n,ast.AnnAssign) and getattr(n.target,'id','') in {'chunked_prefill_size','moe_runner_backend'}];assert len(fields)==2
choices=next(n for n in tree.body if isinstance(n,ast.Assign) and any(getattr(t,'id','')=='MOE_RUNNER_BACKEND_CHOICES' for t in n.targets))
module=types.ModuleType('apac_extra_args');sys.modules[module.__name__]=module
source='from typing import Optional,List\nfrom dataclasses import dataclass\nfrom apac_arg_utils import A,NS,Arg\n'+ast.unparse(choices)+'\n@dataclass\nclass ThinArgs:\n'+''.join('    '+ast.unparse(n)+'\n' for n in fields);exec(source,module.__dict__)
parser=argparse.ArgumentParser();helper.add_cli_args_from_dataclass(parser,module.ThinArgs)
a=parser.parse_args(['--chunked-prefill-size','4096','--moe-runner-backend','deep_gemm']);assert a.chunked_prefill_size==4096 and a.moe_runner_backend=='deep_gemm'
spec=importlib.util.spec_from_file_location('apac_watch_tuning',root/'watch-serving-tuning.py');watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
requests=[]
def fake_submit(state,name,source,ns,purpose,role_flags=None):
 if any(e['id']==name for e in state['entries']):return
 requests.append((name,ns,role_flags));state['entries'].append({'id':name})
watch.submit_followup=fake_submit
m={'concurrency':48,'requests':100,'errors':0,'cancelled_requests':0,'good_output_tokens_s':100,'sla_pass':True}
base={'entries':[{'id':'control-load','state':'MEASURED','bundle':'mock-control','measurements':[dict(m)],'profile_complete':None,'traces':[]},{'id':'dense-decode-graphs','state':'MEASURED','bundle':'mock-dense','measurements':[dict(m,good_output_tokens_s=106)],'profile_complete':None,'traces':[]},{'id':'profile-control','state':'MEASURED','bundle':'mock-profile','measurements':[dict(m)],'profile_complete':True,'traces':[{'trace':'runs/mock/diagnostic-profile/decode-0/example.trace.json','kernels':300,'moe_fraction_of_summed_kernel_time':.30}]}]}
case=copy.deepcopy(base);watch.advance_plan(case);assert {r[0] for r in requests}=={'prefill-chunk4096','decode-deepgemm','dense-graphs-repeat'};watch.advance_plan(case);assert len(requests)==3
requests.clear();case=copy.deepcopy(base);case['entries'][0]['state']='ACTIVE';watch.advance_plan(case);assert not requests
case=copy.deepcopy(base)
for entry in case['entries']:entry['measurements']=[]
watch.advance_plan(case);assert not requests
case=copy.deepcopy(base);case['entries'][2]['profile_complete']=False;watch.advance_plan(case);assert {r[0] for r in requests}=={'prefill-chunk4096','dense-graphs-repeat'}
requests.clear();case=copy.deepcopy(base);case['entries'][0]['measurements'].append(dict(m,concurrency=52,good_output_tokens_s=2096.88));watch.advance_plan(case);assert {r[0] for r in requests}=={'load-best-repeat','prefill-chunk4096','decode-deepgemm','dense-graphs-repeat'};assert next(r[1] for r in requests if r[0]=='load-best-repeat')==[52]
report={'passed':True,'prefill_and_moe_flags_match_actual_image_parser':True,'bounded_followup_decisions':True,'higher_load_repeat_selects_best_passing_N':True,'no_duplicate_followups':True,'waits_for_initial_jobs':True,'no_kernel_trial_without_passing_control':True,'no_moe_trial_without_complete_profiles':True,'scope':'CPU parser and scheduler validation only; fake data isolated from real runs'}
(root/'serving-tuning/followup-cpu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
