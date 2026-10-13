import argparse,ast,hashlib,importlib.util,json,os,subprocess,sys,tempfile,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];engine=ROOT/'serving-tuning/inspection'
spec=importlib.util.spec_from_file_location('apac_args2',engine/'arg_groups/arg_utils.py');helper=importlib.util.module_from_spec(spec);sys.modules[spec.name]=helper;spec.loader.exec_module(helper)
tree=ast.parse((engine/'server_args.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ServerArgs')
fields=[n for n in cls.body if isinstance(n,ast.AnnAssign) and getattr(n.target,'id','') in {'chunked_prefill_size','cuda_graph_max_bs_decode','cuda_graph_bs_decode'}];assert len(fields)==3
module=types.ModuleType('apac_fields2');sys.modules[module.__name__]=module
exec('from typing import Optional,List\nfrom dataclasses import dataclass\nfrom apac_args2 import A,NS,Arg\n@dataclass\nclass Fields:\n'+''.join('    '+ast.unparse(n)+'\n' for n in fields),module.__dict__)
parser=argparse.ArgumentParser();helper.add_cli_args_from_dataclass(parser,module.Fields)
state=json.loads((ROOT/'serving-tuning/registry.json').read_text());results=[]
for e in state['entries']:
 if e.get('wave')!=2:continue
 bundle=Path(e['bundle']);config=json.loads((bundle/'config.json').read_text());p=config['prefill_extra_flags'];d=config['decode_extra_flags'];args=parser.parse_args(p+d)
 assert (args.chunked_prefill_size==config['prefill_chunk_size'] if p else args.chunked_prefill_size is None)
 if not p:assert 'chunked_prefill_size=8192' in (ROOT/'runs/23102/prefill-0.log').read_text(errors='replace')
 assert config['concurrency']==[52] and config['standalone']
 if d:assert args.cuda_graph_bs_decode==list(range(1,65)) and args.cuda_graph_max_bs_decode==64
 old=(ROOT/'serving-tuning/control-load/benchmark.sh').read_text();new=(bundle/'benchmark.sh').read_text()
 assert new.startswith(old), 'Official client body must be unchanged; output smoke is appended after measurements'
 assert (bundle/'nixl-conn.py').read_bytes()==(ROOT/'serving-tuning/control-load/nixl-conn.py').read_bytes()
 assert (bundle/'placement.tsv').read_bytes()==(ROOT/'serving-tuning/control-load/placement.tsv').read_bytes()
 subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
 subprocess.run(['bash','-n',str(bundle/'job.sbatch')],check=True)
 results.append({'id':e['id'],'passed':True,'prefill_flags':p,'decode_graph_count':len(d)-3 if d else 0})
assert len(results)==4
report={'passed':True,'scope':'CPU/source and immutable payload validation, not GPU performance','cases':results,'official_client_unchanged':True,'same_model_topology_patch':True,'standalone_N52_only':True}
(ROOT/'serving-tuning-02/cpu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
