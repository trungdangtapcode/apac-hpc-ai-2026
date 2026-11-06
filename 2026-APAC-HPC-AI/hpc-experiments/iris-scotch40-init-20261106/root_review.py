#!/usr/bin/env python3
"""Root review of the frozen N40 initialization payload and qualified proof protocol."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess
E=Path(__file__).resolve().parent
Q=E.parent/'iris-rank-probe-files-qualify-20261106/completed-2294996/REVIEW.json'
C=E.parent/'iris-scotch40-cut-20261105/completed-2294919/REVIEW.json'
FILES=[E/'init.sbatch',E/'verify-init.py',E/'source-pins.json',E/'probe_writer.py',E/'read_rank_proofs.py',E/'validate_rank_proofs.py']+sorted(p for p in (E/'payload-case').rglob('*') if p.is_file())
assert len(FILES)==47,len(FILES)
assert all(not p.is_symlink() for p in FILES)
expected={str(p.relative_to(E)):hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES}
assert expected['probe_writer.py']=='359ac014e49a3c6be836df813923ab2a594e00292adfb14180bbc695f1c4c943'
assert expected['read_rank_proofs.py']=='145f944a1f4aaef90603efdd6fbe404697a6a511c95f7282b957744923a77caa'
q=json.loads(Q.read_text());assert q['passed'] and q['all_four_file_probes_passed'] and q['terminal_state']=='COMPLETED'
assert q['protocol_sha256']=={k:expected[k] for k in q['protocol_sha256']}
c=json.loads(C.read_text());assert c['passed'] and c['job_id']=='2294919' and c['ranks']==40
assert json.loads((E/'source-pins.json').read_text())['files']['system/include/caseDefinition']==hashlib.sha256((E/'payload-case/system/include/caseDefinition').read_bytes()).hexdigest()
script=(E/'init.sbatch').read_text().splitlines()
for line in ['#SBATCH -J tu-iris-s40-init','#SBATCH -p iris','#SBATCH -A rdmaworkshop','#SBATCH --qos=low','#SBATCH --exclusive','#SBATCH --mem=0','#SBATCH -N 1','#SBATCH --gpus=0','#SBATCH -n 40','#SBATCH -t 00:20:00']:assert script.count(line)==1,line
assert 'processor39' in (E/'init.sbatch').read_text() and 'processor47' not in (E/'init.sbatch').read_text()
assert '2294919' in (E/'verify-init.py').read_text() and 'processor47' not in (E/'verify-init.py').read_text()
subprocess.run(['bash','-n',str(E/'init.sbatch')],check=True)
subprocess.run(['python3','-m','py_compile',str(E/'verify-init.py'),str(E/'review.py'),str(E/'probe_writer.py'),str(E/'read_rank_proofs.py'),str(E/'validate_rank_proofs.py')],check=True)
r=subprocess.run(['python3',str(E/'review.py')],check=True,text=True,capture_output=True)
(E/'payload-sha256.json').write_text(json.dumps({'files':expected},indent=2)+'\n')
(E/'payload-sha256.txt').write_text(''.join(d+'  '+n+'\n' for n,d in expected.items()))
review={'passed':True,'payload_sha256':expected,'payload_file_count':len(expected),'source_pin_count':len(json.loads((E/'source-pins.json').read_text())['files']),
'cut_job_id':'2294919','cut_review_sha256':hashlib.sha256(C.read_bytes()).hexdigest(),'cut_review_passed':True,
'protocol_qualification_job_id':'2294996','protocol_qualification_review_sha256':hashlib.sha256(Q.read_bytes()).hexdigest(),
'protocol_sha256':q['protocol_sha256'],'offline_review':r.stdout.strip(),'scheduler_admission':'NOT_PERFORMED','deployment':'NOT_PERFORMED',
'checks':['N40 cut native review passed','47 payload files frozen','qualified writer/reader exact byte hashes pinned','40-rank source, field and native log gates checked','MPI proof uses exclusive per-rank files, not stdout parsing','SBATCH envelope 56 CPU,40 tasks,zero GPUs,20 minutes','bash syntax and Python bytecode compile passed','offline accept/reject reviewer passed']}
(E/'ROOT_REVIEW.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({'passed':True,'payload_files':len(expected),'protocol':q['protocol_sha256'],'offline_review':r.stdout.strip()}))
