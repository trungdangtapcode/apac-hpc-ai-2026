"""Give each isolated process writable dependency caches without changing HOME."""
import os
from pathlib import Path


def configure(rank, parent=None):
    job = os.environ.get('PBS_JOBID', os.environ.get('SLURM_JOB_ID', 'local'))
    root = Path(parent or '/tmp') / ('apac-fp8-' + job + '-' + str(rank))
    routes = {
        'FLASHINFER_WORKSPACE_BASE': root / 'flashinfer',
        'TRITON_CACHE_DIR': root / 'triton',
        'TORCHINDUCTOR_CACHE_DIR': root / 'inductor',
        'TORCH_EXTENSIONS_DIR': root / 'torch-extensions',
        'SGLANG_DG_CACHE_DIR': root / 'deepgemm',
        'DG_CACHE_DIR': root / 'deepgemm',
        'DG_JIT_CACHE_DIR': root / 'deepgemm',
        'CUDA_CACHE_PATH': root / 'cuda',
        'XDG_CACHE_HOME': root / 'xdg',
    }
    for path in set(routes.values()):
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        probe = path / '.write-probe'
        probe.write_bytes(b'cache-write-check')
        assert probe.read_bytes() == b'cache-write-check'
        probe.unlink()
    os.environ.update({key: str(path) for key, path in routes.items()})
    os.environ['SGLANG_JIT_DEEPGEMM_COMPILE_WORKERS'] = '1'
    return {key: str(path) for key, path in routes.items()}
