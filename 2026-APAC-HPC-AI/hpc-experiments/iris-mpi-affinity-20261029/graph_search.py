#!/usr/bin/env python3
"""Offline balanced NUMA rank bisection over retained processor-face graphs."""
from __future__ import annotations

import hashlib
import json
import pathlib
import random
import sys
import time


ROOT = pathlib.Path(__file__).resolve().parent
INPUT = ROOT / "processor-interface-graphs.json"
OUTPUT = ROOT / "graph-search.json"
SEED_BASE = 2026
SEED_COUNT = 32
TIME_LIMIT_SECONDS = 20.0
CELL_LOAD_FACTOR = 1.01
MIN_REQUIRED_REDUCTION_PERCENT = 5.0
N_RANKS = 56
N_PER_NUMA = 28
DEADLINE = time.monotonic() + TIME_LIMIT_SECONDS


def check_deadline() -> None:
    if time.monotonic() > DEADLINE:
        raise TimeoutError(f"graph search exceeded {TIME_LIMIT_SECONDS:.0f} seconds")


def load_graphs() -> tuple[dict, dict, dict]:
    raw = INPUT.read_bytes()
    data = json.loads(raw)
    if data.get("actual_probe_job") != "2294358":
        raise ValueError("input does not identify the reviewed actual affinity probe")
    orders = data.get("orders", {})
    if set(orders) != {"xyz", "zyx"}:
        raise ValueError("expected exactly xyz and zyx processor graphs")

    graphs = {}
    baseline = {rank: 0 if rank < N_PER_NUMA else 1 for rank in range(N_RANKS)}
    for order, record in orders.items():
        edges = []
        seen = set()
        for row in record["graph_edges"]:
            if len(row) != 3:
                raise ValueError(f"{order}: malformed graph edge {row!r}")
            left, right, weight = map(int, row)
            if not (0 <= left < right < N_RANKS and weight > 0):
                raise ValueError(f"{order}: invalid graph edge {row!r}")
            if (left, right) in seen:
                raise ValueError(f"{order}: duplicate graph edge {(left, right)}")
            seen.add((left, right))
            edges.append((left, right, weight))
        if sum(edge[2] for edge in edges) != int(record["unique_interface_faces"]):
            raise ValueError(f"{order}: interface-face sum does not match retained graph total")
        cells = {int(rank): int(count) for rank, count in record["cell_counts"].items()}
        if set(cells) != set(range(N_RANKS)) or any(count <= 0 for count in cells.values()):
            raise ValueError(f"{order}: invalid per-rank cell counts")
        if sum(cells.values()) != 65_334_765:
            raise ValueError(f"{order}: cell count differs from retained 65,334,765 total")
        actual_baseline = record["maps"]["A-default"]["cross_NUMA_unique_faces"]
        if cut(edges, baseline) != actual_baseline:
            raise ValueError(f"{order}: default partition does not reproduce actual-probe cross-face count")
        graphs[order] = {"edges": edges, "cells": cells, "record": record}

    digest = hashlib.sha256(raw).hexdigest()
    return graphs, baseline, {"sha256": digest, "observed_utc": data["observed_utc"]}


def cut(edges: list[tuple[int, int, int]], side: dict[int, int]) -> int:
    return sum(weight for left, right, weight in edges if side[left] != side[right])


def pair_cut(edges: list[tuple[int, int, int]], side: dict[int, int]) -> int:
    return sum(1 for left, right, _ in edges if side[left] != side[right])


def loads(cells: dict[int, int], side: dict[int, int]) -> tuple[int, int]:
    totals = [0, 0]
    for rank, count in cells.items():
        totals[side[rank]] += count
    return totals[0], totals[1]


def feasible(side: dict[int, int], graphs: dict, caps: dict[str, int]) -> bool:
    if sum(side.values()) != N_PER_NUMA:
        return False
    for order, graph in graphs.items():
        if max(loads(graph["cells"], side)) > caps[order]:
            return False
    return True


def combined_adjacency(graphs: dict, baseline: dict[int, int]) -> dict[int, list[tuple[int, int]]]:
    combined: dict[int, list[tuple[int, int]]] = {rank: [] for rank in range(N_RANKS)}
    weights: dict[tuple[int, int], int] = {}
    scale = 1_000_000
    for graph in graphs.values():
        base_faces = cut(graph["edges"], baseline)
        for left, right, weight in graph["edges"]:
            normalized = round(weight * scale / base_faces)
            weights[(left, right)] = weights.get((left, right), 0) + normalized
    for (left, right), weight in weights.items():
        combined[left].append((right, weight))
        combined[right].append((left, weight))
    return combined


def swap_delta(left: int, right: int, side: dict[int, int], adjacency: dict) -> int:
    """Return combined weighted cut delta for swapping opposite-side vertices."""
    delta = 0
    for neighbor, weight in adjacency[left]:
        if neighbor == right:
            continue
        old_cross = side[left] != side[neighbor]
        new_cross = side[right] != side[neighbor]
        delta += weight * (int(new_cross) - int(old_cross))
    for neighbor, weight in adjacency[right]:
        if neighbor == left:
            continue
        old_cross = side[right] != side[neighbor]
        new_cross = side[left] != side[neighbor]
        delta += weight * (int(new_cross) - int(old_cross))
    return delta


