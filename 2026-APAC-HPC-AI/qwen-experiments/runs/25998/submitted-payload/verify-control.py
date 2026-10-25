"""Review actual completed S59 evidence before any S61 model starts."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
B=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require_control(r):
 assert r['state']=='PASS_UNRANKED_PERFORMANCE_PROTOCOL' and r['arm']=='control'
 assert r['errors']==r['cancelled']==0 and r['completed']>0 and r['good_request_fraction']>=.90
 assert r['quality']=='UNKNOWN_NOT_EVALUATED' and r['ranked'] is False and r['speedup_claim'] is False
 assert r['goodput_req_s']>0 and abs(r['good_output_tokens_per_second']-200*r['goodput_req_s'])<1e-8
 return r
def main(output):
 c=json.loads((B/'matched-control.json').read_text())
 assert c['state']=='BOUND_TO_SUBMITTED_S59_RUNTIME_REVIEW_REQUIRED'
 C=Path(c['control_bundle']);A=Path(c['control_artifact_dir']);job=c['control_job']
 assert job.isdigit() and A.name==job
 assert sha(C/'SHA256SUMS')==sha(A/'submitted-payload/SHA256SUMS')==c['control_manifest_sha256']
 for p in [C,A/'submitted-payload']:subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=p,capture_output=True,check=True)
 terminal=None
 for attempt in range(6):
  text=subprocess.check_output(['sacct','-X','-n','-P','-j',job,'--format=JobIDRaw,State,ExitCode'],text=True)
  rows=[line.split('|') for line in text.splitlines() if line.strip()]
  terminal=next((x for x in rows if x[0]==job),None)
  if terminal is not None:break
  time.sleep(1)
 assert terminal and terminal[1]=='COMPLETED' and terminal[2]=='0:0', ('Control terminal does not qualify',terminal)
 p=subprocess.run([sys.executable,'-B',str(C/'check-performance.py'),str(A)],capture_output=True,text=True,check=True)
 r=require_control(json.loads(p.stdout))
 review={'state':'PASS_ACTUAL_S59_CONTROL_RUNTIME_REVIEW','job_id':job,'terminal':{'state':terminal[1],'exit_code':terminal[2]},'source_manifest_sha256':c['control_manifest_sha256'],'independent_raw_protocol_replay':r,'official_quality':'UNKNOWN','scope':'Actualcontrol protocol completion only; no officialaccuracy orqualifiedspeedup.'}
 path=Path(output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(review,indent=2)+'\n');print(json.dumps(review))
if __name__=='__main__':main(sys.argv[1])
