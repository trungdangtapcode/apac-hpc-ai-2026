#!/usr/bin/env python3
"""Fix the demonstrated native source mount prerequisite without weakening pins."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
S=Path(__file__).resolve().parent;Q=S.parent
P=Q/'serving-tuning-11/s68-h200-nixl-four-role-probe';B=Q/'serving-tuning-11/s68r2-h200-nixl-four-role-probe'
shutil.copytree(P,B,copy_function=shutil.copyfile,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
source=Q/'serving-tuning-10/s35-h200-observed-n64-full-control/nixl-conn.py';raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()=='912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f';(B/'nixl-conn.py').write_bytes(raw)
job=(B/'job.sbatch').read_text().replace('s68-h200-nixl-four-role-probe',B.name).replace('ap42-s68-nixl-fanout','ap42-s68r2-nixl-fanout')
old='--container-mounts="/scratch:/scratch,$ROOT:/research,$ROOT/home/$SLURM_JOB_ID/$role:$HOME"';new='--container-mounts="/scratch:/scratch,$ROOT:/research,$ROOT/home/$SLURM_JOB_ID/$role:$HOME,$BUNDLE/nixl-conn.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py:ro"';assert old in job;job=job.replace(old,new);(B/'job.sbatch').write_text(job)
entry=(B/'entry.sh').read_text().replace('s68-h200-nixl-four-role-probe',B.name)
entry=entry.replace('exec python3 -B ','''python3 - <<'PYNATIVE'
import hashlib
from pathlib import Path
p=Path('/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py')
assert hashlib.sha256(p.read_bytes()).hexdigest()=='912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f', 'effective native source mount mismatch'
print('NATIVE_SOURCE_MOUNT_VERIFIED',flush=True)
PYNATIVE
exec python3 -B ''');(B/'entry.sh').write_text(entry)
c=json.loads((B/'config.json').read_text());c.update(experiment=B.name,failed_parent_job=26308,prerequisite_fix='Mount exact pinned native patched conn.py before peer helper source identity; no gate/API/hash/data algorithm changes.');(B/'config.json').write_text(json.dumps(c,indent=2)+'\n')
(B/'PARENT_BUNDLE.json').write_text(json.dumps({'parent':str(P.relative_to(Q)),'parent_manifest_sha256':hashlib.sha256((P/'SHA256SUMS').read_bytes()).hexdigest(),'native_source':str(source.relative_to(Q)),'native_sha256':hashlib.sha256(raw).hexdigest(),'derivation':str(Path(__file__).relative_to(Q)),'derivation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
(B/'PLAN.md').write_text((P/'PLAN.md').read_text()+'''\n## Reviewed S68r2 prerequisite repair\n\nOriginal26308 failed before any native agent/registration/transfer because the job did not mount the patched source demanded by its retained identity helper. This derivative mounts that exact912b7e source read-only and verifies its effective path/hash before rank launch. All strict original source/API pins stay intact. Actual image API extraction independently matches27c3ce. probe.py and base-peer.py are byte-identical to the failed parent. No measured transport outcome is repeated. Permit one new bounded prerequisite-corrected attempt, then inspect actual evidence before another diagnostic. Four incumbent-recovery serving jobs retain their positions; total own cap5 remains.\n'''.replace('Original26308','Original 26308').replace('exact912','exact 912').replace('matches27','matches 27').replace('cap5','cap 5'))
(B/'README.md').write_text('# S68r2 native source mount correction\n\nDerived after failed26308. Adds only the missing exact native conn.py mount and startup hash check; retains all source/API/data gates and four-role mapping. Native transfer is unmeasured until actual GPU review.16 H200/two nodes/five-minute cap/no PBS SU; one bounded attempt. Run sbatch from qwen-experiments. Read PLAN.md.\n'.replace('failed26308','failed 26308').replace('review.16','review. 16'))
for p in B.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in [B/'entry.sh',B/'job.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
assert (B/'probe.py').read_bytes()==(P/'probe.py').read_bytes();assert (B/'base-peer.py').read_bytes()==(P/'base-peer.py').read_bytes()
subprocess.run(['python3','-B',str(B/'verify.py')],check=True)
api=S/'api-extracted-r2/usr/local/lib/python3.12/dist-packages/nixl_cu13/_api.py';assert hashlib.sha256(api.read_bytes()).hexdigest()=='27c3ce3c4fe58480aa3bce5e5c158c7659821a3bf1e84680778645adfdaa1bea'
proof={'state':'PASS_CPU_SOURCE_MOUNT_REPAIR','native_source_sha256':hashlib.sha256(raw).hexdigest(),'actual_image_api_sha256':hashlib.sha256(api.read_bytes()).hexdigest(),'actual_mount_string_present':new in job,'entry_mount_hash_guard_present':'NATIVE_SOURCE_MOUNT_VERIFIED' in entry,'probe_and_base_helper_byte_identical':True,'no_gpu_outcome':'Actual container mount/native transfer/output unverified until new allocation.'};(B/'MOUNT-VERIFICATION.json').write_text(json.dumps(proof,indent=2)+'\n')
(B/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(B.iterdir()) if p.is_file() and p.name!='SHA256SUMS'));subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=B,stdout=subprocess.DEVNULL,check=True);print(B.name,'prepared and verified')
