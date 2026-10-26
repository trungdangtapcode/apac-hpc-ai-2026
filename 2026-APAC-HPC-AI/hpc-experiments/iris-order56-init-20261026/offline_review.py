"""Exercise exact source transformations and reused initialization checks."""
from pathlib import Path
import ast,importlib.util,re,shutil,subprocess,sys,tempfile
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E))
spec=importlib.util.spec_from_file_location('order_init',E/'init.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for p in E.glob('*.py'):ast.parse(p.read_text(),feature_version=(3,9))
subprocess.run(['bash','-n',str(E/'job.sbatch')],check=True)
with tempfile.TemporaryDirectory() as tmp:
 for order in ['xyz','zyx']:
  case=Path(tmp)/order;shutil.copytree(E/'payload-case',case);(case/'Allrun').unlink()
  p=case/'system/include/caseDefinition';t=p.read_text();t=re.sub(r'(?m)^nCores .*$', 'nCores              56;',t);t=re.sub(r'(?m)^nHierarchical .*$', 'nHierarchical       (7 4 2);',t);p.write_text(t)
  p=case/'system/decomposeParDict';p.write_text(re.sub(r'(?m)^([ \t]+order[ \t]+)xyz;',r'\g<1>'+order+';',p.read_text()))
  assert m.source_check(case,order)['passed']
  p=case/'system/fvSchemes';p.write_text('unexpected numerical change\n')
  try:m.source_check(case,order)
  except AssertionError:pass
  else:raise AssertionError('Numerical source drift accepted')
print('PASS: exact fresh xyz/zyx inputs accepted; numerical drift rejected; syntax checked; reuse of previously verified native/field validators.')
