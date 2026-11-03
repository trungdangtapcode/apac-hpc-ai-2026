from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, shutil, subprocess, tarfile, tempfile
D = Path(__file__).resolve().parent
build = json.loads((D / 'BUILD.json').read_text())
repo = 'trungdangtapcode/apac-hpc-ai-research'
archive = Path('/home/apacsc42/apac-hpc-ai-research')
temp = Path(tempfile.mkdtemp(prefix='ap42-quality-offhost-v4-'))
subprocess.run(['gh','release','download','quality-evidence-20261103-v4','--repo',repo,'--pattern',build['bundle_file'],'--dir',str(temp)],check=True)
bundle = temp / build['bundle_file']
assert bundle.stat().st_size == build['bundle_bytes']
assert hashlib.sha256(bundle.read_bytes()).hexdigest() == build['bundle_sha256']
store = temp / 'scoped-store'; store.mkdir()
z = subprocess.Popen(['zstd','-q','-d','-c',str(bundle)],stdout=subprocess.PIPE)
names = set()
with tarfile.open(fileobj=z.stdout, mode='r|') as t:
    for member in t:
        name = member.name
        assert member.isfile() and not Path(name).is_absolute() and '..' not in Path(name).parts
        assert name not in names; names.add(name)
        assert name in {'manifest.jsonl','objects-index.json','SCOPE.json'} or (name.startswith('objects/') and name.endswith('.zst'))
        path = store / name; path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as f: shutil.copyfileobj(t.extractfile(member),f)
