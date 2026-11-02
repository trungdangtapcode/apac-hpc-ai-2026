from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
E=Path(__file__).resolve().parent;B=E.parent;P=B/'iris-own-zyx40-20261102'
for p in E.glob('*.py'):compile(p.read_text(),str(p),'exec')
subprocess.run(['bash','-n',str(E/'job.sbatch')],check=True)
sys.path.insert(0,str(E));spec=importlib.util.spec_from_file_location('followup_runner_fixture',E/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert m.ARMS==['B1-our-zyx','A1-scotch','A2-scotch','B2-our-zyx']
expected=['mpirun','-np','56','--report-bindings','--display-map','--map-by','socket','--bind-to','core','--','simpleFoam','-parallel','-fileHandler','collated']
assert all(m.solver_launch(x)==expected for x in m.ARMS)
# Label-based metrics must survive temporal reordering; indices from ABBA would invert the effect.
fixture=[{'arm':k,'mean_s_step':v} for k,v in [('B1-our-zyx',20),('A1-scotch',25),('A2-scotch',30),('B2-our-zyx',24)]]
r=m.comparison_metrics(fixture);assert abs(r['our_zyx_vs_scotch_percent']+20)<1e-10
assert r==m.comparison_metrics(list(reversed(fixture)))
for key in ['first_adjacent_B1_vs_A1_percent','reverse_adjacent_B2_vs_A2_percent']:assert abs(r[key]+20)<1e-10
for name in ['accepted-source-manifest.json','accepted-zyx-source-manifest.json','source-pins.json','case_checks.py','native_output.py','helpers.py','native_checks.py','verify-inputs.py','seal_tree.py']:
 assert (P/name).read_bytes()==(E/name).read_bytes(),name
ref=json.loads((E/'source-reference.json').read_text());parent=json.loads((P/'ROOT_REVIEW.json').read_text());assert ref['parent_payload_sha256']==parent['payload_sha256']
assert m.SOURCES['zyx'].name=='order-zyx' and m.SOURCES['scotch'].name=='ready-N56-scotch'
assert m.MANIFESTS['zyx'].name=='accepted-zyx-source-manifest.json'
assert not any((E/n).exists() for n in ['submission-intent.json','submission-receipt.json','deployment.json','admit.py','ROOT_REVIEW.json'])
files={name:hashlib.sha256((E/name).read_bytes()).hexdigest() for name in parent['payload_sha256']}
(E/'payload-sha256.txt').write_text(''.join(f'{value}  {name}\n' for name,value in sorted(files.items())))
report={'passed':True,'state':'PREPARED_ONLY_NOT_DEPLOYED_SUBMITTED_OR_RESERVED','checks':['Python/bash syntax','Common exact teammate-runtime command on both methods','BAAB temporal order','Label-based pooled/adjacent ratio signs survive reordered rows; no ABBA-index inversion','Accepted manifests,41 pins,source gates,native replay and resource helpers byte-identical to frozen parent','Source-specific zyx/scotch paths preserved','No copied admission machinery or real submission state'],'payload_sha256':files,'maximum_if_later_authorized_CPU_hours':140,'parent_job':'2294640','parent_terminal_review_pending':True,'budget_mutations':False,'scheduler_calls':False,'Gadi_result':False}
(E/'PREPARATION_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='payload_sha256'},indent=2))
