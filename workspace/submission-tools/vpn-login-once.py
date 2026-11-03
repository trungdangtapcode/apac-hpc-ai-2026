#!/usr/bin/env python3
"""One manually requested VPN login; credentials remain in a private helper."""
from pathlib import Path
import subprocess,time,json,datetime,os,sys,fcntl
if "--help" in sys.argv:
 print("Run once: python3 workspace/submission-tools/vpn-login-once.py\nUses an existing private local credential helper; never loops authentication. No credentials are stored in this script.")
 raise SystemExit(0)
ROOT=Path(__file__).resolve().parent.parent/'vpn-rootless'
ROOT.joinpath('run').mkdir(exist_ok=True)
lock=ROOT.joinpath('run/login-once.lock').open('a')
try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:
 print('Another login check is active; no new attempt.'); raise SystemExit(0)
helper=Path(os.environ.get('APAC_VPN_CREDENTIAL_HELPER', str(ROOT/'run/credential-reconnect.local.py')))
if not helper.is_file():
 print('Private local credential helper is unavailable. Use bash '+str(ROOT/'vpn.sh')+' connect and enter your password interactively.');raise SystemExit(1)
OUT=(ROOT/'inspection/manual-login-attempts')/('access-retry-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json')
OUT.parent.mkdir(parents=True,exist_ok=True)
record={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorization':'Explicit manual invocation of the one-attempt launcher. Preserve private authentication state.','maximum_attempts':1,'attempts':[],'safe_record_excludes_authentication_material':True}
def alive():
 p=subprocess.run(['python3',str(ROOT.parent.parent/'2026-APAC-HPC-AI/hpc-experiments/tools/nscc_vpn_path_check.py')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=22)
 return p.returncode==0 and json.loads(p.stdout)['state']=='SSH_SERVICE_REACHABLE_AUTH_UNTESTED'
def save():OUT.write_text(json.dumps(record,indent=2)+'\n')
def terminal():
 p=subprocess.run(['tmux','-S',str(ROOT/'run/tmux.sock'),'display-message','-p','-t','nscc-vpn','#{pane_dead}'],text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 return p.returncode!=0 or p.stdout.strip()=='1'
def failed():
 p=subprocess.run(['tmux','-S',str(ROOT/'run/tmux.sock'),'capture-pane','-p','-t','nscc-vpn','-S','-100'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
 return 'Authentication failed' in p.stdout
save()
for attempt in range(1,2):
 if alive():record['outcome']='EXISTING_SSH_TRANSPORT_REUSED_AUTH_UNTESTED';save();print('SSH transport reachable; authenticated access not tested; preserved existing session.',flush=True);break
 if not terminal():record['outcome']='EXISTING_AUTHENTICATION_PENDING_PRESERVED';save();print('Existing authentication pending; no replacement attempt.',flush=True);break
 row={'number':attempt,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};record['attempts'].append(row);save()
 p=subprocess.run(['python3',str(helper)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
 row['credential_helper_returncode']=p.returncode
 if p.returncode!=0:
  row['outcome']='LOCAL_HELPER_FAILED_PRIVATE_OUTPUT_NOT_RETAINED';record['outcome']=row['outcome'];save();print('Local helper failed; stopped without exposing private output.',flush=True);break
 for poll in range(12):
  if alive():row['outcome']='SSH_TRANSPORT_REACHABLE_AUTH_UNTESTED';record['outcome']=row['outcome'];save();print('SSH transport reachable; authenticated access not tested after attempt '+str(attempt),flush=True);break
  if terminal():row['outcome']='AUTHENTICATION_FAILED' if failed() else 'CLIENT_EXITED_CAUSE_NOT_ESTABLISHED';break
  time.sleep(3)
 else:row['outcome']='AUTHENTICATION_PENDING_PRESERVED'
 row['observed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print('Attempt '+str(attempt)+': '+row['outcome'],flush=True)
 if row['outcome'] in ('SSH_TRANSPORT_REACHABLE_AUTH_UNTESTED','AUTHENTICATION_PENDING_PRESERVED'):
  record['outcome']=row['outcome'];save();break
 if attempt<1:time.sleep(20)
else:record['outcome']='ONE_AUTHORIZED_ATTEMPT_ENDED_WITHOUT_VERIFIED_TRANSPORT';save()
print('Bounded authentication action finished.',flush=True)
