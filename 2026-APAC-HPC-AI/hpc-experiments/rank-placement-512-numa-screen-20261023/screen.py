#!/usr/bin/env python3
"""Screen eight balanced logical NUMA groups inside fixed host rank sets."""
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
PARENT = HERE.parent / "rank-placement-512-screen-20261023"
GRAPH_PATH = PARENT / "graph.json"
PARENT_SCREEN_PATH = PARENT / "screen.json"
OUTPUT_PATH = HERE / "screen.json"
QUALIFICATION_PATH = HERE / "qualification.json"
RANKS = 512
HOSTS = 4
RANKS_PER_HOST = 128
NUMA_GROUPS_PER_HOST = 8
RANKS_PER_NUMA_GROUP = 16
SEED = 2026
PROPOSALS_PER_HOST = 250_000
SEARCH_BUDGET_SECONDS = 26.0
HARD_LIMIT_SECONDS = 30.0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def total_same_host_cross_numa_cut(assignment: list[int], host_of: list[int], edges: list[dict]) -> int:
    return sum(edge["faces"] for edge in edges
               if host_of[edge["a"]] == host_of[edge["b"]]
               and assignment[edge["a"]] != assignment[edge["b"]])


def swap_delta(u: int, v: int, assignment: list[int], adjacency: list[list[tuple[int, int]]]) -> int:
    """Change in cut after exchanging two vertices in distinct groups."""
    group_u, group_v = assignment[u], assignment[v]
    delta = 0
    # Their shared edge retains its crossing status when its endpoints are swapped.
    for neighbor, faces in adjacency[u]:
        if neighbor != v:
            delta += faces * ((group_v != assignment[neighbor]) - (group_u != assignment[neighbor]))
    for neighbor, faces in adjacency[v]:
        if neighbor != u:
            delta += faces * ((group_u != assignment[neighbor]) - (group_v != assignment[neighbor]))
    return delta


def full_host_cut(assignment: list[int], ranks: list[int], rank_to_local: dict[int, int],
                  host_edges: list[dict]) -> int:
    return sum(edge["faces"] for edge in host_edges
               if assignment[rank_to_local[edge["a"]]] != assignment[rank_to_local[edge["b"]]])


def normalize_groups(ranks: list[int], assignment: list[int]) -> tuple[list[int], list[list[int]]]:
    groups = [[rank for rank, label in zip(ranks, assignment) if label == group]
              for group in range(NUMA_GROUPS_PER_HOST)]
    order = sorted(range(NUMA_GROUPS_PER_HOST), key=lambda group: min(groups[group]))
    remap = {old: new for new, old in enumerate(order)}
    normalized = [remap[label] for label in assignment]
    members = [[rank for rank, label in zip(ranks, normalized) if label == group]
               for group in range(NUMA_GROUPS_PER_HOST)]
    return normalized, members


def group_metrics(host: int, ranks: list[int], assignment: list[int], edges: list[dict]) -> dict:
    rank_to_local = {rank: index for index, rank in enumerate(ranks)}
    matrix = [[0] * NUMA_GROUPS_PER_HOST for _ in range(NUMA_GROUPS_PER_HOST)]
    external = [0] * NUMA_GROUPS_PER_HOST
    within = [0] * NUMA_GROUPS_PER_HOST
    rank_set = set(ranks)
    for edge in edges:
        if edge["a"] not in rank_set or edge["b"] not in rank_set:
            continue
        group_a = assignment[rank_to_local[edge["a"]]]
        group_b = assignment[rank_to_local[edge["b"]]]
        left, right = sorted((group_a, group_b))
        matrix[left][right] += edge["faces"]
        if group_a == group_b:
            within[group_a] += edge["faces"]
        else:
            external[group_a] += edge["faces"]
            external[group_b] += edge["faces"]
    return {
        "host_group": host,
        "numa_matrix_unique_faces_upper_triangle": matrix,
        "matrix_convention": "Each undirected edge is counted once in [min(group_a,group_b)][max(group_a,group_b)]; lower triangle zero.",
        "same_host_cross_numa_faces": sum(external) // 2,
        "external_faces_by_logical_numa_group": external,
        "max_logical_numa_group_external_faces": max(external),
        "within_numa_faces_by_logical_numa_group": within,
    }