assert z.wait() == 0
index = json.loads((store/'objects-index.json').read_text())
assert names == {'manifest.jsonl','objects-index.json','SCOPE.json'} | {r['object'] for r in index}
for r in index:
    path = store / r['object']; assert path.stat().st_size == r['stored_bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == r['stored_sha256']
scope = json.loads((store/'SCOPE.json').read_text()); assert scope['archive_head'] == build['archive_head']
with (store/'manifest.jsonl').open() as f: rows = [json.loads(l) for l in f if l.strip()]
worktree = temp/'captured-git'; restored = temp/'restored'
# Materialise only the selected committed Git blobs; do not check out unrelated research.
worktree.mkdir()
inline = ['tools/restore_snapshot.py','backup/manifest.jsonl'] + [r['path'] for r in rows if r['storage']=='git']
for rel in sorted(set(inline)):
    out = worktree/rel; out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as f:
        subprocess.run(['git','-C',str(archive),'cat-file','blob',build['archive_head']+':'+rel],stdout=f,check=True)
try:
    cmd = ['python3',str(worktree/'tools/restore_snapshot.py'),'--store',str(store),'--destination',str(restored)]
    for r in rows: cmd += ['--path',r['path']]
    result = subprocess.run(cmd,check=True,capture_output=True,text=True)
    restored_info = json.loads(result.stdout)
    S = restored/'2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102'
    subprocess.run(['python3',str(S/'workflow/restore_required_bytecode.py')],check=True)
    frozen = json.loads((S/'frozen-full8/FROZEN_PAYLOAD.json').read_text())
    for r in frozen['files']: assert hashlib.sha256((S/r['path']).read_bytes()).hexdigest() == r['sha256']
    code = json.loads((S/'workflow/CODE_GUARD.json').read_text())
    for r in code['files']: assert hashlib.sha256((S/r['path']).read_bytes()).hexdigest() == r['sha256']
    spec = importlib.util.spec_from_file_location('restored_quality_aggregate',S/'client/aggregate_full.py')
    agg = importlib.util.module_from_spec(spec); spec.loader.exec_module(agg)
    expected,cs,ps = agg.validate_prepared(S/'prepared-4k/prepare-manifest.json',S/'prepared-4k/compiled-corpus.jsonl')
    scores = []
    all_runs = [
      ('reference',0,28373,S/'jobs/full-ref-00of08/runs/28373/reference/evaluation'),
      ('reference',1,28382,S/'jobs/full-ref-01of08/runs/28382/reference/evaluation'),
      ('reference',2,28386,S/'jobs/full-ref-02of08/runs/28386/reference/evaluation'),
      ('reference',3,28390,S/'jobs/full-ref-03of08/runs/28390/reference/evaluation'),
      ('reference',4,28394,S/'jobs/full-ref-04of08/runs/28394/reference/evaluation'),
      ('reference',5,28398,S/'jobs/full-ref-05of08/runs/28398/reference/evaluation'),
      ('reference',6,28402,S/'jobs/full-ref-06of08/runs/28402/reference/evaluation'),
      ('reference',7,28406,S/'jobs/full-ref-07of08/runs/28406/reference/evaluation'),
      ('candidate',0,28375,S/'jobs/full-cand-00of08/AI_Task/logs/full-shards/28375/evaluation'),
      ('candidate',1,28384,S/'jobs/full-cand-01of08/AI_Task/logs/full-shards/28384/evaluation'),
      ('candidate',2,28388,S/'jobs/full-cand-02of08/AI_Task/logs/full-shards/28388/evaluation'),
      ('candidate',3,28392,S/'jobs/full-cand-03of08/AI_Task/logs/full-shards/28392/evaluation'),
      ('candidate',4,28396,S/'jobs/full-cand-04of08/AI_Task/logs/full-shards/28396/evaluation'),
      ('candidate',5,28400,S/'jobs/full-cand-05of08/AI_Task/logs/full-shards/28400/evaluation'),
      ('candidate',6,28404,S/'jobs/full-cand-06of08/AI_Task/logs/full-shards/28404/evaluation'),
      ('candidate',7,28408,S/'jobs/full-cand-07of08/AI_Task/logs/full-shards/28408/evaluation')]
    for role,shard,job,path in all_runs:
        run=json.loads((path/'run.json').read_text())
        got=agg.aggregate_role([path],{q:expected[q] for q in run['selected_question_ids']},cs,ps)
        scores.append(dict(role=role,shard=shard,job=job,questions=got['n'],correct=got['correct'],service_errors=got['service_errors']))
    assert [r['correct'] for r in scores] == [1200, 1206, 1166, 1175, 1211, 1149, 1156, 1197, 1205, 1204, 1167, 1166, 1203, 1153, 1169, 1185]
    full = agg.aggregate(S/'prepared-4k/prepare-manifest.json',S/'prepared-4k/compiled-corpus.jsonl',[p for role,shard,job,p in all_runs if role=='reference'],[p for role,shard,job,p in all_runs if role=='candidate'])
    assert full['reference']['correct'] == 9460 and full['candidate']['correct'] == 9452
    assert full['status'] == 'LOCAL_FULLSET_GATE_PASS'
    (D/'RESTORED_FULL_COMPARISON.json').write_text(json.dumps(full,indent=2)+'\n')
    receipt = dict(verified_utc=datetime.now(timezone.utc).isoformat(),passed=True,repo=repo,release_tag='quality-evidence-20261103-v4',bundle_file=build['bundle_file'],bundle_sha256=build['bundle_sha256'],bundle_bytes=build['bundle_bytes'],archive_head=build['archive_head'],download_hash_verified=True,external_objects_verified=len(index),restored_source_files=restored_info['selected_paths'],original_frozen_files_verified=len(frozen['files']),additional_code_guard_files_verified=len(code['files']),required_bytecode_restored=16,replayed_scores=scores,full_comparison=full['comparison'],scope='Complete local quality study with all sixteen full-set runs and retained pilots. Model weights, runtime images, other research objects and official certification are excluded.',temporary_check_directory=str(temp))
    (D/'OFFHOST_RESTORE_VERIFIED.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
finally:
    pass  # Keep the isolated verification directory; no live Git worktree was created.
