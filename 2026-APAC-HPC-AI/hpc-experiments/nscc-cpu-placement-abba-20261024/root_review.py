"""Offline source/copy/shim checks; no scheduler or solver execution."""
from pathlib import Path
import ast,json,subprocess,tempfile,shutil,os
E=Path(__file__).resolve().parent;P=E/'payload';R=E.parent
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
def run(args):return subprocess.run(args,capture_output=True,text=True,env=ENV)
checks=[]
for file in P.rglob('*.py'):ast.parse(file.read_text(),feature_version=(3,6))
checks.append('Python3.6 grammar for every payload script')
with tempfile.TemporaryDirectory(prefix='hpc-lifecycle-review-') as tmp:
 result=run(['python3',str(P/'batch-lifecycle.py'),'start',tmp]);assert result.returncode==0,result.stderr
 state=json.loads((Path(tmp)/'batch-lifecycle.json').read_text())
 assert (state['requested_walltime_seconds'],state['maximum_requested_SU'],state['internal_deadline_seconds'])==(5400,768,5220)
 script=(P/'mpi-placement-abba.pbs').read_text()
 assert '#PBS -l walltime=01:30:00' in script and 'INTERNAL_DEADLINE=5220' in script
checks.append('Lifecycle metadata matches PBS90minute request and87minute internal deadline')
with tempfile.TemporaryDirectory(prefix='hpc-ab-rootreview-') as tmp:
 tmp=Path(tmp);case=tmp/'case';shutil.copytree(P/'case',case);(case/'logFiles').mkdir();(case/'logFiles/log').write_text('runtime');(case/'rank-order.txt').write_text('0\n')
 args=['python3',str(P/'verify-case-sources.py'),'--source',str(P/'case'),'--case',str(case),'--accepted',str(P/'accepted-source-manifest.json')]
 result=run(args);assert result.returncode==0,result.stderr
 assert json.loads(result.stdout)['source_file_count']==len(json.loads((P/'accepted-source-manifest.json').read_text())['files'])
 checks.append('Frozen case including figures/COPYING accepted with runtime log and order file')
 (case/'figures/INJECTED').write_text('unexpected');assert run(args).returncode!=0;checks.append('Unexpected frozen-source directory file rejected')
 left=tmp/'baseline';right=tmp/'copy';left.mkdir();right.mkdir()
 for name in ['a','b']:(left/name).write_text(name);(right/name).write_text(name)
 args=['python3',str(P/'verify-copy-isolation.py'),str(left),str(right)];assert run(args).returncode==0;checks.append('Independent regular-file inodes accepted')
 os.link(left/'a',right/'renamed-hardlink');assert run(args).returncode!=0;checks.append('Cross-name hardlink to baseline rejected')
 result=run(['python3',str(P/'test-affinity-shim.py')]);assert result.returncode==0,(result.stdout,result.stderr);checks.append('Exact qualification shim and capture helper pass mocked PMPI tests')
qualified=R/'nscc-cpu-mpi-exec-affinity-20261024/payload'
assert all((P/name).read_bytes()==(qualified/name).read_bytes() for name in ['preserve-affinity.c','capture-affinity-exec.py'])
checks.append('Shim and exec helper bytes exactly match submitted qualification')
assert run(['bash','-n',str(P/'mpi-placement-abba.pbs')]).returncode==0;checks.append('Bash syntax')
script=(P/'mpi-placement-abba.pbs').read_text();assert 'run_logged copy_initialized_baseline' in script and 'run_logged "copy_${arm}"' in script
checks.append('Both copy phases bounded by the shared remaining-time wrapper')
result={'passed':True,'checks':checks,'review_fixes':['Include every frozen source directory, including figures','Detect baseline inode reuse under any relative filename','Bound copies and retain their return codes; first local guard caught unapplied text substitution, corrected with explicit patch','Use exact submitted qualification shim/helper bytes'],'unproven':['Fresh partition graph','Cray MPI build and full current allocation mapping','OpenFOAM compatibility and four complete solver arms','Actual copy/hash/validation runtime'],'state':'DRAFT_UNSEALED_UNSUBMITTED'}
(E/'root-offline-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'checks':checks},indent=2))
