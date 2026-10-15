"""Prepare an isolated loader-policy trial; do not upload, reserve or submit."""
from pathlib import Path
import ast, hashlib, json, shutil, subprocess
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'load-sweep-03'
target=ROOT/'h100-loader-prefetch-06'
assert not target.exists(), 'Keep existing attempts; never overwrite a frozen pilot'
shutil.copytree(source,target)
target.chmod(0o755)
for p in target.iterdir():p.chmod(0o644)
worker=target/'worker.sh'
text=worker.read_text()
old='extra=(--chunked-prefill-size 4096)'
assert text.count(old)==1
worker.write_text(text.replace(old,'extra=(--chunked-prefill-size 4096 --weight-loader-prefetch-checkpoints)'))
pbs=target/'benchmark.pbs'
pbs.write_text(pbs.read_text().replace('ap42-qwen-load32to42','ap42-qwen-loader-prefetch').replace('/load-sweep-03','/h100-loader-prefetch-06'))
for name in ('client-with-longcheck.sh','long-context-check.py'):
 shutil.copyfile(ROOT/'h100-mnnvl-04'/name,target/name)
topology=target/'topology-job.sh'
old='bash "$ART/benchmark.sh"'
assert topology.read_text().count(old)==1
topology.write_text(topology.read_text().replace(old,'bash "$BUNDLE/client-with-longcheck.sh"'))
config=json.loads((target/'config.json').read_text())
config.update(experiment='h100-loader-prefetch-06',source_job='220575.pbs111',control_job='220575.pbs111',
 purpose='Measure prefill startup with built-in checkpoint prefetch policy; decode flags unchanged.',
 prefill_extra_flags=['--chunked-prefill-size','4096','--weight-loader-prefetch-checkpoints'],
 benchmark_runtime_validation='PREPARED_LOCAL_ONLY; no runtime validation',
 accuracy_verified=False, retry_of=None, retry_reason=None,
 quality_status='Full organiser accuracy unverified; short and long diagnostics required separately',
 loader_policy_effect='Built-in prefetch enables background page-cache warming and implicitly selects single-thread iterator with default extra_config. Two TP4 replicas have independent prefetch rank groups; no guaranteed node-wide deduplication.',
 hypothesis='Potential shared-storage page-fault/CPU contention; not isolated from expert-sharding, CPU affinity or cache state.')
(target/'config.json').write_text(json.dumps(config,indent=2)+'\n')
(target/'SHA256SUMS').unlink()
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(target.iterdir()) if p.is_file()}
(target/'SHA256SUMS').write_text(''.join(f'{v}  {k}\n' for k,v in hashes.items()))
for p in target.iterdir():
 if p.suffix in ('.sh','.pbs'):subprocess.run(['bash','-n',str(p)],check=True)
 if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
unchanged=['benchmark.sh','summarize.py','nixl-conn.py','pbs-container.sh','pbs-exec.py','pbs-shim.sh','placement.tsv','output-smoke.py','warm-topology.py']
assert all((source/n).read_bytes()==(target/n).read_bytes() for n in unchanged)
assert config['walltime_minutes']==45 and config['confirm_warmup_s']==60 and config['confirm_measure_s']==120 and config['grace_s']==30
assert config['concurrency']==[32,34,36,38,40,42]
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=target,check=True,capture_output=True)
result=dict(passed=True,state='PREPARED_LOCAL_NOT_UPLOADED_NOT_SUBMITTED',runtime_validated=False,accuracy_verified=False,
 max_charge_su=1536,reservation_recorded=False,unchanged=unchanged,sha256=hashes,
 scope='Syntax, byte-identical workload and source-supported prefill flag. No GPU import or GPU work.')
(ROOT/'h100-loader-prefetch-06-validation.json').write_text(json.dumps(result,indent=2)+'\n')
for p in target.iterdir():p.chmod(0o444)
target.chmod(0o555)
print(json.dumps({k:v for k,v in result.items() if k!='sha256'},indent=2))
