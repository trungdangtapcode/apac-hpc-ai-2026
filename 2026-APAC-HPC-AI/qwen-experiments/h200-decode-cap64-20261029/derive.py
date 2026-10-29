#!/usr/bin/env python3
"""Derive one source-qualified decode-cap trial without changing original gates."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
D=Path(__file__).resolve().parent;Q=D.parent;P=Q/'runs/27270/submitted-payload';B=Q/'serving-tuning-11/s102-h200-decode-cap64'
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=P,check=True,stdout=subprocess.DEVNULL);shutil.copytree(P,B)
cfg=json.loads((P/'config.json').read_text());cfg.update(experiment=B.name,label='Exploratory decode running cap64; separate transfer reserve retained',source_parent_job=27270,source_parent='s101-h200-transfer-poll1',matched_control_job=27270,study_arm='decode_running_cap64',decode_max_running_requests=64,performance_or_GPU_acceptance='UNKNOWN',matched_pair='Only decode running cap256→64; full target-only N64 protocol. Low-upside resource sensitivity, not proven optimization.')
(B/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
s=(P/'topology-job.sh').read_text();old='extra=(--ep-size "$tp" --max-running-requests 256)';assert s.count(old)==1;s=s.replace(old,'extra=(--ep-size "$tp" --max-running-requests 64)');(B/'topology-job.sh').write_text(s)
s=(P/'check-fast-runtime.py').read_text();old="'max_running_requests':prefill_cap if role.startswith('prefill') else 256,";assert s.count(old)==1;s=s.replace(old,"'max_running_requests':prefill_cap if role.startswith('prefill') else cfg['decode_max_running_requests'],")
needle="    graph=kwmap(args.get('cuda_graph_config'),role+'.cuda_graph_config')";assert s.count(needle)==1
s=s.replace(needle,"""    if role=='decode-0':
        final=re.findall(r'TP0 EP0\\] max_total_num_tokens=\\d+,[^\\n]*max_running_requests=(\\d+), context_len=8192',text)
        if final!=[str(cfg['decode_max_running_requests'])]: raise ValueError('decode-0: final scheduler cap absent or differs from configured cap')
"""+needle)
(B/'check-fast-runtime.py').write_text(s)
s=(P/'check-performance.py').read_text();old="cap=cfg['prefill_max_running_requests'] if role.startswith('prefill') else 256";assert s.count(old)==1;s=s.replace(old,"cap=cfg['prefill_max_running_requests'] if role.startswith('prefill') else cfg['decode_max_running_requests']");(B/'check-performance.py').write_text(s)
s=(P/'worker.sh').read_text();needle="print('TRANSFER_POLL_SOURCE_VERIFIED',flush=True)";assert s.count(needle)==1
source=json.loads((Q/'h200-decode-capacity-source-20261029/evidence/SOURCE_MANIFEST.json').read_text())
for f in source['files']:assert hashlib.sha256((Q/'h200-decode-capacity-source-20261029'/f['path']).read_bytes()).hexdigest()==f['sha256']
proof='\n'.join(f"assert hashlib.sha256(Path('/{f['image_path']}').read_bytes()).hexdigest()=='{f['sha256']}', 'Pinned decode pool source mismatch'" for f in source['files'])
s=s.replace(needle,needle+'\n'+proof+"\nprint('DECODE_POOL_SOURCE_VERIFIED',flush=True)");(B/'worker.sh').write_text(s)
s=(P/'job.sbatch').read_text().replace('s101-h200-transfer-poll1',B.name).replace('#SBATCH -J ap42-s101-poll1','#SBATCH -J ap42-s102-dcap64');(B/'job.sbatch').write_text(s)
(B/'README.md').write_bytes((D/'PLAN.md').read_bytes())
unchanged=['benchmark.sh','performance_gates.py','native-container.sh','nixl-conn.py','kv_geometry.py','validate_kv_geometry.py','warm-topology.py','warmup_semantic.py','resource-sampler.py','expected-input-config.json','reference-output-smoke.json']
for n in unchanged:assert (B/n).read_bytes()==(P/n).read_bytes(),n
for p in B.rglob('*'):
 if p.suffix=='.py':ast.parse(p.read_text())
 if p.suffix in ('.sh','.sbatch'):subprocess.run(['bash','-n',str(p)],check=True)
files=sorted(p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='SHA256SUMS');(B/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(B))+'\n' for p in files))
(D/'preparation.json').write_text(json.dumps({'state':'PREPARED_NOT_SUBMITTED','bundle':str(B.relative_to(Q)),'manifest_sha256':hashlib.sha256((B/'SHA256SUMS').read_bytes()).hexdigest(),'source_parent_job':27270,'source_parent_manifest_sha256':hashlib.sha256((P/'SHA256SUMS').read_bytes()).hexdigest(),'unchanged_files':unchanged,'source_evidence':source},indent=2)+'\n')
print(B)