def kl_refine(initial: dict[int, int], graphs: dict, caps: dict[str, int], adjacency: dict) -> dict[int, int]:
    """Kernighan-Lin pair-swap passes, constrained to the per-order cell caps."""
    side = dict(initial)
    if not feasible(side, graphs, caps):
        raise ValueError("attempted to refine an infeasible initial bisection")

    while True:
        check_deadline()
        start = dict(side)
        current_loads = {order: list(loads(graph["cells"], side)) for order, graph in graphs.items()}
        locked: set[int] = set()
        accepted_swaps: list[tuple[int, int]] = []
        deltas: list[int] = []
        temp = dict(side)

        for _ in range(N_PER_NUMA):
            check_deadline()
            best = None
            left_candidates = [r for r in range(N_RANKS) if temp[r] == 0 and r not in locked]
            right_candidates = [r for r in range(N_RANKS) if temp[r] == 1 and r not in locked]
            for left in left_candidates:
                for right in right_candidates:
                    next_loads = {}
                    valid = True
                    for order, graph in graphs.items():
                        a, b = current_loads[order]
                        a += graph["cells"][right] - graph["cells"][left]
                        b -= graph["cells"][right] - graph["cells"][left]
                        if max(a, b) > caps[order]:
                            valid = False
                            break
                        next_loads[order] = [a, b]
                    if not valid:
                        continue
                    delta = swap_delta(left, right, temp, adjacency)
                    choice = (delta, left, right, next_loads)
                    if best is None or choice[:3] < best[:3]:
                        best = choice
            if best is None:
                break
            delta, left, right, next_loads = best
            temp[left], temp[right] = temp[right], temp[left]
            current_loads = next_loads
            locked.update((left, right))
            accepted_swaps.append((left, right))
            deltas.append(delta)

        cumulative = 0
        best_gain = 0
        best_prefix = 0
        for index, delta in enumerate(deltas, start=1):
            cumulative += delta
            if cumulative < best_gain:
                best_gain = cumulative
                best_prefix = index
        if best_prefix == 0:
            return side
        side = dict(start)
        for left, right in accepted_swaps[:best_prefix]:
            side[left], side[right] = side[right], side[left]
        if not feasible(side, graphs, caps):
            raise AssertionError("KL prefix restoration violated a cell-load gate")


def score(side: dict[int, int], graph: dict, baseline: dict[int, int]) -> float:
    return cut(graph["edges"], side) / cut(graph["edges"], baseline)


