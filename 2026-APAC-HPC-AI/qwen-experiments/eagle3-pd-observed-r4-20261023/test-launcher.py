"""CPU fixtures for the actual R4 warmup block and PBS shim."""

from pathlib import Path
import json
import os
import shlex
import shutil
import subprocess
import tempfile

O = Path(__file__).resolve().parent
top = (O / "topology-job.sh").read_text()
start = top.index('timeout --signal=TERM --kill-after=10s "${warmup_remaining}s"')
end = top.index('  >"$ART/pair-warmup.log"', start) + len('  >"$ART/pair-warmup.log"')
block = top[start:end]
client_start = top.index('timeout --signal=TERM --kill-after=10s "${client_remaining}s"')
client_end = top.index('python3 "$BUNDLE/phase-marker.py" "$ART" client_end', client_start)
client_block = top[client_start:client_end]
assert "/bin/bash -c 'srun \"$@\"' qwen-pair-warmup" in block
assert "/bin/bash -c 'srun \"$@\"' qwen-token-client" in client_block
results = []

with tempfile.TemporaryDirectory(prefix="eagle3-r4-launcher-") as temporary:
    T = Path(temporary)
    nodefile = T / "nodes"
    nodefile.write_text("mock-node0\nmock-node1\n")
    art = T / "art with spaces"
    art.mkdir()
    binpath = T / "bin"
    binpath.mkdir()
    for command in ("timeout", "bash", "python3", "awk", "sleep"):
        (binpath / command).symlink_to(shutil.which(command))

    # Run an otherwise byte-identical shim copy with only its absolute site pbsdsh path redirected.
    fixture_bundle = T / "bundle with spaces"
    fixture_bundle.mkdir()
    for name in ("pbs-shim.sh", "pbs-task-log.sh", "pbs-container.sh"):
        shutil.copy2(O / name, fixture_bundle / name)
    mock = binpath / "pbsdsh"
    (fixture_bundle / "pbs-shim.sh").write_text(
        (fixture_bundle / "pbs-shim.sh").read_text().replace(
            "/opt/pbs/bin/pbsdsh", str(mock)))

    env = os.environ.copy()
    env.update(PBS_NODEFILE=str(nodefile), PBS_JOBID="cpu-fixture",
               QWEN_BUNDLE=str(fixture_bundle), SLURM_SUBMIT_DIR=str(T),
               QWEN_EXPERIMENT_ID="eagle3-pd-observed-r4-20261023",
               QWEN_WARMUP_DEADLINE_EPOCH="1234567890",
               APAC_PBS_DRY_RUN="1", PATH=str(binpath))
    prefix = (
        "set -euo pipefail\nsource " + shlex.quote(str(fixture_bundle / "pbs-shim.sh")) +
        "\nNODES=(mock-node0 mock-node1)\nSGLANG='fake image'\nBUNDLE=" +
        shlex.quote(str(O)) + "\nART=" + shlex.quote(str(art)) +
        "\nIPS=(127.0.0.1)\nwarmup_remaining=180\nWARMUP_DEADLINE=1234567890\n" +
        "mounts() { printf '%s' 'path with spaces:target'; }\n"
    )

    def run(code, extra=None):
        return subprocess.run(["bash", "-c", prefix + code], env={**env, **(extra or {})},
                              capture_output=True, text=True, timeout=15)

    # The old timeout -> shell function form must still reproduce its known failure.
    old = run("timeout 1s srun --overlap\n")
    assert old.returncode == 127, (old.returncode, old.stderr)
    results.append({"case": "old_external_timeout_reproduces_127", "passed": True})

    child = run("timeout 1s bash -c 'declare -F srun >/dev/null'\n")
    assert child.returncode == 0
    results.append({"case": "child_bash_imports_actual_exported_shim", "passed": True})

    dry = run(block + "\n")
    assert dry.returncode == 0, (dry.returncode, dry.stderr)
    value = json.loads((art / "pair-warmup.log").read_text())
    expected = ["env", "QWEN_EXPERIMENT_ID=eagle3-pd-observed-r4-20261023",
                "QWEN_WARMUP_DEADLINE_EPOCH=1234567890", "python3",
                str(O / "warm-topology.py"), "127.0.0.1", str(art)]
    assert value["node"] == 0 and value["gpu_indices"] == [] and value["cpus"] == 4
    assert value["command"] == expected, value
    results.append({"case": "actual_r4_warmup_block_preserves_argv_and_spaces", "passed": True})

    client_code = client_block + "\n"
    # The captured block includes outer timeout and writes no client artifacts in shim dry-run mode.
    client_code = client_code.replace('"${client_remaining}s"', '"300s"').replace(
        '"${NODES[0]}"', '"mock-node0"').replace('"$CLIENT_DEADLINE"', '"1234567890"')
    client_code = client_code.replace('"$BUNDLE"', shlex.quote(str(O))).replace(
        '"${IPS[0]}:8000"', '"127.0.0.1:8000"').replace('"$MODEL"', '"/model"').replace(
        '"$ART"', shlex.quote(str(art)))
    client_result = run(client_code)
    assert client_result.returncode == 0, (client_result.returncode, client_result.stderr)
    client_record = json.loads(client_result.stdout.strip())
    assert client_record["command"][-5:] == ["bash", str(O / "token-client.sh"),
                                               "127.0.0.1:8000", "/model", str(art)]
    results.append({"case": "actual_r4_client_dispatch_uses_child_bash", "passed": True})

    mock.write_text('''#!/usr/bin/env bash
set -eu
if [[ ${QWEN_MOCK_MODE:-exit} == sleep ]]; then
  sleep 30 & child=$!
  printf '%s' "$child" > "$QWEN_MOCK_PIDFILE"
  trap 'kill "$child" 2>/dev/null || :; wait "$child" 2>/dev/null || :; printf terminated > "$QWEN_MOCK_TERMFILE"; exit 143' TERM
  wait "$child"
else
  exit "${QWEN_MOCK_STATUS:-0}"
fi
''')
    mock.chmod(0o755)
    env["QWEN_BUNDLE"] = str(fixture_bundle)
    prefix = prefix.replace(shlex.quote(str(fixture_bundle / "pbs-shim.sh")),
                            shlex.quote(str(fixture_bundle / "pbs-shim.sh")))
    for status in (0, 23):
        result = run(block + "\n", {"APAC_PBS_DRY_RUN": "0", "QWEN_MOCK_STATUS": str(status)})
        assert result.returncode == status, (status, result.returncode, result.stderr)
        results.append({"case": f"actual_shim_status_{status}_and_set_e_gate", "passed": True})

    pidfile, termfile = T / "child.pid", T / "term"
    timed_block = block.replace('"${warmup_remaining}s"', '"1s"')
    timed = run(timed_block + "\n", {"APAC_PBS_DRY_RUN": "0", "QWEN_MOCK_MODE": "sleep",
                                  "QWEN_MOCK_PIDFILE": str(pidfile),
                                  "QWEN_MOCK_TERMFILE": str(termfile)})
    assert timed.returncode == 124 and termfile.read_text() == "terminated", (timed.returncode, timed.stderr)
    pid = int(pidfile.read_text())
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        pass
    else:
        raise AssertionError("timed mock child remains alive")
    results.append({"case": "timeout_124_terminates_mock_step_and_blocks_success", "passed": True})

for name in ("benchmark.pbs", "pbs-container.sh", "pbs-shim.sh", "pbs-task-log.sh"):
    first = (O / name).read_text().splitlines()[0]
    assert "bash -l" not in first, (name, first)
assert "/opt/pbs/bin/pbsdsh" in (O / "pbs-shim.sh").read_text()
results.append({"case": "nonlogin_shell_and_absolute_pbsdsh_contract", "passed": True})

(O / "launcher-validation.json").write_text(json.dumps({
    "passed": True, "cases": results,
    "scope": "Actual R4 warmup dispatch block and copied PBS shim on CPU with mocked pbsdsh; no GPU/model/scheduler access.",
    "limits": ["The absolute site pbsdsh was redirected only in an isolated test copy.",
               "Local mock does not prove remote PBS task termination."]
}, indent=2) + "\n")
print("R4 CPU launcher fixtures PASS:", len(results))
