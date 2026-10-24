"""Shared parsing and structural checks for the source mapping and MPI records."""
import hashlib
import json
from collections import Counter
from pathlib import Path

RANKS = 512
HOSTS = 4
RANKS_PER_HOST = 128
DOMAINS_PER_HOST = 8
RANKS_PER_DOMAIN = 16


def normalize_host(value):
    return value.strip().split('.', 1)[0]


def read_assignment(path):
    data = json.loads(Path(path).read_text())
    mapping = data['mapping']
    encoded = json.dumps(mapping, sort_keys=True, separators=(',', ':')).encode('utf-8')
    assert hashlib.sha256(encoded).hexdigest() == data['refinement_sha256'], 'refined assignment hash mismatch'
    assert data['host_count'] == HOSTS and data['ranks_per_host'] == RANKS_PER_HOST
    assert data['logical_numa_groups_per_host'] == DOMAINS_PER_HOST
    assert data['ranks_per_logical_numa_group'] == RANKS_PER_DOMAIN
    assert mapping['rank_zero_first'] is True
    groups = mapping['numa_group_members_by_host']
    assert len(groups) == HOSTS and all(len(host) == DOMAINS_PER_HOST for host in groups)
    flattened = []
    rank_host = [None] * RANKS
    rank_domain = [None] * RANKS
    for host_group, host_groups in enumerate(groups):
        for domain, ranks in enumerate(host_groups):
            assert len(ranks) == RANKS_PER_DOMAIN, (host_group, domain, len(ranks))
            for rank in ranks:
                assert isinstance(rank, int) and 0 <= rank < RANKS
                assert rank_host[rank] is None, ('duplicate assignment rank', rank)
                rank_host[rank] = host_group
                rank_domain[rank] = domain
                flattened.append(rank)
    assert sorted(flattened) == list(range(RANKS))
    assert rank_host == mapping['rank_to_host']
    assert rank_domain == mapping['rank_to_logical_numa_group_within_host']
    assert mapping['full_rank_permutation_host_numa_group_major'] == flattened
    assert groups[0][0][0] == 0, 'rank zero must lead logical host/group zero'
    return data


def read_nodefile(path):
    hosts = [normalize_host(x) for x in Path(path).read_text().splitlines() if x.strip()]
    counts = Counter(hosts)
    assert len(hosts) == RANKS and len(counts) == HOSTS and sorted(counts.values()) == [RANKS_PER_HOST] * HOSTS, \
        ('PBS nodefile host counts', len(hosts), counts)
    return hosts, counts


def read_probe(path):
    rows = []
    marker = 'MAP_JSON\t'
    for line in Path(path).read_text(errors='replace').splitlines():
        if marker in line:
            rows.append(json.loads(line.split(marker, 1)[1]))
    ranks = [row.get('rank') for row in rows]
    assert len(rows) == RANKS and sorted(ranks) == list(range(RANKS)), ('MPI world rank set', len(rows), ranks[:20])
    assert all(row.get('world_size') == RANKS for row in rows), 'MPI_COMM_WORLD size is not 512 for every rank'
    return {row['rank']: row for row in rows}


def validate_probe(path, node_counts):
    rows = read_probe(path)
    host_counts = Counter()
    domain_counts = {}
    cores = set()
    logical_cpus = set()
    for rank in range(RANKS):
        row = rows[rank]
        host = normalize_host(row['processor_name'])
        assert host in node_counts, ('rank host is not in PBS allocation', rank, host)
        host_counts[host] += 1
        cpus = row['affinity_cpus']
        assert isinstance(cpus, list) and len(cpus) == 1 and isinstance(cpus[0], int), \
            ('rank must have one logical CPU affinity', rank, cpus)
        package = row['physical_package_id']; core = row['physical_core_id']; numa = row['numa_node']
        assert all(isinstance(x, int) and x >= 0 for x in (package, core, numa)), ('bad local sysfs topology', rank, row)
        logical = (host, cpus[0])
        physical = (host, package, core)
        assert logical not in logical_cpus, ('logical CPU reused', rank, logical)
        assert physical not in cores, ('physical CPU core reused', rank, physical)
        logical_cpus.add(logical); cores.add(physical)
        domain_counts.setdefault(host, Counter())[numa] += 1
    assert host_counts == node_counts, ('MPI ranks per PBS host', host_counts, node_counts)
    assert len(cores) == RANKS and len(logical_cpus) == RANKS
    for host in node_counts:
        counts = domain_counts[host]
        assert len(counts) == DOMAINS_PER_HOST and sorted(counts.values()) == [RANKS_PER_DOMAIN] * DOMAINS_PER_HOST, \
            ('expected eight actual NUMA domains with 16 ranks per host/domain', host, counts)
    return rows, {'hosts': dict(sorted(host_counts.items())),
                  'numa_ranks_per_host': {host: dict(sorted(counts.items())) for host, counts in sorted(domain_counts.items())},
                  'unique_logical_cpus': len(logical_cpus), 'unique_physical_cores': len(cores)}


def placement_key(row):
    return (normalize_host(row['processor_name']), row['affinity_cpus'][0],
            row['physical_package_id'], row['physical_core_id'], row['numa_node'])