def main() -> None:
    cpu_start = time.process_time()
    wall_start = time.monotonic()
    graphs, baseline, input_info = load_graphs()
    per_order = {}
    best_sides = {}
    seed_rows = {}
    best_seeds = {}
    for order, graph in graphs.items():
        check_deadline()
        one_graph = {order: graph}
        caps = {order: int(max(loads(graph["cells"], baseline)) * CELL_LOAD_FACTOR)}
        if not feasible(baseline, one_graph, caps):
            raise ValueError(f"{order}: retained default assignment fails its own cell-load cap")
        adjacency = combined_adjacency(one_graph, baseline)

        # Keep the actual default assignment as an unconditional fallback.
        best = dict(baseline)
        best_seed = "default"
        best_score = score(best, graph, baseline)
        seed_rows[order] = []
        for seed in range(SEED_BASE, SEED_BASE + SEED_COUNT):
            check_deadline()
            rng = random.Random(seed)
            for _ in range(100):
                side0 = set(rng.sample(range(N_RANKS), N_PER_NUMA))
                candidate = {rank: int(rank not in side0) for rank in range(N_RANKS)}
                if feasible(candidate, one_graph, caps):
                    break
            else:
                seed_rows[order].append({"seed": seed, "status": "skipped_no_feasible_start"})
                continue
            refined = kl_refine(candidate, one_graph, caps, adjacency)
            candidate_score = score(refined, graph, baseline)
            seed_rows[order].append({"seed": seed, "status": "completed", "normalized_cut": candidate_score})
            if candidate_score < best_score:
                best, best_score, best_seed = refined, candidate_score, seed
        best_sides[order] = best
        best_seeds[order] = best_seed

    check_deadline()
    per_order = {}
    improvements = []
    for order, graph in graphs.items():
        best = best_sides[order]
        baseline_faces = cut(graph["edges"], baseline)
        candidate_faces = cut(graph["edges"], best)
        reduction = 100.0 * (baseline_faces - candidate_faces) / baseline_faces
        improvements.append(reduction)
        base_load = loads(graph["cells"], baseline)
        candidate_load = loads(graph["cells"], best)
        max_allowed_load = int(max(base_load) * CELL_LOAD_FACTOR)
        per_order[order] = {
            "graph": {
                "ranks": N_RANKS,
                "weighted_edges": len(graph["edges"]),
                "total_unique_interface_faces": graph["record"]["unique_interface_faces"],
                "total_cells": sum(graph["cells"].values()),
            },
            "baseline": {
                "rank_groups": {"NUMA0": [r for r in range(N_RANKS) if baseline[r] == 0],
                                "NUMA1": [r for r in range(N_RANKS) if baseline[r] == 1]},
                "rank_counts": {"NUMA0": N_PER_NUMA, "NUMA1": N_PER_NUMA},
                "cell_loads": {"NUMA0": base_load[0], "NUMA1": base_load[1]},
                "max_cell_load": max(base_load),
                "cross_NUMA_unique_faces": baseline_faces,
                "cross_NUMA_neighbor_pairs": pair_cut(graph["edges"], baseline),
            },
            "candidate": {
                "rank_groups": {"NUMA0": [r for r in range(N_RANKS) if best[r] == 0],
                                "NUMA1": [r for r in range(N_RANKS) if best[r] == 1]},
                "rank_counts": {"NUMA0": N_PER_NUMA, "NUMA1": N_PER_NUMA},
                "cell_loads": {"NUMA0": candidate_load[0], "NUMA1": candidate_load[1]},
                "max_cell_load": max(candidate_load),
                "max_allowed_cell_load": max_allowed_load,
                "cross_NUMA_unique_faces": candidate_faces,
                "cross_NUMA_neighbor_pairs": pair_cut(graph["edges"], best),
                "face_reduction_percent_vs_default": reduction,
            },
        }

    report = {
        "schema_version": 1,
        "status": "PASS",
        "created_local_date": "2026-10-29",
        "actual_affinity_probe_job": "2294358",
        "input": {"file": INPUT.name, **input_info},
        "objective": "Independently minimize weighted cross-NUMA unique-interface faces for each decomposition order, with exactly 28 ranks per NUMA and maximum cell load <= 1.01 * that order's baseline maximum.",
        "algorithm": {
            "name": "Deterministic multistart Kernighan-Lin pair-swap bisection",
            "initial_assignments_per_order": ["actual default contiguous-rank partition", f"{SEED_COUNT} random balanced starts with seeds {SEED_BASE} through {SEED_BASE + SEED_COUNT - 1}"],
            "seed_results_by_order": seed_rows,
            "best_start_by_order": best_seeds,
            "cell_load_factor": CELL_LOAD_FACTOR,
            "runtime_limit_seconds": TIME_LIMIT_SECONDS,
        },
        "orders": per_order,
        "decision": {
            "required_reduction_percent_per_order": MIN_REQUIRED_REDUCTION_PERCENT,
            "zyx_screen_candidate_reduction_percent": per_order["zyx"]["candidate"]["face_reduction_percent_vs_default"],
            "zyx_screen_candidate_exceeds_threshold": per_order["zyx"]["candidate"]["face_reduction_percent_vs_default"] > MIN_REQUIRED_REDUCTION_PERCENT,
            "xyz_screen_candidate_reduction_percent": per_order["xyz"]["candidate"]["face_reduction_percent_vs_default"],
            "xyz_screen_candidate_exceeds_threshold": per_order["xyz"]["candidate"]["face_reduction_percent_vs_default"] > MIN_REQUIRED_REDUCTION_PERCENT,
            "both_order_specific_candidates_exceed_threshold": min(improvements) > MIN_REQUIRED_REDUCTION_PERCENT,
            "interpretation": "The separate zyx partition is a justified candidate for a later short native ABBA screen after runtime rank-to-core binding is reviewed. The proxy does not establish solver speedup.",
        },
        "limitations": [
            "Unique interface-face count is a logical communication proxy; it is not bytes, message latency, memory-page placement, or measured hardware traffic.",
            "The graph comes from the retained 56-rank processor boundary files and describes only these exact xyz/zyx decompositions.",
            "A rank-to-NUMA grouping does not itself specify a verified rank-to-core mapping or runtime binding command.",
            "The heuristic is deterministic and bounded but does not prove a globally optimal graph bisection.",
        ],
        "elapsed_seconds": time.monotonic() - wall_start,
        "process_cpu_seconds": time.process_time() - cpu_start,
    }
    if report["elapsed_seconds"] >= TIME_LIMIT_SECONDS or report["process_cpu_seconds"] >= TIME_LIMIT_SECONDS:
        raise TimeoutError("time limit exceeded before report emission")
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": report["status"],
        "best_start_by_order": best_seeds,
        "candidate_rank_groups_by_order": {
            order: per_order[order]["candidate"]["rank_groups"] for order in per_order
        },
        "face_reduction_percent": {order: per_order[order]["candidate"]["face_reduction_percent_vs_default"] for order in per_order},
        "zyx_screen_candidate_exceeds_threshold": report["decision"]["zyx_screen_candidate_exceeds_threshold"],
        "elapsed_seconds": report["elapsed_seconds"],
        "process_cpu_seconds": report["process_cpu_seconds"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
