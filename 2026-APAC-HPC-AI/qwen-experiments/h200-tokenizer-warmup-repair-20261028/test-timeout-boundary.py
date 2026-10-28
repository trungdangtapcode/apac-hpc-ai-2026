#!/usr/bin/env python3
"""Run the actual wrapper against delayed disposable Enroot command fixtures."""
import json,os,subprocess,tempfile
from pathlib import Path
D=Path(__file__).resolve().parent
rows=[]
with tempfile.TemporaryDirectory(prefix='apac-native-timeout-fixture-') as tmp:
 t=Path(tmp);(t/'image.sqsh').touch()
 (t/'enroot').write_text('''#!/bin/bash
set -e
operation=$1;shift
case "$operation" in
 create) sleep 0.15;;
 remove) sleep 0.15;;
 start) while [[ $1 != rootfs ]]; do shift; done;shift; "$@";;
 *) exit 2;;
esac
''');(t/'enroot').chmod(0o700)
 (t/'stat').write_text('#!/bin/bash\necho "4096 100000000"\n');(t/'stat').chmod(0o700)
 for name,outer,inner_sleep,wanted in [('old-combined',0.2,0.02,124),('split-valid',2,0.02,0),('split-semantic-timeout',2,0.35,124)]:
  env=os.environ.copy();env.update(PATH=str(t)+':'+env['PATH'],SLURM_JOB_ID='987654321',SLURM_STEP_ID=name,SLURM_STEP_GPUS='',CUDA_VISIBLE_DEVICES='')
  root=Path('/tmp/apacsc42-native-987654321-'+name);assert not root.exists()
  command=['timeout','--signal=TERM','--kill-after=0.5s',str(outer),'bash',str(D/'native-container.sh'),str(t/'image.sqsh'),str(t)+':'+str(t)+':ro','timeout','--signal=TERM','--kill-after=0.5s','0.2','bash','-c',f'sleep {inner_sleep}; echo SEMANTIC_COMMAND_DONE']
  try:
   r=subprocess.run(command,env=env,capture_output=True,text=True,timeout=5)
   rows.append({'case':name,'outer_seconds':outer,'inner_seconds':0.2,'command_sleep_seconds':inner_sleep,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'expected':wanted})
   assert r.returncode==wanted,rows[-1]
  finally:
   if root.exists():root.rmdir()
(D/'timeout-fixture.json').write_text(json.dumps({'state':'PASS','scope':'Actual wrapper; simulated filesystem delays and five-times-shorter toy semantic timeout. No real GPU/image performance claim.','cases':rows},indent=2)+'\n');print('PASS: combined deadline fails after valid command; split passes; actual semantic timeout still fails')
