"""Derive explicit native BF16/unquant repair only after the norm fixture passes."""
from pathlib import Path
import ast,hashlib,json,re,shutil,subprocess,tarfile
O=Path(__file__).resolve().parent;C=O.parent/'eagle3-pd-candidate-20261021';P=O.parent/'eagle3-dtype-probe-20261021'
probe=json.loads((P/'collection.json').read_text());assert probe['state']=='DTYPE_NORM_PASS_FULL_PD_UNVERIFIED' and probe['probe']['passed'] and probe['probe']['auto_mismatch_reproduced']
assert probe['probe']['modes'][1]['cuda_graph_replay_exact']
assert not (O/'SHA256SUMS').exists(),'Never regenerate an existing frozen repair'
files=[line.split('  ',1)[1] for line in (C/'SHA256SUMS').read_text().splitlines()]
for name in files:shutil.copy2(C/name,O/name)
for name in ['native-load-prerequisite.json','corpus-prerequisite.json','reference-prerequisite.json','asset-preflight-code.json','asset-contract.json','validate-candidate.py','collect-terminal.py','inspect-speculative-metadata.py']:
 shutil.copy2(C/name,O/name)
(O/'dtype-prerequisite.json').write_text(json.dumps(probe,indent=2)+'\n')
p=O/'worker.sh';s=p.read_text();needle='--speculative-draft-attention-backend flashinfer)';assert s.count(needle)==1;s=s.replace(needle,'--speculative-draft-attention-backend flashinfer --dtype bfloat16\n        --speculative-draft-model-quantization unquant)');p.write_text(s)
p=O/'benchmark.pbs';s=p.read_text().replace(C.name,O.name);s=re.sub(r'^#PBS -N .*$', '#PBS -N ap42-eagle3-pd-bf16',s,flags=re.M);p.write_text(s)
config=json.loads((O/'config.json').read_text());config.update(experiment=O.name,source_bundle=C.name,source_job='222763.pbs111',retry_of='222763.pbs111',retry_reason='Native auto draft FP16 conflicts with shared BF16 target embedding; cheap actual norm fixture proves explicit BF16 repair',activation_dtype='bfloat16',requested_draft_quantization='unquant',draft_quantization=None,dtype_probe_job=probe['job'],purpose='Native PD correctness with explicit consistent BF16 and unquant draft; official FP8 target unchanged');(O/'config.json').write_text(json.dumps(config,indent=2)+'\n')
s=(C/'submit-pbs.py').read_text().replace("assert json.loads((O / 'semantic-validation.json').read_text())['passed']", "assert json.loads((O / 'semantic-validation.json').read_text())['passed']\nassert json.loads((O / 'dtype-prerequisite.json').read_text())['state']=='DTYPE_NORM_PASS_FULL_PD_UNVERIFIED'")
s=s.replace("'222761.pbs111',", "'222761.pbs111','222763.pbs111',"+repr(probe['job'])+",")
s=re.sub(r"set\(active\) <= \{[^}]*\}","set(active) <= {"+repr(probe['job'])+"}",s)
s=re.sub(r"dependency = '[^']+' if active else ''","dependency = "+repr(probe['job'])+" if active else ''",s)
(O/'submit-pbs.py').write_text(s)
assert (O/'nixl-conn.py').read_bytes()==(C/'nixl-conn.py').read_bytes()
assert (O/'token-control.py').read_bytes()==(C/'token-control.py').read_bytes()
assert (O/'check-token-result.py').read_bytes()==(C/'check-token-result.py').read_bytes()
for p in O.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in list(O.glob('*.sh'))+[O/'benchmark.pbs']:subprocess.run(['bash','-n',str(p)],check=True)
(O/'SHA256SUMS').write_text(''.join(hashlib.sha256((O/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in files))
with tarfile.open(O/'payload.tar.gz','w:gz') as t:
 for name in files+['SHA256SUMS']:t.add(O/name,arcname=O.name+'/'+name)
subprocess.run(['python3',str(O/'validate-candidate.py')],check=True)
(O/'validation.json').write_text(json.dumps(dict(passed=True,scope='Actual cheap norm prerequisite, unchanged target/transport/client/semantic gates and explicit BF16/unquant flags; full PD remains unverified',reference_job='222761.pbs111',dtype_probe_job=probe['job'],max_su=1024,scored_benchmark=False),indent=2)+'\n')
print('Frozen native BF16 repair, not submitted',O.name)
