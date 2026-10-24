#!/usr/bin/env python3
"""Local synthetic coverage for the launcher capture and MPI affinity shim."""

from __future__ import annotations

import json
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
from unittest import mock


HERE = Path(__file__).resolve().parent

MPI_HEADER = r"""
#ifndef APAC_TEST_MPI_H
#define APAC_TEST_MPI_H
typedef int MPI_Comm;
#define MPI_COMM_WORLD 0
#define MPI_SUCCESS 0
int PMPI_Init(int *, char ***);
int PMPI_Init_thread(int *, char ***, int, int *);
int PMPI_Comm_rank(MPI_Comm, int *);
int PMPI_Abort(MPI_Comm, int);
int MPI_Init(int *, char ***);
int MPI_Init_thread(int *, char ***, int, int *);
#endif
"""

STUB_C = r"""
#define _GNU_SOURCE
#include <mpi.h>
#include <sched.h>
#include <stdlib.h>
#include <string.h>

static cpu_set_t current_mask;
static int affinity_reads;
static int initialized;

int apac_test_sched_getaffinity(pid_t pid, size_t size, cpu_set_t *out)
{
    (void)pid; (void)size;
    ++affinity_reads;
    if (affinity_reads == 1) {
        /* Model the affinity wrapper observing a widened mask before MPI_Init. */
        CPU_ZERO(&current_mask);
        CPU_SET(2, &current_mask); CPU_SET(3, &current_mask);
        CPU_SET(5, &current_mask); CPU_SET(7, &current_mask);
    }
    *out = current_mask;
    if (getenv("TEST_VERIFY_FAIL") && affinity_reads == 3) {
        CPU_ZERO(out); CPU_SET(8, out);
    }
    return 0;
}

int apac_test_sched_setaffinity(pid_t pid, size_t size, const cpu_set_t *in)
{
    (void)pid; (void)size;
    if (getenv("TEST_RESTORE_FAIL") || !CPU_ISSET(7, in)) return -1;
    current_mask = *in;
    return 0;
}

static int widen(void)
{
    if (getenv("TEST_INIT_FAIL")) return 77;
    CPU_SET(0, &current_mask); CPU_SET(1, &current_mask);
    CPU_SET(2, &current_mask); CPU_SET(3, &current_mask);
    CPU_SET(5, &current_mask); CPU_SET(7, &current_mask);
    initialized = 1;
    return MPI_SUCCESS;
}

int PMPI_Init(int *argc, char ***argv) { (void)argc; (void)argv; return widen(); }
int PMPI_Init_thread(int *argc, char ***argv, int required, int *provided)
{
    (void)argc; (void)argv; if (provided) *provided = required; return widen();
}
int PMPI_Comm_rank(MPI_Comm comm, int *rank)
{ (void)comm; *rank = 4; return MPI_SUCCESS; }
int PMPI_Abort(MPI_Comm comm, int code)
{ (void)comm; (void)code; return MPI_SUCCESS; }

int main(int argc, char **argv)
{
    int provided = -1;
    int rc = getenv("TEST_THREAD")
        ? MPI_Init_thread(&argc, &argv, 3, &provided)
        : MPI_Init(&argc, &argv);
    (void)initialized;
    if (rc == MPI_SUCCESS) {
        const char *active = getenv("APAC_PRESERVE_AFFINITY");
        if (active && strcmp(active, "1") == 0) {
            if (CPU_COUNT(&current_mask) != 1 || !CPU_ISSET(7, &current_mask)) return 90;
        } else if (CPU_COUNT(&current_mask) != 6 || !CPU_ISSET(0, &current_mask) ||
                   !CPU_ISSET(1, &current_mask) || !CPU_ISSET(2, &current_mask) ||
                   !CPU_ISSET(3, &current_mask) || !CPU_ISSET(5, &current_mask) ||
                   !CPU_ISSET(7, &current_mask)) return 91;
    }
    return rc;
}
"""


def build_shim(temp: Path) -> Path:
    (temp / "mpi.h").write_text(textwrap.dedent(MPI_HEADER), encoding="utf-8")
    (temp / "stub.c").write_text(textwrap.dedent(STUB_C), encoding="utf-8")
    output = temp / "shim-stub"
    subprocess.run([
        os.environ.get("CC", "cc"), "-std=c11", "-Wall", "-Wextra", "-Werror",
        "-DAPAC_TESTING", "-I", str(temp), str(HERE / "preserve-affinity.c"),
        str(temp / "stub.c"), "-o", str(output),
    ], check=True)
    return output


