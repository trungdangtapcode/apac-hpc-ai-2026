"""Freeze a real reference repair only from a passing actual-runtime corpus."""
from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,subprocess,tarfile
O=Path(__file__).resolve().parent
P=O.parent/'eagle3-tokenizer-corpus-20261021';C=O.parent/'eagle3-integration-20261021'
r=json.loads((P/'collection.json').read_text());assert r['state']=='TOKENIZER_CORPUS_PASS'
corpus=r['tokenizer'];assert corpus['passed'] and len(corpus['cases'])==4
assert not (O/'SHA256SUMS').exists(), 'Never mutate frozen repair'
files=[line.split('  ',1)[1] for line in (C/'SHA256SUMS').read_text().splitlines()]
for name in files:shutil.copy2(C/name,O/name)
(O/'prepared-corpus.json').write_text(json.dumps(corpus,indent=2)+'\n')
shutil.copy2(P/'collection.json',O/'corpus-prerequisite.json')
for name in ['native-load-prerequisite.json','asset-preflight-code.json','asset-contract.json']:shutil.copy2(C/name,O/name)
p=O/'token-control.py';s=p.read_text().replace('        from transformers import AutoTokenizer\n','')
a=s.index('        tokenizer = AutoTokenizer.from_pretrained(');z=s.index('        started_all=time.monotonic()',a)
s=s[:a]+'''        corpus=json.loads((Path(__file__).parent/'prepared-corpus.json').read_text())
        assert corpus['passed'] and corpus['target_revision']==expected['revision']
        assert corpus['small_file_sha256']=={n:v['sha256'] for n,v in expected['verified'].items() if not n.endswith('.safetensors')}
        result['cases']=corpus['cases']
        assert len(result['cases'])==4
        for case in result['cases']:
            ids=case['input_ids']
            assert isinstance(ids,list) and ids and all(type(t) is int and 0<=t<VOCAB for t in ids)
        assert len(next(c['input_ids'] for c in result['cases'] if c['name']=='long4000'))==4000
        json.dumps(result)
''' +s[z:];p.write_text(s)
(O/'check-token-result.py').write_text('''"""Enforce semantic success independently of remote task-launch exit status."""
import importlib.util,json,sys
from pathlib import Path
O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('tokens',O/'token-control.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=json.loads(Path(sys.argv[1]).read_text());corpus=json.loads((O/'prepared-corpus.json').read_text())
assert r['passed'] and r['cases']==corpus['cases']
assert set(r['stages'])=={'target-a','target-b'}
for stage in ['target-a','target-b']:
 rows=r['stages'][stage];assert len(rows)==4
 for case,row in zip(corpus['cases'],rows,strict=True):
  assert row['name']==case['name'] and row['request']['input_ids']==case['input_ids']
  assert m.observed(row['response'],len(case['input_ids']))==row['observed']
for a,b in zip(r['stages']['target-a'],r['stages']['target-b'],strict=True):
 assert a['request']==b['request'] and a['observed']==b['observed']
print('REAL_TOKEN_REFERENCE_GATE_PASSED')
''')
p=O/'topology-job.sh';s=p.read_text().replace('echo "TOKEN_DIAGNOSTIC_COMPLETE', 'python3 "$BUNDLE/check-token-result.py" "$ART/token-control.json"\necho "TOKEN_DIAGNOSTIC_COMPLETE');p.write_text(s)
p=O/'benchmark.pbs';p.write_text(p.read_text().replace('ap42-eagle3-token-control','ap42-token-reference-fixed').replace(C.name,O.name))
config=json.loads((O/'config.json').read_text());config.update(experiment=O.name,source_bundle=C.name,source_job='222752.pbs111',purpose='Repair failed real token reference with verified actual-image frozen corpus and independent semantic task gate',retry_of='222752.pbs111',retry_reason='Mapping/tokenizer API normalized in a cheaper actual-image gate; no template API dependency in full client',corpus_job=r['job'],task_result_gate='Head script requires actual valid passed artifact independent of task-launch status');(O/'config.json').write_text(json.dumps(config,indent=2)+'\n')
s=(C/'submit-pbs.py').read_text();s=s.replace("assert json.loads((O / 'validation.json').read_text())['passed']", "assert json.loads((O / 'validation.json').read_text())['passed']\nassert json.loads((O / 'corpus-prerequisite.json').read_text())['state']=='TOKENIZER_CORPUS_PASS'")
job=r['job'];s=s.replace("'222750.pbs111']","'222750.pbs111','222752.pbs111',"+repr(job)+"]").replace("{'222750.pbs111'}",'{'+repr(job)+'}').replace("dependency = '222750.pbs111'",'dependency = '+repr(job));(O/'submit-pbs.py').write_text(s)
shutil.copy2(C/'collect-terminal.py',O/'collect-terminal.py')
shutil.copy2(C/'validate-cpu.py',O/'validate-cpu.py')
p=O/'validate-cpu.py';s=p.read_text().replace("for name in ['worker.sh','nixl-conn.py']:","for name in ['worker.sh','nixl-conn.py']:");p.write_text(s)
files=sorted(set(files+['prepared-corpus.json','check-token-result.py']))
for p in O.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in list(O.glob('*.sh'))+[O/'benchmark.pbs']:subprocess.run(['bash','-n',str(p)],check=True)
assert 'AutoTokenizer' not in (O/'token-control.py').read_text()
assert (O/'worker.sh').read_bytes()==(C/'worker.sh').read_bytes()
assert (O/'nixl-conn.py').read_bytes()==(C/'nixl-conn.py').read_bytes()
(O/'SHA256SUMS').write_text(''.join(hashlib.sha256((O/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in files))
with tarfile.open(O/'payload.tar.gz','w:gz') as t:
 for n in files+['SHA256SUMS']:t.add(O/n,arcname=O.name+'/'+n)
# The frozen corpus is serializable and all observation-rejection fixtures still hold.
subprocess.run(['python3',str(O/'validate-cpu.py')],check=True)
# A successful task launcher cannot make a missing/failed result pass.
for name,data in [('absent',None),('failed',dict(passed=False,cases=[]))]:
 path=O/('fixture-'+name+'.json')
 if data is not None:path.write_text(json.dumps(data))
 result=subprocess.run(['python3',str(O/'check-token-result.py'),str(path)],capture_output=True,text=True)
 assert result.returncode!=0
 if path.exists():path.unlink()
(O/'validation.json').write_text(json.dumps(dict(passed=True,actual_corpus_job=job,scope='Actual-runtime corpus PASS, observation rejection fixtures, failed/missing semantic artifact rejection and unchanged serving/transport; real target reference still unverified',max_su=16*128*20/60,scored_benchmark=False),indent=2)+'\n')
print('Frozen corpus reference repair; no submission',O.name)
