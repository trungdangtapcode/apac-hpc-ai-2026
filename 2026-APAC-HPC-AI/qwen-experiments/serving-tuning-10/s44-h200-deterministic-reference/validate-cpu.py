"""Run CPU-only asset, geometry, deterministic source and resolved-log fixture checks."""
import subprocess,sys
from pathlib import Path
bundle=Path(__file__).resolve().parent
for test in ("test_asset_binding.py","test_kv_geometry.py","test_deterministic_source_contract.py","test_deterministic_runtime.py","test_deterministic_reference_gate.py"):
 subprocess.run([sys.executable,str(bundle/test)],cwd=bundle,check=True)
