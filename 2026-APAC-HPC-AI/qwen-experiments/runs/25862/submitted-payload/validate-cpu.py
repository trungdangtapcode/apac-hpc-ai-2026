"""Validate S49 source fixtures, accepted reference binding, and fail-closed tamper cases."""
import json,subprocess,sys,tempfile,hashlib,shutil
from pathlib import Path
bundle=Path(__file__).resolve().parent
for test in ("test_asset_binding.py","test_kv_geometry.py","test_deterministic_source_contract.py","test_deterministic_runtime.py","test_worker_launch_contract.py"):
 subprocess.run([sys.executable,str(bundle/test)],cwd=bundle,check=True)
binding=json.loads((bundle/"target-reference-binding.json").read_text())
reference=json.loads((bundle/binding["target_reference_file"]).read_text())
corpus=json.loads((bundle/"prepared-corpus.json").read_text())
assert reference["experiment_id"].startswith("s46-h200-deterministic-reference-25855-")
assert reference["cases"]==corpus["cases"] and len(reference["comparisons"])==4
assert sum(len(row["observed"]["output_ids"]) for stage in reference["stages"].values() for row in stage)==1600
assert all(row["exact_ids_and_finish_equal"] for row in reference["comparisons"])
checker=bundle/"check-target-binding.py"; binding_path=bundle/"target-reference-binding.json"
valid=subprocess.run([sys.executable,str(checker),str(binding_path)],cwd=bundle,capture_output=True,text=True)
assert valid.returncode==0 and "S46_TARGET_REFERENCE_BINDING_VERIFIED" in valid.stdout,valid.stderr
x=binding
assert x["target_job"]=="25855" and x["target_reference_sha256"]==hashlib.sha256((bundle/x["target_reference_file"]).read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
 t=Path(td); shutil.copy2(bundle/x["target_reference_file"],t/x["target_reference_file"]); shutil.copy2(bundle/x["target_review_path"],t/x["target_review_path"]); bad=dict(x);bad["target_reference_sha256"]="0"*64;(t/"target-reference-binding.json").write_text(json.dumps(bad))
 r=subprocess.run([sys.executable,str(checker),str(t/"target-reference-binding.json")],capture_output=True,text=True)
 assert r.returncode!=0 and "hash mismatch" in r.stderr
 bad=dict(x);bad["state"]="WAITING_FOR_S46_REVIEW";(t/"target-reference-binding.json").write_text(json.dumps(bad))
 r=subprocess.run([sys.executable,str(checker),str(t/"target-reference-binding.json")],capture_output=True,text=True)
 assert r.returncode!=0 and "accepted actual S46" in r.stderr
print("S49 CPU fixtures pass; actual reference bound; unbound and altered-hash bindings fail closed; no GPU evidence inferred")
