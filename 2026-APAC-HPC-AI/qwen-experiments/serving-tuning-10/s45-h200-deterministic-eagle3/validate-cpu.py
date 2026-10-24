"""Run candidate CPU fixtures and prove the unbound target receipt guard blocks."""
import subprocess,sys
from pathlib import Path
bundle=Path(__file__).resolve().parent
for test in ("test_asset_binding.py","test_kv_geometry.py","test_deterministic_source_contract.py","test_deterministic_runtime.py"):
 subprocess.run([sys.executable,str(bundle/test)],cwd=bundle,check=True)
blocked=subprocess.run([sys.executable,str(bundle/"check-target-binding.py"),str(bundle/"target-reference-binding.json")],cwd=bundle,capture_output=True,text=True)
assert blocked.returncode!=0 and "blocked until root binds" in blocked.stderr
print("S45 waiting binding guard correctly fails closed; no GPU result inferred")
