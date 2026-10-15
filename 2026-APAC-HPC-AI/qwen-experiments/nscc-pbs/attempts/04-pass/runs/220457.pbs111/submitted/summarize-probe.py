import json
from pathlib import Path
import sys

directory=Path(sys.argv[1]);paths=sorted(directory.glob('*.gpu.json'))
assert len(paths)==2, f'Need two node results, got {paths}'
nodes=[json.loads(path.read_text()) for path in paths]
assert len({node['host'] for node in nodes})==2
assert all(node['passed'] and len(node['gpus'])==8 for node in nodes)
summary=dict(passed=True,scope='Two-node PBS allocation, 16 H100 GPUs, Singularity and tiny FP16 GEMM only',
             qwen_benchmark_completed=False,gpu_count=16,nodes=nodes)
(directory/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(dict(passed=True,gpu_count=16,nodes=[node['host'] for node in nodes])))
