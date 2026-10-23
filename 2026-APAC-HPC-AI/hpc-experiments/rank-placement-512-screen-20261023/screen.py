#!/usr/bin/env python3
"""Validate a retained 512-rank graph and screen balanced logical host groups."""
from __future__ import annotations

import datetime
import hashlib
import json
import math
import random
import re
import statistics
import sys
import time
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
COLLECTED = HERE / "collected"
BOUNDARIES = COLLECTED / "boundaries"
GRAPH_PATH = HERE / "graph.json"
VALIDATION_PATH = HERE / "graph-validation.json"
OUTPUT_PATH = HERE / "screen.json"
RANKS = 512
GROUPS = 4
GROUP_SIZE = 128
SEED = 2026
MAX_PROPOSALS = 1_500_000
SEARCH_BUDGET_SECONDS = 25.0
HARD_LIMIT_SECONDS = 30.0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def full_cut(assignment: list[int], edges: list[dict]) -> int:
    return sum(edge["faces"] for edge in edges if assignment[edge["a"]] != assignment[edge["b"]])


def swap_delta(u: int, v: int, assignment: list[int], adjacency: list[list[tuple[int, int]]]) -> int:
    group_u, group_v = assignment[u], assignment[v]
    delta = 0
    for neighbor, faces in adjacency[u]:
        if neighbor != v:
            delta += faces * ((group_v != assignment[neighbor]) - (group_u != assignment[neighbor]))
    for neighbor, faces in adjacency[v]:
        if neighbor != u:
            delta += faces * ((group_u != assignment[neighbor]) - (group_v != assignment[neighbor]))
    # The shared u-v edge retains its crossing status when its endpoints are swapped.
    return delta


def parse_boundary(rank: int, raw: bytes) -> tuple[list[dict], int]:
    text = raw.decode("ascii", errors="strict")
    count_match = re.search(r"(?m)^\s*(\d+)\s*$\s*^\s*\(\s*$", text)
    require(count_match is not None, f"processor{rank}: patch count/list header missing")
    declared_count = int(count_match.group(1))
    body_start = count_match.end()
    body_end = text.rfind("\n)")
    require(body_end > body_start, f"processor{rank}: patch list close missing")
    body = text[body_start:body_end]
    pattern = re.compile(r"(?m)^[ \t]*([^\s{}()]+)[ \t]*\n[ \t]*\{(.*?)^[ \t]*\}", re.S)
    patches = []
    cursor = 0
    for match in pattern.finditer(body):
        require(not body[cursor:match.start()].strip(), f"processor{rank}: unparsed boundary content")
        name, fields = match.group(1), match.group(2)
        face_match = re.search(r"(?m)^\s*nFaces\s+(\d+)\s*;", fields)
        type_match = re.search(r"(?m)^\s*type\s+(\w+)\s*;", fields)
        require(face_match and type_match, f"processor{rank}/{name}: missing type or nFaces")
        patch = {"name": name, "type": type_match.group(1), "nFaces": int(face_match.group(1))}
        if patch["type"] == "processor":
            proc_match = re.fullmatch(r"procBoundary(\d+)to(\d+)", name)
            my_match = re.search(r"(?m)^\s*myProcNo\s+(\d+)\s*;", fields)
            neighbor_match = re.search(r"(?m)^\s*neighbProcNo\s+(\d+)\s*;", fields)
            require(proc_match and my_match and neighbor_match,
                    f"processor{rank}/{name}: malformed processor patch identity")
            local_id, neighbor_id = map(int, proc_match.groups())
            require(local_id == rank and int(my_match.group(1)) == rank,
                    f"processor{rank}/{name}: local processor ID mismatch")
            require(int(neighbor_match.group(1)) == neighbor_id,
                    f"processor{rank}/{name}: neighbor processor ID mismatch")
            require(neighbor_id != rank and 0 <= neighbor_id < RANKS,
                    f"processor{rank}/{name}: invalid neighbor ID")
            require(patch["nFaces"] > 0, f"processor{rank}/{name}: nonpositive interface faces")
            patch["neighbor"] = neighbor_id
        patches.append(patch)
        cursor = match.end()
    require(not body[cursor:].strip(), f"processor{rank}: trailing unparsed boundary content")
    require(len(patches) == declared_count, f"processor{rank}: declared {declared_count} patches, parsed {len(patches)}")
    require(len({patch["name"] for patch in patches}) == len(patches), f"processor{rank}: duplicate patch name")
    processor_patches = [patch for patch in patches if patch["type"] == "processor"]
    require(all(patch["name"].startswith("procBoundary") for patch in processor_patches),
            f"processor{rank}: processor patch name mismatch")
    return processor_patches, declared_count


