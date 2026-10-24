"""Check the pinned CPU router binding and requested prefill policy before launch."""
import argparse,hashlib,json,sys
from pathlib import Path
from sglang_router import router,router_args,sglang_router_rs,version
expected=sys.argv[1]
assert expected in ['round_robin','power_of_two']
expected_hashes={'router.py': '8ea20ba6a921747efe4025d6226e83a010cc04d7ee325d7d7e0d44783b13b198', 'router_args.py': '9cb06e6faa1e4742857650df1b8f4f5e4362cd1fcc1c011086b9f04ef2cb6f2a', 'version.py': 'bcd896275e2bfdcc39b7fed40ea0d021566f95a74a146c871f66afb0ba4ded58', 'sglang_router_rs.abi3.so': 'b2b0609a221b06a875e3e1768899a398288caf3b9c5fbc0f10c70f4d0b8379d7'}
for name,module in [('router.py',router),('router_args.py',router_args),('sglang_router_rs.abi3.so',sglang_router_rs),('version.py',version)]:
 assert hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()==expected_hashes[name],name
p=argparse.ArgumentParser();router_args.RouterArgs.add_cli_args(p)
a=p.parse_args(['--pd-disaggregation','--prefill-policy',expected])
assert router.policy_from_str(a.prefill_policy)==getattr(sglang_router_rs.PolicyType,'RoundRobin' if expected=='round_robin' else 'PowerOfTwo')
print('ROUTER_POLICY_PREFLIGHT_PASSED',json.dumps(dict(prefill_policy=expected,version=version.__version__,native_mapping=str(router.policy_from_str(expected)))),flush=True)
