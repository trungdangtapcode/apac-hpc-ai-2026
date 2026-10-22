"""Seeded offline search for an equal-capacity rank-to-logical-NUMA mapping.

This analyzes the immutable default Scotch rank graph only. It does not alter
processor folders, partition files, solver inputs, or any runtime payload.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent / "nscc-cpu-numa-scotch128-20261021"
GRAPH_PATH = EXP / "validated-graph-default_scotch.json"
PLACEMENT_PATH = EXP / "placement-analysis.json"
INITIAL_RESULT_PATH = HERE / "screen-initial.json"
OUTPUT_PATH = HERE / "screen.json"
SEED = 2026
MAX_PROPOSALS = 1_000_000
MAX_RUNTIME_SECONDS = 29.0


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cut_weight(assignment: list[int], edges: list[dict]) -> int:
    return sum(edge["faces"] for edge in edges if assignment[edge["a"]] != assignment[edge["b"]])


def swap_delta(u: int, v: int, assignment: list[int], adjacency: list[list[tuple[int, int]]]) -> int:
    gu, gv = assignment[u], assignment[v]
    delta = 0
    for neighbor, weight in adjacency[u]:
        if neighbor != v:
            delta += weight * ((gv != assignment[neighbor]) - (gu != assignment[neighbor]))
    for neighbor, weight in adjacency[v]:
        if neighbor != u:
            delta += weight * ((gu != assignment[neighbor]) - (gv != assignment[neighbor]))
    return delta


def main() -> None:
    overall_start = time.monotonic()
    graph_bytes = GRAPH_PATH.read_bytes()
    placement_bytes = PLACEMENT_PATH.read_bytes()
    initial_result_bytes = INITIAL_RESULT_PATH.read_bytes()
    initial_result = json.loads(initial_result_bytes)
    graph = json.loads(graph_bytes)
    placement = json.loads(placement_bytes)
    ranks = graph["ranks"]
    edges = graph["edges"]
    require(ranks == 128, f"expected 128 ranks, got {ranks}")
    require(placement["mpi_ranks"] == 128 and placement["numa_nodes"] == 8 and
            placement["ranks_per_numa"] == 16 and placement["rank_block_matches_numa"],
            "retained placement evidence does not establish the 8x16 baseline")
    require(sorted(row["rank"] for row in placement["mapping"]) == list(range(ranks)),
            "placement mapping rank coverage mismatch")
    require(all(row["rank"] == row["cpu"] for row in placement["mapping"]),
            "expected retained rank-equals-CPU placement map")

    baseline_assignment = [rank // 16 for rank in range(ranks)]
    baseline_cut = cut_weight(baseline_assignment, edges)
    require(baseline_cut == 371658, f"independent baseline cut mismatch: {baseline_cut}")
    total_faces = sum(edge["faces"] for edge in edges)
    require(total_faces == 1549377, f"total interface faces changed: {total_faces}")
    rank_faces = [0] * ranks
    neighbors = [0] * ranks
    adjacency = [[] for _ in range(ranks)]
    for edge in edges:
        a, b, weight = edge["a"], edge["b"], edge["faces"]
        require(0 <= a < ranks and 0 <= b < ranks and a < b and weight > 0,
                f"invalid graph edge {edge}")
        rank_faces[a] += weight
        rank_faces[b] += weight
        neighbors[a] += 1
        neighbors[b] += 1
        adjacency[a].append((b, weight))
        adjacency[b].append((a, weight))
    max_rank_faces = max(rank_faces)
    max_rank_neighbors = max(neighbors)
    require(max_rank_faces == 42141, f"max-rank interface faces changed: {max_rank_faces}")
    require(max_rank_neighbors == 35, f"max rank fanout changed: {max_rank_neighbors}")
    require(len(edges) == len({(edge["a"], edge["b"]) for edge in edges}),
            "duplicate undirected graph edge")

    rng = random.Random(SEED)
    baseline_assignment = [rank // 16 for rank in range(ranks)]
    best_cut = baseline_cut
    best_assignment = baseline_assignment[:]
    best_trail = [{"proposal": 0, "cross_group_faces": baseline_cut}]
    start = time.monotonic()
    restart_count = 20
    proposals_per_restart = MAX_PROPOSALS // restart_count
    start_temperature = 12000.0
    end_temperature = 5.0
    proposal_number = 0

    for restart_index in range(restart_count):
        assignment = [group for group in range(8) for _ in range(16)]
        rng.shuffle(assignment)
        members = [[rank for rank, group in enumerate(assignment) if group == target]
                   for target in range(8)]
        current_cut = cut_weight(assignment, edges)
        if current_cut < best_cut:
            best_cut = current_cut
            best_assignment = assignment[:]
            best_trail.append({"proposal": proposal_number,
                               "cross_group_faces": best_cut,
                               "event": "random_balanced_restart"})

        for local_proposal in range(proposals_per_restart):
            proposal_number += 1
            ga = rng.randrange(8)
            gb = rng.randrange(7)
            if gb >= ga:
                gb += 1
            ia = rng.randrange(16)
            ib = rng.randrange(16)
            u = members[ga][ia]
            v = members[gb][ib]
            delta = swap_delta(u, v, assignment, adjacency)
            fraction = local_proposal / max(1, proposals_per_restart - 1)
            temperature = start_temperature * ((end_temperature / start_temperature) ** fraction)
            accept = delta <= 0 or rng.random() < math.exp(-delta / temperature)
            if not accept:
                continue
            assignment[u], assignment[v] = gb, ga
            members[ga][ia], members[gb][ib] = v, u
            current_cut += delta
            if current_cut < best_cut:
                best_cut = current_cut
                best_assignment = assignment[:]
                best_trail.append({"proposal": proposal_number,
                                   "cross_group_faces": best_cut,
                                   "event": "accepted_swap"})

    annealing_elapsed = time.monotonic() - start
    annealing_best_cut = best_cut
    annealing_best_assignment = best_assignment[:]

    def steepest_descent(seed_assignment: list[int], label: str, first_proposal: int) -> tuple[list[int], int, list[dict], bool]:
        assignment = seed_assignment[:]
        current_cut = cut_weight(assignment, edges)
        trail = [{"move": 0, "cross_group_faces": current_cut, "event": "start"}]
        complete = True
        while True:
            if time.monotonic() - overall_start >= MAX_RUNTIME_SECONDS:
                complete = False
                break
            best_move = None
            for u in range(ranks):
                for v in range(u + 1, ranks):
                    if assignment[u] == assignment[v]:
                        continue
                    delta = swap_delta(u, v, assignment, adjacency)
                    if delta < 0 and (best_move is None or (delta, u, v) < best_move):
                        best_move = (delta, u, v)
            if best_move is None:
                break
            delta, u, v = best_move
            old_u, old_v = assignment[u], assignment[v]
            assignment[u], assignment[v] = old_v, old_u
            next_cut = cut_weight(assignment, edges)
            require(next_cut - current_cut == delta,
                    f"steepest descent delta disagrees with full cut: {label} {(u, v)}")
            current_cut = next_cut
            trail.append({"move": len(trail), "proposal": first_proposal + len(trail) - 1,
                          "swap_ranks": [u, v], "groups_before": [old_u, old_v],
                          "delta_faces": delta, "cross_group_faces": current_cut})
        return assignment, current_cut, trail, complete

    # Independently check incremental swap deltas against full edge recomputation.
    delta_rng = random.Random(SEED ^ 0x5A17)
    delta_check_assignment = baseline_assignment[:]
    delta_check_rows = []
    for check_index in range(100):
        u = delta_rng.randrange(ranks)
        v = delta_rng.randrange(ranks)
        while u == v or delta_check_assignment[u] == delta_check_assignment[v]:
            v = delta_rng.randrange(ranks)
        old_cut = cut_weight(delta_check_assignment, edges)
        delta = swap_delta(u, v, delta_check_assignment, adjacency)
        delta_check_assignment[u], delta_check_assignment[v] = (delta_check_assignment[v],
                                                                 delta_check_assignment[u])
        new_cut = cut_weight(delta_check_assignment, edges)
        require(new_cut - old_cut == delta, f"delta validation mismatch at swap {check_index}")
        delta_check_rows.append({"index": check_index, "ranks": [u, v],
                                 "delta_faces": delta, "full_recomputed_delta_faces": new_cut - old_cut})

    prior_best = initial_result["candidate"]["rank_to_logical_group"]
    require(len(prior_best) == ranks and sorted(prior_best.count(group) for group in range(8)) == [16] * 8,
            "preserved initial best map is not balanced")
    start_assignments = [
        ("baseline_rank_div_16", baseline_assignment),
        ("preserved_initial_best", prior_best),
        ("current_annealing_best", annealing_best_assignment),
    ]
    descent_results = []
    best_trail = [{"proposal": 0, "cross_group_faces": baseline_cut, "event": "baseline"}]
    global_best_cut = baseline_cut
    global_best_assignment = baseline_assignment[:]
    proposal_offset = MAX_PROPOSALS
    for label, seed_assignment in start_assignments:
        final_assignment, final_cut, descent_trail, complete = steepest_descent(
            seed_assignment, label, proposal_offset)
        proposal_offset += len(descent_trail) - 1
        descent_results.append({"start": label,
                                "start_cross_group_faces": cut_weight(seed_assignment, edges),
                                "final_cross_group_faces": final_cut,
                                "local_optimum_reached": complete,
                                "trail": descent_trail})
        if final_cut < global_best_cut:
            global_best_cut = final_cut
            global_best_assignment = final_assignment[:]
            best_trail.extend({"proposal": proposal_offset - len(descent_trail) + i,
                               "cross_group_faces": row["cross_group_faces"],
                               "event": f"{label}_steepest_swap"}
                              for i, row in enumerate(descent_trail[1:], start=1))
        if time.monotonic() - overall_start >= MAX_RUNTIME_SECONDS:
            break

    best_cut = global_best_cut
    best_assignment = global_best_assignment
    candidate_cut = cut_weight(best_assignment, edges)
    elapsed = time.monotonic() - overall_start
    require(elapsed < 30.0, f"screen exceeded 30 second runtime limit: {elapsed:.3f}s")
    require(candidate_cut == best_cut, "best search trail/objective mismatch")
    candidate_groups = [[rank for rank in range(ranks) if best_assignment[rank] == group]
                        for group in range(8)]
    require(sorted(rank for group in candidate_groups for rank in group) == list(range(ranks)),
            "candidate mapping is not a rank bijection")
    require(all(len(group) == 16 for group in candidate_groups),
            "candidate logical group capacity mismatch")
    require(candidate_cut <= baseline_cut, "candidate cut worse than starting baseline")
    rank_permutation = [rank for group in candidate_groups for rank in group]
    require(sorted(rank_permutation) == list(range(ranks)), "rank permutation is not bijective")
    rank_to_slot = [0] * ranks
    for slot, rank in enumerate(rank_permutation):
        rank_to_slot[rank] = slot

    result = {
        "state": "OFFLINE_BALANCED_RANK_MAPPING_SCREEN_COMPLETE",
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seed": SEED,
        "algorithm": "20 seeded random balanced starts with simulated annealing, followed by deterministic steepest improving balanced swaps from the baseline and preserved initial/current best mappings",
        "proposals": proposal_number,
        "restarts": restart_count,
        "annealing_runtime_seconds": annealing_elapsed,
        "runtime_seconds": elapsed,
        "runtime_limit_seconds": MAX_RUNTIME_SECONDS,
        "preserved_initial_result_sha256": sha256(initial_result_bytes),
        "delta_validation": {"seed": SEED ^ 0x5A17, "checked_swaps": len(delta_check_rows),
                             "all_match_full_edge_recomputation": True,
                             "swap_deltas": delta_check_rows},
        "steepest_descent_runs": descent_results,
        "graph_source": str(GRAPH_PATH.relative_to(HERE.parent)),
        "graph_sha256": sha256(graph_bytes),
        "placement_source": str(PLACEMENT_PATH.relative_to(HERE.parent)),
        "placement_sha256": sha256(placement_bytes),
        "unchanged_graph_invariants": {
            "ranks": ranks,
            "undirected_edges": len(edges),
            "total_interface_faces": total_faces,
            "max_rank_interface_faces": max_rank_faces,
            "max_rank_neighbors": max_rank_neighbors,
        },
        "baseline": {
            "assignment": "rank // 16",
            "logical_group_capacity": [16] * 8,
            "cross_group_faces_recomputed_from_edges": baseline_cut,
        },
        "candidate": {
            "rank_to_logical_group": best_assignment,
            "logical_group_members": candidate_groups,
            "rank_permutation_group_major": rank_permutation,
            "rank_to_group_major_slot": rank_to_slot,
            "logical_group_capacity": [len(group) for group in candidate_groups],
            "cross_group_faces_recomputed_from_edges": candidate_cut,
            "reduction_faces": baseline_cut - candidate_cut,
            "reduction_percent": 100.0 * (baseline_cut - candidate_cut) / baseline_cut,
        },
        "annealing_best_before_refinement": {
            "cross_group_faces": annealing_best_cut,
            "rank_to_logical_group": annealing_best_assignment,
        },
        "best_objective_trail": best_trail,
        "decision": "CLOSE_OFFLINE_BRANCH_NO_MATERIAL_GRAPH_GAIN" if
                    (baseline_cut - candidate_cut) / baseline_cut < 0.01 else
                    "REVIEW_FOR_BUDGETED_RUNTIME_SCREEN",
        "interpretation_limits": [
            "This is only a mapping of unchanged Scotch rank IDs to eight equal logical groups.",
            "It does not relabel processor directories or change any decomposition, graph, cells, or fields.",
            "A logical group is physical NUMA only after fresh runtime placement verifies it on the allocated node.",
            "Graph face weights are not measured memory traffic, MPI wait time, or solver critical path.",
            "No solve timing or speedup is measured by this offline search.",
        ],
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "state": result["state"],
        "seed": SEED,
        "proposals": MAX_PROPOSALS,
        "runtime_seconds": elapsed,
        "graph_sha256": result["graph_sha256"],
        "baseline_cross_group_faces": baseline_cut,
        "candidate_cross_group_faces": candidate_cut,
        "reduction_faces": baseline_cut - candidate_cut,
        "reduction_percent": result["candidate"]["reduction_percent"],
        "best_trail_points": len(best_trail),
    }, indent=2))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


if __name__ == "__main__":
    main()
