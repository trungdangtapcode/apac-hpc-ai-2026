"""Derive an immutable candidate only after sealed, reviewed real reference PASS."""
from pathlib import Path
import ast
import argparse
import re
import hashlib
import json
import shutil
import subprocess
import tarfile

O=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reference-dir',type=Path,required=True);args=parser.parse_args()
C=args.reference_dir.resolve()
assert C.parent==O.parent, 'Use an owned sibling experiment reference'
review=json.loads((C/'REFERENCE_REVIEW.json').read_text())
reference_job=json.loads((C/'pbs-receipt.json').read_text())['job']
assert review['reference_usable'] and review['job']==reference_job
collection=json.loads((C/'collection.json').read_text())
assert collection['state']=='TOKEN_REFERENCE_PASS_AWAITING_RUNTIME_REVIEW'
assert hashlib.sha256((C/'collection.json').read_bytes()).hexdigest()==review['collection_sha256']
assert not (O/'SHA256SUMS').exists(), 'Never rebuild an existing frozen candidate'
reference=collection['token_control'];assert reference['passed']
files=[line.split('  ',1)[1] for line in (C/'SHA256SUMS').read_text().splitlines()]
for name in files:shutil.copy2(C/name,O/name)
(O/'target-reference.json').write_text(json.dumps(reference,indent=2)+'\n')
shutil.copy2(C/'REFERENCE_REVIEW.json',O/'reference-prerequisite.json')
shutil.copy2(C/'native-load-prerequisite.json',O/'native-load-prerequisite.json')
shutil.copy2(C/'corpus-prerequisite.json',O/'corpus-prerequisite.json')
shutil.copy2(C/'asset-preflight-code.json',O/'asset-preflight-code.json')
shutil.copy2(C/'asset-contract.json',O/'asset-contract.json')
p=O/'token-control.py';s=p.read_text();s=s.replace("platform='H100', scope='Real target-only PD /generate observation and repeat stability; no ranked score or organiser accuracy'", "platform='H100', scope='Real EAGLE3 PD exact-ID comparison against sealed target reference; no ranked score or organiser accuracy'")
a=s.index('        corpus=json.loads(');z=s.index('        started_all=time.monotonic()',a)
s=s[:a]+'''        reference=json.loads((Path(__file__).parent/'target-reference.json').read_text())
        assert reference['passed'] and reference['platform']=='H100'
        assert reference['target_identity_sha256']==result['target_identity_sha256'], 'Target identity changed'
        result['cases']=reference['cases']
        assert result['cases']==json.loads((Path(__file__).parent/'prepared-corpus.json').read_text())['cases']
        assert len(result['cases'])==4
        assert len(next(c['input_ids'] for c in result['cases'] if c['name']=='long4000'))==4000
''' +s[z:]
s=s.replace("['target-a','target-b']","['draft-a','draft-b']").replace("result['stages']['target-a']","result['stages']['draft-a']").replace("result['stages']['target-b']","result['stages']['draft-b']")
s=s.replace("        result['passed']=True", """        reference_comparisons=[]
        for a,b in zip(reference['stages']['target-a'],result['stages']['draft-a'],strict=True):
            equal=a['name']==b['name'] and a['request']==b['request'] and a['observed']==b['observed']
            reference_comparisons.append(dict(name=a['name'],exact_reference_ids_and_finish_equal=equal))
        result['reference_comparisons']=reference_comparisons
        assert len(reference_comparisons)==4 and all(c['exact_reference_ids_and_finish_equal'] for c in reference_comparisons), 'EAGLE3 differs from sealed target reference'
        result['passed']=True""")
