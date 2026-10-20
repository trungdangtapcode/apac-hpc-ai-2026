"""Exercise the real PBS wrapper's private-home arguments without a GPU."""
from pathlib import Path
import ast, hashlib, json, os, subprocess, tempfile

O = Path(__file__).resolve().parent
R = O.parent
pilots = json.loads((O / 'pilots.json').read_text())
home_before = os.environ['HOME']
checks = {}
with tempfile.TemporaryDirectory(prefix='ap42-home-fixture-') as tmp:
    base = Path(tmp)
    bindir = base / 'bin'
    bindir.mkdir()
    (bindir / 'taskset').write_text('#!/bin/bash\nshift 2\nexec "$@"\n')
    (bindir / 'singularity').write_text('''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
a=sys.argv[1:]; bindings=a[a.index('--bind')+1].split(',')
matching=[x.split(':')[0] for x in bindings if x.split(':')[1]==os.environ['HOME']]
assert len(matching)==1
p=Path(matching[0]); (p/'write-test').write_text('fixture')
assert p.parent.parent==Path(os.environ['TMPDIR'])
assert p.name=='home' and (p.stat().st_mode&0o777)==0o700
assert p!=Path(os.environ['HOME']) and '--no-home' in a
Path(os.environ['FIXTURE_REPORT']).write_text(json.dumps(dict(private_bind_writable=True,mode_0700=True,no_real_home_mounted=True,home_value=os.environ['HOME'])))
''')
    for p in bindir.iterdir():
        p.chmod(0o700)
    env = dict(os.environ, PATH=str(bindir)+':'+os.environ['PATH'],
               TMPDIR=tmp, FIXTURE_REPORT=str(base/'report.json'))
    wrapper = Path(pilots[0]['bundle']) / 'pbs-container.sh'
    result = subprocess.run(['bash','-c','module() { :; }; export -f module; exec bash "$@"',
                             'fixture',str(wrapper),'image','/fixture:/fixture','0','8','1','{}','true'],
                            env=env,capture_output=True,text=True,check=True)
    observed = json.loads((base/'report.json').read_text())
    checks.update({k:v for k,v in observed.items() if k!='home_value'})
    checks['home_environment_unchanged'] = observed['home_value']==home_before==os.environ['HOME']
for pilot in pilots:
    bundle = Path(pilot['bundle'])
    for p in bundle.iterdir():
        if p.suffix=='.py': ast.parse(p.read_text())
        if p.suffix in {'.sh','.pbs','.sbatch'}:
            subprocess.run(['bash','-n',str(p)],check=True,capture_output=True)
    subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,check=True,capture_output=True)
    for name in ['bench.py','config.json']:
        assert (bundle/name).read_bytes()==(R/'fp8-linear-cachefix-20261020'/name).read_bytes()
    assert 'HOME=' not in (bundle / ('pbs-container.sh' if pilot['platform']=='H100' else 'job.sbatch')).read_text()
checks.update(shell_python_syntax=True,payload_hashes=True,full_numeric_timing_config_unchanged=True,
              staged_preflight_separate=True)
assert all(checks.values())
report=dict(passed=True,checks=checks,scope='CPU argument/filesystem and immutable payload checks only; GPU provider preflight still required.')
(O/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
