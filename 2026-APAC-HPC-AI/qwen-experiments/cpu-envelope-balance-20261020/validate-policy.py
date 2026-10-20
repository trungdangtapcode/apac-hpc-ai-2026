"""CPU-only selection fixtures from the observed dual-NUMA CPU numbering."""
import importlib.util
import json
from pathlib import Path

O = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('envelope', O / 'worker-cpu-envelope.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cores = {cpu: (0 if cpu % 112 < 56 else 1, cpu % 112) for cpu in range(224)}
devices = [dict(uuid='GPU-fixture-' + str(i), nvml_index=i, numa_node=0 if i < 4 else 1,
                local_cpus=list(range(0, 56)) + list(range(112, 168)) if i < 4
                else list(range(56, 112)) + list(range(168, 224))) for i in range(8)]
allowed = set(range(224))
a, partitions = module.choose_balanced(allowed, devices, [d['uuid'] for d in devices[:4]], 32, cores)
b, _ = module.choose_balanced(allowed, devices, [d['uuid'] for d in devices[4:]], 32, cores)
c, _ = module.choose_balanced(allowed, devices, [d['uuid'] for d in devices], 64, cores)
assert a == list(range(32))
assert b == list(range(56, 88))
assert c == a + b and not set(a) & set(b)
# Interleaved CUDA order does not change UUID-selected, disjoint CPU partitions.
x, _ = module.choose_balanced(allowed, devices, [devices[i]['uuid'] for i in [0, 2, 4, 6]], 32, cores)
y, _ = module.choose_balanced(allowed, devices, [devices[i]['uuid'] for i in [1, 3, 5, 7]], 32, cores)
assert len(x) == len(y) == 32 and not set(x) & set(y)
assert len({cores[cpu] for cpu in c}) == 64
# Refuse an allocation that cannot supply the requested local core budget.
try:
    module.choose_balanced(set(range(64)), devices, [d['uuid'] for d in devices], 64, cores)
except AssertionError:
    refused = True
else:
    refused = False
assert refused
assert module.normal_uuid('GPU-Aa-bB') == module.normal_uuid('aabb')
(O / 'policy-validation.json').write_text(json.dumps(dict(passed=True, gpu_used=False,
    cases=['prefill NUMA 0 budget', 'prefill NUMA 1 budget', 'balanced decode budget',
           'interleaved CUDA UUID selection', 'disjoint role partitions', 'no SMT siblings',
           'insufficient allocation refused', 'CUDA UUID normalization'],
    observed_legacy_decode=list(range(64)), expected_balanced_decode=c), indent=2) + '\n')
print('CPU envelope selection fixtures PASS')
