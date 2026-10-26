"""Review diagnostic collection gates without invoking a scheduler or real MPI."""
import ast, hashlib, json, os, subprocess, tempfile
from pathlib import Path
E=Path(__file__).resolve().parent;P=E/'payload'
for p in [*P.glob('*.py'),E/'deploy_submit.py']:ast.parse(p.read_text(),feature_version=(3,6))
script=P/'launcher-order-diagnostic.pbs'
subprocess.run(['bash','-n',str(script)],check=True)
s=script.read_text()
assert 'select=4:ncpus=128:mpiprocs=128:mem=32gb:ngpus=0' in s
assert '#PBS -l walltime=00:05:00' in s and 'DEADLINE=$((START + 255))' in s
assert 'MPICH_RANK_REORDER_METHOD=0' in s and 'test -z "${LD_PRELOAD:-}"' in s
assert 'sha256sum -c payload-sha256.txt' in s
with tempfile.TemporaryDirectory() as temp:
 out=Path(temp);env=dict(os.environ,PMI_RANK='0',PYTHONDONTWRITEBYTECODE='1')
 p=subprocess.run(['python3',str(P/'rank-capture.py'),str(out)],env=env,capture_output=True)
 assert p.returncode==0,p.stderr
 row=json.loads((out/'rank-0000.json').read_text())
 assert row['cpus']==sorted(os.sched_getaffinity(0)) and row['pmi_rank']==0
 assert subprocess.run(['python3',str(P/'rank-capture.py'),str(out)],env=env,capture_output=True).returncode!=0
 env.pop('PMI_RANK')
 assert subprocess.run(['python3',str(P/'rank-capture.py'),str(out)],env=env,capture_output=True).returncode!=0
 header='''#define MPI_MAX_PROCESSOR_NAME 256
#define MPI_THREAD_SINGLE 0
#define MPI_SUCCESS 0
#define MPI_COMM_WORLD 0
#define MPI_INT 0
#define MPI_SUM 0
int MPI_Init_thread(int*,char***,int,int*);
int MPI_Comm_rank(int,int*);int MPI_Comm_size(int,int*);
int MPI_Get_processor_name(char*,int*);int MPI_Allreduce(const void*,void*,int,int,int,int);
int MPI_Finalize(void);
'''
 (out/'mpi.h').write_text(header)
 subprocess.run(['cc','-fsyntax-only','-Wall','-Wextra','-Werror','-I'+temp,str(P/'mpi-init-probe.c')],check=True)
checks=['Bash syntax and Python3.6 grammar','512 requested PBS process slots match 512-rank launches','Five-minute wall and 255-second internal deadline','Python entry retains actual affinity without singleton rejection','Exclusive rank files reject a duplicate; missing PMI identity rejected','C syntax against declarations only, not real MPI compile/link','Pinned payload hashes before and after; common method0/no preload']
result={'passed':True,'review_date':'2026-10-26','checks':checks,'payload_sha256':{'payload/'+p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(P.iterdir()) if p.is_file()},'root_corrections':['Changed mistaken 32 mpiprocs to 128 per node before sealing','Write native pre-init observation before MPI_Init_thread, indexed by original PMI rank','Reject module setup and sealed source failures','Treat collection completion separately from successful affinity qualification'],'evidence_basis':'25957725 retained 128 successful preexec records, 17 wide-mask rejections, 367 absent; no MPI audit. mpirun and mpiexec are the same installed PALS binary.','limitations':['Real site MPI compilation/linking and execution pending','Observational diagnostic only; no solver or placement qualification','Filesystem per-rank writes are monitoring overhead and cannot be used as ranked solver timings']}
(E/'ROOT_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'checks':checks},indent=2))
