"""Validate actual-image CLI declarations and isolate the two experimental factors."""
import argparse
import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import types
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];DIR=ROOT/'serving-tuning-04'
engine=ROOT/'serving-tuning/inspection'
spec=importlib.util.spec_from_file_location('prefill_arg_utils',engine/'arg_groups/arg_utils.py')
helper=importlib.util.module_from_spec(spec);sys.modules[spec.name]=helper;spec.loader.exec_module(helper)
tree=ast.parse((engine/'server_args.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ServerArgs')
names={'chunked_prefill_size','prefill_max_requests','cuda_graph_max_bs_decode','cuda_graph_bs_decode'}
fields=[n for n in cls.body if isinstance(n,ast.AnnAssign) and getattr(n.target,'id','') in names];assert len(fields)==4
module=types.ModuleType('prefill_fields');sys.modules[module.__name__]=module
exec('from typing import Optional,List\nfrom dataclasses import dataclass\nfrom prefill_arg_utils import A,NS,Arg\n@dataclass\nclass Fields:\n'+''.join('    '+ast.unparse(n)+'\n' for n in fields),module.__dict__)
parser=argparse.ArgumentParser();helper.add_cli_args_from_dataclass(parser,module.Fields)
router_path=DIR/'inspection/router_args.py'
spec=importlib.util.spec_from_file_location('prefill_router_args',router_path)
router=importlib.util.module_from_spec(spec);sys.modules[spec.name]=router;spec.loader.exec_module(router)
router_parser=argparse.ArgumentParser();router.RouterArgs.add_cli_args(router_parser)
source=ROOT/'serving-tuning/s2-repeat-best'
plan=json.loads((DIR/'prefill-pilots.json').read_text());checked=[]
for pilot in plan['pilots']:
    bundle=Path(pilot['bundle']);config=json.loads((bundle/'config.json').read_text())
    parsed=parser.parse_args(config['prefill_extra_flags']+config['decode_extra_flags'])
    parsed_router=router_parser.parse_args(config['router_extra_flags'])
    assert config['concurrency']==[52] and config['wave']==4 and config['standalone']
    assert parsed.chunked_prefill_size==4096 and parsed.cuda_graph_max_bs_decode==64
    assert parsed.cuda_graph_bs_decode==list(range(1,65))
    for name in ('benchmark.sh','placement.tsv','nixl-conn.py','output-smoke.py'):
        assert (source/name).read_bytes()==(bundle/name).read_bytes(),name
    if config['router_extra_flags']:
        assert parsed_router.prefill_policy=='round_robin' and parsed_router.decode_policy is None
        assert parsed.prefill_max_requests is None
        assert (source/'worker.sh').read_bytes()==(bundle/'worker.sh').read_bytes()
        expected=(source/'topology-job.sh').read_text().replace('--pd-disaggregation "${router_args[@]}"','--pd-disaggregation --prefill-policy round_robin "${router_args[@]}"')
        assert expected==(bundle/'topology-job.sh').read_text()
    else:
        assert parsed.prefill_max_requests==1 and parsed_router.prefill_policy is None
        assert (source/'topology-job.sh').read_bytes()==(bundle/'topology-job.sh').read_bytes()
        expected=(source/'worker.sh').read_text().replace('extra=(--chunked-prefill-size 4096)','extra=(--chunked-prefill-size 4096 --prefill-max-requests 1)')
        assert expected==(bundle/'worker.sh').read_text()
    subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
    checked.append(dict(id=pilot['id'],actual_image_cli_valid=True,single_factor=True))
report=dict(passed=True,scope='CPU/source validation only; GPU measurements pending',cases=checked,
            client_unchanged=True,model_topology_kv_patch_decode_unchanged=True,
            source_files_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (engine/'server_args.py',router_path)})
(DIR/'cpu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
