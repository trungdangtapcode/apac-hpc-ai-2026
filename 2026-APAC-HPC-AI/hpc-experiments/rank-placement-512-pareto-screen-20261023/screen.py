#!/usr/bin/env python3
"""Search balanced whole-group host assignments on a 32-node face graph."""
from __future__ import annotations

import datetime
import hashlib
import json
import math
import random
import statistics
import time
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
GRAPH_PATH = RESEARCH / "rank-placement-512-screen-20261023/graph.json"
HOST_SCREEN_PATH = RESEARCH / "rank-placement-512-screen-20261023/screen.json"
NUMA_SCREEN_PATH = RESEARCH / "rank-placement-512-numa-screen-20261023/screen.json"
OUTPUT_PATH = HERE / "screen.json"
QUALIFICATION_PATH = HERE / "qualification.json"
RANKS = 512
NUMA_NODES = 32
HOSTS = 4
NUMA_GROUPS_PER_HOST = 8
RANKS_PER_GROUP = 16
GROUPS_PER_HOST = 8
SEED = 2026
MAX_PROPOSALS = 500_000
SEARCH_LIMIT_SECONDS = 18.0
HARD_LIMIT_SECONDS = 20.0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def super_cut(hosts: list[int], edges: list[dict]) -> int:
    return sum(edge["faces"] for edge in edges if hosts[edge["a"]] != hosts[edge["b"]])


def swap_delta(u: int, v: int, hosts: list[int], adjacency: list[list[tuple[int, int]]]) -> int:
    """Cut delta for swapping whole supernodes assigned to distinct hosts."""
    host_u, host_v = hosts[u], hosts[v]
    delta = 0
    # The u-v edge stays on the same host before and after the swap.
    for neighbor, faces in adjacency[u]:
        if neighbor != v:
            delta += faces * ((host_v != hosts[neighbor]) - (host_u != hosts[neighbor]))
    for neighbor, faces in adjacency[v]:
        if neighbor != u:
            delta += faces * ((host_u != hosts[neighbor]) - (host_v != hosts[neighbor]))
    return delta


def feasible_distance(cut: int, lower: int, upper: int) -> int:
    if cut < lower:
        return lower - cut
    if cut > upper:
        return cut - upper
    return 0


def target_score(cut: int, lower: int, upper: int) -> tuple[int, int]:
    # Primary criterion is feasibility. Among feasible assignments approach its
    # lower boundary, which minimizes host cut while preserving the NUMA control.
    distance = feasible_distance(cut, lower, upper)
    return distance, (cut - lower if distance == 0 else 0)


def canonicalize(hosts: list[int], groups: list[dict]) -> tuple[list[int], dict[int, int]]:
    min_rank = {node["id"]: min(node["ranks"]) for node in groups}
    current_labels = sorted(set(hosts))
    order = sorted(current_labels, key=lambda label: min(min_rank[node] for node, value in enumerate(hosts)
                                                        if value == label))
    remap = {old: new for new, old in enumerate(order)}
    return [remap[value] for value in hosts], remap


def derived_host_metrics(hosts: list[int], edges: list[dict], groups: list[dict], ranks: int = RANKS) -> dict:
    matrix = [[0] * HOSTS for _ in range(HOSTS)]
    external = [0] * HOSTS
    group_external = [0] * NUMA_NODES
    for edge in edges:
        a, b, faces = edge["a"], edge["b"], edge["faces"]
        if hosts[a] == hosts[b]:
            continue
        left, right = sorted((hosts[a], hosts[b]))
        matrix[left][right] += faces
        external[hosts[a]] += faces
        external[hosts[b]] += faces
        group_external[a] += faces
        group_external[b] += faces
    cells_by_host = [0] * HOSTS
    ranks_by_host = [[] for _ in range(HOSTS)]
    for node, host in enumerate(hosts):
        cells_by_host[host] += groups[node]["cells"]
        ranks_by_host[host].extend(groups[node]["ranks"])
    return {
        "host_interface_matrix_upper_triangle_faces": matrix,
        "matrix_convention": "Each unique inter-supernode edge is counted once in [min(host_a,host_b)][max(host_a,host_b)]; diagonal and lower triangle are zero.",
        "external_interface_faces_by_host": external,
        "maximum_host_external_interface_faces": max(external),
        "maximum_supernode_external_faces_by_host": [
            max(group_external[node] for node, host in enumerate(hosts) if host == label)
            for label in range(HOSTS)
        ],
        "rank_counts_by_host": [len(ranks_by_host[host]) for host in range(HOSTS)],
        "cell_totals_by_host": cells_by_host,
        "cell_min": min(cells_by_host),
        "cell_max": max(cells_by_host),
        "cell_range": max(cells_by_host) - min(cells_by_host),
        "cell_mean": statistics.mean(cells_by_host),
        "maximum_cell_excess_over_mean_fraction": max(cells_by_host) / statistics.mean(cells_by_host) - 1,
    }


