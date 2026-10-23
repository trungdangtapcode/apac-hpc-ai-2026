#!/usr/bin/env python3
"""Run retained target asset, candidate client/head, and NIXL geometry CPU fixtures."""
import subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parent
for script, cwd in ((root/'test_asset_binding.py',root),(root/'test_kv_geometry.py',root),(root.parent/'test_candidate_cpu.py',root.parent)):
 result=subprocess.run([sys.executable,str(script)],cwd=cwd)
 if result.returncode: raise SystemExit(result.returncode)
print('ALL_CPU_FIXTURES_PASSED')
