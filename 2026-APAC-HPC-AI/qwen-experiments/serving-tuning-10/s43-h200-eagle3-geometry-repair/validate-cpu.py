"""Verify frozen bytes, then replay the retained source CPU fixtures."""
from pathlib import Path
import subprocess,sys
bundle=Path(__file__).resolve().parent
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,check=True)
source=bundle.parents[1]/'eagle3-h200-candidate-20261023/payload/validate-cpu.py'
subprocess.run([sys.executable,str(source)],check=True)
