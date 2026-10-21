"""Inspect sealed native Iris toy logs; this cannot award a 65M score."""
from pathlib import Path
import hashlib,json,re
O=Path(__file__).resolve().parent;D=O/'collected/2293751'
for relative,digest in json.loads((D/'evidence-sha256.json').read_text()).items():assert hashlib.sha256((D/relative).read_bytes()).hexdigest()==digest
receipt=json.loads((D/'toy-receipt.json').read_text());assert receipt['returncode']==0 and receipt['stdout'].strip()=='2293751'
assert hashlib.sha256((O/'kit/02-toy-stages.sbatch').read_bytes()).hexdigest()==receipt['sha256']
account=(D/'toy-accounting.txt').read_text();assert '2293751|COMPLETED|0:0|30|56|1|iris031' in account
stdout=(D/'runs/2293751.out').read_text();assert '02-toy-stages: PASS' in stdout
rows=[]
for role in ['hierarchical','scotch']:
 root=D/'runs/2293751'/role
 split=dict(line.split('=',1) for line in (root/'SPLIT').read_text().splitlines());assert split['method']==role and split['nCores']=='4'
 logs=root/'logFiles'
 for name in ['decomposePar','renumberMesh','potentialFoam','simpleFoam']:
  text=(logs/(name+'.log')).read_text();assert re.search(r'^End\s*$',text,re.M),name
  assert 'FOAM FATAL' not in text and 'died from signal' not in text,name
 assert (logs/'restore0Dir.log').is_file()
 text=(logs/'simpleFoam.log').read_text();assert 'OPENFOAM=2512' in text and 'scalar=64' in text
 assert re.search(r'^nProcs\s*:\s*4\s*$',text,re.M)
 times=[int(v) for v in re.findall(r'^Time = (\d+)\s*$',text,re.M)];assert times==list(range(1,times[-1]+1))
 avg=re.search(r'Average wall-clock time per time step\s*=\s*([-+\d.eE]+)',text)
 clock=re.findall(r'ClockTime\s*=\s*([-+\d.eE]+) s',text)
 rows.append(dict(method=role,ranks=4,actual_steps=times[-1],solver_end=True,
                  toy_average_s_step=float(avg[1]) if avg else None,toy_clocktime_s=float(clock[-1]),
                  timing_confidence_warning='smaller than the calculated one by the statistical analysis' in text,
                  scope='Toy diagnostic timing only; not a ranked 65M result'))
result=dict(job='2293751',state='NATIVE_TOY_STAGES_PASS',scheduler_state='COMPLETED',exit_status='0:0',elapsed_seconds=30,allocated_cpus=56,nodes=1,node='iris031',mpi_ranks=4,payload_and_evidence_hashes_passed=True,methods=rows,
            hardware_telemetry='Not collected; no CPU utilization, NUMA, bandwidth, power or network profile inferred',
            full_65m_case_tested=False,cd_acceptance_proven=False,contest_score=None)
(O/'review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
