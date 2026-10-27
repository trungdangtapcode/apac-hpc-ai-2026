"""Pure validation helpers shared only by synthetic offline fixtures and review."""
from collections import Counter, defaultdict


def select_core_slots(topology_rows, online, allowed, required_cores=128):
    by_cpu = {}
    for row in topology_rows:
        cpu = row.get("cpu")
        package = row.get("package")
        core = row.get("core")
        node = row.get("node")
        if not isinstance(cpu, int) or cpu < 0 or cpu in by_cpu:
            raise ValueError("duplicate or invalid logical CPU")
        if cpu not in online or cpu not in allowed:
            raise ValueError("CPU is offline or outside allowed set")
        if not all(isinstance(x, int) and x >= 0 for x in (package, core, node)):
            raise ValueError("incomplete package/core/NUMA topology")
        by_cpu[cpu] = {"cpu": cpu, "package": package, "core": core, "node": node}
    if not allowed or not allowed.issubset(by_cpu):
        raise ValueError("allowed mask includes an unmapped CPU")
    by_core = defaultdict(list)
    for cpu in sorted(allowed):
        row = by_cpu[cpu]
        by_core[(row["package"], row["core"])].append(row)
    if len(by_core) != required_cores:
        raise ValueError("physical core count differs from strict requirement")
    slots = []
    for key in sorted(by_core):
        siblings = by_core[key]
        if len({row["node"] for row in siblings}) != 1:
            raise ValueError("logical siblings disagree on NUMA node")
        slots.append(min(siblings, key=lambda row: row["cpu"]))
    if len({row["cpu"] for row in slots}) != required_cores:
        raise ValueError("selected CPU slot is duplicated")
    if slots != sorted(slots, key=lambda row: (row["package"], row["core"])):
        raise ValueError("slot order is not deterministic")
    return slots


def validate_pin_records(records, slots):
    if len(records) != 512:
        raise ValueError("expected 512 process records")
    by_rank = {}
    for row in records:
        rank = row.get("world_rank")
        if not isinstance(rank, int) or rank in by_rank or not 0 <= rank < 512:
            raise ValueError("duplicate or invalid world rank")
        by_rank[rank] = row
    if set(by_rank) != set(range(512)):
        raise ValueError("missing world rank")
    pmi = [row.get("pmi_rank") for row in records]
    if sorted(pmi) != list(range(512)):
        raise ValueError("PMI ranks are missing or duplicated")
    host_counts = Counter(row.get("host") for row in records)
    if len(host_counts) != 4 or set(host_counts.values()) != {128}:
        raise ValueError("expected four hosts with 128 ranks each")
    pmi_pairs = 0
    for host in host_counts:
        host_slots = slots[host] if isinstance(slots, dict) else slots
        host_rows = [row for row in records if row["host"] == host]
        if any(row.get("world_size") != 512 or row.get("local_size") != 128 for row in host_rows):
            raise ValueError("world or shared-memory local size gate failed")
        if sorted(row.get("local_rank") for row in host_rows) != list(range(128)):
            raise ValueError("local ranks are missing or duplicated")
        targets = []
        physical = []
        for row in host_rows:
            local = row["local_rank"]
            slot = host_slots[local]
            target = row.get("target_cpu")
            identity = (row.get("physical_package_id"), row.get("physical_core_id"), row.get("numa_node"))
            if target != slot["cpu"] or identity != (slot["package"], slot["core"], slot["node"]):
                raise ValueError("target slot does not match validated topology order")
            if row.get("topology_status") != 0:
                raise ValueError("topology phase failed")
            allowed = row.get("post_init_allowed")
            if not isinstance(allowed, list) or target not in allowed:
                raise ValueError("target is outside observed post-init affinity mask")
            targets.append(target)
            physical.append(identity[:2])
            if row.get("pre_init_status") != 0 or row.get("post_init_status") != 0:
                raise ValueError("pre/post MPI initialization affinity snapshot failed")
            phases = {"immediate": ("immediate_mask", "immediate_mask"),
                      "after_allreduce": ("after_allreduce", "after_allreduce_mask"),
                      "after_2s": ("after_2s", "after_2s_mask"),
                      "after_final_allreduce": ("after_final_allreduce", "after_final_allreduce_mask")}
            for phase, (prefix, mask_key) in phases.items():
                if row.get(prefix + "_status") != 0 or row.get(prefix + "_errno") != 0:
                    raise ValueError("affinity audit phase failed")
                if row.get(mask_key) != [target]:
                    raise ValueError("affinity mask changed during pin audit")
            if row.get("sched_setaffinity_status") != 0 or row.get("sched_setaffinity_errno") != 0:
                raise ValueError("sched_setaffinity failed")
            if row.get("preflight_global_error_count") != 0 or row.get("immediate_global_error_count") != 0 or row.get("final_global_error_count") != 0:
                raise ValueError("collective error gate failed")
            if row.get("sleep_status") != 0 or not 1_900_000_000 <= row.get("sleep_elapsed_ns", -1) <= 10_000_000_000:
                raise ValueError("bounded two-second wait did not complete")
            pmi_pairs += row["world_rank"] != row["pmi_rank"]
        if len(set(targets)) != 128 or len(set(physical)) != 128:
            raise ValueError("duplicate logical or physical core assignment on a host")
    return {"records": len(records), "hosts": dict(sorted(host_counts.items())),
            "pmi_nonidentity_pairs": pmi_pairs}
