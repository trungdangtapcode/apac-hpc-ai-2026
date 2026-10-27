"""Record deterministic native executable/library hashes without ASLR addresses."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess

def sha(path):
    result=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):result.update(block)
    return result.hexdigest()

tools={}
for name in ('mpirun','simpleFoam','decomposePar','renumberMesh','potentialFoam','applyBoundaryLayer'):
    path=shutil.which(name)
    assert path and Path(path).is_file(),name
    tools[name]={'path':path,'resolved_path':str(Path(path).resolve()),'sha256':sha(path)}
result=subprocess.run(['ldd',tools['simpleFoam']['path']],capture_output=True,text=True,check=True)
assert 'not found' not in result.stdout.lower(), 'Missing native runtime dependency'
libraries={}
for line in result.stdout.splitlines():
    match=re.search(r'=>\s+(/\S+)',line) or re.match(r'\s*(/\S+)',line)
    if match:
        path=Path(match.group(1));assert path.is_file(),str(path)
        libraries[str(path)]={'resolved_path':str(path.resolve()),'sha256':sha(path)}
assert libraries and any('Pstream' in name for name in libraries), 'Pstream linkage not observed'
assert any('libmpi' in name for name in libraries), 'Native MPI linkage not observed'
print(json.dumps({'tools':tools,'linked_libraries':libraries,'scope':'Deterministic executable and disk-library identities, not kernel ABI or performance proof.'},sort_keys=True,indent=2))
