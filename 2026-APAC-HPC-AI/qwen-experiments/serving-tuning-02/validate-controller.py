import copy,importlib.util,json,tempfile,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('apac_watcher_s2',ROOT/'watch-serving-tuning.py');watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
original=json.loads((ROOT/'serving-tuning-02/backend-pilots.json').read_text());submitted=[];external_jobs=[]
watch.subprocess=types.SimpleNamespace(run=lambda *a,**k:types.SimpleNamespace(stdout='',returncode=0))
def fake_command(args):
 if args[0]=='squeue':return '\n'.join(external_jobs)
 assert args[0]=='sbatch';submitted.append(args);return str(91000+len(submitted))
watch.command=fake_command
watch.submit_followup=lambda state,name,source,ns,purpose: state['entries'].append({'id':name,'planned_ns':ns,'state':'ACTIVE','attempts':[{'job':'92000','state':'SUBMITTED'}]})
row={'concurrency':52,'requests':100,'errors':0,'cancelled_requests':0,'good_output_tokens_s':2000,'sla_pass':True}
def parent(smoke=8):return {'id':'s2-chunk4096-n52','state':'MEASURED','attempts':[{'job':'90001','state':'COMPLETED','output_smoke':{'passed':smoke,'total':8},'measurements':[row]}],'measurements':[row]}
with tempfile.TemporaryDirectory(prefix='apac42-s2-controller-') as temporary:
 directory=Path(temporary);(directory/'serving-tuning-02').mkdir();path=directory/'serving-tuning-02/backend-pilots.json';watch.ROOT=directory;watch.STATE=directory/'registry.json'
 state={'entries':[parent()]};path.write_text(json.dumps(copy.deepcopy(original)));watch.advance_second_wave(state)
 assert {e['id'] for e in state['entries']}=={'s2-chunk4096-n52','s2-deepgemm-control-n52','s2-fp8-kv-n52'}
 assert len(submitted)==2
 dg=next(e for e in state['entries'] if e['id']=='s2-deepgemm-control-n52');dg.update(state='MEASURED',measurements=[row]);dg['attempts'][0].update(state='COMPLETED',output_smoke={'passed':8,'total':8},measurements=[row])
 watch.advance_second_wave(state);assert len(submitted)==3 and any(e['id']=='s2-deepep-ll-n52' for e in state['entries'])
 watch.advance_second_wave(state);assert len(submitted)==3
 submitted.clear();state={'entries':[parent()]+[{'id':str(i),'state':'ACTIVE','attempts':[{'state':'RUNNING'}]} for i in range(4)]};path.write_text(json.dumps(copy.deepcopy(original)));watch.advance_second_wave(state);assert not submitted
 submitted.clear();external_jobs[:]=['88001','88002','88003','88004'];state={'entries':[parent()]};path.write_text(json.dumps(copy.deepcopy(original)));watch.advance_second_wave(state);assert not submitted
 external_jobs.clear()
 submitted.clear();state={'entries':[parent(7)]};path.write_text(json.dumps(copy.deepcopy(original)));pending=watch.advance_second_wave(state);assert not submitted and not pending
 assert all(p['state'].startswith('SKIPPED') for p in json.loads(path.read_text())['pilots'])
 # A documented independent baseline can allow research despite its known failure.
 submitted.clear();entry=parent(7);entry['attempts'][0]['output_baseline_comparison']={'research_eligible':True,'accuracy_verified':False}
 state={'entries':[entry]};path.write_text(json.dumps(copy.deepcopy(original)));watch.advance_second_wave(state);assert len(submitted)==2
 # A passing benchmark on one attempt cannot borrow output checks from another.
 submitted.clear();entry=parent(7);entry['attempts'].append({'job':'90002','state':'COMPLETED','output_smoke':{'passed':8,'total':8},'measurements':[]})
 state={'entries':[entry]};path.write_text(json.dumps(copy.deepcopy(original)));watch.advance_second_wave(state);assert not submitted
report={'passed':True,'actual_sbatch_calls':0,'max_four_active_jobs_enforced':True,'external_jobs_count_towards_cap':True,'matched_control_before_deepep':True,'unexplained_smoke_failure_blocks_backend_trials':True,'independent_baseline_can_allow_research_only':True,'benchmark_and_output_must_share_attempt':True,'blocked_dependency_propagates':True,'no_duplicate_pilots':True,'scope':'Isolated CPU scheduler simulation, not GPU or accuracy validation'}
(ROOT/'serving-tuning-02/controller-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
