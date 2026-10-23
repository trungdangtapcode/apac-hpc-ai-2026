"""Collect only the exiting snapshot of owned H100 production-span transfer diagnostic and safe accounting."""
from pathlib import Path
import argparse,hashlib,io,json,shlex,shutil,subprocess,tarfile
O=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--control-socket',required=True);args=p.parse_args()
assert not (O/'collected-exiting').exists(),'Preserve prior raw collection'
code='''from pathlib import Path
import hashlib,io,json,re,subprocess,sys,tarfile
root=Path('/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/nixl-production-span-probe-20261023')
job='224116.pbs111';run=root/'runs'/job
r=subprocess.run(['qstat','-xf',job],capture_output=True,text=True,check=True)
assert re.search(r'job_state\\s*=\\s*[EF]\\b',r.stdout) and re.search(r'project\\s*=\\s*59010042',r.stdout)
files=[(p,str(p.relative_to(root))) for p in sorted(run.rglob('*')) if p.is_file()]
flat=re.sub(r'\\n\\t','',r.stdout)
for field,name in [('Output_Path','pbs-stdout.txt'),('Error_Path','pbs-stderr.txt')]:
 m=re.search(r'(?m)^\\s*'+field+r'\\s*=\\s*[^:]+:(.+)$',flat)
 if m:
  f=Path(m.group(1).strip());f.relative_to(root)
  if f.is_file():files.append((f,name))
manifest=[]
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz') as archive:
 for path,name in files:
  assert not path.is_symlink();before=path.stat();digest=hashlib.sha256(path.read_bytes()).hexdigest()
  archive.add(path,arcname=name,recursive=False);after=path.stat()
  assert all(getattr(before,k)==getattr(after,k) for k in ['st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns'])
  manifest.append(dict(path=name,bytes=after.st_size,sha256=digest))
 for name,data in [('pbs-accounting.txt',r.stdout.encode()),('evidence-sha256.json',json.dumps(manifest,indent=2).encode())]:
  info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;archive.addfile(info,io.BytesIO(data))
'''
command=['ssh','-F','/dev/null','-S',args.control_socket,'-o','ControlMaster=no','-o','BatchMode=yes','apacsc42@aspire2p.nscc.sg','bash -lc '+shlex.quote('python3 -c '+shlex.quote(code))]
archive_path=O/'raw-evidence-exiting.tar.gz'
with archive_path.open('xb') as output:
 result=subprocess.run(command,stdout=output,stderr=subprocess.PIPE,timeout=90)
(O/'exiting-collection.stderr').write_bytes(result.stderr);assert result.returncode==0,'Inspect partial collection; no overwrite'
dest=O/'collected-exiting';dest.mkdir()
with tarfile.open(archive_path,'r:gz') as archive:
 for member in archive:
  rel=Path(member.name);assert not rel.is_absolute() and '..' not in rel.parts and member.isfile()
  path=dest/rel;path.parent.mkdir(parents=True,exist_ok=True)
  with archive.extractfile(member) as source,path.open('xb') as output:shutil.copyfileobj(source,output)
manifest=json.loads((dest/'evidence-sha256.json').read_text())
for row in manifest:
 path=dest/row['path'];assert path.stat().st_size==row['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
print('Collected',len(manifest),'snapshot files,',sum(x['bytes'] for x in manifest),'bytes; checksums verified')