def parse_native_log(text: str) -> tuple[list[int], list[dict]]:
    blocks = list(re.finditer(r"(?m)^Processor\s+(\d+)\s*$", text))
    require(len(blocks) == RANKS, f"native log has {len(blocks)} processor blocks")
    rows = [None] * RANKS
    for index, match in enumerate(blocks):
        rank = int(match.group(1))
        require(0 <= rank < RANKS and rows[rank] is None, f"duplicate/invalid native processor ID {rank}")
        end = blocks[index + 1].start() if index + 1 < len(blocks) else text.find("\nEnd", match.end())
        require(end > match.end(), f"native processor{rank} block does not terminate")
        block = text[match.end():end]
        cells_match = re.search(r"(?m)^\s*Number of cells\s*=\s*(\d+)\s*$", block)
        processor_faces_match = re.search(r"(?m)^\s*Number of processor faces\s*=\s*(\d+)\s*$", block)
        shared = {int(other): int(faces) for other, faces in re.findall(
            r"(?m)^\s*Number of faces shared with processor\s+(\d+)\s*=\s*(\d+)\s*$", block
        )}
        require(cells_match and processor_faces_match, f"native processor{rank}: cell/interface summary missing")
        require(len(shared) == len(re.findall(r"Number of faces shared with processor", block)),
                f"native processor{rank}: duplicate shared-face row")
        rows[rank] = {"rank": rank, "cells": int(cells_match.group(1)),
                      "processor_faces": int(processor_faces_match.group(1)), "shared_faces": shared}
    return [row["cells"] for row in rows], rows


def normalize_groups(assignment: list[int]) -> tuple[list[int], list[list[int]]]:
    members = [[rank for rank, group in enumerate(assignment) if group == target] for target in range(GROUPS)]
    # Put rank 0's group first, then order other groups by their lowest rank.
    old_order = [assignment[0]] + sorted((group for group in range(GROUPS) if group != assignment[0]),
                                         key=lambda group: min(rank for rank, value in enumerate(assignment) if value == group))
    remap = {old: new for new, old in enumerate(old_order)}
    normalized = [remap[value] for value in assignment]
    normalized_members = [[rank for rank, value in enumerate(normalized) if value == group]
                          for group in range(GROUPS)]
    require(normalized_members[0][0] == 0, "rank-zero group normalization failed")
    return normalized, normalized_members


