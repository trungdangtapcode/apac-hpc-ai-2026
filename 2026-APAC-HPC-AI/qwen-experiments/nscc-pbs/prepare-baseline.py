"""Freeze the known RR deployment with PBS launch adapters; no automatic qsub."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

DIR=Path(__file__).resolve().parent;ROOT=DIR.parent
source=ROOT/'serving-tuning/s5-rr-repeat-n52'
bundle=DIR/'baseline-n32';assert not bundle.exists();bundle.mkdir()
remote_root='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015'
assets='/scratch/users/industry/ai-hpc/apacsc42/qwen-assets'
for path in source.iterdir():
    if path.is_file() and path.name not in ('job.sbatch','SHA256SUMS'):shutil.copyfile(path,bundle/path.name)
for name in ('pbs-shim.sh','pbs-container.sh','pbs-exec.py'):shutil.copyfile(DIR/name,bundle/name)
config=json.loads((bundle/'config.json').read_text())
config.update(experiment='nscc-pbs-baseline-n32',platform='NSCC ASPIRE2A+',gpu='H100 80GB',scheduler='PBS',
              concurrency=[32],purpose='First full official-protocol H100 baseline; do not compare raw scores directly with H200.',
              image=assets+'/sglang-harbor.sqsh',client_image=assets+'/aiperf.sqsh',
              model=assets+'/Qwen3-235B-A22B-Instruct-2507-FP8',source_job='23576',
              cpu_binding='Deterministic source CPU counts, offset 8 CPUs per preceding GPU; not NUMA-tuned.',
              benchmark_runtime_validation='NOT_RUN_ON_NSCC; missing assets',accuracy_verified=False)
(bundle/'config.json').write_text(json.dumps(config,indent=2)+'\n')
topology=(bundle/'topology-job.sh').read_text()
for old,new in [('/scratch/enroot-images/sglang-harbor.sqsh',config['image']),('/scratch/enroot-images/aiperf.sqsh',config['client_image']),('/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8',config['model']),('1020-SECONDS-40','1800-SECONDS-40')]:
    assert old in topology;topology=topology.replace(old,new)
(bundle/'topology-job.sh').write_text(topology)
job='''#!/bin/bash -l
#PBS -P 59010042
#PBS -q normal
#PBS -N ap42-qwen-baseline32
#PBS -l select=2:ngpus=8:mpiprocs=1
#PBS -l place=scatter:excl
#PBS -l walltime=00:30:00
#PBS -j oe
set -euo pipefail
'''
job+=f'export QWEN_BUNDLE={remote_root}/baseline-n32\nexport SLURM_SUBMIT_DIR={remote_root}\n'
job+='''# These three compatibility aliases only preserve source artifact paths.
export SLURM_JOB_ID=$PBS_JOBID SLURM_JOB_NODELIST=from-pbs-nodefile
export QWEN_PREFILL_EP=1 QWEN_PAIR_TIMEOUT=480 QWEN_TUNE_NS=32 QWEN_DIAGNOSTIC_PROFILE=0
export QWEN_NIXL_PATCH_SHA256=912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
source "$QWEN_BUNDLE/pbs-shim.sh"
exec bash "$QWEN_BUNDLE/topology-job.sh"
'''
(bundle/'benchmark.pbs').write_text(job)
assert (bundle/'worker.sh').read_bytes()==(source/'worker.sh').read_bytes()
assert (bundle/'benchmark.sh').read_bytes()==(source/'benchmark.sh').read_bytes()
for path in bundle.iterdir():
    if path.suffix in ('.sh','.pbs'):subprocess.run(['bash','-n',str(path)],check=True)
    if path.suffix=='.py':compile(path.read_text(),str(path),'exec')
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.iterdir())}
(bundle/'SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name,digest in hashes.items()))
for path in bundle.iterdir():path.chmod(0o444)
bundle.chmod(0o555)
print('Frozen PBS baseline bundle:',bundle)
