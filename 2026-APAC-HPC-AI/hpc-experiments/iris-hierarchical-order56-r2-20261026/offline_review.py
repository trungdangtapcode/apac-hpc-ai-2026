"""Exercise input transformations and native cut gates without running OpenFOAM."""
from pathlib import Path
import ast,importlib.util,json,shutil,subprocess,tempfile
E=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('order_screen',E/'screen.py');screen=importlib.util.module_from_spec(spec);spec.loader.exec_module(screen)
for p in [E/'screen.py',E/'deploy_submit.py']:ast.parse(p.read_text(),feature_version=(3,9))
subprocess.run(['bash','-n',str(E/'job.sbatch')],check=True)
with tempfile.TemporaryDirectory() as tmp:
 for order in ['xyz','xzy','yxz','zyx']:
  case=Path(tmp)/order;shutil.copytree(E/'payload-case',case);screen.render_inputs(case,order)
  text=(case/'system/include/caseDefinition').read_text();assert 'nCores              56;' in text and 'nHierarchical       (7 4 2);' in text and 'decompositionMethod hierarchical;' in text
  for p in (E/'payload-case').rglob('*'):
   if p.is_file() and str(p.relative_to(E/'payload-case')) not in ['system/include/caseDefinition','system/decomposeParDict']:assert p.read_bytes()==(case/p.relative_to(E/'payload-case')).read_bytes()
 case=Path(tmp)/'xzy';(case/'logs').mkdir()
 count=65334765//56;remainder=65334765%56
 log='OPENFOAM=2512\nArch scalar=64\n'
 for i in range(56):
  for field in ['U','p','k','omega','nut','nuTilda']:
   p=case/('processor'+str(i))/'0'/field;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture\n')
  p=case/('processor'+str(i))/'constant/polyMesh/boundary';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture boundary\n')
  log+='    Number of cells = '+str(count+(i<remainder))+'\n    Number of processor faces = 100\n'
 log+='Number of processor faces = 2800\nMax number of processor patches = 6\nEnd\n';(case/'logs/decomposePar.log').write_text(log)
 assert screen.native_summary(case,'xzy')['mesh_cells']==65334765
 (case/'processor55/constant/polyMesh/boundary').unlink()
 try:screen.native_summary(case,'xzy')
 except AssertionError:pass
 else:raise AssertionError('Missing partition mesh was accepted')
print('PASS: fresh control and three exact order transformations, all other input bytes retained, native complete cut accepted, missing mesh rejected; syntax checked.')
