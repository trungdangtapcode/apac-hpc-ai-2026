"""Validate queued RR hypotheses against exact staged CLI fields and source bytes."""
import argparse
import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import types
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];DIR=ROOT/'serving-tuning-06';ENGINE=ROOT/'serving-tuning/inspection'
spec=importlib.util.spec_from_file_location('rr_backend_args',ENGINE/'arg_groups/arg_utils.py')
helper=importlib.util.module_from_spec(spec);sys.modules[spec.name]=helper;spec.loader.exec_module(helper)
tree=ast.parse((ENGINE/'server_args.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ServerArgs')
wanted={'chunked_prefill_size','cuda_graph_max_bs_decode','cuda_graph_bs_decode','moe_runner_backend','kv_cache_dtype'}
fields=[n for n in cls.body if isinstance(n,ast.AnnAssign) and getattr(n.target,'id','') in wanted];assert len(fields)==len(wanted)
choice=next(n for n in tree.body if isinstance(n,ast.Assign) and any(getattr(t,'id','')=='MOE_RUNNER_BACKEND_CHOICES' for t in n.targets))
module=types.ModuleType('rr_backend_fields');sys.modules[module.__name__]=module
code='from typing import Optional,List,Literal\nfrom dataclasses import dataclass\nfrom rr_backend_args import A,NS,Arg\n'+ast.unparse(choice)+'\n@dataclass\nclass Fields:\n'+''.join('    '+ast.unparse(n)+'\n' for n in fields)
exec(code,module.__dict__);parser=argparse.ArgumentParser();helper.add_cli_args_from_dataclass(parser,module.Fields)
state=json.loads((ROOT/'serving-tuning/registry.json').read_text());source=Path(next(e for e in state['entries'] if e['id']=='s5-rr-repeat-n52')['bundle'])
source_config=json.loads((source/'config.json').read_text());plan=json.loads((DIR/'prepared-pilots.json').read_text());results=[]
for pilot in plan['pilots']:
    bundle=Path(pilot['bundle']);c=json.loads((bundle/'config.json').read_text())
    p=parser.parse_args(c['prefill_extra_flags']);d=parser.parse_args(c['decode_extra_flags'])
    assert c['concurrency']==[52] and c['wave']==6 and c['standalone'] and c['router_extra_flags']==['--prefill-policy','round_robin']
    assert p.chunked_prefill_size==4096 and d.cuda_graph_max_bs_decode==64 and d.cuda_graph_bs_decode==list(range(1,65))
    for name in ('benchmark.sh','topology-job.sh','placement.tsv','nixl-conn.py','output-smoke.py'):
        assert (source/name).read_bytes()==(bundle/name).read_bytes(),name
    worker=(source/'worker.sh').read_text()
    for key in ('prefill_extra_flags','decode_extra_flags'):
        old='extra=('+__import__('shlex').join(source_config[key])+')'
        worker=worker.replace(old,'extra=('+__import__('shlex').join(c[key])+')')
    assert worker==(bundle/'worker.sh').read_text()
    job=(bundle/'job.sbatch').read_text()
    if c['diagnostic_profile']:
        assert p.kv_cache_dtype=='auto' and d.kv_cache_dtype=='auto' and d.moe_runner_backend=='auto'
        assert 'export QWEN_DIAGNOSTIC_PROFILE=1\nexport QWEN_PROFILE_N=52' in job
        diagnostic=(bundle/'profile-serving.py').read_text()
        assert 'max_workers=concurrency' in diagnostic and 'range(concurrency)' in diagnostic and "'concurrency': concurrency" in diagnostic
        assert 'os.environ.get("QWEN_PROFILE_N", "52")' in diagnostic
        assert pilot['expected_profile_ranks']=={'prefill-0':4,'prefill-1':4,'decode-0':8}
    elif c['kv_dtype']=='fp8_e4m3':
        assert p.kv_cache_dtype==d.kv_cache_dtype=='fp8_e4m3' and d.moe_runner_backend=='auto'
    else:
        assert p.kv_cache_dtype==d.kv_cache_dtype=='auto' and d.moe_runner_backend=='deep_gemm'
    subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
    results.append(dict(id=pilot['id'],passed=True,actual_image_flags_valid=True,official_client_unchanged=True))
report=dict(passed=True,scope='CPU/source validation; no GPU performance or accuracy claim',cases=results,
            profile_traffic_after_official_measurement=True,diagnostic_concurrency_52=True,
            model_topology_router_graphs_patch_preserved=True,
            server_args_sha256=hashlib.sha256((ENGINE/'server_args.py').read_bytes()).hexdigest())
(DIR/'cpu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
