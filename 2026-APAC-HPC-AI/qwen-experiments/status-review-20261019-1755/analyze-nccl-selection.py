"""Review NCCL's actual TUNING decisions instead of representative kernel names."""
from pathlib import Path
import ast
import collections
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PATTERN = re.compile(r'\[(\d+)\] NCCL INFO (\w+): (\d+) Bytes -> Algo (\w+) proto (LL128|LL|SIMPLE)\b')
rows = []
for job in ['221884', '221885']:
    receipt = ROOT / 'research-followup-20261019-1720' / ('collect-' + job + '.json')
    snapshot = Path(json.loads(receipt.read_text())['destination'])
    seal = json.loads((snapshot / 'evidence-sha256.json').read_text())
    for path in sorted((snapshot / 'runs' / (job + '.pbs111')).glob('task-prefill-*-node*.log')):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == seal[str(path.relative_to(snapshot))]
        lines = [line for line in path.read_text().splitlines() if 'Bytes -> Algo' in line]
        counts = collections.Counter()
        protocols = collections.Counter()
        ranks = set()
        for line in lines:
            match = PATTERN.search(line)
            if match:
                rank, collective, size, algorithm, protocol = match.groups()
                ranks.add(int(rank))
                counts[(collective, int(size), algorithm, protocol)] += 1
                protocols[protocol] += 1
        assert counts and ranks == {0}
        if job == '221885':
            assert set(protocols) == {'SIMPLE'}
        rows.append(dict(job=job, source_log=str(path), sha256=digest,
                         observed_selection_lines=len(lines), parsed_lines=sum(counts.values()),
                         unparsed_lines=len(lines)-sum(counts.values()), communicator_ranks_logged=sorted(ranks),
                         protocol_counts=dict(protocols),
                         by_size=[dict(collective=k[0], bytes=k[1], algorithm=k[2], protocol=k[3], count=v)
                                  for k, v in sorted(counts.items())], examples=lines[:5]))
        print(job, path.name, dict(protocols), 'unparsed', rows[-1]['unparsed_lines'])
(OUT / 'nccl-selection-log-review.json').write_text(json.dumps(dict(
    jobs=rows, interpretation='Sealed NCCL TUNING decisions for communicator rank zero. Interleaved/truncated records are counted as unparsed and never treated as protocol decisions. Logs cover run lifetime; records are not labelled as every ranked N54 call. GPU symbol names do not identify the selected protocol.'), indent=2) + '\n')

source = OUT / 'nccl-2.28.9-source/src/device/generate.py'
tree = ast.parse(source.read_text())
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name in {'best_kernel', 'equivalent_primary'}]
context = {'func_filter': lambda *args: True}
exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), 'exec'), context)
cases = []
for algorithm in ['TREE', 'RING']:
    for protocol in ['LL', 'LL128', 'SIMPLE']:
        result = context['best_kernel']('AllReduce', 'Sum', 'bf16', algorithm, protocol)
        assert result == ('AllReduce', 'Sum', 'bf16', algorithm, 'LL')
        cases.append(dict(algorithm=algorithm, protocol=protocol, representative=list(result)))
(OUT / 'representative-kernel-validation.json').write_text(json.dumps(dict(
    passed=True, source_tag='v2.28.9-1', source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    cases=cases, limitation='Exact tagged upstream source, not a binary provenance match or per-call runtime proof.'), indent=2) + '\n')
