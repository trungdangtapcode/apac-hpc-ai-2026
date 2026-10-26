#!/usr/bin/env python3
"""Read selected AI account state through the existing authenticated VPN/SSH path."""
from pathlib import Path
import datetime,json,shlex,subprocess
O=Path(__file__).resolve().parent
jobs=['224466.pbs111','224468.pbs111','224552.pbs111','224553.pbs111','224554.pbs111','224555.pbs111','224559.pbs111','224560.pbs111','224561.pbs111']
code='''import json,re,subprocess,socket
rows=[]
for argv in [['hostname'],['qselect','-u','apacsc42','-P','59010042'],['myprojects']]+[['qstat','-xf',job] for job in JOBS]:
 r=subprocess.run(argv,capture_output=True,text=True,timeout=30)
 text=r.stdout
 if argv[0]=='myprojects':
  selected=[];capture=False
  for line in text.splitlines():
   if 'Project 59010042 balance as of' in line:capture=True
   elif capture and ('Usage breakdown' in line or (line.startswith('Project ') and '59010042' not in line)):capture=False
   if capture:selected.append(line)
  text='\\n'.join(selected)+'\\n'
 elif argv[0]=='qstat':
  # Preserve resource/state/output evidence without Variable_List or unrelated environment.
  allowed={'job_state','Exit_status','resources_used','Resource_List','Output_Path','Error_Path','exec_host','exec_vnode','stime','mtime','qtime','project','queue','comment','Job_Name'}
  selected=[];keep=False
  for line in text.splitlines():
   m=re.match(r'\\s+([A-Za-z_]+(?:\\.[A-Za-z_]+)?)\\s*=',line)
   if line.startswith('Job Id:'):keep=True
   elif m:keep=m[1].split('.')[0] in allowed
   if keep:selected.append(line)
  text='\\n'.join(selected)+'\\n'
 rows.append({'argv':argv,'returncode':r.returncode,'stdout':text,'stderr':r.stderr})
print(json.dumps(rows))
'''.replace('JOBS',repr(jobs))
cmd='bash -lc '+shlex.quote('python3 -c '+shlex.quote(code))
r=subprocess.run(['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch',cmd],capture_output=True,text=True,timeout=180)
assert r.returncode==0,'Transport/remote command failed; do not infer which auth layer'
rows=json.loads(r.stdout)
assert rows[0]['returncode']==0 and 'a2ap-login' in rows[0]['stdout']
assert rows[1]['returncode']==0 and rows[2]['returncode']==0
proof={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Selected AI59010042 only. H100 SSH authenticated via existing user-supplied credential; no secret/session material or CPU ledger retained.','commands':rows}
(O/'access-and-accounting.json').write_text(json.dumps(proof,indent=2)+'\n')
print('AI queue:',rows[1]['stdout'].strip() or '(empty)');print(rows[2]['stdout'])
for row in rows[3:]:
 print(row['argv'][-1],row['returncode'],[(line.strip()) for line in row['stdout'].splitlines() if any(x in line for x in ('job_state =','Exit_status =','resources_used.walltime ='))])
