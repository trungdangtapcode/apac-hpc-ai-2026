"""Check actual captured repr fixtures and reject unrelated graph changes."""
from pathlib import Path
import hashlib,importlib.util,json
O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('graphs',O/'check-derived-graphs.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
x=json.loads((O/'derived-graph-fixtures.json').read_text());a,b=x['reference'],x['candidate']
proof=m.check(a,b)
mutations=[b.replace("decode=PhaseConfig(backend='disabled'","decode=PhaseConfig(backend='full'"),b.replace("prefill=PhaseConfig(backend='breakable'","prefill=PhaseConfig(backend='disabled'"),b.replace('max_bs=8192','max_bs=4096'),b.replace(', 8192]',', 8192, 9999]'),b.replace("tc_compiler='eager'","tc_compiler='inductor'")]
for bad in mutations:
 assert bad!=b
 try:m.check(a,bad)
 except AssertionError:pass
 else:raise AssertionError('Accepted an unrelated graph change')
(O/'derived-graph-validation.json').write_text(json.dumps(dict(passed=True,actual_runtime_proof=proof,negative_mutations_rejected=len(mutations),native_generator_sha256=hashlib.sha256(m.SOURCE.read_bytes()).hexdigest()),indent=2)+'\n')
print('Real runtime derivation matches; five unrelated graph mutations rejected')
