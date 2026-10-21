"""Collect selected PBS accounting/text for one recorded CPU probe; no submission."""
from pathlib import Path
import argparse, datetime, hashlib, io, json, re, shlex, subprocess, tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('experiment', type=Path)
a = parser.parse_args()
r = a.experiment.resolve()
base = Path(__file__).resolve().parents[1]
assert r.parent == base
helper = str(base / 'tools/nscc-cpu-ssh.sh')
receipt = json.loads((r / 'submission.json').read_text())
job = receipt['stdout'].strip()
assert receipt['returncode'] == 0 and re.fullmatch(r'\d+\.\S+', job)
root = receipt['root']
assert root.startswith('/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-')
def remote(command):
    result = subprocess.run([helper, command], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=30)
    assert result.returncode == 0, result.stderr.decode()
    return result.stdout
raw = json.loads(remote('bash -lc ' + shlex.quote('qstat -xf -F json ' + job)))
fields = ['Job_Name', 'Job_Owner', 'job_state', 'queue', 'project', 'Resource_List',
          'exec_host', 'exec_vnode', 'stime', 'resources_used', 'Exit_status']
safe = {'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'jobs': {k: {n: v[n] for n in fields if n in v}
                 for k, v in raw['Jobs'].items()}}
terminal = all(v['job_state'] == 'F' for v in safe['jobs'].values())
(r / ('terminal-accounting.json' if terminal else 'scheduler-snapshot.json')).write_text(
    json.dumps(safe, indent=2) + '\n')
print(json.dumps(safe, indent=2))
if not terminal:
    raise SystemExit(0)
p = r / 'collected' / job
assert not p.exists(), 'Refuse to replace retained terminal evidence'
# Remote Python is 3.6. Exclude processor fields, meshes, compiled objects and
# dynamic sources; retain compiled-library hashes without downloading binaries.
script = '''from pathlib import Path
import tarfile,io,sys,json,hashlib,datetime
r=Path(ROOT);b=io.BytesIO();selected=[];libs=[]
for p in sorted(r.rglob('*')):
 rel=p.relative_to(r)
 if p.is_symlink() or not p.is_file():continue
 if p.suffix=='.so':libs.append({'path':str(rel),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 if any(x.startswith('processor') for x in rel.parts) or 'polyMesh' in rel.parts or 'dynamicCode' in rel.parts:continue
 if p.stat().st_size>500000 or b'\\0' in p.read_bytes():continue
 selected.append(p)
assert sum(p.stat().st_size for p in selected)<4000000
with tarfile.open(fileobj=b,mode='w:gz') as t:
 for p in selected:t.add(str(p),arcname=str(p.relative_to(r)),recursive=False)
 data=json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(r),'compiled_dynamic_libraries':libs},indent=2).encode();i=tarfile.TarInfo('collection.json');i.size=len(data);t.addfile(i,io.BytesIO(data))
sys.stdout.buffer.write(b.getvalue())
'''.replace('ROOT', repr(root))
blob = remote("python3 - <<'APAC_PY'\n" + script + '\nAPAC_PY')
with tarfile.open(fileobj=io.BytesIO(blob)) as t:
    members = t.getmembers()
    assert all(x.isfile() and not x.name.startswith('/') and
               '..' not in Path(x.name).parts for x in members)
    assert sum(x.size for x in members) < 4000000
    p.mkdir(parents=True)
    (p / 'raw-text-evidence.tar.gz').write_bytes(blob)
    for member in members:
        target = p / member.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(t.extractfile(member).read())
(p / 'evidence-sha256.json').write_text(json.dumps({
    str(x.relative_to(p)): hashlib.sha256(x.read_bytes()).hexdigest()
    for x in p.rglob('*') if x.is_file()}, indent=2) + '\n')
print('Sealed', len(members), 'text files')
