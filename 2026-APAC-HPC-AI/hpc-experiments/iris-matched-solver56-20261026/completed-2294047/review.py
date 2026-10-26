"""Retain the failed pair and separately validate its complete H arm."""
from pathlib import Path
import hashlib,importlib.util,json,math,re,statistics,tarfile
E=Path(__file__).resolve().parent;source=E.parent;meta=json.loads((E/'collection.json').read_text());archive=E/'raw-evidence.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==meta['archive_sha256']
with tarfile.open(archive) as tar:
 members={m.name:m for m in tar.getmembers()};assert set(members)==set(meta['files'])
 for name,want in meta['files'].items():
  raw=tar.extractfile(members[name]).read();assert len(raw)==want['bytes'] and hashlib.sha256(raw).hexdigest()==want['sha256']
  p=E/'collected'/name;p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists():assert p.read_bytes()==raw
  else:p.write_bytes(raw)
spec=importlib.util.spec_from_file_location('pair_review',source/'review-pair.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
run=E/'collected/RUNS/2294047';h=module.review_arm(run,'H','hierarchical')
assert '2294047|FAILED|124:0|02:04:02|56|iris009|' in meta['accounting']
s=run/'S';assert (s/'return-code.txt').read_text().strip()=='124'
text=(s/'simpleFoam.log').read_text();assert not re.search(r'(?m)^End\s*$',text)
steps=[int(v) for v in re.findall(r'(?m)^Time = (\d+)\s*$',text)];assert steps==list(range(1,144))
timing=[float(v) for v in re.findall(r'Wall-clock time elapsed during the current time step = ([\deE.+-]+)',text)]
assert len(timing)==141 and all(math.isfinite(v) and v>0 for v in timing)
wall=[list(map(float,l.split())) for l in (s/'postProcessing/wallClockTimeStatistics/0/wallClockTime.dat').read_text().splitlines() if l.strip() and not l.startswith('#')]
assert [int(r[0]) for r in wall]==list(range(2,143)) and all(abs(a-b[2])<1e-8 for a,b in zip(timing,wall))
ht=[float(v) for v in re.findall(r'Wall-clock time elapsed during the current time step = ([\deE.+-]+)',(run/'H/simpleFoam.log').read_text())][:141]
assert len(ht)==len(timing)
result={'passed_replay':True,'complete_pair_valid':False,'job_id':'2294047','scheduler_state':'FAILED','scheduler_exit':'124:0','allocation_wall_seconds':7442,'allocated_CPUs':56,'estimated_allocated_CPU_hours':56*7442/3600,'verified_archive_files':len(members),'H_complete_arm':h,'S_failed_arm':{'returncode':124,'last_started_step':143,'completed_steps':142,'complete_intervals':141,'complete_End':False,'full_150_step_mean':None,'post_run_source_hash_collected':(s/'source-after-run.json').exists()},'exploratory_matched_prefix':{'interval_steps':'2..142','interval_count':141,'H_mean_seconds_per_step':statistics.mean(ht),'S_mean_seconds_per_step':statistics.mean(timing),'S_time_increase_percent':100*(statistics.mean(timing)/statistics.mean(ht)-1),'scored_result':False,'limit':'Censored losing arm; matched prefix is exploratory and cannot replace the intended complete150-step pair.'},'decision':'Close unchanged Scotch-on-Iris branch; retain H150 reference. Screen hierarchical split orders next using cheap native cuts before any more solver spending.','limits':['No complete pair or Scotch150 score','One H-then-S allocation leaves order effects unresolved','S ended at the per-solver cap, not the Slurm wall limit','Post-run S source verification and final native mean absent','Iris remains separate from NSCC; no official score or global optimum claim']}
(E/'review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
