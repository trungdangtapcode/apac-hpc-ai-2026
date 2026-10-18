from pathlib import Path
import json,shutil,subprocess,hashlib,ast,datetime,tarfile
R=Path.cwd();D=R/'serving-tuning-10';P=R/'nscc-pbs';O=R/'research-followup-20261018-0800'
now=datetime.datetime.now(datetime.timezone.utc).isoformat(); validation={};new=[]
preflight="""  python3 - <<'HPCCHECK'
import torch, hpc
assert torch.cuda.get_device_capability()[0] == 9, 'Hopper GPU required'
assert hasattr(hpc, 'fuse_moe_blockwise'), 'Missing HPC-Ops FP8 kernel'
print('HPC_OPS_PREFLIGHT_PASSED', torch.cuda.get_device_name(), flush=True)
HPCCHECK
"""
specs=[(D,'s10-prefill-deepgemm-n56','s11-dg-control-n56','control'),(D,'s10-prefill-deepgemm-chunk8192-n56','s11-dg-chunk8192-repeat-n56','8192'),(D,'s10-prefill-deepgemm-n56','s11-dg-chunk6144-n56','6144'),(D,'s10-prefill-deepgemm-n56','s11-hpc-prefill-n56','hpc-prefill'),(P,'h100-prefetch-repeat-21','h100-prefetch-profile-23','profile'),(P,'h100-prefetch-repeat-21','h100-hpc-decode-24','hpc-decode')]
for parent,source,name,kind in specs:
 src=parent/source;dst=parent/name;assert not dst.exists();shutil.copytree(src,dst)
 job=dst/('job.sbatch' if parent==D else 'benchmark.pbs');s=job.read_text().replace(source,name)
 if kind=='profile':s=s.replace('QWEN_DIAGNOSTIC_PROFILE=0','QWEN_DIAGNOSTIC_PROFILE=1')
 job.write_text(s)
 c=json.loads((dst/'config.json').read_text());c.update(experiment=name,source_experiment=source,source_job='24425' if kind=='8192' else ('221194.pbs111' if parent==P else '24429'),diagnostic_profile=kind=='profile',matched_concurrency=56 if parent==D else 50,accuracy_verified=False)
 c['purpose']={'control':'Fresh DeepGEMM chunk4096 N56 control for chunk and backend trials','8192':'Independent repeat of the provisional 0.20 percent chunk8192 gain','6144':'Test intermediate prefill chunk size; isolate batch geometry while holding backend and load fixed','hpc-prefill':'Source-compatible Hopper FP8 HPC-Ops prefill trial; decode unchanged','profile':'Fresh N50 prefetch control followed by separate N48 diagnostic profile; no claim of prefetch throughput gain','hpc-decode':'Hopper FP8 HPC-Ops decode trial versus fresh prefetch control; prefill unchanged'}[kind]
 w=dst/'worker.sh';s=w.read_text()
 if kind=='6144':
  assert '--chunked-prefill-size 4096' in s;s=s.replace('--chunked-prefill-size 4096','--chunked-prefill-size 6144');c['prefill_chunk_size']=6144;c['prefill_extra_flags'][1]='6144'
 if kind=='hpc-prefill':
  assert '--moe-runner-backend deep_gemm' in s;s=s.replace('--moe-runner-backend deep_gemm','--moe-runner-backend hpc_ops');s=s.replace('if [[ $role == prefill ]]; then\n','if [[ $role == prefill ]]; then\n'+preflight);c['prefill_extra_flags'][-1]='hpc_ops'
 if kind=='hpc-decode':
  assert '--decode-attention-backend flashinfer)' in s;s=s.replace('--decode-attention-backend flashinfer)','--decode-attention-backend flashinfer --moe-runner-backend hpc_ops)');s=s.replace('else\n  extra=','else\n'+preflight+'  extra=');c['decode_extra_flags']+=['--moe-runner-backend','hpc_ops']
 w.write_text(s)
 if parent==P:
  f=dst/'profile-serving.py';s=f.read_text();old="'/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8'";assert old in s;s=s.replace(old,"json.loads((art/'config.json').read_text())['model']");f.write_text(s)
 if kind=='profile':c.update(diagnostic_concurrency=48,diagnostic_prefill_steps=4,diagnostic_decode_steps=32)
 (dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text(),str(f))
  if f.suffix in ['.sh','.sbatch','.pbs']:subprocess.run(['bash','-n',str(f)],check=True)
 unchanged=['benchmark.sh','topology-job.sh','output-smoke.py','long-context-check.py','nixl-conn.py']
 for file in unchanged:assert (src/file).read_bytes()==(dst/file).read_bytes(),file
 hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'}
 (dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in hashes.items()));validation[name]=hashes
 if parent==D:new.append(dict(id=name,bundle=str(dst),planned_ns=[56],state='PLANNED',wave=10,purpose=c['purpose'],diagnostic_profile=False,expected_profile_ranks={},payload_sha256=hashes,measurements=[],missing_ns=[56],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job=c['source_job']))
q=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True);assert not q.strip()
f=D/'prepared-pilots.json';p=json.loads(f.read_text());assert not any(x['id'] in {z['id'] for z in new} for x in p['pilots']);p['pilots'].extend(new);p.update(state='ACTIVE',updated_utc=now);tmp=f.with_suffix('.new.tmp');tmp.write_text(json.dumps(p,indent=2)+'\n');tmp.replace(f)
with tarfile.open(O/'next-pbs.tar.gz','w:gz') as t:
 for name in ['h100-prefetch-profile-23','h100-hpc-decode-24']:t.add(P/name,arcname=name)
(O/'next-validation.json').write_text(json.dumps(dict(created_utc=now,payloads=validation,passed=True,unchanged_scoring_and_quality_scripts=True),indent=2)+'\n')
print('Four H200 pilots armed; two PBS bundles frozen and ready for budget reservation')
