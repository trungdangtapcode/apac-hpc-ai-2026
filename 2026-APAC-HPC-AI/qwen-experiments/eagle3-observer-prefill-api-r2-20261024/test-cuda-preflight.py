"""Replay the actual embedded GPU API preflight with a strict CPU-only stub."""
import sys,types
cuda=types.SimpleNamespace(device_count=lambda:4,get_device_capability=lambda:(9,0),get_device_name=lambda:'NVIDIA H100')
sys.modules['torch']=types.SimpleNamespace(cuda=cuda)
sys.modules['hpc']=types.SimpleNamespace(fuse_moe_blockwise=object())

from pathlib import Path
code=(Path(__file__).parent/'payload/worker.sh').read_text().split("<<'HPCCHECK'\n",1)[1].split('\nHPCCHECK',1)[0]
exec(code)
