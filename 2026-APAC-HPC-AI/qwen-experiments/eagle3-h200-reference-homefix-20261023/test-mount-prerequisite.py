"""Exercise both actual shell launchers with a mount-validating Slurm stub."""
from pathlib import Path
import json,os,subprocess,tempfile,time
O=Path(__file__).resolve().parent;R=O.parent
old=R/'serving-tuning-10/s37-h200-target-reference'
new=Path(json.loads((O/'prepared.json').read_text())['bundle'])
results=[]
for label,bundle,expected_status in [('old',old,86),('repaired',new,7)]:
 with tempfile.TemporaryDirectory() as directory:
  td=Path(directory);fakebin=td/'bin';fakebin.mkdir()
  scripts={
   'scontrol':"#!/bin/sh\nprintf 'node0\\nnode1\\n'\n",
   'getent':"#!/bin/sh\nprintf '10.0.0.1 STREAM\\n'\n",
   'curl':'''#!/usr/bin/env python3
import os,sys
from pathlib import Path
url=sys.argv[-1];name={'30100':'prefill-0','30101':'prefill-1','30200':'decode-0'}
for port,worker in name.items():
 if ':'+port+'/' in url:
  path=Path(os.environ['SLURM_SUBMIT_DIR'])/'runs'/os.environ['SLURM_JOB_ID']/(worker+'.log')
  need=8 if worker=='decode-0' else 4
  raise SystemExit(0 if path.exists() and path.read_text().count('KV Cache is allocated.')==need else 1)
raise SystemExit(0)
''',
   'srun':'''#!/usr/bin/env python3
import os,sys,time
from pathlib import Path
args=sys.argv[1:];joined=' '.join(args)
for arg in args:
 if arg.startswith('--container-mounts='):
  for mount in arg.split('=',1)[1].split(','):
   source=mount.split(':',1)[0]
   if not Path(source).exists():
    print('FIXTURE_MISSING_MOUNT_SOURCE '+source,flush=True);raise SystemExit(86)
if 'warm-topology.py' in joined:
 print('ALL 2 P/D paths semantically initialized experiment_id=fixture',flush=True);raise SystemExit(0)
if 'token-control.py' in joined:
 print('FIXTURE_TOKEN_CLIENT_REACHED_WITH_ALL_MOUNTS',flush=True);raise SystemExit(7)
if 'worker.sh' in joined:
 decode='decode-0' in joined
 for rank in range(8 if decode else 4):
  suffix=f' TP{rank} EP{rank}' if decode else f' TP{rank}'
  print(f'[2026-10-23 00:00:00{suffix}] KV Cache is allocated. dtype: torch.bfloat16, #tokens: 123456, K size: 34.32 GB, V size: 34.32 GB',flush=True)
os.execvp('sleep',['sleep','300'])
'''}
  for name,contents in scripts.items():p=fakebin/name;p.write_text(contents);p.chmod(0o755)
  env=dict(os.environ,PATH=str(fakebin)+os.pathsep+os.environ['PATH'],SLURM_SUBMIT_DIR=str(td),SLURM_JOB_ID='fixture',SLURM_JOB_NODELIST='node0,node1',QWEN_BUNDLE=str(bundle),QWEN_IMAGE_PATH='fixture-image',QWEN_EXPERIMENT_ID='fixture-id',QWEN_NIXL_PATCH_SHA256='fixture-patch',QWEN_JOB_START_EPOCH=str(int(time.time())))
  result=subprocess.run(['bash',str(bundle/'topology-job.sh')],env=env,capture_output=True,text=True,timeout=35)
  client=(td/'runs/fixture/token-client.log').read_text()
  assert result.returncode != 0
  assert f'client_status={expected_status}' in result.stderr,result.stderr
  if label=='old':assert 'FIXTURE_MISSING_MOUNT_SOURCE' in client and 'TOKEN_CLIENT_REACHED' not in client
  else:assert 'FIXTURE_TOKEN_CLIENT_REACHED_WITH_ALL_MOUNTS' in client and 'MISSING_MOUNT' not in client
  assert 'bounded teardown deadline exceeded' not in result.stderr
  results.append(dict(source=label,launcher_returncode=result.returncode,observed_client_status=expected_status,all_source_mounts_existed=(label=='repaired'),deliberate_client_failure_propagated=True))
(O/'mount-validation.json').write_text(json.dumps(dict(passed=True,fixtures=results,scope='Actual source/repaired shell execution with mount-validating Slurm stub; no actual Pyxis/GPU/network simulation'),indent=2)+'\n')
print('MOUNT_PREREQUISITE_REGRESSION_PASS: source rejected; repaired launcher reaches client and propagates exit7')
