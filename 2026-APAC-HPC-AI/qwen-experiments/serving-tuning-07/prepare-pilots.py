"""Keep the queue supplied with independent, justified round-robin experiments."""
import hashlib
import json
import shlex
import shutil
import subprocess
from datetime import datetime,timezone
from pathlib import Path

DIR=Path(__file__).resolve().parent;ROOT=DIR.parent;path=DIR/'prepared-pilots.json'
assert not path.exists(), 'Refusing to overwrite prepared experiment history'
state=json.loads((ROOT/'serving-tuning/registry.json').read_text())
source_entry=next(e for e in state['entries'] if e['id']=='s5-rr-repeat-n52')
assert source_entry['state']=='MEASURED'
row=source_entry['measurements'][0]
assert row['sla_pass'] and row['errors']==0 and row['cancelled_requests']==0 and row['output_baseline_comparison']['research_eligible']
source=Path(source_entry['bundle']);pilots=[]
specs=[
    ('s7-rr-cutlass-n52',[],['--moe-runner-backend','cutlass'],False,'Decode CUTLASS block-FP8 MoE versus auto/Triton. Round-robin N52 profile attributes 27.4% summed decode kernel duration to MoE; actual staged implementation supports SM90 block FP8.'),
    ('s7-rr-flashinfer-n52',[],['--decode-attention-backend','flashinfer'],False,'Decode FlashInfer attention versus FA3, BF16 KV unchanged on both roles. FA3 attention is 19.6% of summed decode kernel duration; leave prefill attention, page size and KV transport unchanged.'),
    ('s7-rr-mnnvl-n52',[],['--flashinfer-allreduce-fusion-backend','mnnvl'],False,'Decode MNNVL fused allreduce versus auto/TRTLLM. Collectives are 20.1% of summed decode kernel duration; exact staged resolver permits SM90 single-node TP8. No quantized communication.')]

for name,pflags,dflags,profile,purpose in specs:
    bundle=DIR/name;bundle.mkdir()
    for p in source.iterdir():
        if p.is_file() and p.name!='SHA256SUMS':shutil.copyfile(p,bundle/p.name)
    config=json.loads((bundle/'config.json').read_text())
    worker=(bundle/'worker.sh').read_text()
    for key,extra in [('prefill_extra_flags',pflags),('decode_extra_flags',dflags)]:
        old='extra=('+shlex.join(config[key])+')'
        assert worker.count(old)==1
        if extra:worker=worker.replace(old,'extra=('+shlex.join(config[key]+extra)+')')
        config[key]+=extra
    (bundle/'worker.sh').write_text(worker)
    config.update(experiment=name,wave=7,concurrency=[52],purpose=purpose,diagnostic_profile=profile,
                  source_experiment=source_entry['id'],source_job='23576',reference_jobs=['23325','23576'],
                  matched_concurrency=52,quality_validation_required=bool(pflags or dflags),
                  quality_status='Research evidence only; organiser full-set accuracy unverified')
    if pflags:config['kv_dtype']='fp8_e4m3'
    if dflags and not pflags:config['decode_backend_override']=dflags
    if profile:
        helper=(bundle/'profile-serving.py').read_text()
        assert 'max_workers=48' in helper and 'range(48)' in helper and "'concurrency': 48" in helper
        helper=helper.replace('import sys\n','import sys\nimport os\n')
        helper=helper.replace('host, art_arg = sys.argv[1:]','host, art_arg = sys.argv[1:]\nconcurrency = int(os.environ.get("QWEN_PROFILE_N", "52"))')
        helper=helper.replace('max_workers=48','max_workers=concurrency').replace('range(48)','range(concurrency)').replace("'concurrency': 48","'concurrency': concurrency")
        (bundle/'profile-serving.py').write_text(helper)
    (bundle/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    script=(bundle/'job.sbatch').read_text().replace(str(source),str(bundle))
    script='\n'.join('#SBATCH -J ap42-'+name[:20] if line.startswith('#SBATCH -J ') else line for line in script.splitlines())+'\n'
    if profile:script=script.replace('export QWEN_DIAGNOSTIC_PROFILE=0','export QWEN_DIAGNOSTIC_PROFILE=1\nexport QWEN_PROFILE_N=52')
    (bundle/'job.sbatch').write_text(script)
    for name_script in ('worker.sh','topology-job.sh','job.sbatch','benchmark.sh'):
        subprocess.run(['bash','-n',str(bundle/name_script)],check=True)
    compile((bundle/'profile-serving.py').read_text(),str(bundle/'profile-serving.py'),'exec')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.iterdir())}
    (bundle/'SHA256SUMS').write_text(''.join(f'{sha}  {name}\n' for name,sha in hashes.items()))
    subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
    for p in bundle.iterdir():p.chmod(0o444)
    bundle.chmod(0o555)
    pilots.append(dict(id=name,bundle=str(bundle),planned_ns=[52],state='PLANNED',wave=7,purpose=purpose,
                       diagnostic_profile=profile,expected_profile_ranks={'prefill-0':4,'prefill-1':4,'decode-0':8} if profile else {},
                       payload_sha256=hashes,measurements=[],missing_ns=[52],benchmark_complete=False,
                       profile_complete=None,traces=[],attempts=[]))
plan=dict(created_utc=datetime.now(timezone.utc).isoformat(),state='PLANNED',
          scope='Three independent initial jobs; same confirmed RR N52 and official protocol. Keep four account jobs pending/running. No automatic submission promotion.',
          source_experiment=source_entry['id'],reference_jobs=['23325','23576'],max_active_jobs=4,pilots=pilots)
path.write_text(json.dumps(plan,indent=2)+'\n');print('Frozen', [p['id'] for p in pilots])