def steepest_descent(host: int, ranks: list[int], seed_assignment: list[int], host_edges: list[dict],
                     adjacency: list[list[tuple[int, int]]], deadline: float) -> tuple[list[int], int, list[dict], bool]:
    rank_to_local = {rank: index for index, rank in enumerate(ranks)}
    assignment = seed_assignment[:]
    current = full_host_cut(assignment, ranks, rank_to_local, host_edges)
    trail = [{"move": 0, "same_host_cross_numa_faces": current, "event": "start"}]
    complete = True
    while True:
        if time.monotonic() >= deadline:
            complete = False
            break
        best_move = None
        pairs_checked = 0
        for left_index, left in enumerate(ranks):
            for right in ranks[left_index + 1:]:
                if assignment[rank_to_local[left]] == assignment[rank_to_local[right]]:
                    continue
                delta = swap_delta(left, right, GLOBAL_ASSIGNMENT, adjacency)
                if delta < 0 and (best_move is None or (delta, left, right) < best_move):
                    best_move = (delta, left, right)
                pairs_checked += 1
                if pairs_checked % 4096 == 0 and time.monotonic() >= deadline:
                    complete = False
                    break
            if not complete:
                break
        if not complete or best_move is None:
            break
        delta, left, right = best_move
        left_i, right_i = rank_to_local[left], rank_to_local[right]
        before = [assignment[left_i], assignment[right_i]]
        assignment[left_i], assignment[right_i] = before[1], before[0]
        GLOBAL_ASSIGNMENT[left], GLOBAL_ASSIGNMENT[right] = before[1], before[0]
        recomputed = full_host_cut(assignment, ranks, rank_to_local, host_edges)
        require(recomputed - current == delta, f"host {host}: steepest swap delta mismatch")
        current = recomputed
        trail.append({"move": len(trail), "swap_ranks": [left, right], "groups_before": before,
                      "delta_faces": delta, "same_host_cross_numa_faces": current})
    return assignment, current, trail, complete


GLOBAL_ASSIGNMENT: list[int] = []


