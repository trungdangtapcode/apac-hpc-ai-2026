"""Create a fresh writable native case from the frozen control template."""
from pathlib import Path
import argparse, re, shutil, json, importlib.util
import sys; sys.dont_write_bytecode=True
_spec=importlib.util.spec_from_file_location('native_verify',Path(__file__).with_name('verify-inputs.py'))
_module=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_module); verify_case=_module.verify_case

ap=argparse.ArgumentParser(); ap.add_argument('--template',required=True); ap.add_argument('--case',required=True); ap.add_argument('--method',choices=['S0','Hxyz','Hzyx'],required=True); a=ap.parse_args()
src=Path(a.template); dst=Path(a.case)
assert not dst.exists(),dst
shutil.copytree(src,dst,copy_function=shutil.copy2)
if a.method!='S0':
 p=dst/'system/include/caseDefinition'; b=p.read_bytes()
 b,n=re.subn(rb'(?m)^(decompositionMethod\s+)scotch(\s*;)',rb'\g<1>hierarchical\g<2>',b); assert n==1
 b,n=re.subn(rb'(?m)^(nHierarchical\s+)\([^)]*\)(\s*;)',rb'\g<1>(16 8 4)\g<2>',b); assert n==1
 p.write_bytes(b)
 p=dst/'system/decomposeParDict'; b=p.read_bytes()
 b,n=re.subn(rb'(?m)^(\s*order\s+)xyz(\s*;)',rb'\g<1>'+('xyz' if a.method=='Hxyz' else 'zyx').encode()+rb'\g<2>',b); assert n==1
 p.write_bytes(b)
print(json.dumps(verify_case(dst,a.method,src),indent=2))
