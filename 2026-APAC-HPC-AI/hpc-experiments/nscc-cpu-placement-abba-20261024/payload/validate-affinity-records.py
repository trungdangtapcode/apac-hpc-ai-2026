"""Validate PMPI affinity audits and tie each application's CPU to its mapping probe."""
import argparse
import json
from collections import Counter
from pathlib import Path

RANKS = 512
PREFIX = 'APAC_AFFINITY_JSON '
EXEC_PREFIX = 'APAC_AFFINITY_EXEC_JSON '
MAP_PREFIX = 'MAP_JSON\t'


def records_from_probe(path):
    records = {}
    for line in Path(path).read_text(errors='replace').splitlines():
        if MAP_PREFIX not in line:
            continue
        row = json.loads(line.split(MAP_PREFIX, 1)[1])
        rank = int(row['rank'])
        assert rank not in records, ('duplicate MAP_JSON rank', rank)
        assert int(row['world_size']) == RANKS
        records[rank] = row
    assert sorted(records) == list(range(RANKS)), ('MAP_JSON rank set', len(records), sorted(records)[:5])
    assert all(int(row.get('thread_provided', -1)) >= 0 for row in records.values()), \
        'MPI_Init_thread probe did not report its provided level'
    return records


def affinity_records(path):
    rows = {}
    for line in Path(path).read_text(errors='replace').splitlines():
        if PREFIX not in line:
            continue
        row = json.loads(line.split(PREFIX, 1)[1])
        rank = int(row['rank'])
        assert rank not in rows, ('duplicate affinity record for MPI rank', rank)
        rows[rank] = row
    assert sorted(rows) == list(range(RANKS)), ('affinity record rank set', len(rows), sorted(rows)[:5])
    return rows


def exec_records(path):
    rows = []
    for line in Path(path).read_text(errors='replace').splitlines():
        if EXEC_PREFIX not in line:
            continue
        rows.append(json.loads(line.split(EXEC_PREFIX, 1)[1]))
    assert len(rows) == RANKS, ('exec-affinity record count', len(rows))
    assert all(row.get('success') is True for row in rows), 'one or more launcher wrapper records failed'
    for row in rows:
        assert len(row.get('launch_cpus', [])) == 1, ('launcher CPU mask is not singleton', row)
        assert int(row['launch_cpus'][0]) == int(row['launch_cpu'])
        assert Path(row['library']).is_absolute()
        assert Path(row['application']).is_absolute()
    return rows


def cpus(value):
    if not value:
        return []
    return [int(item) for item in value.split(',') if item]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--diagnostics', required=True, help='stderr or combined solver log containing APAC_AFFINITY_JSON records')
    parser.add_argument('--mapping-probe', required=True, help='stdout from the immediately preceding matching MPI probe')
    parser.add_argument('--require-entry', choices=('MPI_Init', 'MPI_Init_thread'))
    parser.add_argument('--output')
    args = parser.parse_args()
    affinity = affinity_records(args.diagnostics)
    launch = exec_records(args.diagnostics)
    mapped = records_from_probe(args.mapping_probe)
    entry_types = Counter()
    expanded = 0
    pre_init_truncated = 0
    post_init_truncated = 0
    per_rank = []
    for rank in range(RANKS):
        row, target = affinity[rank], mapped[rank]
        entry_types[row['entry']] += 1
        assert row['entry'] in ('MPI_Init', 'MPI_Init_thread')
        if args.require_entry:
            assert row['entry'] == args.require_entry, ('unexpected MPI initialization entry point', rank, row['entry'])
        assert int(row['mpi_pre_init_status']) == 0 and int(row['post_init_status']) == 0
        assert int(row['restore_set_status']) == 0 and int(row['restored_read_status']) == 0
        assert row['success'] is True
        assert row['restored_truncated'] is False
        before_truncated = bool(row['mpi_pre_init_truncated'])
        after_truncated = bool(row['post_init_truncated'])
        pre_init_truncated += int(before_truncated)
        post_init_truncated += int(after_truncated)
        # Entry-time masks may already be widened by PMI. Truncated masks are
        # retained as unavailable evidence; never infer their full cardinality.
        before = None if before_truncated else cpus(row['mpi_pre_init_cpus'])
        after = None if after_truncated else cpus(row['post_init_cpus'])
        restored = cpus(row['restored_cpus'])
        launch_cpu = int(row['launch_cpu'])
        assert len(restored) == 1 and restored == [launch_cpu], (
            'restored mask differs from captured exec-time CPU', rank, launch_cpu, restored)
        assert len(target['affinity_cpus']) == 1
        assert launch_cpu == int(target['affinity_cpus'][0]), (
            'exec-time captured CPU differs from immediate placement probe', rank, launch_cpu,
            target['affinity_cpus'])
        if after is not None and after != restored:
            expanded += 1
        per_rank.append({'mpi_world_rank': rank, 'entry': row['entry'],
                         'exec_captured_cpu': launch_cpu,
                         'mpi_pre_init_cpu_count': None if before is None else len(before),
                         'mpi_pre_init_mask_truncated': before_truncated,
                         'post_init_cpu_count': None if after is None else len(after),
                         'post_init_mask_truncated': after_truncated,
                         'restored_cpu': restored[0],
                         'mapped_host': target['processor_name'],
                         'mapped_physical_package': target['physical_package_id'],
                         'mapped_physical_core': target['physical_core_id'],
                         'mapped_numa_node': target['numa_node']})
    assert sum(entry_types.values()) == RANKS
    report = {'passed': True, 'rank_count': RANKS, 'entry_type_counts': dict(entry_types),
              'exec_wrapper_records': len(launch), 'exec_time_masks_singleton': True,
              'unique_launcher_pid_count_diagnostic': len(set(row.get('pid') for row in launch)),
              'restored_mask_matches_exec_capture': True,
              'mpi_pre_init_mask_truncated_count': pre_init_truncated,
              'post_init_mask_truncated_count': post_init_truncated,
              'truncated_mask_cardinality_inferred': False,
              'application_affinity_wider_than_restored_during_mpi_init_count': expanded,
              'cpu_matches_immediate_probe_for_all_ranks': True,
              'scope': 'Main MPI-initializing thread only; probe is immediately before the solver and does not prove helper-thread binding or page residency.',
              'per_rank': per_rank}
    text = json.dumps(report, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
