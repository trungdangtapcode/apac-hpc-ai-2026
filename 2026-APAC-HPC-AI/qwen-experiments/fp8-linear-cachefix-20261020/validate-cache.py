"""Check real FlashInfer path expressions under an unwritable-home fixture, without GPU work."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,tempfile,types
from unittest.mock import patch
O=Path(__file__).resolve().parent;R=O.parent
source=R/'fp8-linear-micro-review-20261020/runtime-source/extracted/usr/local/lib/python3.12/dist-packages/flashinfer/jit/env.py'
wanted={'FLASHINFER_BASE_DIR','FLASHINFER_CACHE_DIR','FLASHINFER_WORKSPACE_DIR','FLASHINFER_JIT_DIR','FLASHINFER_GEN_SRC_DIR'};nodes=[]
for n in ast.parse(source.read_text()).body:
 if isinstance(n,ast.FunctionDef) and n.name=='_get_workspace_dir_name':nodes.append(n)
 if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name) and n.target.id in wanted:nodes.append(n)
assert len(nodes)==6
code=compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(source),'exec')
spec=importlib.util.spec_from_file_location('runtime_cache',O/'runtime_cache.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
original_home=os.environ.get('HOME');paths=[]
def env():return dict(os=os,pathlib=__import__('pathlib'),CompilationContext=lambda:types.SimpleNamespace(TARGET_CUDA_ARCHS={(9,0)}),flashinfer_version='fixture')
with tempfile.TemporaryDirectory(prefix='apac-cache-fixture-') as temp, patch.dict(os.environ,{},clear=False):
 os.environ.pop('FLASHINFER_WORKSPACE_BASE',None)
 with patch('pathlib.Path.home',return_value=Path('/unwritable-home')):
  previous=env();exec(code,previous);assert str(previous['FLASHINFER_WORKSPACE_DIR']).startswith('/unwritable-home/')
  for rank in range(8):
   routes=module.configure(rank,Path(temp));current=env();exec(code,current)
   for key in ['FLASHINFER_WORKSPACE_DIR','FLASHINFER_JIT_DIR','FLASHINFER_GEN_SRC_DIR']:
    p=current[key];assert p.is_relative_to(Path(routes['FLASHINFER_WORKSPACE_BASE']));p.mkdir(parents=True,exist_ok=True);(p/'probe').write_text('ok');assert (p/'probe').read_text()=='ok'
   paths.append(routes['FLASHINFER_WORKSPACE_BASE']);assert os.environ.get('HOME')==original_home
 assert len(set(paths))==8
(O/'cache-validation.json').write_text(json.dumps(dict(passed=True,actual_dependency_ast_executed=True,dependency_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),old_readonly_home_failure_path_reproduced=True,eight_disjoint_rank_cache_roots=True,workspace_jit_generated_paths_writable=True,home_unchanged=True,python_syntax_checked=True,gpu_execution_not_validated=True),indent=2)+'\n')
print('Passed actual dependency workspace expressions, eight writable disjoint cache roots and unchanged HOME')
