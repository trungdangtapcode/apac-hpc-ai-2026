"""Targeted checks for rank-density interfaces and complete-arm guards."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E))
import run
from source_checks import expected_case_definition
for p in E.glob('*.py'): ast.parse(p.read_text(),filename=str(p))
subprocess.run(['bash','-n',str(E/'job.sbatch')],check=True)
assert run.ARMS==[('A1-scotch56',56),('B1-scotch48',48),('B2-scotch48',48),('A2-scotch56',56)]
assert run.complete_window(4)==8280 and run.INTERNAL_SECONDS==8700
try:run.require_window(8279,4)
except RuntimeError:pass
else:raise AssertionError('insufficient complete sequence window accepted')
run.require_window(8280,4)
assert run.verify_input_pins_match()['passed']
for n in (48,56):
 expected=json.loads((E/('accepted-source-manifest-%d.json'%n)).read_text())['files']['system/include/caseDefinition']
 actual=expected_case_definition(E/('payload-case-%d'%n)/'system/include/caseDefinition',n)
 assert hashlib.sha256(actual).hexdigest()==expected
report=run.compare_same_partition([[1.0,3.0]],[[1.0,3.0+1e-9]])
assert report['passed'] and report['maximum_absolute_delta_all_columns']>0
assert not run.compare_same_partition([[1.0,3.0]],[[1.0,3.1]])['passed']
for n in (48,56):
 text='\n'.join('Rank %d bound to package[0][core:%d]'%(i,i) for i in range(n))
 assert run.verify_solver_binding_report(text,n)['passed']
 try:run.verify_solver_binding_report(text,n+1)
 except RuntimeError:pass
 else:raise AssertionError('incomplete binding report accepted')
print('PASS: syntax, equal40-step arms, time guards, source transforms, repeat tolerance/delta, 48/56 rank-report completeness')
