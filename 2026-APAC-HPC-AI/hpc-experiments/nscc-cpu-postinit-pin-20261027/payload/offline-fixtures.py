#!/usr/bin/env python3
"""Synthetic topology and phase-gate fixtures; no MPI runtime or site-topology claim."""
from copy import deepcopy
from offline_checks import select_core_slots, validate_pin_records


def synthetic_topology(cores=128):
    rows = []
    for core in range(cores):
        package = core // 64
        core_id = core % 64
        node = package * 2 + core_id // 32
        for sibling in range(2):
            cpu = core * 2 + sibling
            rows.append({"cpu": cpu, "package": package, "core": core_id, "node": node})
    return rows


def good_records(slots):
    records = []
    for world in range(512):
        host_index = world // 128
        local_rank = world % 128
        slot = slots[local_rank]
        records.append({
            "world_rank": world,
            "pmi_rank": (world * 17) % 512,
            "host": f"compute{host_index}",
            "local_rank": local_rank,
            "world_size": 512,
            "local_size": 128,
            "topology_status": 0,
            "target_cpu": slot["cpu"],
            "physical_package_id": slot["package"],
            "physical_core_id": slot["core"],
            "numa_node": slot["node"],
            "pre_init_status": 0,
            "pre_init_allowed": [world % 128],
            "post_init_status": 0,
            "post_init_allowed": list(range(256)),
            "sched_setaffinity_status": 0,
            "sched_setaffinity_errno": 0,
            "immediate_mask_status": 0,
            "immediate_mask_errno": 0,
            "immediate_mask": [slot["cpu"]],
            "after_allreduce_status": 0,
            "after_allreduce_errno": 0,
            "after_allreduce_mask": [slot["cpu"]],
            "after_2s_status": 0,
            "after_2s_errno": 0,
            "after_2s_mask": [slot["cpu"]],
            "after_final_allreduce_status": 0,
            "after_final_allreduce_errno": 0,
            "after_final_allreduce_mask": [slot["cpu"]],
            "preflight_global_error_count": 0,
            "immediate_global_error_count": 0,
            "final_global_error_count": 0,
            "sleep_status": 0,
            "sleep_elapsed_ns": 2_000_000_000,
        })
    return records


def rejects(fn, label):
    try:
        fn()
    except (AssertionError, ValueError):
        return {"name": label, "rejected": True}
    raise AssertionError(f"negative fixture unexpectedly passed: {label}")


def main():
    topology = synthetic_topology()
    online = set(range(256))
    allowed = set(range(256))
    slots = select_core_slots(topology, online, allowed, required_cores=128)
    assert len(slots) == 128
    assert len({slot["cpu"] for slot in slots}) == 128
    assert len({(slot["package"], slot["core"]) for slot in slots}) == 128
    assert slots == sorted(slots, key=lambda row: (row["package"], row["core"]))
    assert all(slot["cpu"] == 2 * (slot["package"] * 64 + slot["core"]) for slot in slots)

    positives = [{"name": "128 physical cores select lowest online allowed sibling in socket/core order", "passed": True}]
    negatives = []
    negatives.append(rejects(lambda: select_core_slots(topology[:-2], online, allowed, 128), "only 127 physical cores"))
    negatives.append(rejects(lambda: select_core_slots(synthetic_topology(129), set(range(258)), set(range(258)), 128), "129 physical cores exceed strict gate"))
    offline = set(range(256)) - {0}
    negatives.append(rejects(lambda: select_core_slots(topology, offline, allowed, 128), "selected logical CPU is offline"))
    unknown = deepcopy(topology)
    unknown[0]["node"] = None
    negatives.append(rejects(lambda: select_core_slots(unknown, online, allowed, 128), "NUMA node mapping is missing"))
    negative_ids = deepcopy(topology)
    negative_ids[0]["package"] = -1
    negatives.append(rejects(lambda: select_core_slots(negative_ids, online, allowed, 128), "negative physical package ID"))
    negative_ids = deepcopy(topology)
    negative_ids[0]["core"] = -1
    negatives.append(rejects(lambda: select_core_slots(negative_ids, online, allowed, 128), "negative physical core ID"))
    negative_ids = deepcopy(topology)
    negative_ids[0]["node"] = -1
    negatives.append(rejects(lambda: select_core_slots(negative_ids, online, allowed, 128), "negative NUMA node ID"))
    bad_sibling = deepcopy(topology)
    bad_sibling[1]["node"] = 99
    negatives.append(rejects(lambda: select_core_slots(bad_sibling, online, allowed, 128), "siblings disagree on NUMA node"))

    records = good_records(slots)
    summary = validate_pin_records(records, slots)
    positives.append({"name": "512 rank records retain unique world/PMI identities and every pin phase", "passed": True,
                      "records": summary["records"], "hosts": summary["hosts"], "pmi_nonidentity_pairs": summary["pmi_nonidentity_pairs"]})
    duplicate = deepcopy(records)
    duplicate[511]["target_cpu"] = duplicate[510]["target_cpu"]
    negatives.append(rejects(lambda: validate_pin_records(duplicate, slots), "duplicate local physical slot"))
    widened = deepcopy(records)
    widened[173]["after_allreduce_mask"] = [widened[173]["target_cpu"], (widened[173]["target_cpu"] + 1) % 256]
    negatives.append(rejects(lambda: validate_pin_records(widened, slots), "mask widened after global allreduce"))
    escaped = deepcopy(records)
    escaped[8]["post_init_allowed"] = [x for x in escaped[8]["post_init_allowed"] if x != escaped[8]["target_cpu"]]
    negatives.append(rejects(lambda: validate_pin_records(escaped, slots), "target outside process post-init allowed mask"))
    phase_error = deepcopy(records)
    phase_error[50]["after_2s_status"] = -1
    negatives.append(rejects(lambda: validate_pin_records(phase_error, slots), "after-two-second phase reports syscall failure"))
    bad_sleep = deepcopy(records)
    bad_sleep[50]["sleep_elapsed_ns"] = 1000
    negatives.append(rejects(lambda: validate_pin_records(bad_sleep, slots), "bounded two-second observation is missing"))
    wrong_pmi = deepcopy(records)
    wrong_pmi[100]["pmi_rank"] = wrong_pmi[99]["pmi_rank"]
    negatives.append(rejects(lambda: validate_pin_records(wrong_pmi, slots), "duplicate PMI rank"))
    missing = records[:-1]
    negatives.append(rejects(lambda: validate_pin_records(missing, slots), "missing world rank record"))

    assert len(positives) == 2 and all(x["passed"] for x in positives)
    assert len(negatives) == 15 and all(x["rejected"] for x in negatives)
    print({"passed": True, "fixture_type": "synthetic CPU/sysfs topology and MPI record data only",
           "positive": positives, "negative": negatives})


if __name__ == "__main__":
    main()
