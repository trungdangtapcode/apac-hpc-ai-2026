"""Select a bounded task CPU envelope before model launch inside its allocation.

Both modes perform identical GPU/CPU metadata queries. Actual CUDA UUIDs select
devices; NVML indices only provide a deterministic order for partitioning CPU
IDs among the node's GPUs. No host memory policy or SGLang argument is changed.
"""
import csv
import datetime
import io
import json
import os
from pathlib import Path
import re
import subprocess


def expand(text):
    result = set()
    for item in text.split(','):
        if item:
            values = [int(x) for x in item.split('-')]
            result.update(range(values[0], values[-1] + 1))
    return result


def normal_uuid(value):
    if isinstance(value, bytes):
        value = value.hex()
    return str(value).strip().lower().removeprefix('gpu-').replace('-', '')


def choose_balanced(allowed, devices, selected_uuids, budget, core_map):
    assert selected_uuids and len(set(selected_uuids)) == len(selected_uuids)
    assert budget % len(selected_uuids) == 0
    per_gpu = budget // len(selected_uuids)
    groups = {}
    for device in devices:
        assert device['numa_node'] >= 0
        groups.setdefault(device['numa_node'], []).append(device)
    partitions = {}
    for node, group in sorted(groups.items()):
        group.sort(key=lambda device: (device['nvml_index'], device['uuid']))
        local = set.intersection(*(set(device['local_cpus']) for device in group)) & set(allowed)
        representatives = []
        seen = set()
        for cpu in sorted(local):
            assert cpu in core_map, ('Missing physical-core metadata', cpu)
            if core_map[cpu] not in seen:
                representatives.append(cpu)
                seen.add(core_map[cpu])
        required = per_gpu * len(group)
        assert len(representatives) >= required, ('Insufficient scheduler-allowed local cores', node, len(representatives), required)
        for position, device in enumerate(group):
            partitions[device['uuid']] = representatives[position * per_gpu:(position + 1) * per_gpu]
    chosen = sorted({cpu for uuid in selected_uuids for cpu in partitions[uuid]})
    assert len(chosen) == budget and set(chosen) <= set(allowed)
    assert len({core_map[cpu] for cpu in chosen}) == budget
    return chosen, partitions


def apply_envelope(role):
    count = int(os.environ['QWEN_TASK_GPU_COUNT'])
    if count == 0:
        return
    assert re.fullmatch(r'(prefill|decode)-[0-9]+', role)
    mode = os.environ['QWEN_CPU_ENVELOPE_MODE']
    assert mode in {'legacy', 'balanced'}
    budget = int(os.environ['QWEN_TASK_CPU_BUDGET'])
    allocation = expand(os.environ['QWEN_ALLOCATION_CPU_MASK'])
    available = set(os.sched_getaffinity(0))
    assert available <= allocation and available
    legacy = sorted(expand(os.environ['QWEN_LEGACY_TASK_CPU_MASK']))
    assert len(legacy) == budget and set(legacy) <= available

    import torch
    torch.set_num_threads(1)
    assert torch.cuda.device_count() == count
    cuda_uuids = [normal_uuid(torch.cuda.get_device_properties(i).uuid) for i in range(count)]
    result = subprocess.run(['nvidia-smi', '--query-gpu=index,uuid,pci.bus_id',
                             '--format=csv,noheader,nounits'], capture_output=True,
                            text=True, check=True, timeout=8)
    devices = []
    for ordinal, uuid, pci in csv.reader(io.StringIO(result.stdout)):
        pci = pci.strip().lower()[-12:]
        folder = Path('/sys/bus/pci/devices') / pci
        devices.append(dict(nvml_index=int(ordinal), uuid=uuid.strip(), pci=pci,
                            numa_node=int((folder / 'numa_node').read_text()),
                            local_cpus=sorted(expand((folder / 'local_cpulist').read_text().strip()))))
    assert len(devices) == 8, 'This experiment requires the allocated full eight-GPU node'
    selected = []
    for value in cuda_uuids:
        matches = [device['uuid'] for device in devices if normal_uuid(device['uuid']) == value]
        assert len(matches) == 1, 'CUDA UUID cannot be matched unambiguously to NVML'
        selected.append(matches[0])
    cpu_info = subprocess.run(['lscpu', '-p=CPU,CORE,SOCKET,NODE'], capture_output=True,
                              text=True, check=True, timeout=8)
    core_map = {}
    for line in cpu_info.stdout.splitlines():
        if not line or line.startswith('#'):
            continue
        cpu, core, socket, node = map(int, line.split(','))
        core_map[cpu] = (socket, core)
    assert len({core_map[cpu] for cpu in legacy}) == budget, 'Legacy task must also have one hardware thread per core for this comparison'
    balanced, partitions = choose_balanced(available, devices, selected, budget, core_map)
    chosen = legacy if mode == 'legacy' else balanced
    os.sched_setaffinity(0, chosen)
    assert set(os.sched_getaffinity(0)) == set(chosen)
    receipt = dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   host=os.uname().nodename, role=role, mode=mode, cpu_budget=budget,
                   allocation_cpu_ids=sorted(allocation), available_before=sorted(available),
                   legacy_cpu_ids=legacy, balanced_cpu_ids=balanced, applied_cpu_ids=chosen,
                   selected_cuda_gpu_uuids=selected, gpu_local_partitions=partitions,
                   devices=devices, physical_cores_selected=len({core_map[cpu] for cpu in chosen}),
                   memory_policy_changed=False, native_sglang_numa_binding_changed=False,
                   model_arguments_changed=False, metadata_only_cuda_queries=True)
    directory = Path(os.environ['QWEN_ARTDIR']) / 'cpu-envelope'
    directory.mkdir(exist_ok=True)
    target = directory / (role + '.json')
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(receipt, indent=2) + '\n')
    temporary.replace(target)
    print('CPU_ENVELOPE_PREFLIGHT_PASS', json.dumps(dict(role=role, mode=mode,
          cpu_budget=budget, applied_cpu_ids=chosen, selected_gpu_uuids=selected)), flush=True)
