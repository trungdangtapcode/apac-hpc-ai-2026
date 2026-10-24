"""Apply the owner's remaining-CPU-grant authorization under the existing lock."""
from pathlib import Path
import datetime,fcntl,json,math,shlex,subprocess
E=Path(__file__).resolve().parent;R=E.parent;B=R/'nscc-cpu-timing-probe-20261021';L=B/'cpu-budget.json'
def remote(cmd):return subprocess.run(['bash',str(R/'tools/nscc-cpu-ssh.sh'),'bash -lc '+shlex.quote(cmd)],capture_output=True,text=True,timeout=60,check=True).stdout
with (B/'cpu-budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);out=E/'budget-authorization.json';assert not out.exists()
 d=json.loads(L.read_text());assert d['project']=='59000042' and d['baseline_wave_planning_ceiling_SU']==5000
 report=remote('myprojects -p 59000042');rows=[x for x in report.splitlines() if x.startswith('| SU')];assert len(rows)==1
 grant,used,balance,doubt=[float(x.strip()) for x in rows[0].split('|')[2:-1]];assert grant==30000 and balance>=0 and doubt>=0
 raw=json.loads(remote('qstat -fx -F json 25956623.pbs101'))['Jobs']['25956623.pbs101'];assert raw['job_state']=='F' and raw['Exit_status']==1 and str(raw['project'])=='59000042'
 resource=raw['Resource_List'];assert int(resource['ncpus'])==512 and int(resource['ngpus'])==0 and float(resource['queue_charge_rate'])==1
 h,m,s=map(int,raw['resources_used']['walltime'].split(':'));seconds=h*3600+m*60+s;assert 0<=seconds<=180
 entry=next(j for j in d['jobs'] if j['id']=='25956623.pbs101');assert entry['state']=='SUBMITTED'
 terminal_estimate=512*seconds/3600
 consumed=max(d['consumed_ceiling_SU']+math.ceil(terminal_estimate),math.ceil(used-d['published_snapshot']['used_SU']+1))
 outstanding=d['outstanding_reserved_max_SU']-entry['maximum_SU'];assert outstanding>=0
 # Campaign figures exclude the recorded pre-campaign site baseline, so retain
 # that baseline outside the new ceiling to remain within the full project grant.
 new_ceiling=grant-d['published_snapshot']['used_SU']
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
 authorization={'observed_utc':utc,'previous_ceiling_SU':5000,'new_cumulative_ceiling_SU':new_ceiling,'authorization':'Owner explicitly authorized using the remaining CPU SU before 30 October 2026, replacing the 5,000-SU research ceiling. Use available CPU grant for justified research, not wasteful burn.','scope':'CPU project59000042 only. Full30000 grant less retained pre-campaign222.154 SU baseline. Fresh balance and reservations still gate every admission; unknown shared maxima retained. One active CPU allocation and combined own PBS cap3 unchanged.','deadline':'Owner says unused SU expire on30October; campaign planning uses that earlier deadline. Site myprojects currently shows ExpDate2026-11-15; user deadline and site expiry are different evidence, not reconciled.','automation':'No background Codex, autopilot, schedule or automatic notification enabled.'}
 d['ceiling_history'].append(authorization)
 entry.update(state='F_EXIT_1_POST_MPI_AFFINITY_EXPANSION',scheduler_state='F',scheduler_exit_status=1,elapsed_seconds=seconds,estimated_actual_SU=terminal_estimate,conservative_terminal_allowance_SU=math.ceil(terminal_estimate),posted_charge_reconciled=False,reservation_note='Retired only this terminal known maximum using validated512core rate1 and observedwall; rounded consumed allowance. Originalmax retained, no exactpostedcharge claim.')
 d.update(baseline_wave_planning_ceiling_SU=new_ceiling,updated_utc=utc,consumed_ceiling_SU=consumed,outstanding_reserved_max_SU=outstanding,planning_committed_SU=consumed+outstanding,reserved_max_SU=consumed+outstanding,last_reconciliation=str(out.relative_to(R)),latest_project_snapshot={'observed_utc':utc,'used_SU':used,'balance_SU':balance,'in_doubt_SU':doubt,'site_timestamp_limitation':'Retained site report may lag recent jobs; not individual billing.'})
 record=dict(authorization=authorization,project_report=report,terminal={k:raw[k] for k in ['job_state','project','Exit_status','Resource_List','resources_used','stime','obittime'] if k in raw},terminal_estimated_SU=terminal_estimate,planning_committed_SU=consumed+outstanding,planning_headroom_SU=new_ceiling-consumed-outstanding,all_other_unknown_maxima_unchanged=True)
 out.write_text(json.dumps(record,indent=2)+'\n');tmp=L.with_suffix('.json.new');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(L)
 print(json.dumps({k:v for k,v in record.items() if k not in ['project_report','terminal']},indent=2))
