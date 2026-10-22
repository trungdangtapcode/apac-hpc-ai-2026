#!/usr/bin/env python3
"""CPU-only structure, failure-propagation, deadline, and semantic fixtures."""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import uuid

root = Path(__file__).resolve().parent
corpus = json.loads((root / "prepared-corpus.json").read_text())
checker = root / "check-token-result.py"
source = (root / "topology-job.sh").read_text()
warm = (root / "warm-topology.py").read_text()
assert "srun --exact" in source and "srun --overlap" in source
assert "PBS" not in source and "pbs" not in source.lower()
assert source.index("ALL_WORKERS_READY") < source.index("warm-topology.py") < source.index("ALL_PAIRS_WARM") < source.index("token-control.py")
assert "client_status != 0 || check_status != 0" in source
assert "STARTUP_DEADLINE=$((T0+600))" in source and "WARMUP_DEADLINE=$((STARTUP_DEADLINE+120))" in source
assert "CLIENT_DEADLINE=$((WARMUP_DEADLINE+210))" in source and "CHECK_DEADLINE=$((CLIENT_DEADLINE+20))" in source
assert "TEARDOWN_DEADLINE=$((CHECK_DEADLINE+40))" in source and "HARD_STOP=$((T0+1020))" in source
assert "write_receipt" in warm and "check(receipt_dir, endpoints, run_token)" in warm
assert "ALL {checked[\"pair_count\"]} P/D paths semantically initialized" in warm
assert "expected_placement=$'prefill-0\\t0\\t4\\t30100\\t9000\\nprefill-1\\t0\\t4\\t30101\\t9001\\ndecode-0\\t1\\t8\\t30200\\t0'" in source

# The BF16 startup gate accepts only the actual rank-tagged allocation records.
rank_checker = root / "check-kv-ranks.py"
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    for worker, ranks, ep in [("prefill-0", 4, False), ("prefill-1", 4, False), ("decode-0", 8, True)]:
        log = td / f"{worker}.log"
        rows = []
        for rank in range(ranks):
            suffix = f" TP{rank} EP{rank}" if ep else f" TP{rank}"
            tokens, size = ("2148119", "48.14") if ep else ("1531197", "34.32")
            rows.append(f"[2026-10-22 00:00:00{suffix}] KV Cache is allocated. dtype: torch.bfloat16, "
                        f"#tokens: {tokens}, K size: {size} GB, V size: {size} GB")
        log.write_text("\n".join(rows) + "\n")
        subprocess.run([sys.executable, str(rank_checker), str(log), worker], check=True, capture_output=True)
        log.write_text("\n".join(rows[:-1]) + "\n")
        bad = subprocess.run([sys.executable, str(rank_checker), str(log), worker], capture_output=True)
        assert bad.returncode != 0, f"rank checker accepted incomplete {worker} rank set"
    log = td / "generic-tp.log"
    log.write_text("2026-10-22 generic TP1 KV Cache is allocated. dtype: torch.bfloat16, "
                   "#tokens: 1531197, K size: 34.32 GB, V size: 34.32 GB\n")
    bad = subprocess.run([sys.executable, str(rank_checker), str(log), "prefill-0"], capture_output=True)
    assert bad.returncode != 0, "rank checker accepted generic TP digits without the actual log shape"
    good_rows = [f"[2026-10-22 00:00:00 TP{r} EP{r}] KV Cache is allocated. dtype: torch.bfloat16, "
                 "#tokens: 2148119, K size: 48.14 GB, V size: 48.14 GB" for r in range(8)]
    for bad_rows, label in [
        (good_rows[:-1], "missing-rank"),
        ([*good_rows[:3], good_rows[3].replace("TP3 EP3", "TP3 EP2"), *good_rows[4:]], "mismatched-ep"),
        ([*good_rows[:2], good_rows[2].replace("#tokens: 2148119", "#tokens: 0"), *good_rows[3:]], "invalid-tokens"),
        ([*good_rows[:1], good_rows[1].replace("K size: 48.14 GB", "K size: NaN GB"), *good_rows[2:]], "invalid-size"),
    ]:
        log.write_text("\n".join(bad_rows) + "\n")
        bad = subprocess.run([sys.executable, str(rank_checker), str(log), "decode-0"], capture_output=True)
        assert bad.returncode != 0, f"rank checker accepted malformed {label} evidence"

