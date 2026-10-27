"""Retire one verified terminal reservation using preserved scheduler evidence."""
from pathlib import Path
import datetime,fcntl,hashlib,json,math,shlex,subprocess
E=Path(__file__).resolve().parent;R=E.parents[1];B=R/'nscc-cpu-timing-probe-20261021';L=B/'cpu-budget.json'
review=json.loads((E/'review.json').read_text());assert review['passed']
snapshot=E.parent/'live-status-1632.json';saved=json.loads(snapshot.read_text());v=saved['job'];r=v['Resource_List']
assert v['job_state']=='F' and v['Exit_status']==0 and str(v['project'])=='59000042'
assert int(r['ngpus'])==0 and float(r['queue_charge_rate'])==1 and r['walltime']=='00:05:00'
assert int(r['ncpus'])==int(v['resources_used']['ncpus'])==512 and v['resources_used']['walltime']=='00:00:11'
assert review['terminal']==v or all(review['terminal'].get(k)==v.get(k) for k in ['job_state','Exit_status','Resource_List','resources_used','project'])
output=E/'budget-reconciliation.json';assert not output.exists()
with (B/'cpu-budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);d=json.loads(L.read_text());before=json.loads(json.dumps(d))
 entry=next(j for j in d['jobs'] if j['id']=='26004608.pbs101');assert entry['state']=='SUBMITTED'
 p=subprocess.run(['bash',str(R/'tools/nscc-cpu-ssh.sh'),'bash -lc '+shlex.quote('myprojects -p 59000042')],capture_output=True,text=True,timeout=25,check=True)
 report=p.stdout;rows=[x for x in report.splitlines() if x.startswith('| SU')];assert len(rows)==1
 grant,used,balance,doubt=[float(x.strip()) for x in rows[0].split('|')[2:-1]]
 rates=[x for x in report.splitlines() if x.startswith('| CPU Hour')];assert grant==30000 and len(rates)==1 and float(rates[0].split('|')[3].strip())==1
 estimate=512*11/3600;added=math.ceil(estimate);assert added==2 and estimate<=entry['maximum_SU']
 entry.update(state='F_EXIT_0_ARCHIVED_TERMINAL_RECONCILED',scheduler_state='F',scheduler_exit_status=0,elapsed_seconds=11,estimated_actual_SU=estimate,conservative_terminal_allowance_SU=estimate,posted_charge_reconciled=False,terminal_evidence_observed_utc=saved['observed_at_utc'],reservation_note='Only selected known terminal maximum retired once using preserved actual scheduler response; fresh history expired. Original maximum retained. Rounded allowance; no posted individual charge claim.')
 consumed=max(d['consumed_ceiling_SU']+added,math.ceil(used-d['published_snapshot']['used_SU']+1));outstanding=d['outstanding_reserved_max_SU']-entry['maximum_SU'];assert outstanding>=0
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 d.update(updated_utc=now,consumed_ceiling_SU=consumed,outstanding_reserved_max_SU=outstanding,planning_committed_SU=consumed+outstanding,reserved_max_SU=consumed+outstanding,last_reconciliation=str(output.relative_to(R)),latest_project_snapshot={'observed_utc':now,'used_SU':used,'balance_SU':balance,'in_doubt_SU':doubt,'site_timestamp_limitation':'Fresh query still labels backend balance 25 October 21:55:31; not individual posted billing.'})
 assert d['shared_cost_observations']==before['shared_cost_observations']
 assert [j for j in d['jobs'] if j['id']!='26004608.pbs101']==[j for j in before['jobs'] if j['id']!='26004608.pbs101']
 result={'utc':now,'job_id':'26004608.pbs101','terminal_evidence_observed_utc':saved['observed_at_utc'],'terminal_snapshot_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),'terminal_evidence':v,'fresh_history_available':False,'fresh_project_query':report,'estimated_SU':estimate,'rounded_added_allowance_SU':added,'retired_original_maximum_SU':entry['maximum_SU'],'committed_SU':d['planning_committed_SU'],'headroom_SU':d['baseline_wave_planning_ceiling_SU']-d['planning_committed_SU'],'unknown_maxima_unchanged':True,'posted_individual_charge_known':False}
 output.write_text(json.dumps(result,indent=2)+'\n');temp=L.with_suffix('.json.new');temp.write_text(json.dumps(d,indent=2)+'\n');temp.replace(L)
 print(json.dumps({k:v for k,v in result.items() if k not in ['terminal_evidence','fresh_project_query']},indent=2))
