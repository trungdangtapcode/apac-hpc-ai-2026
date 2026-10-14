"""Freeze two prefill-only hypotheses derived from measured TTFT failures."""
import hashlib
import json
import shlex
import shutil
import subprocess
from pathlib import Path

DIR=Path(__file__).resolve().parent;ROOT=DIR.parent
plan_path=DIR/'prefill-pilots.json'
assert not plan_path.exists(), 'Refusing to overwrite a prepared research wave'
state=json.loads((ROOT/'serving-tuning/registry.json').read_text())
entry=next(e for e in state['entries'] if e['id']=='s2-repeat-best')
source=Path(entry['bundle']);pilots=[]
for name,pflags,rflags,purpose in [
    ('s4-prefill-single-n52',['--prefill-max-requests','1'],[],
     'Limit each prefill batch to one request at chunk4096; test completion/TTFT against partially packed two-request batches observed in logs.'),
    ('s4-prefill-roundrobin-n52',[],['--prefill-policy','round_robin'],
     'Route prefill round-robin instead of inherited cache_aware policy; test initial burst balance on the cache-busted workload. Decode routing retained.')]:
    bundle=DIR/name;bundle.mkdir()
    for p in source.iterdir():
        if p.is_file() and p.name!='SHA256SUMS':shutil.copyfile(p,bundle/p.name)
    config=json.loads((bundle/'config.json').read_text())
    config.update(experiment=name,concurrency=[52],wave=4,purpose=purpose,
                  source_experiment=entry['id'],source_job='23266',
                  reference_jobs=['23130','23266'],fresh_control_job='23286',
                  router_extra_flags=rflags,quality_status='Research checks only; organiser full-set accuracy unverified')
    if pflags:
        worker=(bundle/'worker.sh').read_text();old='extra=(--chunked-prefill-size 4096)'
        assert worker.count(old)==1
        worker=worker.replace(old,'extra=(--chunked-prefill-size 4096 '+shlex.join(pflags)+')')
        (bundle/'worker.sh').write_text(worker)
        config['prefill_extra_flags']+=pflags
    if rflags:
        job=(bundle/'topology-job.sh').read_text()
        old='python3 -m sglang_router.launch_router --pd-disaggregation "${router_args[@]}"'
        assert job.count(old)==1
        job=job.replace(old,'python3 -m sglang_router.launch_router --pd-disaggregation '+shlex.join(rflags)+' "${router_args[@]}"')
        (bundle/'topology-job.sh').write_text(job)
    (bundle/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    script=(bundle/'job.sbatch').read_text().replace(str(source),str(bundle))
    script=script.replace('#SBATCH -J ap42-tune-s2-repeat-be','#SBATCH -J ap42-'+name[:20])
    (bundle/'job.sbatch').write_text(script)
    for name_script in ('worker.sh','topology-job.sh','job.sbatch','benchmark.sh'):
        subprocess.run(['bash','-n',str(bundle/name_script)],check=True)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.iterdir())}
    (bundle/'SHA256SUMS').write_text(''.join(f'{sha}  {name}\n' for name,sha in hashes.items()))
    subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,check=True,capture_output=True)
    for p in bundle.iterdir():p.chmod(0o444)
    bundle.chmod(0o555)
    pilots.append(dict(id=name,bundle=str(bundle),planned_ns=[52],state='PLANNED',wave=4,
                       purpose=purpose,payload_sha256=hashes,measurements=[],missing_ns=[52],
                       benchmark_complete=False,profile_complete=None,traces=[],attempts=[]))
plan=dict(scope='Two N52 pilots only; one prefill factor per trial, unchanged model/precision/decode/client. No automatic promotion.',
          source_experiment=entry['id'],reference_jobs=['23130','23266'],fresh_control_job='23286',
          required_evidence='Read latency-failures.json and research note; validate actual-image flags before submitting.',
          max_active_jobs=4,pilots=pilots)
plan_path.write_text(json.dumps(plan,indent=2)+'\n');print('Frozen:',[p['id'] for p in pilots])
