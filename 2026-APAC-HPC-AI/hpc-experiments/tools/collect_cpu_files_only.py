"""Collect only safe scratch text when PBS history is unavailable; no terminal claim."""
from pathlib import Path
import argparse,datetime,json,re,subprocess,shlex,io,tarfile,hashlib
p=argparse.ArgumentParser(description=__doc__);p.add_argument('experiment',type=Path);a=p.parse_args();r=a.experiment.resolve();base=Path(__file__).resolve().parents[1];assert r.parent==base
receipt=json.loads((r/'submission.json').read_text());job=receipt['stdout'].strip();assert receipt['returncode']==0 and re.fullmatch(r'\d+\.pbs\d+',job)
root=receipt['root'];assert root.startswith('/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-');target=r/'collected-files-only'/job;assert not target.exists(),'Never replace sealed evidence'
script='''from pathlib import Path
import tarfile,io,sys,json,hashlib,datetime
r=Path(ROOT);assert r.is_dir();b=io.BytesIO();selected=[];libs=[]
for p in sorted(r.rglob('*')):
 rel=p.relative_to(r)
 if p.is_symlink() or not p.is_file():continue
 if p.suffix=='.so':libs.append(dict(path=str(rel),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 if any(x.startswith('processor') for x in rel.parts) or 'polyMesh' in rel.parts or 'dynamicCode' in rel.parts:continue
 if p.stat().st_size>500000 or b'\\0' in p.read_bytes():continue
 selected.append(p)
assert sum(p.stat().st_size for p in selected)<6000000
with tarfile.open(fileobj=b,mode='w:gz') as t:
 for p in selected:t.add(str(p),arcname=str(p.relative_to(r)),recursive=False)
 data=json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(r),scope='Scratch text only, no scheduler terminal assertion',compiled_dynamic_libraries=libs),indent=2).encode();i=tarfile.TarInfo('collection.json');i.size=len(data);t.addfile(i,io.BytesIO(data))
sys.stdout.buffer.write(b.getvalue())
'''.replace('ROOT',repr(root))
res=subprocess.run([str(base/'tools/nscc-cpu-ssh.sh'),'python3 -c '+shlex.quote(script)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120,check=True)
with tarfile.open(fileobj=io.BytesIO(res.stdout)) as t:
 members=t.getmembers();assert all(m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts for m in members);assert sum(m.size for m in members)<6000000
 target.mkdir(parents=True);(target/'raw-text-evidence.tar.gz').write_bytes(res.stdout)
 for m in members:
  f=target/m.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(t.extractfile(m).read())
(target/'evidence-sha256.json').write_text(json.dumps({str(f.relative_to(target)):hashlib.sha256(f.read_bytes()).hexdigest() for f in target.rglob('*') if f.is_file()},indent=2)+'\n')
(r/'files-only-collection.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),job=job,files=len(members),scope='Safe scratch artifacts only; scheduler history unavailable, final PBS exit/resources unknown; retained full reservation',root=root),indent=2)+'\n');print('Sealed',len(members),'files for',job)
