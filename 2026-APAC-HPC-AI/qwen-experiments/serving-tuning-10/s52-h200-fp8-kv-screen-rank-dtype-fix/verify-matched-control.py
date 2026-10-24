"""Recheck the actual completed control before starting candidate GPU workers."""
from pathlib import Path
import hashlib,json,subprocess,sys
B=Path(__file__).resolve().parent;c=json.loads((B/'matched-control.json').read_text());C=Path(c['control_bundle']);A=Path(c['control_artifact_dir'])
assert hashlib.sha256((C/'SHA256SUMS').read_bytes()).hexdigest()==c['control_manifest_sha256']
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=C,capture_output=True,check=True)
result=subprocess.run([sys.executable,str(C/'check-screen.py'),str(A)],capture_output=True,text=True,check=True)
r=json.loads(result.stdout);assert r['status']=='pass' and r['request_errors']==0 and r['cancellations']==0 and r['good_request_fraction']>=.9
out=Path(sys.argv[1]);out.write_text(json.dumps({'control_job':c['control_job'],'control_manifest_sha256':c['control_manifest_sha256'],'replayed_control':r,'status':'pass'},indent=2)+'\n')
