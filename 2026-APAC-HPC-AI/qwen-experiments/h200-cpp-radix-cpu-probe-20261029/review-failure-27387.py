#!/usr/bin/env python3
"""Review the failed CPU envelope without broadening its fixture acceptance."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
D=Path(__file__).resolve().parent;Q=D.parent;a=Q/'runs/27387'
account=subprocess.check_output(['sacct','-X','-j','27387','-P',
    '--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,AllocTRES,NodeList'],text=True)
assert '27387|FAILED|124:0|00:01:33|93|' in account
assert '27387' not in subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split()
result=json.loads((a/'probe.json').read_text());log=(a/'compiler-import.log').read_text()
assert result['state']=='FAIL_TIME_LIMIT_OR_SIGNAL' and result['launcher_exit_code']==124
assert result['cases']==[] and result['native_remove_end_seen'] is False
assert result['torch_visible_device_count']==0 and result['torch_cuda_available'] is False
begin=int(re.search(r'NATIVE_CREATE_BEGIN epoch=(\d+)',log)[1])
end=int(re.search(r'NATIVE_CREATE_END epoch=(\d+)',log)[1]);assert end-begin==76
assert result['process_deadline_epoch']-result['absolute_job_start_epoch']==90
assert end==begin+76
(a/'scheduler-accounting.psv').write_text(account)
manifest=a/'artifact-manifest.json';assert not manifest.exists()
files=[]
for p in sorted(a.rglob('*'))+[Q/'runs/27387.out',Q/'runs/27387.err']:
    if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p==manifest:continue
    before=p.stat();digest=hashlib.sha256(p.read_bytes()).hexdigest();after=p.stat()
    assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    files.append({'path':str(p.relative_to(Q)),'bytes':after.st_size,'sha256':digest})
manifest.write_text(json.dumps({'job':27387,'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal_accounting':account,'files':files},indent=2)+'\n')
review={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job':27387,
    'state':'FAILED_DIAGNOSTIC_PROCESS_ENVELOPE_NOT_CPP_COMPATIBILITY_RESULT',
    'scheduler_accounting':account,'container_creation_seconds':76,
    'torch_import_seconds':result['phase_import_torch_seconds'],
    'seconds_after_container_creation_until_absolute_process_deadline':result['process_deadline_epoch']-end,
    'fixtures_completed':0,'source_prebuild_hashes_recorded':len(result['prebuild_runtime_source_sha256']),
    'native_cleanup_end_seen':False,'old_rootfs_actual_presence':'UNKNOWN; inspect only exact allowlisted path on g1 inside a future allocated step.',
    'source_observation':'Outer timeout killed the srun step at its absolute 90-second deadline; no native-remove-end marker survives. This is not a supported cleanup pass.',
    'actual_allocated_GPU_hours':0,'actual_CPU_hours':2*93/3600,
    'maximum_reserved_CPU_hours':2*2/60,'PBS_SU':0,
    'decision':'Keep S106 blocked. Prepare a separate R2 zero-GPU 4-CPU 16GiB six-minute stage, 300-second internal process window plus cleanup allowance; keep original fixture/source scope and independently review cleanup. This revises an agent stage envelope under existing Slurm authorization, not owner budget. Never extend old frozen job.',
    'limits':'No C++ binary completion, post-build hashes, CPU tree fixture, full allocator/P-D/Qwen/output or performance proof. Exact rootfs existence and residual process state were not observed after the allocation.'}
(D/'failure-review-27387.json').write_text(json.dumps(review,indent=2)+'\n')
(D/'FAILURE-27387.md').write_text("""# CPU prerequisite: bounded process window was too short

Actual job 27387 ended FAILED 124:0 after 93 seconds on g1, zero requested/allocated GPUs and two CPUs. It did not complete the C++ fixture and cannot qualify S106.

The fixed 90-second process window included container creation. Actual Enroot creation took 76 seconds; Torch import took 2.142 seconds. Only 14 seconds remained after container creation for imports, cold C++ JIT and fixtures. The final CPU result has empty fixture cases and state FAIL_TIME_LIMIT_OR_SIGNAL. Eight pre-build source hashes, compiler/Ninja/PyTorch versions and hidden-GPU checks were recorded. No successful C++ binary, post-build source record or fixture result exists. This does not establish an unsupported extension.

The outer timeout terminated srun itself. No native cleanup-end marker is present. Do not call cleanup complete or assume the exact rootfs still exists; inspect its allowlisted path and process ownership only inside an authorised allocated step on the original host. Original logs and failure JSON are sealed and unchanged.

Prepare a new bounded R2 stage with zero GPUs, four CPUs, 16 GiB and six minutes. Use an internal 300-second process deadline so native cleanup can complete before the scheduler limit, preserve the original source/toolchain/fixture and zero-GPU scope, and review residual state explicitly. The longer envelope is justified by actual setup cost and revises an agent-created bound under the owner's existing Slurm authorization. It is not a request for extra PBS spending or a silent extension of 27387.

Observed cost is 0 allocated GPU-hours and 0.051667 CPU-hours; maximum original reservation 0.066667 CPU-hours. The partition's exclusive placement occupied one node during the 93 seconds even though it allocated no GPU resource. No PBS SU. Full model integration, output quality, official accuracy and performance remain unmeasured. Keep S106 blocked until an actual reviewed replacement prerequisite passes.
""")
print(json.dumps({'job':27387,'state':review['state'],'creation_seconds':76,'remaining_seconds':14}))
