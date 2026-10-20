"""Check actual read bounds, immutable input bytes and invalid manifest rejection."""
import hashlib, importlib.util, json, tempfile
from pathlib import Path
O = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('prefetch', O/'prefetch-weights.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='ap42-prefetch-fixture-') as tmp:
    root = Path(tmp)
    (root/'a.safetensors').write_bytes(b'A'*513)
    (root/'b.safetensors').write_bytes(b'B'*1025)
    index = root/'model.safetensors.index.json'
    index.write_text(json.dumps({'weight_map': {'a': 'a.safetensors', 'b': 'b.safetensors'}}))
    files, proof = m.manifest(root, minimum=0, maximum=2048)
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p,_ in files}
    reads = m.read_files(files, workers=2, block_bytes=127, budget_s=5)
    assert sum(x['bytes_read'] for x in reads) == proof['total_bytes'] == 1538
    assert before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p,_ in files}
    try: m.manifest(root, minimum=0, maximum=1000)
    except AssertionError: pass
    else: raise AssertionError('Oversized model accepted')
    index.write_text(json.dumps({'weight_map': {'a': '../outside.safetensors'}}))
    try: m.manifest(root, minimum=0)
    except AssertionError: pass
    else: raise AssertionError('Escaping shard accepted')
    try: m.read_files(files, workers=9)
    except AssertionError: pass
    else: raise AssertionError('Unbounded parallelism accepted')
(O/'prefetch-validation.json').write_text(json.dumps(dict(passed=True,actual_parallel_read_bytes=1538,input_bytes_unchanged=True,oversized_model_rejected=True,path_escape_rejected=True,excess_workers_rejected=True,scope='CPU read/manifest fixture only; actual allocated-node startup and cost still require jobs'),indent=2)+'\n')
print('Bounded read and negative fixtures pass')
