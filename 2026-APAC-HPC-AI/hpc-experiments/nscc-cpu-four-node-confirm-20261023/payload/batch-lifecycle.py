"""Persist wrapper lifecycle and pre-exit live PBS observations, not billing proof."""
from pathlib import Path
import datetime,json,os,shutil,subprocess,sys,time
mode,runarg=sys.argv[1],sys.argv[2];run=Path(runarg);dest=run/'batch-lifecycle.json'
if mode=='start':
 dest.write_text(json.dumps({'job':os.environ.get('PBS_JOBID'),'utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'start_monotonic':time.monotonic(),'requested_ncpus':512,'requested_nodes':4,'requested_walltime_seconds':2400,'maximum_SU':512*2400/3600,'internal_deadline_seconds':2220,'scope':'Wrapper duration/resource snapshot only. Does not establish final PBS exit status or actual charge.'},indent=2)+'\n')
elif mode=='finish':
 d=json.loads(dest.read_text());d.update({'utc_wrapper_end':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wrapper_exit_status':int(sys.argv[3]),'observed_wrapper_elapsed_seconds':time.monotonic()-d['start_monotonic']});d['estimated_wrapper_core_hour_SU']=d['observed_wrapper_elapsed_seconds']*512/3600;d.pop('start_monotonic',None)
 qstat=shutil.which('qstat')
 if qstat:
  try:
   r=subprocess.run([qstat,'-f','-F','json',os.environ['PBS_JOBID']],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=10)
   if r.returncode==0:
    jobs=json.loads(r.stdout).get('Jobs',{});job=jobs.get(os.environ['PBS_JOBID']) or next(iter(jobs.values()),None)
    d['pre_exit_live_snapshot']={k:job[k] for k in ('job_state','resources_used','exec_host','Resource_List') if k in job} if job else {'result':'No matching live record'}
   else:d['pre_exit_live_snapshot']={'result':'Not collected','returncode':r.returncode,'stderr':r.stderr[-1000:]}
  except Exception as e:d['pre_exit_live_snapshot']={'result':'Not collected','reason':type(e).__name__}
 else:d['pre_exit_live_snapshot']={'result':'Not collected','reason':'qstat not in compute PATH'}
 d['limits']='A live pre-exit query is not terminal scheduler accounting. Wrapper time excludes scheduler prologue/epilogue and does not prove final PBS completion or billed SU.'
 dest.write_text(json.dumps(d,indent=2)+'\n')
else:raise SystemExit('mode must be start or finish')
