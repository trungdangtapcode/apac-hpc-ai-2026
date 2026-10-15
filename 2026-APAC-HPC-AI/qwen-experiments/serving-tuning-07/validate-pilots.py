"""Validate each isolated kernel experiment against the actual staged engine."""
import argparse
import ast
import hashlib
import importlib.util
import json
import shlex
import subprocess
import sys
import types
from pathlib import Path

DIR=Path(__file__).resolve().parent;ROOT=DIR.parent;ENGINE=ROOT/'serving-tuning/inspection'
spec=importlib.util.spec_from_file_location('kernel_args',ENGINE/'arg_groups/arg_utils.py')
helper=importlib.util.module_from_spec(spec);sys.modules[spec.name]=helper;spec.loader.exec_module(helper)
tree=ast.parse((ENGINE/'server_args.py').read_text())
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ServerArgs')
wanted={'chunked_prefill_size','cuda_graph_max_bs_decode','cuda_graph_bs_decode','moe_runner_backend',
        'kv_cache_dtype','decode_attention_backend','flashinfer_allreduce_fusion_backend'}
fields=[n for n in cls.body if isinstance(n,ast.AnnAssign) and getattr(n.target,'id','') in wanted]
assert len(fields)==len(wanted)
choices=[n for n in tree.body if isinstance(n,ast.Assign) and any(getattr(t,'id','') in
         ('MOE_RUNNER_BACKEND_CHOICES','ATTENTION_BACKEND_CHOICES') for t in n.targets)]
assert len(choices)==2
module=types.ModuleType('kernel_fields');sys.modules[module.__name__]=module
code='from typing import Optional,List,Literal\nfrom dataclasses import dataclass\nfrom kernel_args import A,NS,Arg\n'
code+='\n'.join(ast.unparse(n) for n in choices)+'\n@dataclass\nclass Fields:\n'
code+=''.join('    '+ast.unparse(n)+'\n' for n in fields)
exec(code,module.__dict__);parser=argparse.ArgumentParser();helper.add_cli_args_from_dataclass(parser,module.Fields)
state=json.loads((ROOT/'serving-tuning/registry.json').read_text())
source=Path(next(e for e in state['entries'] if e['id']=='s5-rr-repeat-n52')['bundle'])
source_config=json.loads((source/'config.json').read_text())
expected={
 's7-rr-cutlass-n52':['--moe-runner-backend','cutlass'],
 's7-rr-flashinfer-n52':['--decode-attention-backend','flashinfer'],
 's7-rr-mnnvl-n52':['--flashinfer-allreduce-fusion-backend','mnnvl']}
results=[]
for pilot in json.loads((DIR/'prepared-pilots.json').read_text())['pilots']:
    bundle=Path(pilot['bundle']);c=json.loads((bundle/'config.json').read_text())
    p=parser.parse_args(c['prefill_extra_flags']);d=parser.parse_args(c['decode_extra_flags'])
    assert c['prefill_extra_flags']==source_config['prefill_extra_flags']
    assert c['decode_extra_flags']==source_config['decode_extra_flags']+expected[pilot['id']]
    assert c['concurrency']==[52] and c['wave']==7 and c['standalone'] and not c['diagnostic_profile']
    assert c['router_extra_flags']==['--prefill-policy','round_robin']
    assert p.kv_cache_dtype==d.kv_cache_dtype=='auto' and p.chunked_prefill_size==4096
    assert d.cuda_graph_max_bs_decode==64 and d.cuda_graph_bs_decode==list(range(1,65))
    for name in ('benchmark.sh','topology-job.sh','placement.tsv','nixl-conn.py','output-smoke.py','profile-serving.py'):
        assert (source/name).read_bytes()==(bundle/name).read_bytes(),name
    worker=(source/'worker.sh').read_text()
    old='extra=('+shlex.join(source_config['decode_extra_flags'])+')'
    assert worker.count(old)==1
    assert worker.replace(old,'extra=('+shlex.join(c['decode_extra_flags'])+')')==(bundle/'worker.sh').read_text()
    assert 'export QWEN_DIAGNOSTIC_PROFILE=0' in (bundle/'job.sbatch').read_text()
    subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
    results.append(dict(id=pilot['id'],passed=True,actual_image_flags_valid=True,single_decode_change=True))
report=dict(passed=True,scope='CPU and actual-image source validation; GPU backend use and accuracy remain unverified',
            cases=results,model_topology_router_client_graphs_transport_preserved=True,
            server_args_sha256=hashlib.sha256((ENGINE/'server_args.py').read_bytes()).hexdigest())
(DIR/'cpu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
