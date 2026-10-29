#!/usr/bin/env python3
"""Derive cache-class-controlled cold-prefill trials from the actual full control."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
D=Path(__file__).resolve().parent
Q=D.parent
P=Q/'runs/27270/submitted-payload'
source=json.loads((Q/'h200-cold-prefill-cache-source-20261029/SOURCE_MANIFEST.json').read_text())
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=P,check=True,stdout=subprocess.DEVNULL)
for f in source['files']:
    assert hashlib.sha256((Q/'h200-cold-prefill-cache-source-20261029'/f['path']).read_bytes()).hexdigest()==f['sha256']
records=[]
for label,disabled in [('s103-h200-cold-cache-control',False),('s104-h200-prefill-chunk-cache',True)]:
    B=Q/'serving-tuning-11'/label
    shutil.copytree(P,B)
    cfg=json.loads((P/'config.json').read_text())
    cfg.update(experiment=label,label=label,source_parent_job=27270,source_parent='s101-h200-transfer-poll1',study_arm='prefill_chunk_cache' if disabled else 'fresh_radix_control',prefill_disable_radix_cache=disabled,decode_disable_radix_cache=True,prefill_expected_cache='ChunkCache' if disabled else 'RadixCache',decode_expected_cache='ChunkCache',performance_or_GPU_acceptance='UNKNOWN',matched_pair='Prospective control vs prefill-only disable_radix_cache; all other settings unchanged.')
    (B/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    s=(P/'worker.sh').read_text()
    if disabled:
        old='extra=(--chunked-prefill-size 8192 --moe-runner-backend deep_gemm --cuda-graph-backend-prefill breakable)'
        assert s.count(old)==1
        s=s.replace(old,old[:-1]+' --disable-radix-cache)')
    needle="print('TRANSFER_POLL_SOURCE_VERIFIED',flush=True)"
    assert s.count(needle)==1
    proof='\n'.join(f"assert hashlib.sha256(Path('/{f['image_path']}').read_bytes()).hexdigest()=='{f['sha256']}', 'Pinned cache lifecycle source mismatch'" for f in source['files'])
    s=s.replace(needle,needle+'\n'+proof+"\nprint('CACHE_LIFECYCLE_SOURCE_VERIFIED',flush=True)")
    (B/'worker.sh').write_text(s)
    s=(P/'check-fast-runtime.py').read_text()
    needle='    for key,wanted in common.items():'
    assert s.count(needle)==1
    s=s.replace(needle,"""    common.update(disable_radix_cache=cfg['prefill_disable_radix_cache'] if role.startswith('prefill') else cfg['decode_disable_radix_cache'],
        prefill_only_disable_kv_cache=False,radix_cache_backend=None,enable_session_radix_cache=False,enable_streaming_session=False,enable_hierarchical_cache=False)
"""+needle)
    needle="    expected_kv=1 if arm=='control' else 2"
    assert s.count(needle)==1
    s=s.replace(needle,"""    expected_cache=cfg['prefill_expected_cache'] if role.startswith('prefill') else cfg['decode_expected_cache']
    cache_rows=re.findall(r'TP(\\d+)(?: EP\\d+)?\\] Tree cache initialized: source=default impl=(\\w+) hybrid_swa=False hybrid_ssm=False hierarchical=False streaming_wrapped=False',text)
    if collections.Counter(cache_rows)!=collections.Counter({(str(i),expected_cache):1 for i in range(nranks)}):
        raise ValueError(f'{role}: actual per-rank cache implementation differs or is incomplete')
"""+needle)
    s=s.replace("'server_args_records':1","'server_args_records':1,'actual_cache_class':expected_cache,'disable_radix_cache':common['disable_radix_cache']")
    (B/'check-fast-runtime.py').write_text(s)
    s=(P/'job.sbatch').read_text().replace('s101-h200-transfer-poll1',label).replace('#SBATCH -J ap42-s101-poll1','#SBATCH -J ap42-s104-pcache' if disabled else '#SBATCH -J ap42-s103-ctrl')
    (B/'job.sbatch').write_text(s)
    (B/'README.md').write_bytes((D/'PLAN.md').read_bytes())
    unchanged=['topology-job.sh','check-performance.py','benchmark.sh','performance_gates.py','native-container.sh','nixl-conn.py','kv_geometry.py','validate_kv_geometry.py','warm-topology.py','warmup_semantic.py','resource-sampler.py','expected-input-config.json','reference-output-smoke.json']
    for n in unchanged:
        assert (B/n).read_bytes()==(P/n).read_bytes(),n
    for p in B.rglob('*'):
        if p.suffix=='.py':ast.parse(p.read_text())
        if p.suffix in ('.sh','.sbatch'):subprocess.run(['bash','-n',str(p)],check=True)
    files=sorted(p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='SHA256SUMS')
    (B/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(B))+'\n' for p in files))
    records.append({'bundle':str(B.relative_to(Q)),'disabled_prefill_radix':disabled,'manifest_sha256':hashlib.sha256((B/'SHA256SUMS').read_bytes()).hexdigest()})
(D/'preparation.json').write_text(json.dumps({'state':'PREPARED_NOT_SUBMITTED','bundles':records,'source_evidence':source,'parent_manifest_sha256':hashlib.sha256((P/'SHA256SUMS').read_bytes()).hexdigest(),'unchanged_files':unchanged},indent=2)+'\n')
print(json.dumps(records,indent=2))
