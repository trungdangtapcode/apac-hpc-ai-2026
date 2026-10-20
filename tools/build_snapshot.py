#!/usr/bin/env python3
"""Build a local, secret-filtered snapshot with content-addressed large artifacts."""
import argparse,concurrent.futures,datetime,hashlib,json,os,re,shutil,stat,subprocess,tarfile,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATTERNS=[('private_key',rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),('github_token',rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),('openai_key',rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{35,}\b'),('aws_access_key',rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),('bearer_value',rb'(?i)authorization[\s\x22\x27:=]+Bearer\s+[A-Za-z0-9_.-]{24,}'),('literal_secret',rb'''(?i)\b(?:password|passwd|api_key|api-key|access_token|refresh_token|session_token|client_secret|session_secret)[\x22\x27]?\s*[:=]\s*[\x22\x27]([A-Za-z0-9_!@#$%^&*+./=:-]{10,})[\x22\x27]'''),('literal_sshpass',rb'''sshpass\s+-p\s+[\x22\x27]([A-Za-z0-9_!@#%^&*+./=:-]{8,})[\x22\x27]''')]
COMPILED=[(k,re.compile(v)) for k,v in PATTERNS]
PLACEHOLDERS=[b'not_used']
PRUNE={'.git','__pycache__','.cache','node_modules','.venv','venv'}
VPN_ALLOW={'vpn.sh','netns.py','enter.py','inside.py','vpn-session.sh','vpn-persistent.sh','README.md','.gitignore'}

def policy(path):
 p=Path(path);parts=p.parts;low=path.lower()
 if 'hf-cache' in parts and 'drafts' in parts:return 'Recreatable public draft model cache; retain pinned recovery metadata outside this directory'
 if p.suffix.lower() in {'.safetensors','.gguf'} or (p.name.startswith('pytorch_model') and p.suffix=='.bin'):return 'Model tensor weights excluded; retain source revision, file digest and recovery instructions'
 if path.rstrip('/')=='workspace/vpn-rootless':return None
 if path.startswith('workspace/vpn-rootless/'):
  tail=parts[2:]
  if len(tail)!=1 or tail[0] not in VPN_ALLOW:return 'VPN authentication, inspection, binaries or runtime state excluded; reviewed source allowlist only'
 if path.startswith('workspace/docker-rootless/'):return 'Recreatable rootless container installation and runtime state'
 if path.startswith('2026-APAC-HPC-AI/qwen-experiments/home/'):return 'Container home/mount runtime state'
 if p.name in ['.env','.netrc','.git-credentials','credentials','id_rsa','id_ed25519','known_hosts'] or p.suffix in ['.key','.p12','.pfx','.kdbx','.db','.sqlite','.sqlite3']:return 'Credential, private-key or session database filename'
 if p.name.startswith('.env.') and not p.name.endswith(('.example','.sample','.template')):return 'Environment secrets filename'
 if any(x in {'.ssh','.aws','private-cache','private-logs'} for x in parts):return 'Authentication material'
 return None

def findings(data):
 found=set();low=data.lower()
 for name,pattern in COMPILED:
  # Cheap necessary-condition checks preserve exactly the same match rules.
  if name=='private_key' and b'-----BEGIN ' not in data:continue
  if name=='github_token' and not any(x in data for x in [b'ghp_',b'gho_',b'ghu_',b'ghs_',b'ghr_',b'github_pat_']):continue
  if name=='openai_key' and b'sk-' not in data:continue
  if name=='aws_access_key' and b'AKIA' not in data and b'ASIA' not in data:continue
  if name=='bearer_value' and (b'authorization' not in low or b'bearer' not in low):continue
  if name=='literal_secret' and not any(x in low for x in [b'password',b'passwd',b'api_key',b'api-key',b'access_token',b'refresh_token',b'session_token',b'client_secret',b'session_secret']):continue
  if name=='literal_sshpass' and b'sshpass' not in data:continue
  for m in pattern.finditer(data):
   value=m.group(1) if m.lastindex else m.group(0)
   if value.lower() in PLACEHOLDERS:continue
   found.add(name)
 return sorted(found)

def inspect(path,synthetic=False):
 h=hashlib.sha256();flags=set();tail=b''
 with path.open('rb') as f:
  while True:
   b=f.read(4*1024*1024)
   if not b:break
   h.update(b)
   if not synthetic:flags.update(findings(tail+b));tail=b[-512:]
 return h.hexdigest(),sorted(flags)

def archive_scan(path):
 flags=set()
 try:
  if path.suffix=='.zip':
   with zipfile.ZipFile(path) as z:
    members=[(x.filename,lambda x=x:z.open(x)) for x in z.infolist() if not x.is_dir()]
    for name,opener in members:
     if policy(name) or any(t in Path(name).parts for t in ['.ssh','private-cache','private-logs']):flags.add('sensitive_archive_member');continue
     if Path(name).name=='inputs.json':continue
     with opener() as f:
      tail=b''
      while True:
       b=f.read(4*1024*1024)
       if not b:break
       flags.update(findings(tail+b));tail=b[-512:]
  elif path.name.endswith(('.tar','.tar.gz','.tgz','.tar.xz')):
   with tarfile.open(path,'r|*') as t:
    for x in t:
     if not x.isfile():continue
     if policy(x.name) or any(k in Path(x.name).parts for k in ['.ssh','private-cache','private-logs']):flags.add('sensitive_archive_member');continue
     if Path(x.name).name=='inputs.json':continue
     f=t.extractfile(x);tail=b''
     while True:
      b=f.read(4*1024*1024)
      if not b:break
      flags.update(findings(tail+b));tail=b[-512:]
 except (OSError,tarfile.TarError,zipfile.BadZipFile):flags.add('archive_not_safely_inspectable')
 return sorted(flags)

def main():
 a=argparse.ArgumentParser();a.add_argument('--source',type=Path,default=Path('/home/apacsc42'));a.add_argument('--store',type=Path,default=ROOT.with_name(ROOT.name+'-artifacts'));a.add_argument('--workers',type=int,default=4);args=a.parse_args();source=args.source;store=args.store;
 if (ROOT/'.git').exists():raise RuntimeError('Build only in a fresh archive tree; do not overwrite committed snapshots')
 objects=store/'objects';objects.mkdir(parents=True,exist_ok=True);manifest=[];excluded=[];candidates=[];errors=[]
 for top in ['2026-APAC-HPC-AI','workspace']:
  for directory,dirs,files in os.walk(source/top,followlinks=False):
   directory=Path(directory);rel=directory.relative_to(source);why=policy(str(rel)+'/')
   if why:excluded.append(dict(path=str(rel),reason=why,kind='directory'));dirs[:]=[];continue
   for d in list(dirs):
    if d in PRUNE or (directory/d).is_symlink():excluded.append(dict(path=str(rel/d),reason='Recreatable cache/environment, nested git metadata or symlink',kind='directory'));dirs.remove(d)
   for name in files:
    path=directory/name;relpath=str(path.relative_to(source));why=policy(relpath)
    try:st=path.lstat()
    except OSError as e:errors.append(dict(path=relpath,error=type(e).__name__));continue
    if why or not stat.S_ISREG(st.st_mode):excluded.append(dict(path=relpath,reason=why or 'Non-regular runtime file'));continue
    candidates.append((relpath,path))
 # Preserve exact serving/client containers locally; they are never Git blobs.
 for name in ['sglang-harbor.sqsh','aiperf.sqsh']:
  path=Path('/scratch/enroot-images')/name
  if path.is_file():candidates.append(('external-runtime/enroot-images/'+name,path))
 def job(item):
  rel,path=item;st=path.stat();synthetic=path.name=='inputs.json' or path.name.endswith('-inputs.json') or path.suffix=='.sqsh';digest,flags=inspect(path,synthetic)
  if not flags and path.name.endswith(('.zip','.tar','.tar.gz','.tgz','.tar.xz')):flags=archive_scan(path)
  end=path.stat()
  if (st.st_size,st.st_mtime_ns)!=(end.st_size,end.st_mtime_ns):return dict(path=rel,unstable=True)
  return dict(path=rel,source=str(path),sha256=digest,bytes=st.st_size,mtime_ns=st.st_mtime_ns,mode=stat.S_IMODE(st.st_mode),findings=flags,secret_scan='synthetic public benchmark dataset' if synthetic and path.suffix!='.sqsh' else 'opaque frozen runtime container' if path.suffix=='.sqsh' else 'patterns plus archive members' if path.name.endswith(('.zip','.tar','.tar.gz','.tgz','.tar.xz')) else 'patterns')
 metadata=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
  futures={pool.submit(job,item):item[0] for item in candidates}
  for i,f in enumerate(concurrent.futures.as_completed(futures),1):
   try:r=f.result()
   except Exception as e:errors.append(dict(path=futures[f],error=type(e).__name__));continue
   if r.get('unstable'):errors.append(dict(path=r['path'],error='Source changed during snapshot; rerun catch-up'));continue
   if r['findings']:excluded.append(dict(path=r['path'],reason='Potential secret content; quarantined from all portable outputs',rules=r['findings'],bytes=r['bytes']));continue
   metadata.append(r)
   if i%500==0:print(json.dumps(dict(phase='hash_and_scan',completed=i,total=len(candidates),excluded=len(excluded),errors=len(errors))),flush=True)
 (ROOT/'backup/scan-results.json').write_text(json.dumps(dict(excluded=excluded,errors=errors,scanner='Conservative local regex signatures and inspected tar/zip members. Synthetic benchmark datasets and opaque frozen runtime images are hashed but not secret-scanned.',known_limit='Pattern scanning cannot certify absence of every secret. No authentication cache or private VPN logs are copied.'),indent=2)+'\n')
 # Write a checkpoint before compression, so interrupted work can be inspected.
 checkpoint=ROOT/'backup/snapshot-metadata.json';checkpoint.write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(dict(phase='hash_complete',safe_files=len(metadata),excluded=len(excluded),errors=len(errors))),flush=True)
 by_hash={};inline_limit=1024*1024
 for r in metadata:
  target=ROOT/r['path'];path=Path(r['source']);common={k:v for k,v in r.items() if k not in ['source','findings']}
  if r['bytes']<=inline_limit and not r['path'].startswith('external-runtime/'):
   target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target);os.chmod(target,r['mode']);os.utime(target,ns=(r['mtime_ns'],r['mtime_ns']))
   if hashlib.sha256(target.read_bytes()).hexdigest()!=r['sha256']:errors.append(dict(path=r['path'],error='Copy changed after hash'));target.unlink();continue
   common['storage']='git';manifest.append(common)
  else:
   common.update(storage='object',object='objects/'+r['sha256'][:2]+'/'+r['sha256']+'.zst');manifest.append(common);by_hash.setdefault(r['sha256'],r)
 def compress(r):
  dest=store/'objects'/r['sha256'][:2]/(r['sha256']+'.zst');dest.parent.mkdir(exist_ok=True);tmp=dest.with_suffix('.tmp')
  subprocess.run(['zstd','-q','-T1','-3','-f',r['source'],'-o',str(tmp)],check=True)
  # Re-read decompression to verify actual stored content, not only source metadata.
  p=subprocess.Popen(['zstd','-q','-d','-c',str(tmp)],stdout=subprocess.PIPE);h=hashlib.sha256();n=0
  while True:
   b=p.stdout.read(4*1024*1024)
   if not b:break
   h.update(b);n+=len(b)
  if p.wait() or h.hexdigest()!=r['sha256'] or n!=r['bytes']:tmp.unlink();raise ValueError('Object checksum mismatch: '+r['path'])
  tmp.replace(dest);return dict(sha256=r['sha256'],bytes=r['bytes'],stored_bytes=dest.stat().st_size,object=str(dest.relative_to(store)))
 stored=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
  fs={pool.submit(compress,r):r['path'] for r in by_hash.values()}
  for i,f in enumerate(concurrent.futures.as_completed(fs),1):
   try:stored.append(f.result())
   except Exception as e:errors.append(dict(path=fs[f],error=type(e).__name__))
   if i%10==0:print(json.dumps(dict(phase='verified_objects',completed=i,total=len(fs))),flush=True)
 manifest.sort(key=lambda x:x['path']);(ROOT/'backup/manifest.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in manifest));(store/'objects-index.json').write_text(json.dumps(stored,indent=2)+'\n');summary=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_root=str(source),source_files_considered=len(candidates),retained_files=len(manifest),git_files=sum(x['storage']=='git' for x in manifest),logical_bytes=sum(x['bytes'] for x in manifest),git_worktree_bytes=sum(x['bytes'] for x in manifest if x['storage']=='git'),unique_external_objects=len(stored),external_object_bytes=sum(x['stored_bytes'] for x in stored),excluded_entries=len(excluded),errors=errors,remote_uploaded=False,model_weights='Not copied; retained model metadata and download identity must accompany the public checkpoint.');(ROOT/'backup/summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