def response(prompt):
    return {"meta_info": {"completion_tokens": 200, "prompt_tokens": prompt,
            "finish_reason": {"type": "length"},
            "output_token_logprobs": [["x", (i % 1000), -0.1] for i in range(200)]}}

def valid_result():
    result = {"schema": "h200-target-reference-v1", "passed": True, "platform": "H200",
              "cases": corpus["cases"], "corpus_sha256": hashlib.sha256((root / "prepared-corpus.json").read_bytes()).hexdigest(),
              "asset_identity": {"weight_bytes_total": 1, "container_image_path": "fixture", "container_image_bytes": None,
                                 "large_weight_sha256": "not_collected", "container_image_sha256": "not_collected"},
              "stages": {}, "comparisons": []}
    for stage in ("target-a", "target-b"):
        result["stages"][stage] = []
        for case in corpus["cases"]:
            request = {"input_ids": case["input_ids"], "stream": False, "return_logprob": True,
                "logprob_start_len": -1, "return_text_in_logprobs": False,
                "sampling_params": {"temperature": 0.0, "top_p": 1.0, "sampling_seed": 2026,
                                    "max_new_tokens": 200, "ignore_eos": True}}
            value = response(len(case["input_ids"]))
            observed = {"output_ids": [row[1] for row in value["meta_info"]["output_token_logprobs"]],
                        "finish_reason": value["meta_info"]["finish_reason"]}
            result["stages"][stage].append({"name": case["name"], "request": request,
                                              "response": value, "observed": observed})
    result["comparisons"] = [{"name": c["name"], "exact_ids_and_finish_equal": True} for c in corpus["cases"]]
    return result

def accepted(result, expected):
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "result.json"
        path.write_text(json.dumps(result))
        proc = subprocess.run([sys.executable, str(checker), str(path)], capture_output=True, text=True)
        assert (proc.returncode == 0) is expected, proc.stdout + proc.stderr

good = valid_result()
accepted(good, True)
mutations = []
bad = valid_result(); row = bad["stages"]["target-a"][0]; row["response"]["meta_info"]["output_token_logprobs"].pop(); row["response"]["meta_info"]["completion_tokens"] = 199; mutations.append(bad)
bad = valid_result(); bad["stages"]["target-a"].pop(); mutations.append(bad)
bad = valid_result(); bad["stages"]["target-a"][1]["request"]["input_ids"] = [1]; mutations.append(bad)
bad = valid_result(); bad["stages"]["target-b"][2]["response"]["meta_info"]["finish_reason"] = {"type": "stop"}; mutations.append(bad)
bad = valid_result(); bad["stages"]["target-b"][0] = bad["stages"]["target-b"][1]; mutations.append(bad)
bad = valid_result(); bad["stages"]["target-a"][0]["response"]["meta_info"]["output_token_logprobs"][9][1] = -1; mutations.append(bad)
bad = valid_result(); bad["passed"] = False; mutations.append(bad)
for result in mutations: accepted(result, False)

# Exercise the real client main() against a local /generate endpoint, not only its checker.
class MockGenerate(BaseHTTPRequestHandler):
    mode = "ok"

    def log_message(self, *_args):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        ids = [["token", i % 1000, -0.1] for i in range(200)]
        count, prompt, finish = 200, len(body["input_ids"]), {"type": "length"}
        if self.mode == "199": count, ids = 199, ids[:-1]
        elif self.mode == "missing-row": ids = ids[:-1]
        elif self.mode == "duplicate-row": ids.append(ids[-1])
        elif self.mode == "invalid-id": ids[5][1] = -1
        elif self.mode == "missing-id": ids[5][1] = None
        elif self.mode == "wrong-prompt": prompt += 1
        elif self.mode == "wrong-finish": finish = {"type": "stop"}
        payload = {"meta_info": {"completion_tokens": count, "prompt_tokens": prompt,
                   "finish_reason": finish, "output_token_logprobs": ids}}
        raw = json.dumps(payload).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