def augment_existing_result() -> None:
    """Derive per-group interface summaries without rerunning the randomized search."""
    graph = json.loads(GRAPH_PATH.read_text())
    result = json.loads(OUTPUT_PATH.read_text())
    graph_bytes = GRAPH_PATH.read_bytes()
    require(sha256(graph_bytes) == result["graph_file_sha256"], "existing screen refers to a different graph")
    edges = graph["edges"]
    total_faces = sum(edge["faces"] for edge in edges)
    cell_counts = graph["cells_by_rank"]

    def derive(assignment: list[int], expected_cut: int) -> dict:
        require(len(assignment) == RANKS and sorted(Counter(assignment).values()) == [GROUP_SIZE] * GROUPS,
                "existing mapping is not four balanced groups")
        matrix = [[0] * GROUPS for _ in range(GROUPS)]
        external = [0] * GROUPS
        within = [0] * GROUPS
        for edge in edges:
            left_group = assignment[edge["a"]]
            right_group = assignment[edge["b"]]
            faces = edge["faces"]
            first, second = sorted((left_group, right_group))
            matrix[first][second] += faces
            if left_group == right_group:
                within[left_group] += faces
            else:
                external[left_group] += faces
                external[right_group] += faces
        cut = full_cut(assignment, edges)
        require(cut == expected_cut, f"derived full cut {cut} differs from retained result {expected_cut}")
        cells = [sum(cell_counts[rank] for rank, group in enumerate(assignment) if group == target)
                 for target in range(GROUPS)]
        details = [{"group": group, "ranks": GROUP_SIZE, "cells": cells[group],
                    "within_group_interface_faces": within[group],
                    "external_interface_faces": external[group]}
                   for group in range(GROUPS)]
        return {
            "unique_interface_face_matrix_upper_triangle": matrix,
            "interface_matrix_convention": (
                "Each undirected edge is counted once in [min(group_a, group_b)][max(group_a, group_b)]; "
                "lower triangle is zero. Diagonal entries are within-group faces."
            ),
            "cross_group_interface_cut_faces": cut,
            "fraction_of_all_unique_interface_faces_crossing_groups": cut / total_faces,
            "external_interface_faces_by_logical_host": external,
            "max_logical_host_external_interface_faces": max(external),
            "cell_totals_by_logical_host": cells,
            "group_details": details,
        }

    baseline_assignment = [rank // GROUP_SIZE for rank in range(RANKS)]
    control_metrics = derive(baseline_assignment, result["control"]["cross_group_interface_cut_faces"])
    candidate_metrics = derive(result["candidate"]["rank_to_logical_host"],
                               result["candidate"]["cross_group_interface_cut_faces"])
    result["control"].update(control_metrics)
    result["candidate"].update(candidate_metrics)
    result["cut_reduction_fraction_of_all_unique_interface_faces"] = (
        (control_metrics["cross_group_interface_cut_faces"] -
         candidate_metrics["cross_group_interface_cut_faces"]) / total_faces
    )
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "state": result["state"],
        "cut_reduction_fraction_of_all_unique_interface_faces": result["cut_reduction_fraction_of_all_unique_interface_faces"],
        "control_external_faces_by_group": control_metrics["external_interface_faces_by_logical_host"],
        "candidate_external_faces_by_group": candidate_metrics["external_interface_faces_by_logical_host"],
        "candidate_max_group_external_faces": candidate_metrics["max_logical_host_external_interface_faces"],
    }, indent=2))


