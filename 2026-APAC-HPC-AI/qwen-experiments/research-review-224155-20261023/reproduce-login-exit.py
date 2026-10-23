"""Reproduce the login-shell/errexit exit bug on the authenticated AI login host."""
import argparse,json,shlex,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--control-socket',required=True);a=p.parse_args()
code=r'''from pathlib import Path
import os,json,subprocess,tempfile,hashlib
nl=chr(10)
expected=['if [ "$SHLVL" = 1 ]; then','[ -x /usr/bin/clear_console ] && /usr/bin/clear_console -q','fi']
logout=Path.home()/'.bash_logout';text=logout.read_text()
actual=[x.strip() for x in text.splitlines() if x.strip() and not x.lstrip().startswith('#')]
rows=[]
with tempfile.TemporaryDirectory(prefix='ap42-errexit-isolation-') as t:
 root=Path(t)
 for mode in ['empty-home','console-home']:
  home=root/mode;home.mkdir()
  if mode=='console-home':(home/'.bash_logout').write_text(nl.join(expected)+nl)
  for enabled in [False,True]:
   body=root/'probe.sh';body.write_text(nl.join(['set -e' if enabled else ':',"trap 'echo AP42_TRAP=$?' EXIT",'echo AP42_SHLVL=$SHLVL','exit 0'])+nl)
   for login in [False,True]:
    r=subprocess.run(['/bin/bash']+(['-l'] if login else [])+[str(body)],env=dict(os.environ,HOME=str(home),SHLVL='0'),capture_output=True,text=True,timeout=15)
    rows.append(dict(home_case=mode,errexit=enabled,login=login,returncode=r.returncode,markers=[x for x in r.stdout.splitlines() if x.startswith('AP42_')]))
print(json.dumps(dict(cases=rows,real_logout_matches_console_only_commands=actual==expected,logout_sha256=hashlib.sha256(logout.read_bytes()).hexdigest(),scope='Private temporary HOME fixtures; user startup/logout files unchanged; no GPU'),indent=2))
'''
cmd=['ssh','-F','/dev/null','-S',a.control_socket,'-o','ControlMaster=no','-o','BatchMode=yes','apacsc42@aspire2p.nscc.sg','bash -lc '+shlex.quote('python3 -c '+shlex.quote(code))]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=45);assert r.returncode==0,r.stderr
print(r.stdout)