def main() -> None:
    started = time.monotonic()
    graph_bytes = GRAPH_PATH.read_bytes()
    host_screen_bytes = HOST_SCREEN_PATH.read_bytes()
    numa_screen_bytes = NUMA_SCREEN_PATH.read_bytes()
    graph = json.loads(graph_bytes)
    host_screen = json.loads(host_screen_bytes)
    numa_screen = json.loads(numa_screen_bytes)
    graph_hash = digest(graph_bytes)
    require(graph_hash == host_screen["graph_file_sha256"] == numa_screen["parent_graph_sha256"],
            "parent graph hash pins disagree")
    require(numa_screen["parent_screen_sha256"] == digest(host_screen_bytes),
            "fixed-host NUMA screen does not pin the exact parent screen")
    require(graph["ranks"] == RANKS and host_screen["state"] == "OFFLINE_512_RANK_GROUP_SCREEN_COMPLETE",
            "512-rank graph or host screen is invalid")
    require(numa_screen["state"] == "OFFLINE_FIXED_HOST_NUMA_TRADEOFF_COMPLETE",
            "fixed-host NUMA screen is incomplete")

    graph_edges = graph["edges"]
    raw_total_faces = sum(edge["faces"] for edge in graph_edges)
    raw_cells = graph["cells_by_rank"]
    fixed = numa_screen["optimized_fixed_host_mapping"]
    group_members = fixed["numa_group_members_by_host"]
    require(len(group_members) == HOSTS and all(len(host) == NUMA_GROUPS_PER_HOST for host in group_members),
            "fixed NUMA mapping does not contain 4 x 8 groups")
    groups = []
    rank_to_supernode = [-1] * RANKS
    aggressive_host_by_group = []
    for host, host_groups in enumerate(group_members):
        for numa, members in enumerate(host_groups):
            node_id = host * NUMA_GROUPS_PER_HOST + numa
            ranks = sorted(members)
            require(len(ranks) == RANKS_PER_GROUP and len(set(ranks)) == RANKS_PER_GROUP,
                    f"supernode {node_id}: expected 16 unique ranks")
            require(all(0 <= rank < RANKS and rank_to_supernode[rank] == -1 for rank in ranks),
                    f"supernode {node_id}: rank missing or duplicated")
            for rank in ranks:
                rank_to_supernode[rank] = node_id
                require(fixed["rank_to_host"][rank] == host and
                        fixed["rank_to_logical_numa_group_within_host"][rank] == numa,
                        f"rank {rank}: fixed-screen vectors disagree with group membership")
            groups.append({"id": node_id, "source_host_group": host, "source_numa_group": numa,
                           "ranks": ranks, "cells": sum(raw_cells[rank] for rank in ranks)})
            aggressive_host_by_group.append(host)
    require(sorted(rank_to_supernode) == [node for node in range(NUMA_NODES) for _ in range(RANKS_PER_GROUP)],
            "32 fixed groups do not partition all 512 ranks exactly once")

    super_edges_map: dict[tuple[int, int], int] = {}
    internal_same_group_faces = 0
    for edge in graph_edges:
        node_a, node_b = rank_to_supernode[edge["a"]], rank_to_supernode[edge["b"]]
        require(node_a >= 0 and node_b >= 0, "processor graph has a rank outside the fixed groups")
        faces = edge["faces"]
        if node_a == node_b:
            internal_same_group_faces += faces
        else:
            key = tuple(sorted((node_a, node_b)))
            super_edges_map[key] = super_edges_map.get(key, 0) + faces
    super_edges = [{"a": a, "b": b, "faces": faces}
                   for (a, b), faces in sorted(super_edges_map.items())]
    super_total = sum(edge["faces"] for edge in super_edges)
    require(internal_same_group_faces + super_total == raw_total_faces,
            "32-supernode aggregation does not conserve all rank-graph faces")
    require(super_total == 993822, f"fixed supergroup cross-NUMA total changed: {super_total}")
    require(internal_same_group_faces == 1933200, "fixed group internal faces changed")

    aggressive_hosts = aggressive_host_by_group[:]
    require(sorted(Counter(aggressive_hosts).values()) == [GROUPS_PER_HOST] * HOSTS,
            "aggressive parent supernode assignment is not 8 groups per host")
    aggressive_cut = super_cut(aggressive_hosts, super_edges)
    require(aggressive_cut == 261110, f"aggressive parent host cut mismatch: {aggressive_cut}")
    require(super_total - aggressive_cut == 732712, "aggressive parent intra-host cross-NUMA cut mismatch")

    original_host_by_rank = [rank // 128 for rank in range(RANKS)]
    original_numa_by_rank = [(rank % 128) // 16 for rank in range(RANKS)]
    original_host_cut = sum(edge["faces"] for edge in graph_edges
                            if original_host_by_rank[edge["a"]] != original_host_by_rank[edge["b"]])
    original_same_host_numa_cut = sum(edge["faces"] for edge in graph_edges
                                      if original_host_by_rank[edge["a"]] == original_host_by_rank[edge["b"]]
                                      and original_numa_by_rank[edge["a"]] != original_numa_by_rank[edge["b"]])
    require(original_host_cut == 337324 and original_same_host_numa_cut == 710081,
            "original control cuts no longer match the parent graph screen")
    lower_bound = super_total - original_same_host_numa_cut
    upper_bound = original_host_cut
    require(lower_bound == 283741 and lower_bound < upper_bound,
            "control-derived non-regression interval changed")

    # Every group swap is an inter-host balanced exchange. The adjacency is the
    # aggregated 32-node graph, independent of any assumed physical topology.
    adjacency = [[] for _ in range(NUMA_NODES)]
    for edge in super_edges:
        adjacency[edge["a"]].append((edge["b"], edge["faces"]))
        adjacency[edge["b"]].append((edge["a"], edge["faces"]))

    single_swap_feasible: dict[int, list[int]] = {}
    single_swap_count = 0
    single_swap_feasible_assignment_count = 0
    single_swap_best = None
    for left in range(NUMA_NODES):
        for right in range(left + 1, NUMA_NODES):
            if aggressive_hosts[left] == aggressive_hosts[right]:
                continue
            candidate = aggressive_hosts[:]
            candidate[left], candidate[right] = candidate[right], candidate[left]
            cut = super_cut(candidate, super_edges)
            single_swap_count += 1
            if lower_bound <= cut <= upper_bound:
                single_swap_feasible_assignment_count += 1
                single_swap_feasible.setdefault(cut, candidate)
                if single_swap_best is None or cut < single_swap_best[0]:
                    single_swap_best = (cut, candidate)

    archive: dict[int, dict] = {}

    def retain_nondominated(candidate: list[int], cut: int, source: str, proposal: int | None) -> None:
        if lower_bound <= cut <= upper_bound and cut not in archive:
            archive[cut] = {"host_cut_faces": cut,
                            "same_host_cross_numa_faces": super_total - cut,
                            "host_assignment_by_supernode": candidate[:],
                            "source": source,
                            "proposal": proposal}

    for cut, candidate in single_swap_feasible.items():
        retain_nondominated(candidate, cut, "deterministic_single_swap_from_aggressive_parent", None)
    current_hosts = (single_swap_best[1][:] if single_swap_best is not None else aggressive_hosts[:])
    current_cut = super_cut(current_hosts, super_edges)
    initial_distance = feasible_distance(current_cut, lower_bound, upper_bound)
    current_score = target_score(current_cut, lower_bound, upper_bound)
    best_feasible = None
    if lower_bound <= current_cut <= upper_bound:
        best_feasible = (current_cut, current_hosts[:])
    best_score = current_score
    objective_trail = [{"phase": "aggressive_parent_start", "cut_faces": aggressive_cut,
                        "distance_to_feasible_interval_faces": feasible_distance(aggressive_cut, lower_bound, upper_bound)}]
    if single_swap_best is not None:
        objective_trail.append({"phase": "best_deterministic_single_swap",
                                "cut_faces": single_swap_best[0],
                                "distance_to_feasible_interval_faces": 0,
                                "swapped_supernodes": [
                                    index for index, (before, after) in enumerate(zip(aggressive_hosts, single_swap_best[1]))
                                    if before != after
                                ]})

    rng = random.Random(SEED)
    proposals = 0
    accepted = 0
    search_start = time.monotonic()
    start_temperature, end_temperature = 12000.0, 1.0
    while proposals < MAX_PROPOSALS and time.monotonic() - search_start < SEARCH_LIMIT_SECONDS:
        proposals += 1
        left = rng.randrange(NUMA_NODES)
        right = rng.randrange(NUMA_NODES - 1)
        if right >= left:
            right += 1
        if current_hosts[left] == current_hosts[right]:
            continue
        delta = swap_delta(left, right, current_hosts, adjacency)
        candidate_cut = current_cut + delta
        old_score = target_score(current_cut, lower_bound, upper_bound)
        new_score = target_score(candidate_cut, lower_bound, upper_bound)
        progress = proposals / MAX_PROPOSALS
        temperature = start_temperature * ((end_temperature / start_temperature) ** progress)
        accept = False
        if new_score < old_score:
            accept = True
        elif new_score == old_score:
            accept = rng.random() < 0.5
        else:
            if new_score[0] > old_score[0]:
                worsening = new_score[0] - old_score[0]
            else:
                worsening = new_score[1] - old_score[1]
            accept = rng.random() < math.exp(-max(0, worsening) / temperature)
        if not accept:
            continue
        accepted += 1
        current_hosts[left], current_hosts[right] = current_hosts[right], current_hosts[left]
        current_cut = candidate_cut
        current_score = new_score
        retain_nondominated(current_hosts, current_cut, "seeded_balanced_whole_group_swap", proposals)
        if lower_bound <= current_cut <= upper_bound:
            if best_feasible is None or current_cut < best_feasible[0]:
                best_feasible = (current_cut, current_hosts[:])
        if current_score < best_score:
            best_score = current_score
            objective_trail.append({"phase": "seeded_best_distance_or_threshold_step",
                                    "proposal": proposals,
                                    "cut_faces": current_cut,
                                    "distance_to_feasible_interval_faces": feasible_distance(
                                        current_cut, lower_bound, upper_bound)})

    search_elapsed = time.monotonic() - search_start
    total_elapsed = time.monotonic() - started
    require(total_elapsed < HARD_LIMIT_SECONDS,
            f"bounded assignment search exceeded {HARD_LIMIT_SECONDS}s: {total_elapsed:.3f}")

    if best_feasible is not None:
        best_cut, best_hosts = best_feasible
        require(lower_bound <= best_cut <= upper_bound, "selected assignment is outside the feasibility interval")
        require(sorted(Counter(best_hosts).values()) == [GROUPS_PER_HOST] * HOSTS,
                "best feasible assignment is not 8 whole groups per host")
    else:
        best_cut, best_hosts = aggressive_cut, aggressive_hosts[:]

    # Validate random incremental deltas on the final assignment with full cuts.
    delta_rng = random.Random(SEED ^ 0x5A17)
    delta_checks = []
    for index in range(128):
        left = delta_rng.randrange(NUMA_NODES)
        right = delta_rng.randrange(NUMA_NODES - 1)
        if right >= left:
            right += 1
        while best_hosts[left] == best_hosts[right]:
            right = delta_rng.randrange(NUMA_NODES)
        old_full = super_cut(best_hosts, super_edges)
        delta = swap_delta(left, right, best_hosts, adjacency)
        test_hosts = best_hosts[:]
        test_hosts[left], test_hosts[right] = test_hosts[right], test_hosts[left]
        new_full = super_cut(test_hosts, super_edges)
        require(new_full - old_full == delta, f"random swap delta mismatch at sample {index}")
        delta_checks.append({"index": index, "supernodes": [left, right],
                             "incremental_delta_faces": delta,
                             "full_recomputed_delta_faces": new_full - old_full})

    # Canonical host labels and construct an explicit 512-rank permutation.
    normalized_hosts, host_label_map = canonicalize(best_hosts, groups)
    rank_to_host = [-1] * RANKS
    rank_to_numa = [-1] * RANKS
    permutation = []
    normalized_group_members_by_host = []
    for node_id, group in enumerate(groups):
        host = normalized_hosts[node_id]
        for rank in group["ranks"]:
            rank_to_host[rank] = host
    for host in range(HOSTS):
        node_ids = [node for node, label in enumerate(normalized_hosts) if label == host]
        node_ids.sort(key=lambda node: min(groups[node]["ranks"]))
        group_members = []
        for numa_label, node in enumerate(node_ids):
            members = sorted(groups[node]["ranks"])
            require(len(members) == RANKS_PER_GROUP, "group membership changed")
            group_members.append(members)
            permutation.extend(members)
            for rank in members:
                rank_to_numa[rank] = numa_label
        require(len(node_ids) == GROUPS_PER_HOST, f"host {host}: must receive eight whole groups")
        normalized_group_members_by_host.append(group_members)
    require(permutation[0] == 0 and sorted(permutation) == list(range(RANKS)),
            "rendered rank permutation must be a rank-zero-first bijection")
    require(rank_to_host == [host for host in rank_to_host] and min(rank_to_host) == 0,
            "invalid rank-to-host vector")

    # Recompute all 512-rank cut categories from the original graph, independently
    # of the aggregated supergraph objective.
    cross_host_full = sum(edge["faces"] for edge in graph_edges
                          if rank_to_host[edge["a"]] != rank_to_host[edge["b"]])
    same_host_cross_numa_full = sum(edge["faces"] for edge in graph_edges
                                    if rank_to_host[edge["a"]] == rank_to_host[edge["b"]]
                                    and rank_to_numa[edge["a"]] != rank_to_numa[edge["b"]])
    same_numa_full = raw_total_faces - cross_host_full - same_host_cross_numa_full
    require(cross_host_full == best_cut == super_cut(best_hosts, super_edges),
            "full graph cross-host recomputation disagrees with supergraph")
    require(same_host_cross_numa_full == super_total - best_cut,
            "full graph same-host cross-NUMA subtotal disagrees with conservation")
    require(cross_host_full + same_host_cross_numa_full + same_numa_full == raw_total_faces,
            "full graph cut classes do not conserve all faces")

    metrics = derived_host_metrics(normalized_hosts, super_edges, groups)
    per_host_cell_totals = metrics["cell_totals_by_host"]
    parent_optimized_parts = {"cross_host_faces": aggressive_cut,
                              "same_host_cross_numa_faces": super_total - aggressive_cut}
    new_parts = {"cross_host_faces": cross_host_full,
                 "same_host_cross_numa_faces": same_host_cross_numa_full,
                 "within_host_same_numa_faces": same_numa_full}
    is_feasible = lower_bound <= cross_host_full <= upper_bound
    require(metrics["rank_counts_by_host"] == [128] * HOSTS, "host rank balance failed")
    require(sum(group["cells"] for group in groups) == sum(raw_cells), "supernode cell total changed")
    require(len(archive) >= len(single_swap_feasible), "feasible deterministic candidates not retained")

    original_host_external = [0] * HOSTS
    original_host_matrix = [[0] * HOSTS for _ in range(HOSTS)]
    for edge in graph_edges:
        left, right = original_host_by_rank[edge["a"]], original_host_by_rank[edge["b"]]
        if left != right:
            lo, hi = sorted((left, right))
            original_host_matrix[lo][hi] += edge["faces"]
            original_host_external[left] += edge["faces"]
            original_host_external[right] += edge["faces"]
    original_host_cells = [sum(raw_cells[rank] for rank in range(RANKS)
                               if original_host_by_rank[rank] == host) for host in range(HOSTS)]
    original_host_metrics = {
        "host_interface_matrix_upper_triangle_faces": original_host_matrix,
        "external_interface_faces_by_host": original_host_external,
        "maximum_host_external_interface_faces": max(original_host_external),
        "rank_counts_by_host": [128] * HOSTS,
        "cell_totals_by_host": original_host_cells,
        "cell_min": min(original_host_cells),
        "cell_max": max(original_host_cells),
        "cell_range": max(original_host_cells) - min(original_host_cells),
        "cell_mean": statistics.mean(original_host_cells),
        "maximum_cell_excess_over_mean_fraction": max(original_host_cells) / statistics.mean(original_host_cells) - 1,
    }

    pareto_candidates = []
    for cut, row in sorted(archive.items()):
        canonical, _ = canonicalize(row["host_assignment_by_supernode"], groups)
        pareto_candidates.append({
            "host_cut_faces": cut,
            "same_host_cross_numa_faces": super_total - cut,
            "host_assignment_by_supernode_canonical": canonical,
            "source": row["source"],
            "proposal": row["proposal"],
        })

    qualification = {
        "state": "WHOLE_NUMA_GROUP_ASSIGNMENT_QUALIFICATION_PASS" if is_feasible else "NO_FEASIBLE_WHOLE_GROUP_ASSIGNMENT_FOUND",
        "structural_checks_passed": True,
        "source_graph_sha256": graph_hash,
        "source_host_screen_sha256": digest(host_screen_bytes),
        "source_numa_screen_sha256": digest(numa_screen_bytes),
        "numa_supernodes": len(groups),
        "ranks_per_supernode": RANKS_PER_GROUP,
        "supernode_partition_exactly_covers_512_ranks": True,
        "supergraph_unique_edges": len(super_edges),
        "original_rank_graph_total_faces": raw_total_faces,
        "supernode_internal_faces": internal_same_group_faces,
        "superedge_face_total": super_total,
        "aggregation_conserves_all_faces": internal_same_group_faces + super_total == raw_total_faces,
        "aggressive_parent_host_cut_recomputed": aggressive_cut,
        "original_control_host_cut": original_host_cut,
        "original_control_same_host_cross_numa_cut": original_same_host_numa_cut,
        "feasibility_interval_inclusive": [lower_bound, upper_bound],
        "deterministic_interhost_single_swaps_checked": single_swap_count,
        "deterministic_feasible_single_swap_assignments": single_swap_feasible_assignment_count,
        "distinct_feasible_single_swap_cut_values": len(single_swap_feasible),
        "best_feasible_found": is_feasible,
        "best_candidate_host_cut": cross_host_full,
        "best_candidate_same_host_cross_numa_cut": same_host_cross_numa_full,
        "host_counts": metrics["rank_counts_by_host"],
        "rank_permutation_bijection": sorted(permutation) == list(range(RANKS)),
        "rank_zero_first": permutation[0] == 0,
        "host_cell_totals": per_host_cell_totals,
        "random_swap_deltas_checked": len(delta_checks),
        "all_random_swap_deltas_match_full_supergraph": True,
        "final_512_edge_cuts_match_supergraph": True,
        "topology_claim": "None. Eight NUMA groups per host is an unverified historical-topology assumption.",
        "solver_or_runtime_claim": False,
    }
    result = {
        "state": "OFFLINE_WHOLE_GROUP_PARETO_SCREEN_COMPLETE" if is_feasible else "OFFLINE_WHOLE_GROUP_SCREEN_NO_FEASIBLE_RESULT",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "input_hashes": {"rank_graph_sha256": graph_hash,
                         "four_host_screen_sha256": digest(host_screen_bytes),
                         "fixed_host_numa_screen_sha256": digest(numa_screen_bytes)},
        "parameters": {
            "seed": SEED,
            "proposal_limit": MAX_PROPOSALS,
            "proposals_completed": proposals,
            "accepted_whole_group_swaps": accepted,
            "single_swap_enumeration_candidates": single_swap_count,
            "search_time_limit_seconds": SEARCH_LIMIT_SECONDS,
            "search_elapsed_seconds": search_elapsed,
            "total_local_elapsed_seconds": total_elapsed,
            "hard_limit_seconds": HARD_LIMIT_SECONDS,
            "no_global_optimum_claim": True,
        },
        "supergraph": {"nodes": NUMA_NODES, "unique_edges": len(super_edges),
                       "total_cross_numa_faces": super_total,
                       "internal_faces_within_fixed_numa_groups": internal_same_group_faces,
                       "weighted_edges": super_edges,
                       "group_metadata": groups,
                       "aggregation_conservation": raw_total_faces == super_total + internal_same_group_faces},
        "cut_invariants": {"cross_numa_total_if_groups_stay_intact": super_total,
                           "original_control_host_cut": original_host_cut,
                           "original_control_same_host_cross_numa_cut": original_same_host_numa_cut,
                           "feasible_host_cut_interval": [lower_bound, upper_bound],
                           "derivation": "same-host cross-NUMA = 993822 - host cut; do not combine the two proxy objectives with physical weights"},
        "original_control": {"description": "host=rank//128; within-host NUMA=(rank%128)//16",
                             "cross_host_faces": original_host_cut,
                             "same_host_cross_numa_faces": original_same_host_numa_cut,
                             "within_host_same_numa_faces": raw_total_faces - original_host_cut - original_same_host_numa_cut,
                             "host_metrics": original_host_metrics},
        "aggressive_parent_mapping": {"description": "Fixed 32 groups from the within-host screen, eight per logical host",
                                       "cross_host_faces": aggressive_cut,
                                       "same_host_cross_numa_faces": super_total - aggressive_cut,
                                       "within_host_same_numa_faces": raw_total_faces - super_total,
                                       "host_assignment_by_supernode": aggressive_hosts,
                                       "host_metrics": derived_host_metrics(aggressive_hosts, super_edges, groups)},
        "single_swap_enumeration": {"swaps_checked": single_swap_count,
                                    "feasible_assignments_found": single_swap_feasible_assignment_count,
                                    "distinct_feasible_host_cut_values": len(single_swap_feasible),
                                    "best_feasible_host_cut": None if single_swap_best is None else single_swap_best[0],
                                    "best_feasible_assignment_by_supernode": None if single_swap_best is None else single_swap_best[1]},
        "search": {"starting_assignment": current_hosts,
                   "starting_cut_faces": current_cut,
                   "starting_distance_to_feasible_interval_faces": initial_distance,
                   "aggressive_parent_starting_cut_faces": aggressive_cut,
                   "aggressive_parent_distance_to_feasible_interval_faces": feasible_distance(
                       aggressive_cut, lower_bound, upper_bound),
                   "algorithmic_objective": "Distance to the feasible interval first; among feasible points, approach the lower cut boundary. This is search guidance only, not a physical weighting.",
                   "objective_trail": objective_trail},
        "qualification": qualification,
        "best_feasible": None if not is_feasible else {
            "host_cut_faces": cross_host_full,
            "same_host_cross_numa_faces": same_host_cross_numa_full,
            "within_host_same_numa_faces": same_numa_full,
            "host_assignment_by_supernode_canonical": canonicalize(best_hosts, groups)[0],
            "rank_to_host": rank_to_host,
            "rank_to_logical_numa_group_within_host": rank_to_numa,
            "whole_group_membership_by_host": [
                [groups[node]["ranks"] for node, label in enumerate(canonicalize(best_hosts, groups)[0]) if label == host]
                for host in range(HOSTS)
            ],
            "full_rank_permutation_host_numa_group_major": permutation,
            "rank_zero_first": permutation[0] == 0,
            "host_metrics": metrics,
            "search_distance_to_feasible_interval_faces": feasible_distance(cross_host_full, lower_bound, upper_bound),
        },
        "nondominated_feasible_candidates_observed": pareto_candidates,
        "nondominated_candidate_interpretation": "The two proxy objectives sum to a fixed 993,822 for these intact groups; every distinct feasible host-cut value is nondominated. The listed assignments are the distinct feasible values encountered by deterministic one-swap enumeration or accepted seeded search, not an exhaustive Pareto frontier.",
        "delta_validation": {"seed": SEED ^ 0x5A17, "checked_swaps": len(delta_checks),
                             "all_match_full_supergraph_recomputation": True, "checks": delta_checks},
        "final_full_512_edge_recomputation": {"cross_host_faces": cross_host_full,
                                              "same_host_cross_numa_faces": same_host_cross_numa_full,
                                              "within_host_same_numa_faces": same_numa_full,
                                              "total_unique_faces": raw_total_faces,
                                              "matches_supergraph": True},
        "limitations": [
            "The fixed groups of 16 ranks are logical groups from the previous offline mapping, not verified physical NUMA domains.",
            "Eight NUMA groups per host is an unverified historical-topology assumption for four new hosts.",
            "No original rank-to-host/core mapping, NUMA page placement, MPI wait, traffic, bytes, solver timing or speedup was measured.",
            "The rank graph boundaries were collected after submission and do not establish original mesh identity.",
            "Search is bounded and does not prove a global optimum or exhaustive Pareto frontier.",
            "The new host assignment is offline analysis only and is not a runnable rank-order payload.",
        ],
    }
    QUALIFICATION_PATH.write_text(json.dumps(qualification, indent=2) + "\n")
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"state": result["state"], "proposals": proposals,
                      "elapsed_seconds": total_elapsed,
                      "single_swap_feasible": len(single_swap_feasible),
                      "feasible_pareto_points_retained": len(pareto_candidates),
                      "best_feasible_host_cut": cross_host_full if is_feasible else None,
                      "best_feasible_same_host_cross_numa_cut": same_host_cross_numa_full if is_feasible else None}, indent=2))


if __name__ == "__main__":
    main()
