"""Freeze one H200-specific routing hypothesis; no scheduler action."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
O=Path(__file__).resolve().parent;R=O.parent;C=R/'serving-tuning-10/s21-dg8192-hpc-n60-control';B=R/'serving-tuning-10/s26-h200-power2-n60';assert not B.exists(),'Do not rewrite frozen candidates';B.mkdir()
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=C,check=True,capture_output=True)
files=[line.split('  ',1)[1] for line in (C/'SHA256SUMS').read_text().splitlines()]
for name in files:shutil.copyfile(C/name,B/name)
p=B/'topology-job.sh';t=p.read_text();old='--prefill-policy round_robin';new='--prefill-policy power_of_two';assert t.count(old)==1;t=t.replace(old,new);assert t.replace(new,old)==(C/'topology-job.sh').read_text();p.write_text(t)
p=B/'job.sbatch';t=p.read_text().replace(C.name,B.name).replace('ap42-s21-dg8192-hpc-n60-control','ap42-s26-h200-power2-n60');p.write_text(t)
c=json.loads((B/'config.json').read_text());c.update(experiment=B.name,source_experiment=C.name,source_job='24964',fresh_control_job='24964',control_job='24964',control_experiment=C.name,router_extra_flags=['--prefill-policy','power_of_two'],changed_factor={'prefill_router_policy':['round_robin','power_of_two']},purpose='H200 transient sampled prefill-queue skew; only route by native power_of_two vs fresh equally observed N60 RR control',hypothesis_evidence_job='24928',negative_transfer_evidence='H100 power_of_two previously loses 4.865%; H200-specific test, no inferred gain',practical_gain_gate_fraction=.01,dependency_afterok='24964');(B/'config.json').write_text(json.dumps(c,indent=2)+'\n')
unchanged=[name for name in files if name not in {'config.json','job.sbatch','topology-job.sh'}];assert all((C/name).read_bytes()==(B/name).read_bytes() for name in unchanged)
for p in B.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in list(B.glob('*.sh'))+[B/'job.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
(B/'SHA256SUMS').write_text(''.join(hashlib.sha256((B/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in files))
pilot=dict(platform='H200',id=B.name,bundle=str(B),planned_ns=[60],state='PREPARED_NOT_SUBMITTED',minutes=17,max_su=None,dependency_afterok='24964',payload_sha256={name:hashlib.sha256((B/name).read_bytes()).hexdigest() for name in files})
(O/'pilots.json').write_text(json.dumps([pilot],indent=2)+'\n');(O/'validation.json').write_text(json.dumps(dict(passed=True,source_bundle=str(C),fresh_control_job='24964',changed_runtime_factor='prefill-policy round_robin -> power_of_two only',unchanged_control_files=unchanged,inverse_runtime_diff_exact=True,python_ast_and_shell_syntax=True,scored_protocol='Full 60/120/30 at N60, fixed4000/200 seed2026 coldprefix',requires_completed_24928_review=True,actual_gpu_run=False),indent=2)+'\n');print('Frozen one H200 routing candidate; not submitted')
