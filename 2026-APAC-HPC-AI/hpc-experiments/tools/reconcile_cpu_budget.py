"""Reconcile only terminal CPU allocations; preserve requested maxima as provenance."""
from pathlib import Path
import datetime,fcntl,json,math,re,shlex,subprocess
R=Path(__file__).resolve().parents[1];base=R/'nscc-cpu-timing-probe-20261021';ledger=base/'cpu-budget.json';helper=str(R/'tools/nscc-cpu-ssh.sh')
def remote(cmd):return subprocess.run([helper,'bash -lc '+shlex.quote(cmd)],capture_output=True,text=True,timeout=60,check=True).stdout
def seconds(s):
 h,m,v=map(int,s.split(':'));return h*3600+m*60+v
with (base/'cpu-budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);d=json.loads(ledger.read_text());assert d['schema']==2 and d['project']=='59000042'
 ids=[j['id'] for j in d['jobs']];assert all(re.fullmatch(r'\d+\.pbs\d+',j) for j in ids) and len(set(ids))==len(ids)
 own=remote('qstat -u apacsc42');assert 'apacsc42' not in own,'An own CPU job is still queued/running; no reconciliation'
 raw=json.loads(remote('qstat -xf -F json '+' '.join(ids)))['Jobs'];assert set(raw)==set(ids)
 safe={};total=0
 for job in ids:
  v=raw[job];assert v['job_state']=='F' and str(v['project'])=='59000042'
  requested=v['Resource_List'];assert int(requested['ngpus'])==0 and float(requested['queue_charge_rate'])==1
  elapsed=seconds(v['resources_used']['walltime']);charge=int(requested['ncpus'])*elapsed/3600;assert charge>=0;total+=charge
  safe[job]={k:v[k] for k in ['job_state','Exit_status','resources_used','Resource_List','project']}
  entry=next(x for x in d['jobs'] if x['id']==job)
  entry.update(state=entry['state'] if entry['state'].startswith('F_') else 'F_EXIT_'+str(v['Exit_status'])+'_TERMINAL',scheduler_state='F',scheduler_exit_status=v['Exit_status'],elapsed_seconds=elapsed,estimated_actual_SU=charge,reservation_note='Terminal resource-based maximum retired during locked reconciliation; original maximum retained for audit.',posted_charge_reconciled=False)
 report=remote('myprojects -p 59000042');lines=[x for x in report.splitlines() if x.startswith('| SU')];assert len(lines)==1
 grant,used,balance,indoubt=[float(x.strip()) for x in lines[0].split('|')[2:-1]];assert grant==30000 and balance>=0 and indoubt==0,'Retain reservations if prepaid/unknown activity remains'
 delta=used-d['published_snapshot']['used_SU'];assert delta>=0
 conservative=math.ceil(max(delta,total)+1.0);assert conservative<=d['baseline_wave_planning_ceiling_SU'],'No new spending: observed usage already exceeds this wave'
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat();tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');p=base/('reconciliation-'+tag+'.json');p.write_text(json.dumps(dict(observed_utc=utc,jobs=safe,project_report=report,own_queue=own,terminal_estimated_SU=total,reported_delta_SU=delta,consumed_ceiling_SU=conservative,policy='ceil(max(project reported delta, all recorded terminal core-hour estimates)+1 SU buffer); no exact posted per-job charge claimed',limits='Project report timestamp and refresh lag unresolved. Runtime requested core counts charged at validated queue rate 1. No individual billing export.'),indent=2)+'\n')
 d.update(updated_utc=utc,consumed_ceiling_SU=conservative,outstanding_reserved_max_SU=0,reserved_max_SU=conservative,planning_committed_SU=conservative,latest_project_snapshot=dict(observed_utc=utc,used_SU=used,balance_SU=balance,in_doubt_SU=indoubt,site_timestamp_limitation='See retained raw report; timestamp/refresh chronology unresolved'),reconciliation_note='All recorded CPU jobs terminal; own queue empty and report In Doubt zero. Requested maxima retired with actual terminal resources plus one SU rounding buffer; not individual posted billing.',last_reconciliation=str(p.relative_to(R)))
 ledger.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(report=str(p),estimated_SU=total,reported_delta_SU=delta,consumed_ceiling_SU=conservative,planning_remaining_SU=d['baseline_wave_planning_ceiling_SU']-conservative),indent=2))
