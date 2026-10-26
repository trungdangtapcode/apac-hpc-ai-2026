#!/usr/bin/env python3
"""Collect selected AI credit and terminal states for the no-buffer policy update."""
from pathlib import Path
import datetime,json,shlex,subprocess
S=Path(__file__).resolve().parent;Q=S.parent
b=json.loads((Q/'nscc-pbs/nscc-budget.json').read_text());jobs=[r['job_id'] for r in b['pending_reservations'] if r['state']!='RECONCILED_IN_LEDGER']
code='''import json,re,subprocess
result={}
for key,argv in [('queue',['qselect','-u','apacsc42','-P','59010042']),('credit',['myprojects'])]+[(job,['qstat','-xf',job]) for job in JOBS]:
 r=subprocess.run(argv,capture_output=True,text=True,timeout=30);text=r.stdout
 if key=='credit':
  lines=[];capture=False
  for line in text.splitlines():
   if 'Project 59010042 balance as of' in line:capture=True
   elif capture and ('Usage breakdown' in line or (line.startswith('Project ') and '59010042' not in line)):capture=False
   if capture:lines.append(line)
  text='\\n'.join(lines)
 elif key not in {'queue','credit'}:
  text='\\n'.join(l for l in text.splitlines() if l.startswith('Job Id:') or re.match(r'\\s+(job_state|Exit_status|resources_used.walltime|project)\\s*=',l))
 result[key]={'returncode':r.returncode,'stdout':text,'stderr':r.stderr}
print(json.dumps(result))
'''.replace('JOBS',repr(jobs))
r=subprocess.run(['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch','bash -lc '+shlex.quote('python3 -c '+shlex.quote(code))],capture_output=True,text=True,timeout=150);assert r.returncode==0
proof={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Selected AI59010042 only; no CPU state inferred.','commands':json.loads(r.stdout)};(S/'terminal-and-credit.json').write_text(json.dumps(proof,indent=2)+'\n')
print(proof['commands']['credit']['stdout']);print('AI queue',proof['commands']['queue']['stdout'] or '(empty)')
for job in jobs:print(job,proof['commands'][job]['stdout'].replace('\n',' | '))
