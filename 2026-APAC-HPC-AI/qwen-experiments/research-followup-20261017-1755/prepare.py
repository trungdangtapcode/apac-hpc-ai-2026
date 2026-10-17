"""Prepare source-justified trials; preserve submitted and historical artifacts."""
from pathlib import Path
import shutil,json,hashlib,subprocess,datetime,tempfile,tarfile
R=Path.cwd();O=R/'research-followup-20261017-1755';D=R/'serving-tuning-10';P=R/'nscc-pbs';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
# Re-run the actual equal-TP range tests in an isolated copy, preserving old evidence.
with tempfile.TemporaryDirectory(prefix='ap42-equal-geometry-') as td:
 t=Path(td);shutil.copytree(R/'nixl-equal-ondemand',t/'nixl-equal-ondemand');shutil.copy2(R/'test-nixl-equal-ondemand.py',t/'test-nixl-equal-ondemand.py')
 r=subprocess.run(['/tmp/ap42-cross-platform-venv/bin/python',str(t/'test-nixl-equal-ondemand.py')],capture_output=True,text=True,check=True);(O/'equal-geometry-test.json').write_text(r.stdout);geometry=json.loads(r.stdout);assert geometry['passed'] and geometry['range_equivalence_cases']==936
report={'created_utc':now,'bundles':{}};new=[]
for src,name,kind,pbs in [(D/'s10-prefill-tp8ep2-n56','s10-prefill-tp8ep2-equal-n56','equal',False),(D/'s10-combo-repeat-n56','s10-prefill-no-graph-n56','graphs',False),(P/'h100-combo-control-16','h100-prefill-no-graph-20','graphs',True)]:
 dst=src.parent/name;assert not dst.exists();shutil.copytree(src,dst);allowed={'config.json','SHA256SUMS','benchmark.pbs' if pbs else 'job.sbatch'}
 f=dst/('benchmark.pbs' if pbs else 'job.sbatch');s=f.read_text().replace(src.name,name)
 c=json.loads((dst/'config.json').read_text());c.update(experiment=name,source_job='221151.pbs111' if pbs else '24321' if kind=='equal' else '24320')
 if kind=='equal':
  patch=R/'nixl-equal-ondemand';old='912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f';newhash='e979738ef1681b793b09e3b81d2d4e4563535c1a354bf2e7ac76da14f73c856c';assert old in s;s=s.replace(old,newhash)
  for source,target in [('conn.py','nixl-conn.py'),('metadata.json','nixl-patch-metadata.json'),('nixl-ondemand.patch','nixl-ondemand.patch'),('geometry-test.json','nixl-geometry-test.json')]:shutil.copyfile(patch/source,dst/target);allowed.add(target)
  assert hashlib.sha256((dst/'nixl-conn.py').read_bytes()).hexdigest()==newhash
  c.update(purpose='Repair TP8-to-TP8 warmup timeout using exact previously GPU-validated equal-TP transport patch; no model/kernel/load changes',retry_of='24321',transport_patch='equal-tp8-request-descriptors-v1',transport_patch_metadata=json.loads((patch/'metadata.json').read_text()),prior_gpu_validation_job='22809',prior_gpu_validation_record=str(patch/'gpu-validation.json'))
 else:
  f2=dst/'worker.sh';s2=f2.read_text();assert s2.count('extra=(--chunked-prefill-size 4096)')==1;f2.write_text(s2.replace('extra=(--chunked-prefill-size 4096)','extra=(--chunked-prefill-size 4096 --disable-prefill-cuda-graph)'));allowed.add('worker.sh');c.update(purpose='Measure prefill CUDA graph startup cost versus scored goodput; decode graphs and kernels unchanged',prefill_extra_flags=['--chunked-prefill-size','4096','--disable-prefill-cuda-graph'])
 f.write_text(s);(dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in src.iterdir():
  if f.is_file() and f.name not in allowed:assert f.read_bytes()==(dst/f.name).read_bytes(),f.name
 for f in list(dst.glob('*.sh'))+[dst/('benchmark.pbs' if pbs else 'job.sbatch')]:subprocess.run(['bash','-n',str(f)],check=True)
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));report['bundles'][name]=h
 if not pbs:new.append(dict(id=name,bundle=str(dst),planned_ns=[56],state='PLANNED',wave=10,purpose=c['purpose'],diagnostic_profile=False,expected_profile_ranks={},payload_sha256=h,measurements=[],missing_ns=[56],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job=c['source_job']))
 else:
  with tarfile.open(O/'h100-no-graph.tar.gz','w:gz') as tar:tar.add(dst,arcname=name)
q=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True);assert len(q.splitlines())+2<=5
f=D/'prepared-pilots.json';p=json.loads(f.read_text());p['pilots'].extend(new);p['updated_utc']=now;tmp=f.with_suffix('.repair-graphs.tmp');tmp.write_text(json.dumps(p,indent=2)+'\n');tmp.replace(f)
(O/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('Armed equal-TP repair and prefill graph test on H200; prepared H100 graph test; 936 geometry cases pass')
