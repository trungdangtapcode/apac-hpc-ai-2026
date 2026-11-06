"""Offline recipe wiring, full-window, and label-based arithmetic checks."""
from pathlib import Path
import ast,subprocess,sys,json,textwrap,types,statistics,hashlib
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E));import run
for p in E.glob('*.py'):ast.parse(p.read_text())
subprocess.run(['bash','-n',str(E/'job.sbatch')],check=True)
assert run.ARMS==[('T1-teammate56',56,'teammate56'),('O1-original48',48,'original48'),('D1-io48',48,'io48'),('D2-io48',48,'io48'),('O2-original48',48,'original48'),('T2-teammate56',56,'teammate56')]
assert run.complete_window(6)==12180 and run.INTERNAL_SECONDS==13900
run.require_window(12180,6)
try:run.require_window(12179,6)
except RuntimeError:pass
else:raise AssertionError('truncated complete-window accepted')
assert run.verify_input_pins_match()['passed']
from source_checks import expected_case_definition
for n in [48,56]:
 digest=hashlib.sha256(expected_case_definition(E/f'payload-case-{n}/system/include/caseDefinition',n)).hexdigest()
 assert digest==json.loads((E/f'accepted-source-manifest-{n}.json').read_text())['files']['system/include/caseDefinition']
parent=json.loads((E.parent/'iris-rank-density40-reverse-20261105/completed-2294918/collected/runs/2294918/comparison.json').read_text());forces={r['rank_count']:r['force_coefficients_by_step'] for r in parent['arms']}
means={'T1-teammate56':22,'T2-teammate56':24,'O1-original48':26,'O2-original48':28,'D1-io48':20,'D2-io48':22}
# These numbers are synthetic arithmetic fixtures, not native measurements.
rows=[{'arm':label,'mean_s_step':means[label],'median_s_step':means[label],'force_coefficients_by_step':forces[n]} for label,n,recipe in run.ARMS]
source=(E/'run.py').read_text();segment=textwrap.dedent(source[source.index('    by_arm='):source.index("    print('IRIS_BEST_RECIPES40_COMPLETE')")]);saved={}
scope={'results':rows,'compare_same_partition':run.compare_same_partition,'max_series_delta':run.max_series_delta,'statistics':statistics,'h':types.SimpleNamespace(save=lambda path,value:saved.update(value)),'run':Path('/not-written')};exec(segment,scope,scope)
assert saved['complete_six_arm_recipe_comparison'] and saved['arm_order']==[x[0] for x in run.ARMS]
assert {k:saved['recipe_means'][k]['mean_seconds_per_step'] for k in ['teammate56','original48','io48']}=={'teammate56':23,'original48':27,'io48':21}
assert saved['recipe_means']['io48_vs_teammate56']['mean_seconds_per_step_delta']==-2
assert saved['recipe_means']['io48_vs_original48']['mean_seconds_per_step_delta']==-6
bad=[sys.executable,str(E/'prepare_arm.py')]
for option in ['source','destination','manifest','supplementary','probe-writer','proof-reader','result']:bad+=['--'+option,'/unused']
bad+=['--rank-count','48','--mpirun','/unused','--recipe','teammate56']
p=subprocess.run(bad,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);assert p.returncode!=0 and 'recipe/rank-count mismatch' in p.stderr
print('PASS: imports/syntax, recipe-rank wiring, full six-arm window, source transforms, absolute mean/delta arithmetic, guard rejection; no native run')