server = ThreadingHTTPServer(("127.0.0.1", 0), MockGenerate)
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    for mode, should_pass in [("ok", True), ("199", False), ("missing-row", False),
                              ("duplicate-row", False), ("invalid-id", False),
                              ("missing-id", False), ("wrong-prompt", False), ("wrong-finish", False)]:
        MockGenerate.mode = mode
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td); model = tmp / "model"; model.mkdir(); (model / "model.safetensors").write_bytes(b"fixture")
            artifact = tmp / "artifact"; artifact.mkdir()
            env = dict(os.environ, QWEN_EXPERIMENT_ID=str(uuid.uuid4()),
                       QWEN_CLIENT_DEADLINE_EPOCH=str(time.time() + 60), QWEN_IMAGE_PATH="fixture-image")
            client = subprocess.run([sys.executable, str(root / "token-control.py"),
                f"127.0.0.1:{server.server_port}", str(model), str(artifact)],
                env=env, capture_output=True, text=True)
            assert (client.returncode == 0) is should_pass, f"{mode}: {client.stdout}{client.stderr}"
            result_path = artifact / "target-reference.json"
            if should_pass:
                check = subprocess.run([sys.executable, str(checker), str(result_path)], capture_output=True, text=True)
                assert check.returncode == 0, check.stdout + check.stderr
            else:
                check = subprocess.run([sys.executable, str(checker), str(result_path)], capture_output=True, text=True)
                assert check.returncode != 0, f"head checker accepted client failure {mode}"
finally:
    server.shutdown(); server.server_close()

# Run the actual launcher with fake Slurm/network commands. Its failed token
# client must make the launcher fail and enter bounded cleanup immediately.
with tempfile.TemporaryDirectory() as td:
    td = Path(td); fakebin = td / "bin"; fakebin.mkdir()
    (fakebin / "scontrol").write_text("#!/bin/sh\nprintf 'node0\\nnode1\\n'\n")
    (fakebin / "getent").write_text("#!/bin/sh\nprintf '10.0.0.1 STREAM\\n'\n")
    (fakebin / "curl").write_text("#!/bin/sh\nexit 0\n")
    (fakebin / "srun").write_text("""#!/bin/bash
args="$*"
if [[ "$args" == *warm-topology.py* ]]; then
  echo 'ALL 2 P/D paths semantically initialized experiment_id=fixture'
  exit 0
fi
if [[ "$args" == *token-control.py* ]]; then exit 7; fi
if [[ "$args" == *worker.sh* ]]; then
  name="${*: -7:1}"
  # The final arguments are worker.sh name port model TP flags; use name
  # directly from the command substring to keep this fixture independent of srun options.
  if [[ "$args" == *prefill-0* || "$args" == *prefill-1* ]]; then
    for rank in 0 1 2 3; do echo "[2026-10-22 00:00:00 TP$rank] KV Cache is allocated. dtype: torch.bfloat16, #tokens: 1531197, K size: 34.32 GB, V size: 34.32 GB"; done
  else
    for rank in 0 1 2 3 4 5 6 7; do echo "[2026-10-22 00:00:00 TP$rank EP$rank] KV Cache is allocated. dtype: torch.bfloat16, #tokens: 2148119, K size: 48.14 GB, V size: 48.14 GB"; done
  fi
fi
exec sleep 300
""")
    for script in fakebin.iterdir(): script.chmod(0o755)
    env = dict(os.environ, PATH=str(fakebin) + os.pathsep + os.environ["PATH"],
               SLURM_SUBMIT_DIR=str(td), SLURM_JOB_ID="fixture", SLURM_JOB_NODELIST="node0,node1",
               QWEN_BUNDLE=str(root), QWEN_IMAGE_PATH="fixture-image", QWEN_EXPERIMENT_ID="fixture-id",
               QWEN_NIXL_PATCH_SHA256="fixture-patch", QWEN_JOB_START_EPOCH=str(int(time.time())))
    proc = subprocess.run(["bash", str(root / "topology-job.sh")], env=env,
                          capture_output=True, text=True, timeout=35)
    assert proc.returncode != 0, "launcher accepted a failed exact-token client"
    artifact = td / "runs" / "fixture"
    assert "FATAL: token reference rejected client_status=7" in proc.stderr, proc.stdout + proc.stderr
    assert "FATAL: bounded teardown deadline exceeded" not in proc.stderr
    assert (artifact / "token-client.log").exists()

for path in (root / "job.sbatch", root / "topology-job.sh", root / "worker.sh", root / "warm-topology.py"):
    if path.suffix == ".sh" or path.name.endswith(".sbatch"):
        subprocess.run(["bash", "-n", str(path)], check=True)
print("CPU_REFERENCE_FIXTURES_PASSED: real client/head checker, production-shaped BF16 rank gate, launcher failure propagation, and 1600-ID fixtures")
