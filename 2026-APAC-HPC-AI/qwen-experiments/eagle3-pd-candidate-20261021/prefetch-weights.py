"""Bounded per-node page-cache preparation; never changes model files or GPU state."""
import argparse, concurrent.futures, datetime, hashlib, json, os, socket, time
from pathlib import Path


def manifest(model, minimum=200 * 1024**3, maximum=300 * 1024**3):
    model = Path(model)
    index = model / 'model.safetensors.index.json'
    names = sorted(set(json.loads(index.read_text())['weight_map'].values()))
    assert 1 <= len(names) <= 128
    assert all(isinstance(n, str) and Path(n).name == n and n.endswith('.safetensors') for n in names)
    files = [(model / name, (model / name).stat().st_size) for name in names]
    assert all(size > 0 for _, size in files)
    total = sum(size for _, size in files)
    assert minimum <= total <= maximum, (total, minimum, maximum)
    return files, dict(index_sha256=hashlib.sha256(index.read_bytes()).hexdigest(),
                       shards=[dict(name=p.name, bytes=n) for p, n in files], total_bytes=total)


def read_files(files, workers=8, block_bytes=16 * 1024**2, budget_s=120):
    assert 1 <= workers <= 8 and 0 < block_bytes <= 16 * 1024**2 and budget_s > 0
    deadline = time.monotonic() + budget_s
    def read_one(item):
        path, expected = item
        count = 0
        with path.open('rb', buffering=0) as stream:
            while True:
                if time.monotonic() >= deadline:
                    raise TimeoutError('Bounded shard-read deadline exceeded')
                chunk = stream.read(block_bytes)
                if not chunk:
                    break
                count += len(chunk)
        assert count == expected
        return dict(name=path.name, bytes_read=count)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(read_one, files))


def meminfo():
    keys = {'MemAvailable', 'Cached', 'Buffers'}
    return {line.split(':')[0]: line.split(':', 1)[1].strip()
            for line in Path('/proc/meminfo').read_text().splitlines()
            if line.split(':')[0] in keys}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode', choices=['off', 'read'], required=True)
    p.add_argument('--model', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    start = time.monotonic()
    report = dict(mode=a.mode, host=socket.gethostname(), started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  model=str(a.model), helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  workers=8, max_block_bytes=16 * 1024**2, internal_read_budget_s=120,
                  memory_before=meminfo(), completed=False, model_files_modified=False,
                  limitations='No cache flush or initial page-residency measurement. Logical reads and node cache counters do not prove cold physical storage reads.')
    try:
        files, proof = manifest(a.model)
        report.update(proof)
        report['reads'] = read_files(files) if a.mode == 'read' else []
        report['completed'] = True
    finally:
        report.update(elapsed_s=time.monotonic() - start, memory_after=meminfo(), ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(report, indent=2) + '\n')
    print('STARTUP_PREFETCH_COMPLETED', a.mode, report['elapsed_s'], flush=True)


if __name__ == '__main__':
    main()
