#!/usr/bin/env python3
"""Prepare a conditional same-runtime control/candidate using user-level Enroot."""
from pathlib import Path
import ast,datetime,hashlib,json,os,re,shutil,subprocess,tempfile
S=Path(__file__).resolve().parent;Q=S.parent
for parent,name in [('s72-h200-full-pgraph-breakable-capnative','s82-h200-native-enroot-control'),('s78-h200-full-chunk12288','s83-h200-native-enroot-chunk12288')]:
 P=Q/'serving-tuning-11'/parent;B=Q/'serving-tuning-11'/name;assert not B.exists();shutil.copytree(P,B,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 shutil.copyfile(S/'native-container.sh',B/'native-container.sh')
 c=json.loads((B/'config.json').read_text());c.update(experiment=name,label=name,container_runtime='Standalone unprivileged Enroot within existing Slurm steps/cgroups',prerequisite_job=26538,performance_or_GPU_acceptance='UNKNOWN',source_parent=parent);(B/'config.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
 p=B/'topology-job.sh';s=p.read_text();pattern=r'--container-image=("[^"\n]*"|\S+) --container-mounts=([^\n]+) \\\n';s,n=re.subn(pattern,lambda m:'bash "$BUNDLE/native-container.sh" '+m[1]+' '+m[2]+' \\\n',s);assert n==5 and '--container-image=' not in s,(name,n);p.write_text(s)
 p=B/'job.sbatch';s=p.read_text().replace(str(P),str(B)).replace(parent,name);s=s.replace('#SBATCH -J '+s.split('#SBATCH -J ',1)[1].splitlines()[0],'#SBATCH -J '+('ap42-s82-native' if 'control' in name else 'ap42-s83-native'))
 needle='set -euo pipefail';guard='''set -euo pipefail
python3 - <<'PREREQ'
import json
from pathlib import Path
p=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/26538.out')
rows=[]
for line in p.read_text().splitlines():
 try: rows.append(json.loads(line))
 except ValueError: pass
assert any(r.get('state')=='NATIVE_LOCAL_ENROOT_GPU_PASS' and r.get('visible_gpu_count')==1 for r in rows), 'Native GPU prerequisite26538 has not passed; no serving step may start'
PREREQ''';assert needle in s;s=s.replace(needle,guard,1);p.write_text(s)
 for f in P.glob('*.py'):assert f.read_bytes()==(B/f.name).read_bytes()
 assert (P/'worker.sh').read_bytes()==(B/'worker.sh').read_bytes()
 for f in B.glob('*.py'):ast.parse(f.read_text())
 for f in list(B.glob('*.sh'))+[B/'job.sbatch']:subprocess.run(['bash','-n',str(f)],check=True)
 (B/'PLAN.md').write_text('''# Conditional direct-Enroot full control and larger-batch test

Default g4 /data rootfs storage is full; the attempted environment override is deliberately filtered by Pyxis and did not fix26531/26533. Do not repeat it. This bundle uses the supported unprivileged Enroot CLI inside ordinary Slurm steps. It changes no privileged plugin configuration, account privilege, Slurm CPU/GPU allocation or cgroup. All sources/images/model arithmetic/workload/acceptance gates remain. Physical GPU devices are taken from SLURM_STEP_GPUS, with the separate cgroup-relative CUDA mask preserved. CPU-only steps expose no GPU. Source/target mounts preserve read-only patch flags.

The allocated real-image one-GPU prerequisite26538 must actually print its CUDA tensor pass before any serving step starts. Jobs use afterany plus an explicit prerequisite receipt gate to avoid an indefinitely unsatisfied dependency; a failed prerequisite yields no benchmark and does not authorise continuing. Do not call these conditional preparations measured or validated before that proof and actual full native runtime/semantic/output checks. No automatic retry.

Both derived arms use the same direct-runtime policy. S82 is full N64 chunk8192 control; S83 is chunk12288/HPC-Ops interaction candidate. Rootfs extraction may change startup and filesystem effects, so old Pyxis controls are not exact deployment matches. The current pair still needs actual runtime, graph capture, KV geometry, both semantic routes, exact N64/4000:200/seed2026/cold/full60:120:30 raw denominator,>=90% joint SLA, no errors/cancels, smoke7/8 without regression and retrieval12/12. Official full-set accuracy is UNKNOWN. Require >1% useful valid paired gain before independent confirmation. Retain prior smaller-chunk failures and old auto-decode12288 loss.

Each16 H200/two nodes/17minutes, no PBS SU, fresh cap5. Rootfs paths are per-job and per-step under local /tmp; remove only roots created by this wrapper. The source image regular-file size upper bound is30.635GB and local NVMe free space is over360/424GB; every step requires120GiB available before extraction. Installed Enroot/Pyxis behavior and actual probe results are separately retained. No other users' data, frozen payload, HPC work, schedule or background Codex is changed.

References: NVIDIA Enroot CLI (installed enroot start --help); NVIDIA pyxis_slurmstepd.c enroot_deny_env; SchedMD srun SLURM_STEP_GPUS documentation: https://slurm.schedmd.com/srun.html (accessed27October2026). Global GPU IDs are distinct from cgroup-relative CUDA indices.
''')
 (B/'SHA256SUMS').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in sorted(B.iterdir()) if f.is_file() and f.name!='SHA256SUMS'))
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=B,check=True,stdout=subprocess.DEVNULL)
# Real shell argument test: global second four GPUs and cgroup-relative CUDA0..3 stay distinct.
env=os.environ.copy();env.update(SLURM_JOB_ID='fixture',SLURM_STEP_ID='fixture',SLURM_STEP_GPUS='4,5,6,7',CUDA_VISIBLE_DEVICES='0,1,2,3',APAC_NATIVE_DRY_RUN='1')
r=subprocess.run(['bash',str(S/'native-container.sh'),'/scratch/enroot-images/sglang-harbor.sqsh',str(S)+':'+str(S)+':ro','python3','-c','print(1)'],env=env,capture_output=True,text=True);assert r.returncode==0,r.stderr;row=json.loads(r.stdout);assert row['physical_gpu_ids']=='4,5,6,7' and row['cuda_mask']=='0,1,2,3';assert any('bind,ro,nosuid,nodev' in s for s in row['enroot_args_and_command'])
(S/'preparation.json').write_text(json.dumps({'state':'CONDITIONAL_PREPARATION_PASS_GPU_RUNTIME_UNVERIFIED','pyxis_container_calls_replaced':5,'worker_and_python_gates_byte_identical':True,'physical_vs_relative_GPU_mask_fixture':'PASS','readonly_mount_argv_fixture':'PASS','prerequisite':26538,'limits':'CPU argv fixtures do not prove GPU rootfs/namespace/transport behavior; real prerequisite and full gates mandatory.'},indent=2)+'\n');print('Conditional native serving pair prepared')
