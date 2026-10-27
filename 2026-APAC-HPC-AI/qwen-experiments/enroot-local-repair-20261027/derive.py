#!/usr/bin/env python3
"""Use per-job node-local NVMe for container roots after measured g4 data ENOSPC."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,tempfile,os
S=Path(__file__).resolve().parent;Q=S.parent
# Verify the actual installed Enroot respects a custom rootfs data path, without GPU/model work.
with tempfile.TemporaryDirectory(prefix='enroot-path-proof-') as td:
 t=Path(td);(t/'root').mkdir();(t/'root/proof').write_text('local-rootfs\n')
 subprocess.run(['mksquashfs',str(t/'root'),str(t/'tiny.sqsh'),'-noappend','-processors','1','-quiet'],check=True,stdout=subprocess.DEVNULL)
 env=os.environ.copy();env.update(ENROOT_DATA_PATH=str(t/'data'),ENROOT_MAX_PROCESSORS='1')
 result=subprocess.run(['enroot','create','--name','apac-proof',str(t/'tiny.sqsh')],env=env,capture_output=True,text=True);assert result.returncode==0,result.stderr
 assert (t/'data/apac-proof/proof').read_text()=='local-rootfs\n'
 (S/'enroot-env-proof.json').write_text(json.dumps({'state':'INSTALLED_ENROOT_CUSTOM_DATA_PATH_PASS','scope':'Tiny CPU-only squashfs; no model/GPU/throughput proof','enroot':shutil.which('enroot')},indent=2)+'\n')
for parent,name in [('s72-h200-full-pgraph-breakable-capnative','s80-h200-local-enroot-control'),('s78-h200-full-chunk12288','s81-h200-local-enroot-chunk12288')]:
 P=Q/'serving-tuning-11'/parent;B=Q/'serving-tuning-11'/name;assert not B.exists();shutil.copytree(P,B,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 c=json.loads((B/'config.json').read_text());c.update(experiment=name,label=name,parent_source=parent,enroot_data_policy='Per-job node-local /tmp on NVMe; matched across control/candidate; no existing cache deletion.',infrastructure_failure_parent='26524' if 'control' in name else '26521');(B/'config.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
 p=B/'job.sbatch';s=p.read_text().replace(str(P),str(B)).replace(parent,name);s=s.replace('#SBATCH -J '+s.split('#SBATCH -J ',1)[1].splitlines()[0], '#SBATCH -J '+('ap42-s80-local' if 'control' in name else 'ap42-s81-local'))
 needle='export QWEN_JOB_START_EPOCH=$(date +%s)';assert needle in s
 patch='''export ENROOT_DATA_PATH="/tmp/apacsc42-enroot-${SLURM_JOB_ID}"
srun --exact -N2 -n2 --ntasks-per-node=1 --gres=gpu:0 --cpus-per-task=1 bash -c '
  set -euo pipefail
  umask 077
  path=${ENROOT_DATA_PATH:?}
  [[ ! -L "$path" ]] || exit 1
  if [[ -e "$path" ]]; then
    [[ -d "$path" && $(stat -c %u "$path") == $(id -u) ]] || exit 1
  else
    mkdir -m 700 "$path"
  fi
  read -r block_size free_blocks < <(stat -f -c "%S %a" "$path")
  (( block_size * free_blocks >= 256 * 1024 * 1024 * 1024 )) || { echo "FATAL: insufficient local NVMe for container roots" >&2; exit 1; }
  printf "ENROOT_LOCAL_STORAGE_READY host=%s path=%s free_bytes=%s\\n" "$(hostname)" "$path" "$((block_size*free_blocks))"
'
'''
 s=s.replace(needle,needle+'\n'+patch);p.write_text(s)
 (B/'PLAN.md').write_text('''# Infrastructure-repaired full chunk comparison

Actual26521 and26524 failed before model startup because g4 /data/enroot had only about2.65GB free. Read-only allocated probe26526 confirms g4 local root/NVMe has435GB free, g1 has360GB, and our default Enroot roots are already empty. No own stale roots can be removed to solve the full volume; no other user's data was touched.

This derivative changes only launcher rootfs storage to per-job node-local /tmp, guarded against symlinks/wrong ownership and requiring256GiB free on both nodes. Installed Enroot custom-data-path behavior was validated with a tiny CPU-only squashfs. Actual Pyxis/model operation still needs this allocation. Model weights/images and every operational worker/client/runtime/quality gate are unchanged. Both control and larger-chunk treatment use identical storage policy. No inference improvement or completed score is claimed from a filesystem repair. Node-local rootfs placement may change startup/page-cache behavior; compare these derived arms together rather than treating an old control as exact same environment.

S80 is full N64 chunk8192 control; S81 is full N64 chunk12288 candidate with HPC-Ops decode. Keep all original fixed4000/200/seed2026/coldprefix/full60/120/30 and original source/graph/semantic/raw denominator/SLA/error/output gates. Prior smaller chunks lose and old auto-decode12288 loses; the declared current HPC-Ops interaction is one test, not permission for blind widening. Need >1% useful valid paired gain before independent confirmation. Official full-set accuracy remains UNKNOWN. Each job16H200/two nodes/17minutes; no PBS SU. No frozen parent edit, automatic retry, external message or background Codex.

Primary Enroot configuration reference: https://github.com/NVIDIA/enroot/blob/main/conf/enroot.conf.in (accessed27October). Actual installed implementation /usr/bin/enroot config::export ENROOT_DATA_PATH is also retained by path/hash in preparation proof.
'''.replace('Actual26521','Actual 26521').replace('and26524','and 26524').replace('about2.65GB','about 2.65 GB').replace('probe26526','probe 26526').replace('has435GB','has 435 GB').replace('has360GB','has 360 GB').replace('requiring256GiB','requiring 256 GiB').replace('chunk8192','chunk 8192').replace('chunk12288','chunk 12288').replace('fixed4000','fixed 4000').replace('seed2026','seed 2026').replace('full60','full 60').replace('auto-decode12288','auto-decode 12288').replace('job16H200','job 16 H200').replace('/17minutes','/17 minutes').replace('accessed27October','accessed 27 October'))
 for f in P.glob('*.py'):assert f.read_bytes()==(B/f.name).read_bytes()
 assert (P/'worker.sh').read_bytes()==(B/'worker.sh').read_bytes()
 for f in B.glob('*.py'):ast.parse(f.read_text())
 for f in list(B.glob('*.sh'))+[B/'job.sbatch']:subprocess.run(['bash','-n',str(f)],check=True)
 (B/'SHA256SUMS').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in sorted(B.iterdir()) if f.is_file() and f.name!='SHA256SUMS'))
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=B,check=True,stdout=subprocess.DEVNULL)
 print('Prepared',name)
