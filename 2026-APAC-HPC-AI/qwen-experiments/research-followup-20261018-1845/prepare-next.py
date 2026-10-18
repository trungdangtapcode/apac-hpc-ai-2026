"""Prepare three bounded H200 followups; submit only after completed reviews pass."""
from pathlib import Path
import json,shutil,hashlib,subprocess,ast
R=Path.cwd();D=R/'serving-tuning-10';O=R/'research-followup-20261018-1845';pilots=[];payloads={}
specs=[('s11-hpc-decode-n56','s13-hpc-decode-n58','load'),('s12-hpc-prefill-repeat-n56','s13-hpc-prefill-chunk6144-n56','chunk'),('s12-hpc-prefill-repeat-n56','s13-hpc-both-n56','decode')]
for source,name,kind in specs:
 src=D/source;dst=D/name;assert not dst.exists();shutil.copytree(src,dst);f=dst/'job.sbatch';s=f.read_text().replace(source,name)
 if kind=='load':assert 'QWEN_TUNE_NS=56' in s;s=s.replace('QWEN_TUNE_NS=56','QWEN_TUNE_NS=58')
 f.write_text(s);c=json.loads((dst/'config.json').read_text());n=58 if kind=='load' else 56;c.update(experiment=name,source_experiment=source,source_job='24538' if kind=='load' else '24574',concurrency=[n],matched_concurrency=n,diagnostic_profile=False,accuracy_verified=False)
 c['purpose']={'load':'One N58 HPC-Ops decode trial from verified N56 ITL headroom; retain DeepGEMM prefill chunk4096 and compare same-load control24589','chunk':'Combine independently repeated HPC-Ops prefill with independently repeated chunk6144; compare24574 for chunk and24573 for runner effects','decode':'Add verified HPC-Ops decode to repeated HPC-Ops prefill at N56; isolate decode against24574 and prefill against24538'}[kind]
 if kind=='chunk':
  f=dst/'worker.sh';s=f.read_text();assert '--chunked-prefill-size 4096' in s;s=s.replace('--chunked-prefill-size 4096','--chunked-prefill-size 6144');f.write_text(s);c['prefill_chunk_size']=6144;c['prefill_extra_flags'][1]='6144'
 if kind=='decode':
  f=dst/'worker.sh';s=f.read_text();assert '--decode-attention-backend flashinfer)' in s;s=s.replace('--decode-attention-backend flashinfer)','--decode-attention-backend flashinfer --moe-runner-backend hpc_ops)');probe=(D/'s11-hpc-decode-n56/worker.sh').read_text().split('else\n',1)[1].split('  extra=',1)[0];assert 'HPCCHECK' in probe;s=s.replace('else\n  extra=','else\n'+probe+'  extra=');f.write_text(s);c['decode_extra_flags']+=['--moe-runner-backend','hpc_ops']
 (dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in ['.sh','.sbatch']:subprocess.run(['bash','-n',str(f)],check=True)
 for filename in ['benchmark.sh','profile-serving.py','topology-job.sh','nixl-conn.py','output-smoke.py','long-context-check.py']:assert (src/filename).read_bytes()==(dst/filename).read_bytes()
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));payloads[name]=h
 pilots.append(dict(id=name,bundle=str(dst),planned_ns=[n],state='PLANNED',wave=10,purpose=c['purpose'],diagnostic_profile=False,expected_profile_ranks={},payload_sha256=h,measurements=[],missing_ns=[n],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job=c['source_job']))
(O/'slurm-pilots.json').write_text(json.dumps(pilots,indent=2)+'\n');(O/'next-validation.json').write_text(json.dumps(dict(passed=True,payloads=payloads,scoring_quality_transport_unchanged=True),indent=2)+'\n');print('Three H200 bundles frozen; not yet armed')
