#!/usr/bin/env python3
"""Fix a PBS shell-function timeout boundary in a new immutable derivative."""
from pathlib import Path
import ast,hashlib,json,os,shutil,subprocess,tarfile,tempfile
S=Path(__file__).resolve().parent;Q=S.parent;P=Q/'eagle3-h100-equal-tp-bench-n24-20261026';B=Q/'eagle3-h100-equal-tp-bench-n24-r2-20261026'
assert not B.exists();shutil.copytree(P,B,ignore=shutil.ignore_patterns('__pycache__','*.pyc','payload.tar.gz'))
c=json.loads((B/'config.json').read_text());c.update(experiment_id=B.name,parent_failed_benchmark_job='225306.pbs111',repair='Execute exported PBS srun shim inside bash under external timeout; no model or workload change.');(B/'config.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
p=B/'benchmark.pbs';p.write_text(p.read_text().replace(P.name,B.name).replace('ap42-equal-tp-bench-n24','ap42-equal-tp-n24-r2'))
p=B/'topology-job.sh';s=p.read_text();old='timeout --signal=TERM --kill-after=5s "${score_remaining}s" srun --overlap';new='timeout --signal=TERM --kill-after=5s "${score_remaining}s" bash -c \'source "$QWEN_BUNDLE/pbs-shim.sh"; srun "$@"\' _ --overlap';assert old in s;s=s.replace(old,new);p.write_text(s)
# Regress the exact PBS compatibility boundary: no native srun binary exists in isolated PATH.
with tempfile.TemporaryDirectory(prefix='pbs-timeout-function-regression-') as td:
 t=Path(td);bin=t/'bin';bin.mkdir()
 for name in ['timeout','bash','awk','python3']:(bin/name).symlink_to(shutil.which(name))
 node=t/'nodefile';node.write_text('fixture-node\n');env=os.environ.copy();env.update(PATH=str(bin),PBS_NODEFILE=str(node),QWEN_BUNDLE=str(B),APAC_PBS_DRY_RUN='1')
 args='--overlap -N1 -n1 -w fixture-node --gres=gpu:0 --cpus-per-task=8 --container-image=/fixture.sqsh --container-mounts=/tmp:/tmp echo fixture'
 before=subprocess.run([str(bin/'bash'),'-c','source "$QWEN_BUNDLE/pbs-shim.sh"; timeout 5s srun '+args],env=env,capture_output=True,text=True);assert before.returncode==127,before
 after=subprocess.run([str(bin/'bash'),'-c','source "$QWEN_BUNDLE/pbs-shim.sh"; timeout 5s bash -c \'source "$QWEN_BUNDLE/pbs-shim.sh"; srun "$@"\' _ '+args],env=env,capture_output=True,text=True);assert after.returncode==0,after.stderr
 row=json.loads(after.stdout);assert row['node']==0 and row['gpu_indices']==[] and row['cpus']==8 and row['command']==['echo','fixture']
 proof={'state':'PASS_ACTUAL_PBS_SHIM_CPU_DRY_RUN_NOT_GPU_EXECUTION','old_function_under_external_timeout_exit':before.returncode,'corrected_function_via_bash_exit':after.returncode,'actual_shim_argv':row,'isolated_PATH_has_no_native_srun':True}
(S/'regression.json').write_text(json.dumps(proof,indent=2)+'\n')
unchanged=[]
for name in ['worker.sh','placement.tsv','nixl-conn.py','metadata-gate.py','pd-observer/observer.py','benchmark.sh','phase-controller.py','check-benchmark.py','performance_gates.py','expected-input-config.json','output-smoke.py','long-context-check.py']:
 assert (P/name).read_bytes()==(B/name).read_bytes(),name;unchanged.append(name)
(B/'PLAN.md').write_text((P/'PLAN.md').read_text()+'''\n## R2: repair the actual PBS launcher boundary\n\nParent225306 reached native source/device/metadata and semantic acceptance, then stopped before AIPerf. The PBS compatibility layer defines srun as an exported Bash function. External timeout cannot directly execute a shell function when no binary named srun exists. Root added that faulty boundary in the previous finalization; this is a script error, not an EAGLE performance failure.\n\nR2 keeps the hard outer scoring timeout but executes Bash, explicitly sources the unchanged PBS shim and forwards every original argument through srun "$@". A CPU regression invokes the actual shim in dry-run mode under an isolated PATH with no native srun: the old boundary returns127, the corrected boundary returns0 and preserves node/GPU/CPU/command arguments. This test catches a cluster compatibility issue that syntax and JSON fixtures missed. Native serving/model/precision/observer/client workload/output gates are byte-identical. Full N24 score and official accuracy remain unmeasured.\n\nExactly one derived8-H100/one-node/30-minute attempt, maximum512SU, remains within existing authorization. Preserve failed225306 and its charge; do not relabel it a measured loss. No frozen payload edits or automatic retry. If this derivative fails, inspect actual stage before another change.\n'''.replace('Parent225306','Parent 225306').replace('returns127','returns 127').replace('returns0','returns 0').replace('derived8','derived 8').replace('maximum512SU','maximum 512 SU').replace('failed225306','failed 225306'))
(B/'REPAIR.json').write_text(json.dumps({'parent':str(P.relative_to(Q)),'parent_manifest_sha256':hashlib.sha256((P/'SHA256SUMS').read_bytes()).hexdigest(),'failed_job':'225306.pbs111','unchanged_operational_files':unchanged,'root_regression_proof':str((S/'regression.json').relative_to(Q)),'original_finalizer_is_historical':'ROOT_FINALIZATION.json is inherited parent metadata; this REPAIR.json describes R2.'},indent=2)+'\n')
for p in B.rglob('*.py'):ast.parse(p.read_text())
for p in list(B.glob('*.sh'))+list(B.glob('*.pbs')):subprocess.run(['bash','-n',str(p)],check=True)
files=sorted(p for p in B.rglob('*') if p.is_file() and p.name not in {'SHA256SUMS','payload.tar.gz'} and '__pycache__' not in p.parts)
(B/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(B))+'\n' for p in files))
with tarfile.open(B/'payload.tar.gz','w:gz') as tar:
 for p in files+[B/'SHA256SUMS']:tar.add(p,arcname=str(p.relative_to(B)),recursive=False)
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=B,check=True,stdout=subprocess.DEVNULL)
print('R2 prepared; actual PBS-shim regression reproduced127 and corrected0')