def main() -> None:
    overall_start = time.monotonic()
    intake = json.loads((HERE / "intake-validation.json").read_text())
    collection = json.loads((COLLECTED / "collection.json").read_text())
    require(intake.get("passed") is True and intake.get("ascii_boundaries") == RANKS,
            "boundary intake validation did not pass")
    require(intake.get("decompose_log_matches_sealed_native_intake") is True,
            "native decomposition log seal did not match")
    require(collection.get("ranks") == RANKS and collection.get("originating_native_job") == "25921488.pbs101",
            "collection provenance does not identify the expected 512-rank run")
    rows = collection.get("members", [])
    require(len(rows) == RANKS and sorted(row.get("rank") for row in rows) == list(range(RANKS)),
            "collection member IDs are not exactly 0 through 511")

    seals = []
    patches_by_rank = {}
    declared_patch_counts = []
    for row in rows:
        rank = row["rank"]
        path = BOUNDARIES / f"processor{rank}" / "boundary"
        before = path.stat()
        raw = path.read_bytes()
        after = path.stat()
        require(before.st_size == after.st_size == len(raw) == row["bytes"], f"processor{rank}: size changed")
        require(before.st_mtime_ns == after.st_mtime_ns, f"processor{rank}: mtime changed while read")
        digest = sha256(raw)
        require(digest == row["sha256"], f"processor{rank}: SHA256 differs from intake manifest")
        # Reject actual binary content; do not reject the dictionary's global format header value.
        require(b"\0" not in raw, f"processor{rank}: binary content found")
        processor_patches, declared_count = parse_boundary(rank, raw)
        patches_by_rank[rank] = processor_patches
        declared_patch_counts.append(declared_count)
        seals.append({"rank": rank, "path": row["path"], "bytes": len(raw), "sha256": digest})

    edges = {}
    patch_counts_by_rank = [0] * RANKS
    for rank in range(RANKS):
        neighbors = [patch["neighbor"] for patch in patches_by_rank[rank]]
        require(len(neighbors) == len(set(neighbors)), f"processor{rank}: duplicate processor neighbor patch")
        patch_counts_by_rank[rank] = len(neighbors)
        for patch in patches_by_rank[rank]:
            neighbor = patch["neighbor"]
            key = (min(rank, neighbor), max(rank, neighbor))
            require(key not in edges or rank > neighbor, f"duplicate edge declaration {key}")
            if rank < neighbor:
                edges[key] = patch["nFaces"]
    require(len(edges) == len(set(edges)), "duplicate unique graph edge")
    for (rank, neighbor), faces in edges.items():
        reciprocal = [patch for patch in patches_by_rank[neighbor] if patch["neighbor"] == rank]
        require(len(reciprocal) == 1, f"{rank}<->{neighbor}: reciprocal patch missing or duplicated")
        require(reciprocal[0]["nFaces"] == faces,
                f"{rank}<->{neighbor}: reciprocal nFaces mismatch {faces} vs {reciprocal[0]['nFaces']}")
    directed_patch_count = sum(patch_counts_by_rank)
    require(directed_patch_count == 2 * len(edges), "processor patch count is not exactly twice unique edges")

    native_log_bytes = (COLLECTED / "10_decomposePar.log").read_bytes()
    require(sha256(native_log_bytes) == collection["decompose_log_sha256"], "native log hash mismatch")
    native_cells, native_rows = parse_native_log(native_log_bytes.decode("ascii", errors="strict"))
    for rank, row in enumerate(native_rows):
        boundary_shared = {patch["neighbor"]: patch["nFaces"] for patch in patches_by_rank[rank]}
        require(row["shared_faces"] == boundary_shared,
                f"processor{rank}: boundary graph disagrees with native decomposePar shared-face rows")
        require(row["processor_faces"] == sum(boundary_shared.values()),
                f"processor{rank}: native processor face subtotal mismatch")
    total_unique_faces = sum(edge["faces"] for edge in ({"faces": faces} for faces in edges.values()))
    require(sum(row["processor_faces"] for row in native_rows) == 2 * total_unique_faces,
            "native processor-face total differs from unique boundary graph")
    require(len(native_cells) == RANKS and all(cells > 0 for cells in native_cells),
            "native per-rank cell counts incomplete or nonpositive")

    edge_rows = [{"a": a, "b": b, "faces": faces} for (a, b), faces in sorted(edges.items())]
    baseline_assignment = [rank // GROUP_SIZE for rank in range(RANKS)]
    baseline_cut = full_cut(baseline_assignment, edge_rows)
    baseline_cells = [sum(native_cells[rank] for rank in range(RANKS)
                          if baseline_assignment[rank] == group) for group in range(GROUPS)]
    graph = {
        "state": "VALIDATED_512_RANK_PROCESSOR_GRAPH",
        "originating_native_job": collection["originating_native_job"],
        "source_directory": collection["source_directory"],
        "intake_archive_sha256": intake["archive_sha256"],
        "decompose_log_sha256": collection["decompose_log_sha256"],
        "ranks": RANKS,
        "nodes_for_screen": GROUPS,
        "ranks_per_logical_host": GROUP_SIZE,
        "edges": edge_rows,
        "boundary_sha256": seals,
        "cells_by_rank": native_cells,
        "native_processor_faces_by_rank": [row["processor_faces"] for row in native_rows],
        "processor_patch_counts_by_rank": patch_counts_by_rank,
        "baseline": {
            "grouping": "rank // 128",
            "logical_group_cell_totals": baseline_cells,
            "cross_group_interface_faces": baseline_cut,
        },
        "limitations": [
            "Boundary files are current retained artifacts and were not sealed at original submission time.",
            "Matching the sealed native decomposition log does not prove complete mesh identity or frozen submission.",
            "Logical rank groups are not historical physical hosts; no original rank-to-host mapping is available.",
            "Interface faces are a graph cut proxy, not bytes, network traffic, MPI wait, or solver time.",
        ],
    }
    graph_bytes = (json.dumps(graph, indent=2) + "\n").encode()
    validation = {
        "state": "PROCESSOR_GRAPH_VALIDATION_PASS",
        "passed": True,
        "ranks": RANKS,
        "rank_ids_exact": True,
        "strict_ascii_and_stable_local_reads": True,
        "member_hashes_match_intake": True,
        "boundary_headers_may_say_binary": "Accepted because member bytes decode as strict ASCII with no NUL bytes.",
        "processor_patch_count": directed_patch_count,
        "unique_undirected_edges": len(edge_rows),
        "reciprocal_patch_pairs_equal_nFaces": True,
        "duplicate_patch_or_edge_count": 0,
        "native_log_rank_ids_exact": True,
        "native_shared_face_rows_match_boundary_graph": True,
        "native_processor_face_total": sum(row["processor_faces"] for row in native_rows),
        "graph_unique_interface_faces": total_unique_faces,
        "native_cell_count_sum": sum(native_cells),
        "native_cell_min": min(native_cells),
        "native_cell_max": max(native_cells),
        "native_cell_mean": statistics.mean(native_cells),
        "native_log_sha256_matches_collection": True,
        "graph_sha256": sha256(graph_bytes),
    }

    adjacency = [[] for _ in range(RANKS)]
    for edge in edge_rows:
        a, b, faces = edge["a"], edge["b"], edge["faces"]
        adjacency[a].append((b, faces))
        adjacency[b].append((a, faces))

    # At least 100 deterministic, independently recomputed swap-delta checks.
    check_rng = random.Random(SEED ^ 0x5A17)
    check_assignment = baseline_assignment[:]
    delta_checks = []
    for index in range(128):
        u = check_rng.randrange(RANKS)
        v = check_rng.randrange(RANKS)
        while u == v or check_assignment[u] == check_assignment[v]:
            v = check_rng.randrange(RANKS)
        old = full_cut(check_assignment, edge_rows)
        delta = swap_delta(u, v, check_assignment, adjacency)
        check_assignment[u], check_assignment[v] = check_assignment[v], check_assignment[u]
        recomputed = full_cut(check_assignment, edge_rows)
        require(recomputed - old == delta, f"swap delta mismatch at validation sample {index}")
        delta_checks.append({"index": index, "ranks": [u, v], "incremental_delta_faces": delta,
                             "full_recomputed_delta_faces": recomputed - old})

    rng = random.Random(SEED)
    assignment = baseline_assignment[:]
    members = [list(range(group * GROUP_SIZE, (group + 1) * GROUP_SIZE)) for group in range(GROUPS)]
    current = baseline_cut
    best = baseline_cut
    best_assignment = assignment[:]
    improvement_trail = [{"proposal": 0, "cross_group_interface_faces": baseline_cut, "event": "baseline"}]
    started_search = time.monotonic()
    proposals = 0
    start_temperature = 30000.0
    end_temperature = 2.0
    while proposals < MAX_PROPOSALS and time.monotonic() - started_search < SEARCH_BUDGET_SECONDS:
        proposals += 1
        group_a = rng.randrange(GROUPS)
        group_b = rng.randrange(GROUPS - 1)
        if group_b >= group_a:
            group_b += 1
        index_a = rng.randrange(GROUP_SIZE)
        index_b = rng.randrange(GROUP_SIZE)
        u, v = members[group_a][index_a], members[group_b][index_b]
        delta = swap_delta(u, v, assignment, adjacency)
        fraction = proposals / MAX_PROPOSALS
        temperature = start_temperature * ((end_temperature / start_temperature) ** fraction)
        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            assignment[u], assignment[v] = group_b, group_a
            members[group_a][index_a], members[group_b][index_b] = v, u
            current += delta
            if current < best:
                best = current
                best_assignment = assignment[:]
                improvement_trail.append({"proposal": proposals, "cross_group_interface_faces": best,
                                          "event": "accepted_balanced_swap"})

    annealing_elapsed = time.monotonic() - started_search
    annealing_best = best
    annealing_best_assignment = best_assignment[:]

    # Deterministic best-improvement descent from baseline and annealing best.
    def steepest_descent(seed_assignment: list[int], label: str) -> tuple[list[int], int, list[dict], bool]:
        current_assignment = seed_assignment[:]
        value = full_cut(current_assignment, edge_rows)
        trail = [{"move": 0, "cross_group_interface_faces": value, "event": "start"}]
        complete = True
        while True:
            if time.monotonic() - started_search >= SEARCH_BUDGET_SECONDS:
                complete = False
                break
            best_move = None
            for left in range(RANKS):
                for right in range(left + 1, RANKS):
                    if current_assignment[left] == current_assignment[right]:
                        continue
                    delta = swap_delta(left, right, current_assignment, adjacency)
                    if delta < 0 and (best_move is None or (delta, left, right) < best_move):
                        best_move = (delta, left, right)
            if best_move is None:
                break
            delta, left, right = best_move
            groups_before = [current_assignment[left], current_assignment[right]]
            current_assignment[left], current_assignment[right] = groups_before[1], groups_before[0]
            recomputed_value = full_cut(current_assignment, edge_rows)
            require(recomputed_value - value == delta,
                    f"steepest descent delta disagrees with full cut for {label}")
            value = recomputed_value
            trail.append({"move": len(trail), "swap_ranks": [left, right],
                          "groups_before": groups_before, "delta_faces": delta,
                          "cross_group_interface_faces": value})
        return current_assignment, value, trail, complete

    descent_runs = []
    best_trail = [{"proposal": 0, "cross_group_interface_faces": baseline_cut, "event": "baseline"}]
    final_best = baseline_assignment[:]
    final_cut = baseline_cut
    final_source = "baseline"
    for label, start_assignment in (("baseline", baseline_assignment), ("annealing_best", annealing_best_assignment)):
        descended, descended_cut, trail, completed = steepest_descent(start_assignment, label)
        descent_runs.append({"start": label, "start_cross_group_interface_faces": full_cut(start_assignment, edge_rows),
                             "final_cross_group_interface_faces": descended_cut,
                             "local_optimum_reached": completed, "trail": trail})
        if descended_cut < final_cut:
            final_cut, final_best = descended_cut, descended
            final_source = label
        if time.monotonic() - started_search >= SEARCH_BUDGET_SECONDS:
            break

    normalized_assignment, normalized_members = normalize_groups(final_best)
    recomputed_final = full_cut(normalized_assignment, edge_rows)
    require(recomputed_final == final_cut, "normalized candidate objective changed")
    require(sorted(Counter(normalized_assignment).values()) == [GROUP_SIZE] * GROUPS,
            "candidate logical-host groups are unbalanced")
    permutation = [rank for group in normalized_members for rank in sorted(group)]
    require(permutation[0] == 0 and sorted(permutation) == list(range(RANKS)),
            "candidate full rank permutation is not a rank-zero-first bijection")
    candidate_cells = [sum(native_cells[rank] for rank in group) for group in normalized_members]
    if final_source == "annealing_best":
        best_trail = [dict(row) for row in improvement_trail]
        final_descent = next(row for row in descent_runs if row["start"] == "annealing_best")
        best_trail.extend({"phase": "deterministic_steepest_swap", **row}
                          for row in final_descent["trail"][1:])
    else:
        final_descent = next(row for row in descent_runs if row["start"] == "baseline")
        best_trail = [{"proposal": 0, "cross_group_interface_faces": baseline_cut, "event": "baseline"}]
        best_trail.extend({"phase": "deterministic_steepest_swap", **row}
                          for row in final_descent["trail"][1:])
    trail_values = [row["cross_group_interface_faces"] for row in best_trail]
    require(all(after <= before for before, after in zip(trail_values, trail_values[1:])),
            "best objective trail is not monotonically improving")
    require(trail_values[-1] == recomputed_final, "best objective trail does not end at candidate cut")
    candidate_degree = [0] * RANKS
    rank_interface_faces = [0] * RANKS
    for edge in edge_rows:
        candidate_degree[edge["a"]] += 1
        candidate_degree[edge["b"]] += 1
        rank_interface_faces[edge["a"]] += edge["faces"]
        rank_interface_faces[edge["b"]] += edge["faces"]
    cross_edges = [edge for edge in edge_rows
                   if normalized_assignment[edge["a"]] != normalized_assignment[edge["b"]]]
    per_group = []
    for group, ranks in enumerate(normalized_members):
        local_faces = sum(edge["faces"] for edge in edge_rows
                          if normalized_assignment[edge["a"]] == group == normalized_assignment[edge["b"]])
        crossing_faces = sum(edge["faces"] for edge in cross_edges
                             if normalized_assignment[edge["a"]] == group or normalized_assignment[edge["b"]] == group)
        per_group.append({"group": group, "ranks": len(ranks), "cells": candidate_cells[group],
                          "within_group_interface_faces": local_faces,
                          "cross_group_incident_faces": crossing_faces})

    elapsed = time.monotonic() - overall_start
    require(elapsed < HARD_LIMIT_SECONDS, f"offline screen exceeded {HARD_LIMIT_SECONDS}s: {elapsed:.3f}s")
    graph_path = GRAPH_PATH
    GRAPH_PATH.write_text(json.dumps(graph, indent=2) + "\n")
    VALIDATION_PATH.write_text(json.dumps(validation, indent=2) + "\n")
    graph_file_sha = sha256(graph_bytes)
    result = {
        "state": "OFFLINE_512_RANK_GROUP_SCREEN_COMPLETE",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "originating_native_job": collection["originating_native_job"],
        "graph_file_sha256": graph_file_sha,
        "seed": SEED,
        "search": {
            "method": "Seeded simulated annealing with balanced cross-group swaps, then deterministic steepest improving balanced swaps from baseline and annealing best",
            "proposal_limit": MAX_PROPOSALS,
            "proposals_completed": proposals,
            "search_time_limit_seconds": SEARCH_BUDGET_SECONDS,
            "annealing_elapsed_seconds": annealing_elapsed,
            "elapsed_local_seconds": elapsed,
            "hard_limit_seconds": HARD_LIMIT_SECONDS,
            "restarts": 0,
            "no_optimum_claim": True,
        },
        "delta_validation": {
            "seed": SEED ^ 0x5A17,
            "checked_random_swaps": len(delta_checks),
            "all_match_full_recomputation": True,
            "checks": delta_checks,
        },
        "graph_summary": {
            "ranks": RANKS,
            "unique_undirected_processor_edges": len(edge_rows),
            "total_unique_interface_faces": total_unique_faces,
            "mean_neighbor_count": statistics.mean(patch_counts_by_rank),
            "max_neighbor_count": max(patch_counts_by_rank),
            "max_rank_incident_interface_faces": max(rank_interface_faces),
        },
        "control": {
            "assignment": "rank // 128",
            "logical_host_sizes": [GROUP_SIZE] * GROUPS,
            "cross_group_interface_cut_faces": baseline_cut,
            "cell_totals_by_logical_host": baseline_cells,
        },
        "candidate": {
            "rank_to_logical_host": normalized_assignment,
            "logical_host_members": normalized_members,
            "logical_host_sizes": [len(group) for group in normalized_members],
            "full_rank_permutation_group_major": permutation,
            "rank_zero_first": permutation[0] == 0,
            "cross_group_interface_cut_faces": recomputed_final,
            "cut_reduction_faces": baseline_cut - recomputed_final,
            "cut_reduction_percent": 100 * (baseline_cut - recomputed_final) / baseline_cut,
            "cell_totals_by_logical_host": candidate_cells,
            "group_details": per_group,
        },
        "annealing_best_before_deterministic_refinement": {
            "cross_group_interface_cut_faces": annealing_best,
            "rank_to_logical_host": normalize_groups(annealing_best_assignment)[0],
            "best_objective_trail": improvement_trail,
        },
        "deterministic_refinement_runs": descent_runs,
        "best_improvement_trail": best_trail,
        "decision": "REVIEW_CANDIDATE_MAPPING" if recomputed_final < baseline_cut else "NO_GRAPH_CUT_IMPROVEMENT",
        "interpretation_limits": [
            "Groups are logical groups of existing rank IDs, not historical physical hosts; no original placement map was available.",
            "The processor decomposition and processor directories remain unchanged; no runnable rank-order payload is emitted.",
            "Boundary artifacts were not sealed at original submission, and full mesh and field identity were not established by this intake.",
            "Interface-face cuts do not measure network bytes, MPI wait, solver critical path, locality, or speedup.",
            "Cell totals are rank cell counts grouped under a hypothetical logical host mapping; no cell migration or solver balance was tested.",
            "The seeded bounded heuristic is not an optimizer proof and can return a local or nonoptimal assignment.",
        ],
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n")
    # Add all-pair and per-group cut summaries from the just-validated mapping.
    augment_existing_result()
    print(json.dumps({"state": result["state"], "proposals": proposals,
                      "elapsed_local_seconds": elapsed, "edges": len(edge_rows),
                      "baseline_cut_faces": baseline_cut, "candidate_cut_faces": recomputed_final,
                      "cut_reduction_percent": result["candidate"]["cut_reduction_percent"]}, indent=2))


if __name__ == "__main__":
    if sys.argv[1:] == ["--augment-existing"]:
        augment_existing_result()
    else:
        main()
