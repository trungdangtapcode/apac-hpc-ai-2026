"""CPU fixtures prove repeat stability gates acceptance while old identity is informational."""
import copy,json,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parent
baseline=json.loads((root/'accepted-25585-target-reference.json').read_text())
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'new-target.json'; stable=copy.deepcopy(baseline)
 for stage in ('target-a','target-b'):
  stable['stages'][stage][0]['observed']['output_ids'][0]+=1
 p.write_text(json.dumps(stable))
 r=subprocess.run([sys.executable,str(root/'check-deterministic-reference.py'),str(p),str(root/'accepted-25585-target-reference.json')],capture_output=True,text=True)
 assert r.returncode==0,r.stderr
 out=json.loads(r.stdout); assert out['state']=='PASS' and out['historical_25585_identity_match'] is False and out['historical_25585_identity_is_acceptance_gate'] is False
 unstable=copy.deepcopy(stable); unstable['stages']['target-b'][0]['observed']['output_ids'][0]+=1; p.write_text(json.dumps(unstable))
 r=subprocess.run([sys.executable,str(root/'check-deterministic-reference.py'),str(p),str(root/'accepted-25585-target-reference.json')],capture_output=True,text=True)
 assert r.returncode!=0 and 'target-a/target-b output IDs' in r.stderr
print('DETERMINISTIC_REFERENCE_GATE_CPU_FIXTURES_PASS; old identity mismatch is informational, repeat mismatch fails')
