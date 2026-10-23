"""Run the actual node shell around mocked containers; no scheduler/GPU access."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

here = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    fake_bin = root / 'bin'
    fake_bin.mkdir()
    singularity = fake_bin / 'singularity'
    singularity.write_text('#!/bin/sh\nexit "$FIXTURE_CONTAINER_STATUS"\n')
    singularity.chmod(0o755)
    for code in (0, 17):
        art = root / f'art-{code}'
        exchange = root / f'exchange-{code}'
        art.mkdir()
        exchange.mkdir()
        (exchange / 'component-start.json').write_text(json.dumps(dict(t0_epoch_s=int(time.time()))))
        env = dict(os.environ, PATH=str(fake_bin) + ':' + os.environ['PATH'],
                   CUDA_VISIBLE_DEVICES='GPU-fixture-only', FIXTURE_CONTAINER_STATUS=str(code),
                   TMPDIR=str(root), **{'BASH_FUNC_module%%': '() { return 0; }'})
        result = subprocess.run(['bash', str(here / 'node-entry.sh'), '0', str(here), str(art),
                                 str(exchange)], env=env, text=True, capture_output=True, timeout=15)
        assert result.returncode == code, result.stderr
        node = json.loads((art / 'rank0-node-exit.json').read_text())
        assert node['container_returncode'] == node['final_returncode'] == code
        assert node['cleanup_returncode'] == 0 and node['cleanup_deleted'] is True
        assert not list(root.glob('ap42-exit-boundary.*'))
print('PASS: actual node shell preserves mocked container exit0/exit17 and records bounded cleanup')
