"""Capture wrapper duration and best-effort pre-exit PBS snapshot, never final accounting."""
from pathlib import Path
import datetime,json,os,shutil,subprocess,sys,time
mode,runarg=sys.argv[1:3];run=Path(runarg);dest=run/'batch-lifecycle.json'
if mode=='start':
 nodes,ranks,steps=map(int,sys.argv[3:6]);dest.write_text(json.dumps({'job':os.environ.get('PBS_JOBID'),'utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'start_monotonic':time.monotonic(),'requested_nodes':nodes,'requested_ranks':ranks,'steps':steps,'requested_ncpus':ranks,'requested_walltime_seconds':2400,'maximum_SU':ranks*2400/3600,'internal_deadline_seconds':2220,'scope':'Wrapper duration and best-effort live snapshot; not terminal PBS exit/resource accounting.'},indent=2)+'\n')
elif mode=='finish':
 d=json.loads(dest.read_text());d.update({'utc_wrapper_end':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wrapper_exit_status':int(sys.argv[3]),'observed_wrapper_elapsed_seconds':time.monotonic()-d['start_monotonic']});d['estimated_wrapper_core_hour_SU']=d['observed_wrapper_elapsed_seconds']*d['requested_ncpus']/3600;d.pop('start_monotonic',None);q=shutil.which('qstat')
 if q:
  try:
   r=subprocess.run([q,'-f','-F','json',os.environ['PBS_JOBID']],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=10)
   if r.returncode==0:
    jobs=json.loads(r.stdout).get('Jobs',{});j=jobs.get(os.environ['PBS_JOBID']) or next(iter(jobs.values()),None);d['pre_exit_live_snapshot']={k:j[k] for k in ('job_state','resources_used','exec_host','Resource_List') if k in j} if j else {'result':'No matching live record'}
   else:d['pre_exit_live_snapshot']={'result':'Not collected','returncode':r.returncode,'stderr':r.stderr[-1000:]}
  except Exception as e:d['pre_exit_live_snapshot']={'result':'Not collected','reason':type(e).__name__}
 else:d['pre_exit_live_snapshot']={'result':'Not collected','reason':'qstat unavailable'}
 d['limits']='A pre-exit snapshot is diagnostic, not final PBS exit status or billed SU; wrapper timing excludes scheduler prologue and epilogue.';dest.write_text(json.dumps(d,indent=2)+'\n')
else:raise SystemExit('mode must be start or finish')
