#!/usr/bin/env python3
"""Compile and exercise the affinity wrapper against synthetic MPI/affinity calls."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap


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
static int initialized;
static int affinity_reads;
static int abort_code = -1;

int apac_test_sched_getaffinity(pid_t pid, size_t size, cpu_set_t *out)
{
    (void)pid; (void)size;
    ++affinity_reads;
    if (!initialized) {
        const char *mode = getenv("TEST_PRE");
        CPU_ZERO(&current_mask);
        if (!mode || strcmp(mode, "singleton") == 0) CPU_SET(7, &current_mask);
        else if (strcmp(mode, "multi") == 0) { CPU_SET(7, &current_mask); CPU_SET(9, &current_mask); }
    }
    *out = current_mask;
    if (getenv("TEST_POST_FAIL") && affinity_reads == 2) return -1;
    if (getenv("TEST_VERIFY_FAIL") && affinity_reads == 3) {
        CPU_ZERO(out);
        CPU_SET(8, out);
    }
    return 0;
}

int apac_test_sched_setaffinity(pid_t pid, size_t size, const cpu_set_t *in)
{
    (void)pid; (void)size;
    if (getenv("TEST_RESTORE_FAIL") && CPU_COUNT(in) == 1) return -1;
    current_mask = *in;
    return 0;
}

static int widen(void)
{
    const char *failure = getenv("TEST_INIT_FAIL");
    if (failure) return atoi(failure);
    if (affinity_reads == 0) {
        CPU_ZERO(&current_mask);
        CPU_SET(7, &current_mask);
    }
    /* Preserve the original allowed mask and broaden it with extra CPUs. */
    CPU_SET(2, &current_mask); CPU_SET(3, &current_mask); CPU_SET(5, &current_mask);
    initialized = 1;
    return MPI_SUCCESS;
}

int PMPI_Init(int *argc, char ***argv)
{
    (void)argc; (void)argv;
    return widen();
}

int PMPI_Init_thread(int *argc, char ***argv, int required, int *provided)
{
    (void)argc; (void)argv;
    if (provided) *provided = required;
    return widen();
}

int PMPI_Comm_rank(MPI_Comm comm, int *rank)
{
    (void)comm;
    *rank = 12;
    return MPI_SUCCESS;
}

int PMPI_Abort(MPI_Comm comm, int code)
{
    (void)comm;
    abort_code = code;
    return MPI_SUCCESS; /* The wrapper must still terminate if an implementation returns. */
}

int main(int argc, char **argv)
{
    int provided = -1;
    int rc = getenv("TEST_THREAD")
        ? MPI_Init_thread(&argc, &argv, 3, &provided)
        : MPI_Init(&argc, &argv);
    if (rc == MPI_SUCCESS) {
        int count = CPU_COUNT(&current_mask);
        if (getenv("APAC_PRESERVE_AFFINITY") &&
            strcmp(getenv("APAC_PRESERVE_AFFINITY"), "1") == 0) {
            if (count != 1 || !CPU_ISSET(7, &current_mask)) return 90;
        } else if (count != 4 || !CPU_ISSET(2, &current_mask) ||
                   !CPU_ISSET(3, &current_mask) || !CPU_ISSET(5, &current_mask) ||
                   !CPU_ISSET(7, &current_mask)) {
            return 91;
        }
    }
    (void)abort_code;
    return rc;
}
"""


def build(temp: Path) -> Path:
    (temp / "mpi.h").write_text(textwrap.dedent(MPI_HEADER), encoding="utf-8")
    (temp / "stub.c").write_text(textwrap.dedent(STUB_C), encoding="utf-8")
    binary = temp / "affinity-stub"
    command = [
        os.environ.get("CC", "cc"), "-std=c11", "-Wall", "-Wextra", "-Werror",
        "-DAPAC_TESTING", "-I", str(temp), str(HERE / "preserve-affinity.c"),
        str(temp / "stub.c"), "-o", str(binary),
    ]
    subprocess.run(command, check=True)
    return binary


def run(binary: Path, **variables: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    for key in ("APAC_PRESERVE_AFFINITY", "TEST_PRE", "TEST_THREAD",
                "TEST_INIT_FAIL", "TEST_RESTORE_FAIL", "TEST_VERIFY_FAIL",
                "TEST_POST_FAIL"):
        env.pop(key, None)
    env.update(variables)
    return subprocess.run([str(binary)], env=env, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def record(result: subprocess.CompletedProcess[str]) -> dict:
    lines = [line for line in result.stderr.splitlines()
             if line.startswith("APAC_AFFINITY_JSON ")]
    assert len(lines) == 1, result.stderr
    return json.loads(lines[0].split(" ", 1)[1])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="apac-affinity-test-") as directory:
        binary = build(Path(directory))

        # The opt-in wrapper restores after synthetic PMPI_Init and MPI_Init_thread.
        for thread in (False, True):
            env = {"APAC_PRESERVE_AFFINITY": "1"}
            if thread:
                env["TEST_THREAD"] = "1"
            result = run(binary, **env)
            assert result.returncode == 0, result.stderr
            diag = record(result)
            assert diag["entry"] == ("MPI_Init_thread" if thread else "MPI_Init")
            assert diag["rank"] == 12
            assert diag["pre_init_cpus"] == "7"
            assert diag["post_init_cpus"] == "2,3,5,7"
            assert diag["restored_cpus"] == "7"
            assert diag["success"] is True

        # Unset/zero means pass-through: synthetic MPI broadening remains untouched.
        for activation in (None, "0"):
            env = {} if activation is None else {"APAC_PRESERVE_AFFINITY": activation}
            result = run(binary, **env)
            assert result.returncode == 0 and result.stderr == "", result.stderr

        # An empty or multi-CPU entry mask must fail closed after MPI init.
        for pre_mode in ("empty", "multi"):
            result = run(binary, APAC_PRESERVE_AFFINITY="1", TEST_PRE=pre_mode)
            assert result.returncode == 127, (pre_mode, result.returncode, result.stderr)
            diag = record(result)
            assert diag["success"] is False
            assert diag["rank"] == 12
            assert diag["restore_set_status"] == -1

        # A failed restore syscall and a failed verification are fail-closed.
        result = run(binary, APAC_PRESERVE_AFFINITY="1", TEST_RESTORE_FAIL="1")
        assert result.returncode == 127, result.stderr
        assert record(result)["restore_set_status"] == -1

        result = run(binary, APAC_PRESERVE_AFFINITY="1", TEST_VERIFY_FAIL="1")
        assert result.returncode == 127, result.stderr
        diag = record(result)
        assert diag["restore_set_status"] == 0 and diag["restored_read_status"] == 0
        assert diag["success"] is False

        result = run(binary, APAC_PRESERVE_AFFINITY="1", TEST_POST_FAIL="1")
        assert result.returncode == 127, result.stderr
        diag = record(result)
        assert diag["post_init_status"] == -1
        assert diag["restore_set_status"] == 0 and diag["restored_read_status"] == 0
        assert diag["restored_cpus"] == "7" and diag["success"] is False

        # MPI initialization failure is returned unchanged; no rank/affinity work follows.
        result = run(binary, APAC_PRESERVE_AFFINITY="1", TEST_INIT_FAIL="77")
        assert result.returncode == 77 and result.stderr == "", result.stderr

    print("synthetic affinity wrapper checks passed")


if __name__ == "__main__":
    main()
