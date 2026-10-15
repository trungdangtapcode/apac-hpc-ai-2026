"""Exercise the real preflight on tiny assets, including same-size corruption."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parent
results=[]
with tempfile.TemporaryDirectory(prefix='ap42-assets-') as tmp:
    root=Path(tmp);model=root/'model';model.mkdir();inspection=root/'inspection';inspection.mkdir()
    shutil.copyfile(ROOT/'check-assets.py',root/'check-assets.py')
    files={'config.json':b'{}','model.safetensors.index.json':b'{"weight_map":{"weight":"shard"}}','shard':b'weights'}
    for name,data in files.items():(model/name).write_bytes(data)
    siblings=[dict(rfilename=n,size=len(b),lfs={'sha256':hashlib.sha256(b).hexdigest()}) for n,b in files.items()]
    revision='a'*40
    (inspection/'official-model-metadata.json').write_text(json.dumps(dict(sha=revision,siblings=siblings)))
    image=root/'image';image.write_bytes(b'image')
    cache=root/'cache/models--Qwen--Qwen3-235B-A22B-Instruct-2507';(cache/'refs').mkdir(parents=True)
    (cache/'refs/main').write_text(revision);(cache/'snapshots'/revision).mkdir(parents=True)
    (cache/'snapshots'/revision/'tokenizer.json').write_text('{}')
    contract=dict(model_path=str(model),model_config_canonical_sha256=hashlib.sha256(b'{}').hexdigest(),tokenizer_cache=str(root/'cache'),images={'test':dict(path=str(image),bytes=5,sha256=hashlib.sha256(b'image').hexdigest())})
    (root/'asset-contract.json').write_text(json.dumps(contract))
    status=dict(revision=revision,complete=True,errors={},verified={s['rfilename']:dict(bytes=s['size'],sha256=s['lfs']['sha256']) for s in siblings})
    def run(name,ready):
        (root/'model-transfer-status.json').write_text(json.dumps(status))
        p=subprocess.run(['python3',str(root/'check-assets.py')],capture_output=True,text=True)
        actual=json.loads(p.stdout)
        assert actual['ready'] is ready and p.returncode==(0 if ready else 2),(name,p.stdout,p.stderr)
        results.append(dict(case=name,expected_ready=ready,passed=True))
    run('fully verified assets',True)
    status['complete']=False;run('download still hashing',False);status['complete']=True
    (model/'shard').write_bytes(b'w');run('truncated shard',False);(model/'shard').write_bytes(b'weights')
    status['verified']['shard']['sha256']='0'*64;run('wrong official shard digest in manifest',False)
    status['verified']['shard']['sha256']=hashlib.sha256(b'weights').hexdigest()
    image.write_bytes(b'wrong');run('same-size corrupted image',False)
report=dict(passed=True,scope='CPU fixture checks of submission asset preflight; no GPU runtime claim',cases=results)
(ROOT/'asset-preflight-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Asset preflight:',len(results),'cases passed')
