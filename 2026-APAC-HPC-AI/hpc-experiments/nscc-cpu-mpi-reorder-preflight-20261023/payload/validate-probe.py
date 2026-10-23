"""Validate actual MPI_COMM_WORLD and affinity records for the four-rank probe."""
import argparse
import json
from collections import Counter
from pathlib import Path
import re


def normalize_host(value):
    return value.strip().split('.', 1)[0]


def read_nodefile(path):
    hosts = [normalize_host(x) for x in Path(path).read_text().splitlines() if x.strip()]
    assert len(hosts) == 4, ('PBS nodefile must expose four slots', len(hosts))
    counts = Counter(hosts)
    assert len(counts) == 1 and list(counts.values()) == [4], ('expected one four-slot host', counts)
    return hosts[0]


def read_records(path):
    records = []
    for line in Path(path).read_text(errors='replace').splitlines():
        marker = 'PROBE_JSON\t'
        if marker not in line:
            continue
        records.append(json.loads(line.split(marker, 1)[1]))
    ranks = [x['rank'] for x in records]
    assert len(records) == 4 and sorted(ranks) == [0, 1, 2, 3], ('MPI_COMM_WORLD rank set', ranks)
    assert all(x['world_size'] == 4 for x in records), 'MPI_COMM_WORLD size must be four'
    return {x['rank']: x for x in records}


def topology(cpu, sysfs_root):
    base = Path(sysfs_root) / 'devices/system/cpu' / ('cpu%d' % cpu) / 'topology'
    package = int((base / 'physical_package_id').read_text().strip())
    core = int((base / 'core_id').read_text().strip())
    return package, core


def enrich(records, expected_host, sysfs_root):
    out = {}
    for rank, row in records.items():
        host = normalize_host(row['processor_name'])
        assert host == expected_host, ('MPI processor differs from PBS allocation host', rank, host, expected_host)
        cpus = row['affinity_cpus']
        assert isinstance(cpus, list) and len(cpus) == 1, ('expected single logical CPU affinity', rank, cpus)
        assert isinstance(cpus[0], int) and cpus[0] >= 0
        physical = topology(cpus[0], sysfs_root)
        out[rank] = {'host': host, 'cpu': cpus[0], 'physical_core': physical,
                     'pmi_rank_diagnostic': row.get('pmi_rank')}
    logical = [(x['host'], x['cpu']) for x in out.values()]
    physical = [(x['host'], x['physical_core']) for x in out.values()]
    assert len(set(logical)) == 4, ('logical CPU reused', logical)
    assert len(set(physical)) == 4, ('physical core reused', physical)
    return out


def validate(identity_path, candidate_path, nodefile_path, sysfs_root='/sys'):
    alloc_host = read_nodefile(nodefile_path)
    identity = enrich(read_records(identity_path), alloc_host, sysfs_root)
    candidate = enrich(read_records(candidate_path), alloc_host, sysfs_root)
    order = [0, 2, 1, 3]
    assert sorted(order) == [0, 1, 2, 3] and order[0] == 0
    inverse = {rank: slot for slot, rank in enumerate(order)}
    comparisons = []
    for candidate_rank in range(4):
        control_slot = inverse[candidate_rank]
        expected = identity[control_slot]
        actual = candidate[candidate_rank]
        assert (actual['host'], actual['cpu'], actual['physical_core']) == \
               (expected['host'], expected['cpu'], expected['physical_core']), (
                   'candidate rank does not occupy expected control slot', candidate_rank, control_slot, actual, expected)
        comparisons.append({'candidate_mpi_rank': candidate_rank, 'control_slot_index': control_slot,
                            'host': actual['host'], 'logical_cpu': actual['cpu'],
                            'physical_package_core': list(actual['physical_core'])})
    assert (candidate[0]['host'], candidate[0]['cpu'], candidate[0]['physical_core']) == \
           (identity[0]['host'], identity[0]['cpu'], identity[0]['physical_core']), \
           'rank zero must remain in first slot'
    return {'passed': True, 'world_size': 4, 'pbs_slots': 4, 'allocation_host': alloc_host,
            'identity_unique_physical_cores': 4, 'candidate_unique_physical_cores': 4,
            'candidate_order_file_sequence': order,
            'mapping_rule': 'candidate MPI rank r must occupy identity control slot order.index(r)',
            'candidate_slot_checks': comparisons,
            'pmi_rank_policy': 'recorded for diagnostics only; MPI_Comm_rank is authoritative'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('identity')
    ap.add_argument('candidate')
    ap.add_argument('nodefile')
    ap.add_argument('--sysfs-root', default='/sys')
    ap.add_argument('--output')
    args = ap.parse_args()
    result = validate(args.identity, args.candidate, args.nodefile, args.sysfs_root)
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
