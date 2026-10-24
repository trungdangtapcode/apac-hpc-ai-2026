"""Reconcile only three known terminal allocations; preserve all unknown maxima."""
from pathlib import Path
import datetime,fcntl,json,math,shlex,subprocess
E=Path(__file__).resolve().parent;R=E.parent;B=R/'nscc-cpu-timing-probe-20261021';L=B/'cpu-budget.json'
IDS=['25940700.pbs101','25943865.pbs101','25947168.pbs101']
def remote(cmd):
 return subprocess.run(['bash',str(R/'tools/nscc-cpu-ssh.sh'),'bash -lc '+shlex.quote(cmd)],capture_output=True,text=True,timeout=60,check=True).stdout
def seconds(text):
 h,m,s=map(int,text.split(':'));return h*3600+m*60+s
with (B/'cpu-budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 out=E/'budget-reconciliation.json';assert not out.exists(),'Do not repeat retirement'
 d=json.loads(L.read_text());assert d['schema']==2 and d['project']=='59000042'
 before=json.loads(json.dumps(d));raw=json.loads(remote('qstat -fx -F json '+' '.join(IDS)))['Jobs'];assert set(raw)==set(IDS)
 estimates={};safe={}
 for job in IDS:
  v=raw[job];r=v['Resource_List'];entry=next(x for x in d['jobs'] if x['id']==job)
  assert entry['state']=='SUBMITTED' and v['job_state']=='F' and str(v['project'])=='59000042'
  assert int(r['ngpus'])==0 and float(r['queue_charge_rate'])==1
  elapsed=seconds(v['resources_used']['walltime']);ncpus=int(r['ncpus']);assert elapsed<=seconds(r['walltime'])
  # Preserve the conservative full-node treatment for the shared 4-core request.
  charge=max(ncpus,128)*elapsed/3600
  assert charge<=entry['maximum_SU']
  entry.update(state='F_EXIT_'+str(v['Exit_status'])+'_REVIEW_PENDING',scheduler_state='F',scheduler_exit_status=v['Exit_status'],elapsed_seconds=elapsed,estimated_actual_SU=ncpus*elapsed/3600,conservative_terminal_allowance_SU=charge,posted_charge_reconciled=False,reservation_note='Original maximum retained. Outstanding maximum retired once using terminal requested resources at verified rate 1; full-node conservative allowance retained for 4-core shared probe. This is not individual posted billing.')
  estimates[job]=charge
  safe[job]={k:v[k] for k in ['job_state','project','Exit_status','resources_used','Resource_List','stime','obittime'] if k in v}
 report=remote('myprojects -p 59000042')
 rows=[s for s in report.splitlines() if s.startswith('| SU')];assert len(rows)==1
 grant,used,balance,doubt=[float(s.strip()) for s in rows[0].split('|')[2:-1]];assert grant==30000 and balance>=0 and doubt>=0
 rates=[s for s in report.splitlines() if s.startswith('| CPU Hour')];assert len(rates)==1 and float(rates[0].split('|')[3].strip())==1
 retired=sum(next(j['maximum_SU'] for j in before['jobs'] if j['id']==i) for i in IDS)
 allowance=math.ceil(sum(estimates.values()))
 # Deliberate possible double-counting: add a rounded terminal allowance even
 # if a lagging aggregate site report already covered part of these jobs.
 consumed=max(before['consumed_ceiling_SU']+allowance,math.ceil(used-before['published_snapshot']['used_SU']+1))
 outstanding=before['outstanding_reserved_max_SU']-retired;assert outstanding>=0
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 d.update(updated_utc=now,consumed_ceiling_SU=consumed,outstanding_reserved_max_SU=outstanding,reserved_max_SU=consumed+outstanding,planning_committed_SU=consumed+outstanding,last_reconciliation=str(out.relative_to(R)),latest_project_snapshot=dict(observed_utc=now,used_SU=used,balance_SU=balance,in_doubt_SU=doubt,site_timestamp_limitation='Raw report retained; not individual posted-job billing.'))
 assert d['shared_cost_observations']==before['shared_cost_observations']
 unchanged=[j for j in before['jobs'] if j['id'] not in IDS];assert unchanged==[j for j in d['jobs'] if j['id'] not in IDS]
 record=dict(observed_utc=now,terminal=safe,project_report=report,conservative_estimates_SU=estimates,rounded_added_consumed_allowance_SU=allowance,retired_outstanding_maximum_SU=retired,prior_consumed_allowance_SU=before['consumed_ceiling_SU'],prior_outstanding_SU=before['outstanding_reserved_max_SU'],new_consumed_allowance_SU=consumed,new_outstanding_SU=outstanding,new_committed_SU=consumed+outstanding,remaining_SU=d['baseline_wave_planning_ceiling_SU']-consumed-outstanding,unknown_maxima_unchanged=True,individual_posted_charge_known=False)
 out.write_text(json.dumps(record,indent=2)+'\n')
 temp=L.with_suffix('.json.new');temp.write_text(json.dumps(d,indent=2)+'\n');temp.replace(L)
 print(json.dumps({k:v for k,v in record.items() if k not in ['terminal','project_report']},indent=2))
