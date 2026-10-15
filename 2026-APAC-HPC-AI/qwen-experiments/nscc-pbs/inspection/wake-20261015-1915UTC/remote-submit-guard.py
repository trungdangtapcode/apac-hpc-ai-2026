import subprocess,re,sys
from pathlib import Path
root=Path('/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015')
queue=subprocess.check_output(['qstat','-u','apacsc42'],text=True)
print('OWN_QUEUE\n'+queue,flush=True)
assert not re.search(r'^\s*\d+\.pbs\d+',queue,re.M),'Own GPU job active; refuse submission'
history=subprocess.check_output(['qstat','-x','-u','apacsc42'],text=True)
print('OWN_HISTORY\n'+history,flush=True)
known={'220453.pbs111','220454.pbs111','220456.pbs111','220457.pbs111','220486.pbs111','220489.pbs111'}
seen=set(re.findall(r'^\s*(\d+\.pbs\d+)',history,re.M))
assert seen<=known,('Unreconciled PBS job',seen-known)
ledger=subprocess.check_output(['myprojects'],text=True)
print('CREDIT\n'+ledger,flush=True)
m=re.search(r'\| SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)',ledger)
assert m,'Cannot parse credit'
grant,used,balance,doubt=map(float,m.groups())
assert used==539.307 and doubt==0,('Ledger changed, reconcile before submission',used,doubt)
assert used+1024<=4096 and balance-1024>=13000
bundle=root/'baseline-n32-readiness-02'
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,check=True)
job=subprocess.check_output(['qsub',str(bundle/'benchmark.pbs')],cwd=root,text=True).strip()
assert re.fullmatch(r'\d+\.pbs\d+',job),('Uncertain qsub reply',job)
print('SUBMITTED_JOB='+job,flush=True)
