"""Check the exact image's CPU router CLI and Rust policy enum without GPUs."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, tempfile

O = Path(__file__).resolve().parent
IMAGE = '/scratch/enroot-images/sglang-harbor.sqsh'
package = 'usr/local/lib/python3.12/dist-packages/sglang_router/'
libraries = 'usr/lib/x86_64-linux-gnu/'
members = [package+n for n in ['router.py','router_args.py','version.py','sglang_router_rs.abi3.so']]
members += [libraries+n for n in ['ld-linux-x86-64.so.2','libc.so.6','libm.so.6','libgcc_s.so.1']]
probe = '''import argparse,contextlib,io,json
from sglang_router.router_args import RouterArgs
from sglang_router.router import policy_from_str
from sglang_router.sglang_router_rs import PolicyType
p=argparse.ArgumentParser()
RouterArgs.add_cli_args(p)
for name,expected in [('round_robin',PolicyType.RoundRobin),('power_of_two',PolicyType.PowerOfTwo)]:
 a=p.parse_args(['--pd-disaggregation','--prefill-policy',name])
 assert a.pd_disaggregation and policy_from_str(a.prefill_policy)==expected
with contextlib.redirect_stderr(io.StringIO()):
 try:p.parse_args(['--prefill-policy','shortest_queue'])
 except SystemExit as e:assert e.code==2
 else:raise AssertionError('Unsupported policy was accepted')
print(json.dumps(dict(passed=True,native_enum=True,pinned_cli_parser=True,pinned_mapping=True,unsupported_shortest_queue_rejected=True,gpu_used=False,network_router_started=False)))
'''
with tempfile.TemporaryDirectory(prefix='ap42-native-router-') as temporary:
    root = Path(temporary)/'image'
    extraction = subprocess.run(['unsquashfs','-no-progress','-processors','1','-d',str(root),IMAGE,*members],
                                check=True,capture_output=True,text=True)
    env = dict(os.environ,PYTHONPATH=str(root/'usr/local/lib/python3.12/dist-packages'))
    # Use only the image's matching loader/libc in this child process.
    # The account's operating system libraries are never installed or modified.
    command = [str(root/libraries/'ld-linux-x86-64.so.2'),'--library-path',
               str(root/libraries)+':/lib64:/usr/lib64',sys.executable,'-c',probe]
    result = subprocess.run(command,env=env,capture_output=True,text=True,timeout=30,check=True)
    proof = json.loads(result.stdout)
    proof.update(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 source_image=IMAGE,member_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in members},
                 scope='CPU parser/native enum/mapping only. No router was started, model loaded, GPU allocated or routing performance measured.')
    (O/'native-validation.json').write_text(json.dumps(proof,indent=2)+'\n')
    (O/'native-validation.stdout').write_text(result.stdout)
    (O/'native-validation.stderr').write_text(result.stderr)
    print(result.stdout.strip())
