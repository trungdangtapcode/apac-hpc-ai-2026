"""Use the existing AI SSH master only; no VPN or password authentication."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,shlex,subprocess
O=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--control-socket',required=True)
SOCKET=parser.parse_args().control_socket
ssh=['ssh','-F','/dev/null','-S',SOCKET,'-o','ControlMaster=no','-o','BatchMode=yes','-o','ConnectTimeout=5','apacsc42@aspire2p.nscc.sg']
subprocess.run(['ssh','-F','/dev/null','-S',SOCKET,'-O','check','apacsc42@aspire2p.nscc.sg'],check=True,capture_output=True,timeout=10)
commands=[['hostname'],['qselect','-u','apacsc42','-P','59010042'],['qstat','-xf','223132.pbs111'],['myprojects']]
code='''import subprocess,json,re
commands = COMMANDS
rows=[]
for argv in commands:
 r=subprocess.run(argv,capture_output=True,text=True,timeout=30)
 text=r.stdout
 if argv==['myprojects']:
  # Retain the AI project's resource balance only, no CPU project ledger.
  selected=[];capture=False
  for line in text.splitlines():
   if 'Project 59010042 balance as of' in line:capture=True
   elif capture and ('Usage breakdown' in line or (line.startswith('Project ') and '59010042' not in line)):capture=False
   if capture:selected.append(line)
  text='\\n'.join(selected)+'\\n'
 rows.append(dict(argv=argv,returncode=r.returncode,stdout=text,stderr=r.stderr))
print(json.dumps(rows))
'''.replace('COMMANDS',repr(commands))
result=subprocess.run(ssh+['bash -lc '+shlex.quote('python3 -c '+shlex.quote(code))],capture_output=True,text=True,timeout=100)
(O/'access-check.stderr').write_text(result.stderr)
if result.returncode:raise RuntimeError('Existing transport or remote command failed; inspect stderr without inferring an authentication failure')
rows=json.loads(result.stdout);assert all(row['returncode']==0 for row in rows),[(x['argv'],x['returncode'],x['stderr']) for x in rows]
assert '59010042' in rows[-1]['stdout'] and '| SU' in rows[-1]['stdout']
(O/'access-and-accounting.json').write_text(json.dumps(dict(checked_utc=datetime.now(timezone.utc).isoformat(),commands=rows,scope='Existing SSH master only; selected AI project 59010042; no authentication, submit, reservation, VPN mutation or CPU project query'),indent=2)+'\n')
print(rows[0]['stdout'].strip());print('AI queue IDs:',rows[1]['stdout'].strip() or '(none)');print(rows[-1]['stdout'])