def main() -> None:
    global GLOBAL_ASSIGNMENT
    started = time.monotonic()
    graph_bytes = GRAPH_PATH.read_bytes()
    parent_bytes = PARENT_SCREEN_PATH.read_bytes()
    graph = json.loads(graph_bytes)
    parent = json.loads(parent_bytes)
    require(sha256(graph_bytes) == parent["graph_file_sha256"], "parent mapping does not match the validated graph")
    require(graph["ranks"] == RANKS and len(graph["edges"]) == 2887,
            "parent graph rank/edge invariant changed")
    require(parent["state"] == "OFFLINE_512_RANK_GROUP_SCREEN_COMPLETE", "parent screen is not complete")

    edges = graph["edges"]
    host_assignment = parent["candidate"]["rank_to_logical_host"]
    require(len(host_assignment) == RANKS and sorted(Counter(host_assignment).values()) == [RANKS_PER_HOST] * HOSTS,
            "parent host grouping is not four sets of 128")
    host_members = [[rank for rank, host in enumerate(host_assignment) if host == group]
                    for group in range(HOSTS)]
    require(host_members == parent["candidate"]["logical_host_members"], "parent host membership list disagrees")
    require(sorted(rank for members in host_members for rank in members) == list(range(RANKS)),
            "parent host mapping is not a 512-rank bijection")
    parent_permutation = parent["candidate"]["full_rank_permutation_group_major"]
    require(len(parent_permutation) == RANKS and sorted(parent_permutation) == list(range(RANKS)),
            "parent full permutation is not a rank bijection")
    require(parent_permutation[0] == 0, "parent permutation does not keep rank 0 first")

    original_host = [rank // RANKS_PER_HOST for rank in range(RANKS)]
    original_numa = [(rank % RANKS_PER_HOST) // RANKS_PER_NUMA_GROUP for rank in range(RANKS)]
    parent_numa = [0] * RANKS
    for host in range(HOSTS):
        ordered = [rank for rank in parent_permutation if host_assignment[rank] == host]
        require(len(ordered) == RANKS_PER_HOST and ordered == sorted(host_members[host]),
                f"parent permutation host {host} is not sorted host membership")
        for slot, rank in enumerate(ordered):
            parent_numa[rank] = slot // RANKS_PER_NUMA_GROUP

    def cut_parts(numa_assignment: list[int], host_of: list[int]) -> dict:
        cross_host = 0
        same_host_cross_numa = 0
        within_numa = 0
        for edge in edges:
            a, b, faces = edge["a"], edge["b"], edge["faces"]
            if host_of[a] != host_of[b]:
                cross_host += faces
            elif numa_assignment[a] != numa_assignment[b]:
                same_host_cross_numa += faces
            else:
                within_numa += faces
        return {"cross_host_faces": cross_host,
                "same_host_cross_numa_faces": same_host_cross_numa,
                "within_host_same_numa_faces": within_numa}

    original_parts = cut_parts(original_numa, original_host)
    parent_parts = cut_parts(parent_numa, host_assignment)
    require(parent_parts["cross_host_faces"] == parent["candidate"]["cross_group_interface_cut_faces"] == 261110,
            "recomputed parent host cut disagrees with sealed parent result")
    require(sum(original_parts.values()) == sum(parent_parts.values()) == graph["baseline"]["cross_group_interface_faces"] +
            (sum(edge["faces"] for edge in edges) - graph["baseline"]["cross_group_interface_faces"]),
            "partition of unique interface faces does not sum to graph total")

    cells = graph["cells_by_rank"]
    host_cell_totals = [sum(cells[rank] for rank in members) for members in host_members]
    require(host_cell_totals == parent["candidate"]["cell_totals_by_logical_host"],
            "native rank cell counts do not reproduce parent host cell totals")
    host_edge_lists = [[] for _ in range(HOSTS)]
    host_adjacency = [[[] for _ in range(RANKS)] for _ in range(HOSTS)]
    for edge in edges:
        a, b = edge["a"], edge["b"]
        if host_assignment[a] == host_assignment[b]:
            host = host_assignment[a]
            host_edge_lists[host].append(edge)
            host_adjacency[host][a].append((b, edge["faces"]))
            host_adjacency[host][b].append((a, edge["faces"]))

    candidate_labels = [0] * RANKS
    control_labels = original_numa[:]
    host_results = []
    total_proposals = 0
    search_start = time.monotonic()
    deadline = search_start + SEARCH_BUDGET_SECONDS
    delta_rng = random.Random(SEED ^ 0x5A17)
    delta_checks = []
    GLOBAL_ASSIGNMENT = parent_numa[:]
    # Test swaps on the parent host mapping before altering any local mapping.
    for index in range(128):
        host = delta_rng.randrange(HOSTS)
        ranks = host_members[host]
        rank_to_local = {rank: i for i, rank in enumerate(ranks)}
        assignment = [parent_numa[rank] for rank in ranks]
        u_i, v_i = delta_rng.sample(range(RANKS_PER_HOST), 2)
        while assignment[u_i] == assignment[v_i]:
            v_i = delta_rng.randrange(RANKS_PER_HOST)
        u, v = ranks[u_i], ranks[v_i]
        old = full_host_cut(assignment, ranks, rank_to_local, host_edge_lists[host])
        delta = swap_delta(u, v, GLOBAL_ASSIGNMENT, host_adjacency[host])
        assignment[u_i], assignment[v_i] = assignment[v_i], assignment[u_i]
        new = full_host_cut(assignment, ranks, rank_to_local, host_edge_lists[host])
        require(new - old == delta, f"random swap delta validation failed at sample {index}")
        delta_checks.append({"index": index, "host": host, "ranks": [u, v], "incremental_delta_faces": delta,
                             "full_recomputed_delta_faces": new - old})

    GLOBAL_ASSIGNMENT = [0] * RANKS
    candidate_numa = parent_numa[:]

    for host in range(HOSTS):
        ranks = host_members[host]
        rank_to_local = {rank: index for index, rank in enumerate(ranks)}
        baseline = [parent_numa[rank] for rank in ranks]
        require(sorted(Counter(baseline).values()) == [RANKS_PER_NUMA_GROUP] * NUMA_GROUPS_PER_HOST,
                f"host {host}: parent logical NUMA groups are not 8 x 16")
        for rank in ranks:
            GLOBAL_ASSIGNMENT[rank] = parent_numa[rank]
        host_edges = host_edge_lists[host]
        adjacency = host_adjacency[host]
        baseline_cut = full_host_cut(baseline, ranks, rank_to_local, host_edges)

        # Start with a deterministic steepest-improvement path anchored at this host's baseline.
        baseline_path, baseline_path_cut, baseline_trail, baseline_complete = steepest_descent(
            host, ranks, baseline, host_edges, adjacency, deadline)
        best_assignment = baseline[:]
        best_cut = baseline_cut
        selected_path = "baseline"
        if baseline_path_cut < best_cut:
            best_assignment, best_cut = baseline_path, baseline_path_cut
            selected_path = "baseline_steepest"
        for rank, label in zip(ranks, best_assignment):
            GLOBAL_ASSIGNMENT[rank] = label

        # Seeded annealing stays inside the fixed 128-rank host and swaps equal-sized groups.
        rng = random.Random(SEED + host)
        anneal_assignment = best_assignment[:]
        group_members = [[rank for rank, label in zip(ranks, anneal_assignment) if label == group]
                         for group in range(NUMA_GROUPS_PER_HOST)]
        current = best_cut
        annealing_best = best_cut
        annealing_assignment = best_assignment[:]
        annealing_trail = [{"proposal": 0, "same_host_cross_numa_faces": best_cut,
                            "event": "baseline_or_deterministic_start"}]
        proposals = 0
        start_temp, end_temp = 18000.0, 2.0
        while proposals < PROPOSALS_PER_HOST and time.monotonic() < deadline:
            proposals += 1
            group_a = rng.randrange(NUMA_GROUPS_PER_HOST)
            group_b = rng.randrange(NUMA_GROUPS_PER_HOST - 1)
            if group_b >= group_a:
                group_b += 1
            u = group_members[group_a][rng.randrange(RANKS_PER_NUMA_GROUP)]
            v = group_members[group_b][rng.randrange(RANKS_PER_NUMA_GROUP)]
            delta = swap_delta(u, v, GLOBAL_ASSIGNMENT, adjacency)
            fraction = proposals / PROPOSALS_PER_HOST
            temperature = start_temp * ((end_temp / start_temp) ** fraction)
            if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                local_u, local_v = rank_to_local[u], rank_to_local[v]
                anneal_assignment[local_u], anneal_assignment[local_v] = group_b, group_a
                group_members[group_a][next(i for i, rank in enumerate(group_members[group_a]) if rank == u)] = v
                group_members[group_b][next(i for i, rank in enumerate(group_members[group_b]) if rank == v)] = u
                GLOBAL_ASSIGNMENT[u], GLOBAL_ASSIGNMENT[v] = group_b, group_a
                current += delta
                if current < annealing_best:
                    annealing_best = current
                    annealing_assignment = anneal_assignment[:]
                    annealing_trail.append({"proposal": proposals, "same_host_cross_numa_faces": current,
                                            "event": "accepted_balanced_swap"})
        total_proposals += proposals

        # Polish the best randomized mapping with a deterministic full swap-neighborhood scan.
        if time.monotonic() < deadline:
            for rank, label in zip(ranks, annealing_assignment):
                GLOBAL_ASSIGNMENT[rank] = label
            polished, polished_cut, polished_trail, polish_complete = steepest_descent(
                host, ranks, annealing_assignment, host_edges, adjacency, deadline)
            if polished_cut < best_cut:
                best_assignment, best_cut = polished, polished_cut
                selected_path = "annealing_then_steepest"
            elif annealing_best < best_cut:
                best_assignment, best_cut = annealing_assignment, annealing_best
                selected_path = "annealing_best"
        else:
            polished, polished_cut, polished_trail, polish_complete = annealing_assignment, annealing_best, [], False
            if annealing_best < best_cut:
                best_assignment, best_cut = annealing_assignment, annealing_best
                selected_path = "annealing_best_before_deadline"

        require(best_cut <= baseline_cut, f"host {host}: optimization worsened its own baseline")
        require(full_host_cut(best_assignment, ranks, rank_to_local, host_edges) == best_cut,
                f"host {host}: retained objective does not match full recomputation")
        require(sorted(Counter(best_assignment).values()) == [RANKS_PER_NUMA_GROUP] * NUMA_GROUPS_PER_HOST,
                f"host {host}: optimized NUMA groups are unbalanced")
        normalized, normalized_members = normalize_groups(ranks, best_assignment)
        for rank, label in zip(ranks, normalized):
            candidate_numa[rank] = label
        host_results.append({
            "host_group": host,
            "ranks": ranks,
            "parent_baseline_numa_labels_by_rank_order": baseline,
            "baseline_same_host_cross_numa_faces": baseline_cut,
            "baseline_steepest_final_faces": baseline_path_cut,
            "baseline_steepest_local_optimum_reached": baseline_complete,
            "baseline_steepest_trail": baseline_trail,
            "annealing_seed": SEED + host,
            "annealing_proposals": proposals,
            "annealing_best_faces": annealing_best,
            "annealing_best_trail": annealing_trail,
            "annealing_polish_final_faces": polished_cut,
            "annealing_polish_local_optimum_reached": polish_complete,
            "annealing_polish_trail": polished_trail,
            "selected_source": selected_path,
            "optimized_same_host_cross_numa_faces": best_cut,
            "improvement_faces": baseline_cut - best_cut,
            "optimized_numa_group_members": normalized_members,
            "optimized_numa_labels_by_rank_order": normalized,
            "cell_totals_by_logical_numa_group": [sum(cells[rank] for rank in group)
                                                    for group in normalized_members],
        })
        for rank, label in zip(ranks, normalized):
            GLOBAL_ASSIGNMENT[rank] = label

    total_elapsed = time.monotonic() - started
    search_elapsed = time.monotonic() - search_start
    require(total_elapsed < HARD_LIMIT_SECONDS,
            f"combined validation and search exceeded {HARD_LIMIT_SECONDS}s: {total_elapsed:.3f}")
    optimized_host = host_assignment[:]
    optimized_parts = cut_parts(candidate_numa, optimized_host)
    require(optimized_parts["cross_host_faces"] == parent_parts["cross_host_faces"],
            "optimization changed host membership/cross-host faces")
    require(optimized_parts["same_host_cross_numa_faces"] <= parent_parts["same_host_cross_numa_faces"],
            "optimized NUMA cut is worse than the parent mapping")
    require(sum(optimized_parts.values()) == sum(edge["faces"] for edge in edges),
            "optimized graph partition does not conserve all interface faces")

    normalized_global = [0] * RANKS
    numa_members = []
    permutation = []
    matrix_summaries = {"contiguous_control": [], "parent_mapping": [], "optimized": []}
    for host in range(HOSTS):
        ranks = host_members[host]
        local_parent = [parent_numa[rank] for rank in ranks]
        pnorm, pmembers = normalize_groups(ranks, local_parent)
        local_candidate = [candidate_numa[rank] for rank in ranks]
        cnorm, cmembers = normalize_groups(ranks, local_candidate)
        for rank, label in zip(ranks, cnorm):
            normalized_global[rank] = label
        numa_members.append(cmembers)
        for group in cmembers:
            permutation.extend(sorted(group))
        original_ranks = list(range(host * RANKS_PER_HOST, (host + 1) * RANKS_PER_HOST))
        original_local = [original_numa[rank] for rank in original_ranks]
        matrix_summaries["contiguous_control"].append(
            group_metrics(host, original_ranks, original_local, edges))
        matrix_summaries["parent_mapping"].append(group_metrics(host, ranks, pnorm, edges))
        matrix_summaries["optimized"].append(group_metrics(host, ranks, cnorm, edges))

    require(permutation[0] == 0 and sorted(permutation) == list(range(RANKS)),
            "optimized full permutation is not rank-zero-first 512-rank bijection")
    require([sum(1 for rank in permutation if host_assignment[rank] == host) for host in range(HOSTS)] ==
            [RANKS_PER_HOST] * HOSTS, "rendered permutation changed host rank counts")
    require([sum(1 for group in numa_members[host] for rank in group) for host in range(HOSTS)] ==
            [RANKS_PER_HOST] * HOSTS, "NUMA grouping lost ranks")

    original_host_cell_totals = [sum(cells[rank] for rank in range(RANKS) if original_host[rank] == host)
                                 for host in range(HOSTS)]
    qualification = {
        "state": "OFFLINE_FIXED_HOST_NUMA_GROUP_QUALIFICATION_PASS",
        "structural_checks_passed": True,
        "parent_graph_sha256": sha256(graph_bytes),
        "parent_screen_sha256": sha256(parent_bytes),
        "parent_candidate_host_cut_recomputed_faces": parent_parts["cross_host_faces"],
        "host_membership_fixed_to_parent_candidate": True,
        "parent_rank_ids_exactly_once": True,
        "host_group_sizes": [len(group) for group in host_members],
        "logical_numa_group_sizes_per_host": [RANKS_PER_NUMA_GROUP] * NUMA_GROUPS_PER_HOST,
        "optimized_full_permutation_bijection": len(permutation) == RANKS and len(set(permutation)) == RANKS,
        "rank_zero_first": permutation[0] == 0,
        "cross_host_cut_unchanged": optimized_parts["cross_host_faces"] == parent_parts["cross_host_faces"],
        "host_cell_totals_unchanged": host_cell_totals == parent["candidate"]["cell_totals_by_logical_host"],
        "random_swap_deltas_checked": len(delta_checks),
        "all_random_swap_deltas_match_full_cut": True,
        "topology_assumption": "Eight logical NUMA groups of 16 ranks per 128-rank host; fresh four-node NUMA topology and page placement are unverified.",
        "runtime_or_speedup_qualification": False,
    }
    result = {
        "state": "OFFLINE_FIXED_HOST_NUMA_TRADEOFF_COMPLETE",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parent_graph_sha256": sha256(graph_bytes),
        "parent_screen_sha256": sha256(parent_bytes),
        "seed": SEED,
        "search": {
            "method": "Per-host seeded simulated annealing with balanced swaps; deterministic best-improvement descent anchored at each host's parent baseline, then deterministic descent from annealing best",
            "proposals_per_host_limit": PROPOSALS_PER_HOST,
            "proposals_completed_total": total_proposals,
            "search_time_limit_seconds_total": SEARCH_BUDGET_SECONDS,
            "search_elapsed_seconds_total": search_elapsed,
            "total_local_elapsed_seconds": total_elapsed,
            "hard_limit_seconds_total": HARD_LIMIT_SECONDS,
            "no_global_optimum_claim": True,
        },
        "delta_validation": {"seed": SEED ^ 0x5A17, "checked_swaps": len(delta_checks),
                             "all_match_full_recomputation": True, "checks": delta_checks},
        "host_membership_fixed": True,
        "host_membership_source": "parent screen.json candidate.rank_to_logical_host",
        "ranks_per_host": [RANKS_PER_HOST] * HOSTS,
        "numa_groups_per_host": NUMA_GROUPS_PER_HOST,
        "ranks_per_logical_numa_group": RANKS_PER_NUMA_GROUP,
        "original_contiguous_control": {
            "host_assignment": "rank // 128",
            "numa_assignment_within_host": "(rank % 128) // 16",
            **original_parts,
            "host_cell_totals": original_host_cell_totals,
        },
        "parent_four_host_mapping": {
            "host_assignment": "unchanged parent screen candidate membership",
            "numa_assignment": "sorted ranks within each parent logical host, divided into consecutive groups of 16",
            **parent_parts,
            "host_cell_totals": host_cell_totals,
        },
        "optimized_fixed_host_mapping": {
            "host_assignment": "unchanged parent screen candidate membership",
            "numa_assignment": "independently optimized balanced groups of 16 within each fixed host set",
            **optimized_parts,
            "host_cell_totals": host_cell_totals,
            "rank_to_host": optimized_host,
            "rank_to_logical_numa_group_within_host": normalized_global,
            "numa_group_members_by_host": numa_members,
            "full_rank_permutation_host_numa_group_major": permutation,
            "rank_zero_first": permutation[0] == 0,
            "numa_group_interface_matrices": matrix_summaries["optimized"],
        },
        "per_host_search": host_results,
        "numa_interface_matrices": matrix_summaries,
        "tradeoff_summary": {
            "cross_host_faces_are_unchanged": optimized_parts["cross_host_faces"] == parent_parts["cross_host_faces"],
            "parent_cross_host_faces": parent_parts["cross_host_faces"],
            "original_cross_host_faces": original_parts["cross_host_faces"],
            "parent_same_host_cross_numa_faces": parent_parts["same_host_cross_numa_faces"],
            "optimized_same_host_cross_numa_faces": optimized_parts["same_host_cross_numa_faces"],
            "same_host_cross_numa_reduction_faces": parent_parts["same_host_cross_numa_faces"] -
                                                     optimized_parts["same_host_cross_numa_faces"],
            "original_same_host_cross_numa_faces": original_parts["same_host_cross_numa_faces"],
            "parent_host_cell_totals_unchanged": True,
            "physical_cost_weights": None,
        },
        "limitations": [
            "Eight NUMA groups of 16 ranks per host are a historical-topology assumption, not verified for the current four-node allocation.",
            "The parent candidate host sets are logical membership only; the original physical rank-to-host mapping is not available.",
            "No NUMA page placement, memory locality, process affinity, MPI communication, traffic or solver time was measured.",
            "Graph face counts are proxies, not bytes or hardware cost. No weighted objective combines host and NUMA cuts.",
            "The bounded seeded search with local swap improvement is not a global optimizer and proves no speedup.",
        ],
    }
    QUALIFICATION_PATH.write_text(json.dumps(qualification, indent=2) + "\n")
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"state": result["state"], "elapsed_seconds": total_elapsed,
                      "parent_host_cut": parent_parts["cross_host_faces"],
                      "original_same_host_cross_numa_cut": original_parts["same_host_cross_numa_faces"],
                      "parent_same_host_cross_numa_cut": parent_parts["same_host_cross_numa_faces"],
                      "optimized_same_host_cross_numa_cut": optimized_parts["same_host_cross_numa_faces"],
                      "reduction": result["tradeoff_summary"]["same_host_cross_numa_reduction_faces"]}, indent=2))


if __name__ == "__main__":
    main()
