"""Retain wrapper timing and safe live resource snapshot before scheduler history expires."""
from pathlib import Path
import json,sys,time,datetime,os,subprocess,shutil
mode,run=sys.argv[1],Path(sys.argv[2]);p=run/'batch-lifecycle.json'
if mode=='start':
 d=dict(job=os.environ['PBS_JOBID'],utc_start=datetime.datetime.now(datetime.timezone.utc).isoformat(),start_monotonic=time.monotonic(),requested_ncpus=256,requested_walltime_seconds=2400,maximum_SU=256*40/60,scope='Batch wrapper timestamps, not final scheduler accounting')
else:
 d=json.loads(p.read_text());d.update(utc_end=datetime.datetime.now(datetime.timezone.utc).isoformat(),wrapper_exit_status=int(sys.argv[3]),observed_wrapper_elapsed_seconds=time.monotonic()-d['start_monotonic']);d['estimated_wrapper_core_hour_SU']=d['observed_wrapper_elapsed_seconds']*256/3600
 q=shutil.which('qstat')
 if q:
  try:
   x=subprocess.run([q,'-f','-F','json',os.environ['PBS_JOBID']],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=12)
   if x.returncode==0:
    job=json.loads(x.stdout)['Jobs'][os.environ['PBS_JOBID']];d['pre_exit_live_snapshot']={k:job[k] for k in ['job_state','resources_used','exec_host'] if k in job}
   else:d['resource_snapshot']='Not collected: live query failed'
  except Exception:d['resource_snapshot']='Not collected: live query unavailable'
 else:d['resource_snapshot']='Not collected: qstat absent from compute PATH'
 d['limits']='Wrapper status/timing excludes scheduler prologue/cleanup and does not prove final PBS exit or exact billed SU. Live snapshot is not terminal accounting.'
p.write_text(json.dumps(d,indent=2)+'\n')
