"""Independently recheck the actual matched control before candidate model startup."""
from pathlib import Path
import hashlib,json,subprocess,sys
B=Path(__file__).resolve().parent
c=json.loads((B/'matched-control.json').read_text());C=Path(c['control_bundle']);A=Path(c['control_artifact_dir'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(C/'SHA256SUMS')==c['control_manifest_sha256'], 'Control source manifest changed'
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=C,capture_output=True,check=True)
assert sha(A/'submitted-payload/SHA256SUMS')==c['control_manifest_sha256'], 'Control submitted payload differs'
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=A/'submitted-payload',capture_output=True,check=True)
p=subprocess.run([sys.executable,'-B',str(C/'check-performance.py'),str(A)],capture_output=True,text=True,check=True)
r=json.loads(p.stdout)
assert r['state']=='PASS_UNRANKED_PERFORMANCE_PROTOCOL' and r['arm']=='control'
assert r['errors']==r['cancelled']==0 and r['completed']>0 and r['good_request_fraction']>=.9
assert r['quality']=='UNKNOWN_NOT_EVALUATED' and r['ranked'] is False and r['speedup_claim'] is False
out=Path(sys.argv[1]);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({'status':'PASS','control_job':c['control_job'],'matched_control_manifest_sha256':c['control_manifest_sha256'],'independent_replay':r,'quality':'UNKNOWN_NOT_EVALUATED','claim':'Control protocol completion only; no official accuracy or qualified speedup.'},indent=2)+'\n')