p.write_text(s)
guard=(O/'check-token-result.py').read_text().replace("'target-a'","'draft-a'").replace("'target-b'","'draft-b'").replace(',strict=True','').replace('REAL_TOKEN_REFERENCE_GATE_PASSED','SPECULATIVE_LOCAL_PAIR_GATE_PASSED')
guard+="\nreference=json.loads((O/'target-reference.json').read_text())\nassert r['target_identity_sha256']==reference['target_identity_sha256'] and r['platform']==reference['platform']\nfor a,b in zip(reference['stages']['target-a'],r['stages']['draft-a']):\n assert a['request']==b['request'] and a['observed']==b['observed']\n"
(O/'check-token-result.py').write_text(guard)
# Add only native speculation flags before the unchanged target server invocation.
p=O/'worker.sh';s=p.read_text();needle='exec python3 -m sglang.launch_server \\\n';assert s.count(needle)==1
s=s.replace(needle,'''draft=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/drafts/nebius-eagle3-qwen235b-ff0f0c09
python3 "$QWEN_BUNDLE/verify-draft.py" "$draft"
extra+=(--speculative-algorithm EAGLE3 --speculative-draft-model-path "$draft"
        --speculative-num-steps 2 --speculative-eagle-topk 1 --speculative-num-draft-tokens 3
        --speculative-draft-attention-backend flashinfer)
'''+needle);p.write_text(s)
(O/'verify-draft.py').write_text('''"""Verify only the pinned public draft; never change official target files."""
import hashlib,json,sys
from pathlib import Path
p=Path(sys.argv[1]);digest=hashlib.sha256()
with (p/'model.safetensors').open('rb') as f:
 while block:=f.read(4194304):digest.update(block)
assert digest.hexdigest()=='bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86'
a=json.loads((p/'config.json').read_text());b=json.loads((p/'publisher-config.json').read_text())
assert {k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}=={'architectures'}
assert a['architectures']==['LlamaForCausalLMEagle3']
print('PINNED_DRAFT_VERIFIED',digest.hexdigest(),flush=True)
''')
p=O/'benchmark.pbs';pbs=p.read_text().replace(C.name,O.name).replace('00:20:00','00:30:00');pbs=re.sub(r'^#PBS -N .*$', '#PBS -N ap42-eagle3-pd-candidate', pbs, flags=re.M);p.write_text(pbs)
p=O/'topology-job.sh';p.write_text(p.read_text().replace('deadline=${2:-1050}','deadline=${2:-1650}').replace('1200-SECONDS-40','1800-SECONDS-40'))
config=json.loads((O/'config.json').read_text());config.update(experiment=O.name,source_bundle=C.name,source_job=reference_job,purpose='Real EAGLE3 PD exact IDs against sealed target-only reference',paired_role='speculative correctness candidate',walltime_minutes=30,speculative_algorithm='EAGLE3',speculative_num_steps=2,speculative_eagle_topk=1,speculative_num_draft_tokens=3,draft_quantization=None,speculative_draft_attention_backend='flashinfer',reference_identity_sha256=reference['target_identity_sha256'],capacity_limit='Decode explicit 256; native speculative unspecified prefill default may resolve 48; correctness N1 only, not a matched throughput pair')
(O/'config.json').write_text(json.dumps(config,indent=2)+'\n')
s=(C/'submit-pbs.py').read_text().replace("assert json.loads((O / 'validation.json').read_text())['passed']", "assert json.loads((O / 'validation.json').read_text())['passed']\nassert json.loads((O / 'reference-prerequisite.json').read_text())['reference_usable']")
s=s.replace("'222750.pbs111']","'222750.pbs111','222752.pbs111']").replace("{'222750.pbs111'}","{'222752.pbs111'}").replace("dependency = '222750.pbs111'","dependency = '222752.pbs111'").replace('16 * 128 * 20 / 60','16 * 128 * 30 / 60').replace("'00:20:00'","'00:30:00'").replace('minutes=20','minutes=30').replace('target_token_reference_gate','speculative_pd_correctness_gate').replace('16-H100/20-minute real target-only token reference gate','16-H100/30-minute real EAGLE3 PD correctness gate').replace('draft_model_instantiated=False','draft_model_instantiated=True')
s=s.replace('AWAITING_COMPONENT_CHECK','AWAITING_SPECULATIVE_CORRECTNESS').replace('Review actual target-only full output IDs and repeat stability before preparing separately frozen speculative comparison; no ranked benchmark.','Review native speculative runtime and exact output IDs against the accepted reference; no ranked benchmark.')
# The chosen repaired reference's own receipt is the only allowed active predecessor.
s=s.replace("'222752.pbs111',", "'222752.pbs111',"+repr(reference_job)+",")
s=re.sub(r"set\(active\) <= \{[^}]*\}", "set(active) <= {"+repr(reference_job)+"}", s)
s=re.sub(r"dependency = '[^']+' if active else ''", "dependency = "+repr(reference_job)+" if active else ''", s)
(O/'submit-pbs.py').write_text(s)
collector=(C/'collect-terminal.py').read_text().replace('TOKEN_REFERENCE_PASS_AWAITING_RUNTIME_REVIEW','SPECULATIVE_IDS_MATCH_AWAITING_RUNTIME_REVIEW').replace('TOKEN_REFERENCE_FAILED_REVIEW_REQUIRED','SPECULATIVE_IDS_FAILED_REVIEW_REQUIRED').replace('token_reference_passed=passed','speculative_exact_ids_matched=passed').replace('speculative_inference_tested=False','speculative_requested=True, speculative_runtime_reviewed=False')
(O/'collect-terminal.py').write_text(collector)
files=sorted(set(files+['target-reference.json','verify-draft.py']))
for p in O.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in list(O.glob('*.sh'))+[O/'benchmark.pbs']:subprocess.run(['bash','-n',str(p)],check=True)
assert (O/'nixl-conn.py').read_bytes()==(C/'nixl-conn.py').read_bytes()
assert (O/'token-control.py').read_text().count("reference['cases']")==1
(O/'SHA256SUMS').write_text(''.join(hashlib.sha256((O/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in files))
with tarfile.open(O/'payload.tar.gz','w:gz') as t:
 for n in files+['SHA256SUMS']:t.add(O/n,arcname=O.name+'/'+n)
(O/'validation.json').write_text(json.dumps(dict(passed=True,scope='Syntax, reference prerequisite and unchanged native transport; actual EAGLE3 PD inference/IDs still unverified',reference_job=reference_job,scored_benchmark=False,max_su=1024),indent=2)+'\n')
print('Frozen',O.name,'with',len(files),'runtime files; not submitted')
