#!/usr/bin/env python3
"""Create a synthetic 512-rank pass tree and exercise strict negative replay gates."""
from __future__ import annotations
import importlib.util
import json
import pathlib
import shutil
import tempfile

HERE = pathlib.Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("latepin_review", HERE / "review.py")
REVIEW = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(REVIEW)


def dump(path, row):
    path.write_text(json.dumps(row, separators=(",", ":")) + "\n")


def make_fixture(root: pathlib.Path):
    for folder in ("logs", "resources", "commands", "arms/no-adapter/native/pre",
                   "arms/with-adapter/native/pre", "arms/with-adapter/adapter-ranks",
                   "arms/pstream-checkmesh/adapter-ranks", "diagnostic-case/processor511/constant/polyMesh"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    for name in ("expected-payload-sha256.txt", "payload-sha256-before.txt", "payload-sha256-after.txt"):
        (root / name).write_text("a" * 64 + "  fixture\n")
    for name in ("runtime-hashes-before.txt", "runtime-hashes-after.txt"):
        (root / name).write_text("b" * 64 + "  /fixture/libmpi.so\n")
    dump(root / "worker-status.json", {"worker_return_code": 0, "payload_unchanged_return_code": 0,
                                        "runtime_objects_unchanged_return_code": 0})
    commands = list(REVIEW.COMMANDS) + ["payload_unchanged", "runtime_objects_unchanged", "payload_matches_frozen_before"]
    (root / "command-return-codes.jsonl").write_text("".join(json.dumps({"command": n, "return_code": 0}) + "\n" for n in commands))
    (root / "phases.tsv").write_text("\n".join(f"2026-10-27T00:00:00Z\tstart\t{name}" for name in
        ("module_setup", "blockMesh", "decomposePar", "arm-no-adapter", "arm-with-adapter", "arm-pstream-checkmesh")) + "\n")
    for name in REVIEW.PREP_RESOURCES + ("arm-no-adapter", "arm-with-adapter", "arm-pstream-checkmesh"):
        (root / f"resources/{name}.time.txt").write_text("synthetic resource record; not measured\n")
    argv = {
        "arm-no-adapter": "mpiexec -n 512 /run/mpi-init-probe /run/arms/no-adapter/native\n",
        "arm-with-adapter": "mpiexec -n 512 /run/payload/rank-exec.sh /run with-adapter /run/latepin-pmpi-adapter.so -- /run/mpi-init-probe /run/arms/with-adapter/native\n",
        "arm-pstream-checkmesh": "mpiexec -n 512 /run/payload/rank-exec.sh /run pstream-checkmesh /run/latepin-pmpi-adapter.so -- checkMesh -parallel -case /run/diagnostic-case\n",
    }
    for name, command in argv.items():
        (root / f"commands/{name}.argv.txt").write_text(command)
    (root / "logs/pstream-path.txt").write_text("/opt/openfoam2512/platforms/mpich/libPstream.so\n")
    (root / "logs/mpi-shared-library-path.txt").write_text("/opt/cray/pe/mpich/8.1.15/lib/libmpi.so\n")
    for name in ("pstream-ldd", "checkMesh-ldd", "adapter-ldd", "native-probe-ldd"):
        (root / f"logs/{name}.stdout.txt").write_text("libmpi.so => /opt/cray/pe/mpich/8.1.15/lib/libmpi.so (0x0)\n")
    (root / "logs/selected-runtime-settings.txt").write_text(
        "WM_PROJECT_DIR=/opt/openfoam2512\nMPICH_RANK_REORDER_METHOD=0\nPALS_CPU_BIND=unset\nMPICH_RANK_ORDER=unset\n"
        "MPICH_RANK_REORDER_FILE=unset\nLD_PRELOAD=empty\n")
    (root / "logs/arm-pstream-checkmesh.stdout.txt").write_text('Build: OPENFOAM=2512\nArch: "LSB;label=32;scalar=64"\nnProcs : 512\ncells: 8192\nMesh OK.\nEnd\n')
    (root/"logs/blockMesh.stdout.txt").write_text("nCells: 8192\nEnd\n")

    for arm in ("no-adapter", "with-adapter"):
        (root/f"logs/arm-{arm}.stdout.txt").write_text('MPI_SUMMARY_JSON {"world_size":512,"ranks_with_capture_or_identity_errors":0}\n')
        native = root / "arms" / arm / "native"
        for pmi in range(512):
            host_idx, local_pmi = divmod(pmi, 128)
            host = f"n{host_idx:02d}"
            world = host_idx * 128 + (127 - local_pmi)
            local_rank = world % 128
            cpu = local_rank
            dump(native / "pre" / f"rank-{pmi:04d}.json", {
                "phase": "before_mpi_init_thread", "rank": pmi, "pmi_rank": pmi, "host": host,
                "affinity_status": 0, "errno": 0, "cpus": [cpu]})
            dump(native / f"rank-{world:04d}.json", {
                "phase": "after_mpi_init_thread", "rank": world, "pmi_rank": pmi,
                "host": host, "world_size": 512, "affinity_status": 0, "errno": 0, "cpus": list(range(256))})
    for arm in REVIEW.ADAPTED_ARMS:
        for pmi in range(512):
            host_idx, local_pmi = divmod(pmi, 128)
            host = f"n{host_idx:02d}"
            world = host_idx * 128 + (127 - local_pmi)
            local_rank = world % 128
            target = local_rank
            rank_dir = root / "arms" / arm / "adapter-ranks" / f"rank-{pmi:04d}"
            rank_dir.mkdir(parents=True)
            rows = []
            slots = []
            for core in range(128):
                package = core // 64
                numa = core // 16
                rows.append({"cpu": core, "online": True, "package": package, "core": core % 64, "node": numa})
                rows.append({"cpu": core + 128, "online": True, "package": package, "core": core % 64, "node": numa})
                slots.append({"cpu": core, "package": package, "core": core % 64, "node": numa})
            topo_rows = sorted(rows, key=lambda row: (row["package"], row["core"], row["cpu"]))
            source_world = host_idx * 128
            topology = {"world_rank": world, "pmi_rank": pmi, "host": host,
                        "post_init_allowed": list(range(256)), "topology_source_world_rank": source_world,
                        "topology_source_allowed": list(range(256)), "allowed_cpu_sysfs_map": topo_rows,
                        "selected_slots_sorted_package_core": slots}
            dump(rank_dir / f"host-topology-world-{world:04d}.json", topology)
            hook = "MPI_Init_thread" if arm == "with-adapter" else "MPI_Init"
            init = {"schema": 1, "hook": hook, "requested_thread_level": 0, "provided_thread_level": 0,
                    "underlying_init_rc": 0, "process_pid": 100000 + pmi, "hook_thread_tid": 100000 + pmi, "hook_thread_is_process_main": True, "repeated_or_nested_init_rejected": False, "world_rank": world, "pmi_rank": pmi, "world_size": 512,
                    "local_rank": local_rank, "local_size": 128, "host": host, "topology_status": 0,
                    "target_cpu": target, "physical_socket": target // 64, "physical_core": target % 64,
                    "numa_node": target // 16, "init_thread_matches_hook_thread": True,
                    "sched_setaffinity_status": 0, "sched_setaffinity_errno": 0,
                    "preflight_global_error_count": 0, "collective_init_error_count": 0, "before_init_status": 0, "before_init_errno": 0,
                    "before_init_mask": [target], "post_init_status": 0, "post_init_errno": 0,
                    "post_init_mask": list(range(256)), "after_pin_status": 0, "after_pin_errno": 0,
                    "after_pin_mask": [target]}
            dump(rank_dir / "init.json", init)
            final = {"schema": 1, "hook": "MPI_Finalize", "world_rank": world, "pmi_rank": pmi,
                     "world_size": 512, "local_rank": local_rank, "local_size": 128, "host": host,
                     "target_cpu": target, "physical_socket": target // 64, "physical_core": target % 64,
                     "numa_node": target // 16, "finalize_process_pid": 100000 + pmi, "finalize_thread_tid": 100000 + pmi,
                     "finalize_thread_is_process_main": True, "finalize_thread_matches_hook_thread": True,
                     "target_present": True, "singleton_target_mask": True, "repeated_or_nested_init_rejected": False, "local_error": 0,
                     "collective_finalize_error_count": 0, "audit_phase": "immediately_before_PMPI_Finalize",
                     "pmpi_finalize_return_code": None, "before_pmpi_finalize_status": 0,
                     "before_pmpi_finalize_errno": 0, "before_pmpi_finalize_mask": [target]}
            dump(rank_dir / "finalize.json", final)
            dump(rank_dir / "finalize-return.json", {
                "schema": 1, "hook": "PMPI_Finalize_return", "world_rank": world, "pmi_rank": pmi,
                "local_rank": local_rank, "host": host, "target_cpu": target,
                "process_pid": 100000 + pmi, "finalize_thread_tid": 100000 + pmi,
                "pmpi_finalize_return_code": 0, "mpi_success_constant": 0,
                "collective_finalize_error_count": 0, "pre_finalize_audit_write_error_count": 0})


def expect_failure(root, label, mutate, restore):
    mutate()
    try:
        REVIEW.validate(root)
    except REVIEW.ReviewError:
        pass
    else:
        raise AssertionError(f"negative acceptance fixture unexpectedly passed: {label}")
    finally:
        restore()


def main():
    with tempfile.TemporaryDirectory(prefix="nscc-pstream-latepin-fixture-") as temp:
        root = pathlib.Path(temp) / "run"
        root.mkdir()
        make_fixture(root)
        passed = REVIEW.validate(root)
        assert passed["passed"] and passed["adapter_arms"]["pstream-checkmesh"]["all_init_and_finalize_audits_pass"]
        init_path = root / "arms/pstream-checkmesh/adapter-ranks/rank-0000/init.json"
        saved_init = init_path.read_bytes()
        row = json.loads(saved_init); row["after_pin_mask"] = [255]
        expect_failure(root, "after-pin mask differs from target", lambda: dump(init_path, row), lambda: init_path.write_bytes(saved_init))
        final_path = root / "arms/with-adapter/adapter-ranks/rank-0000/finalize.json"
        saved_final = final_path.read_bytes()
        expect_failure(root, "missing pre-finalize audit", lambda: final_path.unlink(), lambda: final_path.write_bytes(saved_final))
        final_rc_path = root / "arms/pstream-checkmesh/adapter-ranks/rank-0000/finalize-return.json"
        saved_final_rc = final_rc_path.read_bytes()
        rc_row = json.loads(saved_final_rc); rc_row["pmpi_finalize_return_code"] = 23
        expect_failure(root, "nonzero actual PMPI_Finalize return", lambda: dump(final_rc_path, rc_row), lambda: final_rc_path.write_bytes(saved_final_rc))
        utility = root / "logs/arm-pstream-checkmesh.stdout.txt"
        saved_utility = utility.read_bytes()
        expect_failure(root, "missing Mesh OK marker", lambda: utility.write_text("End\n"), lambda: utility.write_bytes(saved_utility))
        codes_path = root / "command-return-codes.jsonl"
        saved_codes = codes_path.read_bytes()
        changed = [json.loads(line) for line in saved_codes.decode().splitlines()]
        changed[changed.index(next(row for row in changed if row["command"] == "arm-pstream-checkmesh"))]["return_code"] = 23
        expect_failure(root, "nonzero target command status", lambda: codes_path.write_text("".join(json.dumps(row) + "\n" for row in changed)), lambda: codes_path.write_bytes(saved_codes))
        hash_path = root / "runtime-hashes-after.txt"
        saved_hash = hash_path.read_bytes()
        expect_failure(root, "runtime hash mismatch", lambda: hash_path.write_text("changed\n"), lambda: hash_path.write_bytes(saved_hash))
        print(json.dumps({"positive_fixture": "PASS", "negative_fixtures": [
            "after-pin mismatch", "missing pre-finalize audit", "nonzero actual PMPI_Finalize return", "missing Mesh OK", "nonzero command status", "runtime hash mismatch"],
            "scope": "synthetic-only; not MPI ABI or NSCC runtime evidence"}, indent=2))

if __name__ == "__main__":
    main()
