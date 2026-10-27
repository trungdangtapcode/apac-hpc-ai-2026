"""Offline source, sequence, shell, and fixed-work gate checks; no site access."""
from pathlib import Path
import json, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parent; P=ROOT/'payload'
subprocess.run(['bash','-n',str(P/'native-wave.pbs')],check=True)
for path in P.glob('*.py'): compile(path.read_text(),str(path),'exec')
for seq in ('S0,Hxyz,Hzyx','Hzyx,Hxyz,S0'):
 subprocess.run([sys.executable,str(P/'validate-sequence.py'),seq],check=True,stdout=subprocess.DEVNULL)
for seq in ('S0,S0,Hzyx','S0,Hxyz','S0,Hxyz,Hzyx,extra'):
 assert subprocess.run([sys.executable,str(P/'validate-sequence.py'),seq],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode!=0
template=P/'case'; canonical=Path('/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-scotch128-20261021/payload/case')
with tempfile.TemporaryDirectory(prefix='native-stage-check-') as temp:
 base='End\nOPENFOAM=2512\nversion=v2512\nArch   : "LSB;label=32;scalar=64"\n'
 for method in ('scotch','hierarchical'):
  log=Path(temp)/f'decompose-{method}.log'
  counts=[127607]*493+[127606]*19
  log.write_text(base+f'Decomposition method {method} [512]\n'+'nProcs          : 512\n'+'\n'.join(f'    Number of cells = {n}' for n in counts)+'\n')
  subprocess.run([sys.executable,str(P/'validate-stage.py'),str(log),'decompose','none',method],check=True,stdout=subprocess.DEVNULL)
 bad=Path(temp)/'bad.log'; bad.write_text(base+'Decomposition method scotch [512]\n'+'\n'.join('    Number of cells = 127606' for _ in range(512))+'\n')
 assert subprocess.run([sys.executable,str(P/'validate-stage.py'),str(bad),'decompose','none','hierarchical'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode!=0
with tempfile.TemporaryDirectory(prefix='native-wave-offline-') as temp:
 for method in ('S0','Hxyz','Hzyx'):
  case=Path(temp)/method
  subprocess.run([sys.executable,str(P/'make-variant.py'),'--template',str(template),'--case',str(case),'--method',method],check=True,stdout=subprocess.DEVNULL)
  subprocess.run([sys.executable,str(P/'verify-inputs.py'),'case','--case',str(case),'--method',method,'--template',str(template),'--source-case',str(canonical)],check=True,stdout=subprocess.DEVNULL)
  for generated in ('processor0','postProcessing','dynamicCode','logFiles','1'):
   (case/generated).mkdir(exist_ok=True)
   (case/generated/'retained.txt').write_text('generated-output fixture\n')
  subprocess.run([sys.executable,str(P/'verify-inputs.py'),'case','--case',str(case),'--method',method,'--template',str(template),'--allow-run-output'],check=True,stdout=subprocess.DEVNULL)
  evil=case/'unexpected'; evil.mkdir(); (evil/'x').write_text('reject\n')
  assert subprocess.run([sys.executable,str(P/'verify-inputs.py'),'case','--case',str(case),'--method',method,'--template',str(template),'--allow-run-output'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode!=0
  (evil/'x').unlink(); evil.rmdir()
  changed=case/'system/fvSolution'; changed.write_bytes(changed.read_bytes()+b'\n// unauthorized source edit\n')
  assert subprocess.run([sys.executable,str(P/'verify-inputs.py'),'case','--case',str(case),'--method',method,'--template',str(template),'--allow-run-output'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode!=0
print(json.dumps({'passed':True,'checks':['bash syntax','Python syntax','default/reverse/invalid sequence','Scotch and hierarchical fixed-cell decomposition validator','wrong-method log rejection','three exact canonical source derivations','allowed generated roots','unexpected source/root rejection','unauthorized numerical source edit rejection'],'scope':'Offline only; no NSCC runtime or performance claim.'},indent=2))
