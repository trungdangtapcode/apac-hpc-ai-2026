#!/usr/bin/env python3
"""Add reviewed operational source and public model metadata to the snapshot."""
import importlib.util,json,hashlib,os,subprocess,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 s=importlib.util.spec_from_file_location('builder',ROOT/'tools/build_snapshot.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);store=ROOT.with_name(ROOT.name+'-artifacts');manifest=[json.loads(x) for x in (ROOT/'backup/manifest.jsonl').read_text().splitlines()];paths={r['path'] for r in manifest};report=json.loads((ROOT/'backup/scan-results.json').read_text());index=json.loads((store/'objects-index.json').read_text());known={r['sha256'] for r in index};extras=[]
 vpn=Path('/home/apacsc42/workspace/vpn-rootless')
 for name in sorted(m.VPN_ALLOW):
  p=vpn/name
  if p.is_file():extras.append(('workspace/vpn-rootless/'+name,p))
 model=Path('/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8')
 for p in sorted(model.iterdir()):
  if p.is_file() and p.suffix!='.safetensors' and p.stat().st_size<64*1024*1024:extras.append(('external-runtime/model-metadata/'+p.name,p))
 for rel,path in extras:
  if rel in paths:continue
  st=path.stat();h,flags=m.inspect(path)
  if flags:report['excluded'].append(dict(path=rel,reason='Potential secret content in allowlisted source',rules=flags));continue
  r=dict(path=rel,sha256=h,bytes=st.st_size,mtime_ns=st.st_mtime_ns,mode=st.st_mode&0o777,secret_scan='patterns',storage='git');dest=ROOT/rel
  if st.st_size<=1024*1024:
   dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes());os.chmod(dest,r['mode']);os.utime(dest,ns=(st.st_mtime_ns,st.st_mtime_ns))
  else:
   r.update(storage='object',object='objects/'+h[:2]+'/'+h+'.zst');obj=store/r['object'];obj.parent.mkdir(exist_ok=True)
   if h not in known:
    subprocess.run(['zstd','-q','-T1','-3','-f',str(path),'-o',str(obj)],check=True);p=subprocess.Popen(['zstd','-q','-d','-c',str(obj)],stdout=subprocess.PIPE);check=hashlib.sha256();n=0
    while True:
     b=p.stdout.read(4*1024*1024)
     if not b:break
     check.update(b);n+=len(b)
    assert p.wait()==0 and check.hexdigest()==h and n==st.st_size;index.append(dict(sha256=h,bytes=st.st_size,stored_bytes=obj.stat().st_size,object=r['object']));known.add(h)
   if dest.exists():dest.unlink()
  manifest.append(r);paths.add(rel)
 for e in report['excluded']:
  if e['path']=='workspace/vpn-rootless':e['reason']='Private/runtime VPN subtree excluded; separately scanned root source allowlist is retained in manifest'
 manifest.sort(key=lambda r:r['path']);(ROOT/'backup/manifest.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in manifest));(store/'objects-index.json').write_text(json.dumps(index,indent=2)+'\n');(ROOT/'backup/scan-results.json').write_text(json.dumps(report,indent=2)+'\n')
 summary=json.loads((ROOT/'backup/summary.json').read_text());summary.update(retained_files=len(manifest),git_files=sum(r['storage']=='git' for r in manifest),logical_bytes=sum(r['bytes'] for r in manifest),git_worktree_bytes=sum(r['bytes'] for r in manifest if r['storage']=='git'),unique_external_objects=len(index),external_object_bytes=sum(r['stored_bytes'] for r in index),excluded_entries=len(report['excluded']),operational_source_allowlist_added=True,finalized_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(ROOT/'backup/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 # Container identity is checked against the original tested contract.
 contract=json.loads((ROOT/'2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/asset-contract.json').read_text());checks={}
 for name,expected in contract['images'].items():
  row=next(r for r in manifest if r['path']=='external-runtime/enroot-images/'+name);checks[name]=dict(expected_sha256=expected['sha256'],captured_sha256=row['sha256'],matches=row['sha256']==expected['sha256'])
 # Keep damaged collection archives as local-only evidence, never as approved publishable payloads.
 review=[]
 for excluded in list(report['excluded']):
  if excluded.get('rules')!=['archive_not_safely_inspectable']:continue
  rel=excluded['path'];source=Path('/home/apacsc42')/rel;st=source.stat();h=hashlib.sha256()
  with source.open('rb') as f:
   for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
  digest=h.hexdigest();objrel='local-review-objects/'+digest+'.zst';obj=store/objrel;obj.parent.mkdir(exist_ok=True)
  subprocess.run(['zstd','-q','-T1','-3','-f',str(source),'-o',str(obj)],check=True)
  process=subprocess.Popen(['zstd','-q','-d','-c',str(obj)],stdout=subprocess.PIPE);check=hashlib.sha256();n=0
  while True:
   block=process.stdout.read(4*1024*1024)
   if not block:break
   check.update(block);n+=len(block)
  assert process.wait()==0 and check.hexdigest()==digest and n==st.st_size
  manifest.append(dict(path=rel,sha256=digest,bytes=st.st_size,mtime_ns=st.st_mtime_ns,mode=st.st_mode&0o777,storage='object',object=objrel,secret_scan='raw signatures scanned; archive member decoding incomplete',distribution_status='LOCAL_ONLY_REVIEW_REQUIRED'))
  index.append(dict(sha256=digest,bytes=st.st_size,stored_bytes=obj.stat().st_size,object=objrel,distribution_status='LOCAL_ONLY_REVIEW_REQUIRED'));review.append(dict(path=rel,reason='Damaged collection archive retained byte-for-byte; no credential finding, but member inspection incomplete',object=objrel));report['excluded'].remove(excluded)
 report['local_only_review']=review
 manifest.sort(key=lambda r:r['path']);(ROOT/'backup/manifest.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in manifest));(store/'objects-index.json').write_text(json.dumps(index,indent=2)+'\n');(ROOT/'backup/scan-results.json').write_text(json.dumps(report,indent=2)+'\n');summary.update(retained_files=len(manifest),logical_bytes=sum(r['bytes'] for r in manifest),unique_external_objects=len(index),external_object_bytes=sum(r['stored_bytes'] for r in index),excluded_entries=len(report['excluded']),local_only_review_files=len(review));(ROOT/'backup/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 # Record empty directories so the required empty HPC_Task layout can be restored.
 directories=[]
 for top in ['2026-APAC-HPC-AI','workspace']:
  for directory,children,files in os.walk(Path('/home/apacsc42')/top,followlinks=False):
   directory=Path(directory);rel=directory.relative_to('/home/apacsc42')
   if m.policy(str(rel)+'/'):
    children[:]=[];continue
   children[:]=[x for x in children if x not in m.PRUNE and not (directory/x).is_symlink()]
   directories.append(str(rel))
 (ROOT/'backup/directories.json').write_text(json.dumps(sorted(directories),indent=2)+'\n')
 (ROOT/'backup/runtime-identity.json').write_text(json.dumps(checks,indent=2)+'\n');assert all(x['matches'] for x in checks.values()),'Container differs from tested contract';print(json.dumps(summary))
if __name__=='__main__':main()
