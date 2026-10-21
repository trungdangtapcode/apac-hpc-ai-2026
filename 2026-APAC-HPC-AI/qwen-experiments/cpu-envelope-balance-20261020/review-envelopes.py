"""Verify sealed applied CPU envelopes and actual GPU scheduler thread masks."""
from pathlib import Path
import collections
import hashlib
import json

O = Path(__file__).resolve().parent

def cpu_ids(text):
    result = set()
    for part in text.split(','):
        ends = part.split('-')
        if len(ends) == 1:
            result.add(int(ends[0]))
        else:
            result.update(range(int(ends[0]), int(ends[1]) + 1))
    return result

results = []
for number, mode in [('222551', 'legacy'), ('222552', 'balanced')]:
    snapshot = Path(json.loads((O / f'collect-{number}.json').read_text())['destination'])
    run = snapshot / 'runs' / f'{number}.pbs111'
    seal = json.loads((snapshot / 'evidence-sha256.json').read_text())
    def read(path):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == seal[str(path.relative_to(snapshot))]
        return json.loads(path.read_text())
    roles = {}
    uuids = set()
    for role, expected, budget in [('prefill-0', 4, 32), ('prefill-1', 4, 32), ('decode-0', 8, 64)]:
        envelope = read(run / f'cpu-envelope/{role}.json')
        assert envelope['mode'] == mode
        chosen = set(envelope['applied_cpu_ids'])
        assert len(chosen) == envelope['cpu_budget'] == envelope['physical_cores_selected'] == budget
        assert chosen == set(envelope[f'{mode}_cpu_ids'])
        assert chosen <= set(envelope['allocation_cpu_ids'])
        capture = read(run / f'worker-locality/{role}.ready.json')
        assert capture['state'] == 'CAPTURE_COMPLETE'
        data = capture['snapshot']
        assert not data['ambiguous_gpu_pid_matches'] and not data['thread_capture_truncated']
        devices = {d['uuid']: d for d in data['visible_devices']}
        matched = data['matched_gpu_processes']
        assert len(matched) == expected
        mapping = {row['process_pid']: row['gpu_uuid'] for row in matched}
        assert len(mapping) == expected and len(set(mapping.values())) == expected
        assert set(mapping.values()) == set(envelope['selected_cuda_gpu_uuids'])
        assert not uuids & set(mapping.values())
        uuids.update(mapping.values())
        processes = {p['pid']: p for p in data['processes']}
        schedulers = []
        for pid, uuid in mapping.items():
            process = processes[pid]
            assert process['name'] == 'sglang::schedul'
            local = cpu_ids(devices[uuid]['local_cpulist'])
            expected_mask = chosen & local
            assert expected_mask and set(process['allowed_cpus']) == expected_mask
            assert all(cpu_ids(mask) == expected_mask for mask in process['thread_mask_counts'])
            schedulers.append(dict(pid=pid, gpu_uuid=uuid, numa_node=devices[uuid]['numa_node'],
                                   allowed_cpus=process['allowed_cpus'],
                                   thread_mask_counts=process['thread_mask_counts']))
        other = collections.Counter()
        for process in data['processes']:
            if process['pid'] not in mapping:
                other.update(process['thread_mask_counts'])
        roles[role] = dict(host=envelope['host'], applied_cpu_ids=sorted(chosen),
                           physical_core_count=envelope['physical_cores_selected'],
                           scheduler_count=len(schedulers), schedulers=schedulers,
                           non_gpu_process_thread_masks=dict(other),
                           pre_score_capture_s=capture['snapshot_duration_s'])
    assert len(uuids) == 16
    results.append(dict(job=f'{number}.pbs111', mode=mode, mapping_pass=True, roles=roles))
assert results[0]['roles']['prefill-0']['applied_cpu_ids'] == results[1]['roles']['prefill-0']['applied_cpu_ids']
for role in ['prefill-1', 'decode-0']:
    assert results[0]['roles'][role]['applied_cpu_ids'] != results[1]['roles'][role]['applied_cpu_ids']
output = dict(passed=True, jobs=results,
              scope='Sealed pre-score applied envelopes and GPU scheduler/thread masks; not scored per-thread demand',
              limits=['Some non-GPU parent threads retain the full allocation mask; their placement is recorded separately.',
                      'All GPU scheduler masks are checked against the actual selected envelope and GPU-local CPU IDs.',
                      'Scored per-thread demand, NUMA memory placement and CPU critical-path saturation were not collected.',
                      'A more symmetric envelope is not proof of a causal serving speedup.'])
(O / 'envelope-review.json').write_text(json.dumps(output, indent=2) + '\n')
print('Actual intended equal-budget change verified across 16 GPU schedulers in each job')