def run(binary: Path, **variables: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    for key in ("APAC_PRESERVE_AFFINITY", "APAC_LAUNCH_CPU", "TEST_THREAD",
                "TEST_INIT_FAIL", "TEST_RESTORE_FAIL", "TEST_VERIFY_FAIL"):
        env.pop(key, None)
    env.update(variables)
    return subprocess.run([str(binary)], env=env, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def record(stderr: str, prefix: str = "APAC_AFFINITY_JSON ") -> dict:
    matches = [line for line in stderr.splitlines() if line.startswith(prefix)]
    assert len(matches) == 1, stderr
    return json.loads(matches[0].split(" ", 1)[1])


def test_shim(binary: Path) -> None:
    for thread in (False, True):
        env = {"APAC_PRESERVE_AFFINITY": "1", "APAC_LAUNCH_CPU": "7"}
        if thread:
            env["TEST_THREAD"] = "1"
        result = run(binary, **env)
        assert result.returncode == 0, result.stderr
        diag = record(result.stderr)
        assert diag["entry"] == ("MPI_Init_thread" if thread else "MPI_Init")
        assert diag["rank"] == 4 and diag["launch_cpu"] == 7
        assert diag["mpi_pre_init_cpus"] == "2,3,5,7"
        assert diag["post_init_cpus"] == "0,1,2,3,5,7"
        assert diag["restored_cpus"] == "7" and diag["success"] is True

    for activation in (None, "0"):
        env = {"APAC_LAUNCH_CPU": "7"}
        if activation is not None:
            env["APAC_PRESERVE_AFFINITY"] = activation
        result = run(binary, **env)
        assert result.returncode == 0 and result.stderr == "", result.stderr

    for bad_value in (None, "", "-1", "+7", "7x", "1024"):
        env = {"APAC_PRESERVE_AFFINITY": "1"}
        if bad_value is not None:
            env["APAC_LAUNCH_CPU"] = bad_value
        result = run(binary, **env)
        assert result.returncode == 126, (bad_value, result.returncode, result.stderr)
        diag = record(result.stderr)
        assert diag["stage"] == "before_mpi_init" and diag["success"] is False

    result = run(binary, APAC_PRESERVE_AFFINITY="1", APAC_LAUNCH_CPU="7",
                 TEST_RESTORE_FAIL="1")
    assert result.returncode == 127 and record(result.stderr)["success"] is False

    result = run(binary, APAC_PRESERVE_AFFINITY="1", APAC_LAUNCH_CPU="7",
                 TEST_VERIFY_FAIL="1")
    assert result.returncode == 127 and record(result.stderr)["success"] is False

    result = run(binary, APAC_PRESERVE_AFFINITY="1", APAC_LAUNCH_CPU="7",
                 TEST_INIT_FAIL="1")
    assert result.returncode == 77 and result.stderr == "", result.stderr


def test_exec_wrapper(temp: Path) -> None:
    helper = HERE / "capture-affinity-exec.py"
    fake_app = temp / "fake-app"
    fake_app.write_text("#!/bin/sh\nprintf '%s|%s|%s\\n' \\\"$APAC_LAUNCH_CPU\\\" \\\"$APAC_PRESERVE_AFFINITY\\\" \\\"$LD_PRELOAD\\\"\n",
                        encoding="utf-8")
    fake_app.chmod(0o755)
    library = temp / "fake.so"
    library.write_text("synthetic readable file\n", encoding="ascii")
    spec = importlib.util.spec_from_file_location("capture_affinity_exec", helper)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    writes: list[bytes] = []
    exec_calls: list[tuple[str, list[str], dict[str, str]]] = []

    class ExecCaptured(Exception):
        pass

    def fake_write(fd: int, payload: bytes) -> int:
        assert fd == 2
        writes.append(payload)
        return len(payload)

    def fake_execve(path: str, argv: list[str], env: dict[str, str]) -> None:
        exec_calls.append((path, argv, env))
        raise ExecCaptured

    arguments = ["--library", str(library), "--", str(fake_app)]
    with mock.patch.dict(module.os.environ, {}, clear=True), \
         mock.patch.object(module.os, "sched_getaffinity", return_value={7}), \
         mock.patch.object(module.os, "write", side_effect=fake_write), \
         mock.patch.object(module.os, "execve", side_effect=fake_execve):
        try:
            module.main(arguments)
            raise AssertionError("expected synthetic execve")
        except ExecCaptured:
            pass
    assert len(exec_calls) == 1
    path, argv, child_env = exec_calls[0]
    assert path == str(fake_app.resolve()) and argv == [str(fake_app)]
    assert child_env["APAC_LAUNCH_CPU"] == "7"
    assert child_env["APAC_PRESERVE_AFFINITY"] == "1"
    assert child_env["LD_PRELOAD"] == str(library.resolve())
    diag = record(writes[0].decode(), "APAC_AFFINITY_EXEC_JSON ")
    assert diag["success"] is True and diag["launch_cpus"] == [7]

    # A non-singleton launcher mask is rejected before execve.
    writes.clear()
    exec_calls.clear()
    with mock.patch.dict(module.os.environ, {}, clear=True), \
         mock.patch.object(module.os, "sched_getaffinity", return_value={7, 8}), \
         mock.patch.object(module.os, "write", side_effect=fake_write), \
         mock.patch.object(module.os, "execve", side_effect=fake_execve):
        assert module.main(arguments) == 125
    assert not exec_calls
    assert record(writes[0].decode(), "APAC_AFFINITY_EXEC_JSON ")["error"] == \
        "launcher_mask_not_single_cpu"

    # A caller's existing nonempty preload is rejected rather than overwritten.
    writes.clear()
    with mock.patch.dict(module.os.environ, {"LD_PRELOAD": "/tmp/inherited.so"}, clear=True), \
         mock.patch.object(module.os, "write", side_effect=fake_write), \
         mock.patch.object(module.os, "execve", side_effect=fake_execve):
        assert module.main(arguments) == 125
    assert not exec_calls
    assert record(writes[0].decode(), "APAC_AFFINITY_EXEC_JSON ")["error"] == \
        "refusing_nonempty_inherited_LD_PRELOAD"


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="apac-affinity-exec-test-") as directory:
        temp = Path(directory)
        test_shim(build_shim(temp))
        test_exec_wrapper(temp)
    print("synthetic exec-time affinity preservation checks passed")


if __name__ == "__main__":
    main()
