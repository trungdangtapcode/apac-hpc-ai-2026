"""Retire selected known-terminal CPU reservations; never retire unknown maxima."""
from pathlib import Path
import argparse,datetime,fcntl,json,math,re,shlex,subprocess
R=Path(__file__).resolve().parents[1];B=R/'nscc-cpu-timing-probe-20261021';L=B/'cpu-budget.json'
def remote(cmd):return subprocess.run(['bash',str(R/'tools/nscc-cpu-ssh.sh'),'bash -lc '+shlex.quote(cmd)],capture_output=True,text=True,timeout=60,check=True).stdout
def seconds(value):
 h,m,s=map(int,value.split(':'));return h*3600+m*60+s

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--job',action='append',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 assert len(a.job)==len(set(a.job)) and all(re.fullmatch(r'\d+\.pbs\d+',x) for x in a.job)
 out=a.output.resolve();assert R in out.parents and not out.exists()
 with (B/'cpu-budget.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not out.exists()
  d=json.loads(L.read_text());assert d['schema']==2 and d['project']=='59000042';before=json.loads(json.dumps(d))
  raw=json.loads(remote('qstat -fx -F json '+' '.join(a.job)))['Jobs'];assert set(raw)==set(a.job)
  allowances={};safe={};retired=0
  for job in a.job:
   v=raw[job];r=v['Resource_List'];entry=next(j for j in d['jobs'] if j['id']==job)
   assert entry['state']=='SUBMITTED' and v['job_state']=='F' and str(v['project'])=='59000042'
   assert int(r['ngpus'])==0 and float(r['queue_charge_rate'])==1
   cpus=int(r['ncpus']);elapsed=seconds(v['resources_used']['walltime']);assert cpus==int(v['resources_used']['ncpus']) and 0<=elapsed<=seconds(r['walltime'])
   estimate=cpus*elapsed/3600;allowance=max(128,cpus)*elapsed/3600;assert allowance<=entry['maximum_SU']
   retired+=entry['maximum_SU'];allowances[job]=allowance
   entry.update(state='F_EXIT_'+str(v['Exit_status'])+'_TERMINAL_RECONCILED',scheduler_state='F',scheduler_exit_status=v['Exit_status'],elapsed_seconds=elapsed,estimated_actual_SU=estimate,conservative_terminal_allowance_SU=allowance,posted_charge_reconciled=False,reservation_note='Only this selected known terminal maximum retired once; original maximum retained. Rounded conservative consumed allowance. No exact posted-job billing claim.')
   safe[job]={k:v[k] for k in ['job_state','project','Exit_status','Resource_List','resources_used','stime','obittime'] if k in v}
  report=remote('myprojects -p 59000042');row=[x for x in report.splitlines() if x.startswith('| SU')];assert len(row)==1
  grant,used,balance,doubt=[float(s.strip()) for s in row[0].split('|')[2:-1]];rates=[x for x in report.splitlines() if x.startswith('| CPU Hour')]
  assert grant==30000 and balance>=0 and doubt>=0 and len(rates)==1 and float(rates[0].split('|')[3].strip())==1
  consumed=max(d['consumed_ceiling_SU']+math.ceil(sum(allowances.values())),math.ceil(used-d['published_snapshot']['used_SU']+1))
  outstanding=d['outstanding_reserved_max_SU']-retired;assert outstanding>=0
  now=datetime.datetime.now(datetime.timezone.utc).isoformat()
  d.update(updated_utc=now,consumed_ceiling_SU=consumed,outstanding_reserved_max_SU=outstanding,planning_committed_SU=consumed+outstanding,reserved_max_SU=consumed+outstanding,last_reconciliation=str(out.relative_to(R)),latest_project_snapshot={'observed_utc':now,'used_SU':used,'balance_SU':balance,'in_doubt_SU':doubt,'site_timestamp_limitation':'Displayed site report may lag recent jobs; not individual posted billing.'})
  assert d['shared_cost_observations']==before['shared_cost_observations']
  assert [j for j in d['jobs'] if j['id'] not in a.job]==[j for j in before['jobs'] if j['id'] not in a.job]
  record={'observed_utc':now,'jobs':safe,'project_report':report,'conservative_terminal_allowances_SU':allowances,'retired_original_maximum_SU':retired,'rounded_added_allowance_SU':math.ceil(sum(allowances.values())),'old_committed_SU':before['planning_committed_SU'],'new_committed_SU':consumed+outstanding,'headroom_SU':d['baseline_wave_planning_ceiling_SU']-consumed-outstanding,'unknown_maxima_unchanged':True,'posted_individual_charge_known':False}
  out.write_text(json.dumps(record,indent=2)+'\n');tmp=L.with_suffix('.json.new');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(L)
  print(json.dumps({k:v for k,v in record.items() if k not in ['jobs','project_report']},indent=2))
if __name__=='__main__':main()
