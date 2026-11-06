"""Retry only a pre-admission transport failure with a fresh-line frame boundary.

The prior call failed during read-only queue preflight before reservation or
sbatch. Frozen native payload and scheduler admission gates remain unchanged.
"""
from pathlib import Path
import sys,runpy
E=Path(__file__).resolve().parent
assert not any((E/n).exists() for n in ('submission-intent.json','submission-receipt.json','submission-uncertain.json'))
sys.path.insert(0,str(E.parent/'tools'))
import iris_bridge
original=iris_bridge.run_json
def framed(body,**kwargs):
    return original("print('\\n', flush=True)\n"+body,**kwargs)
iris_bridge.run_json=framed
sys.argv=[str(E/'deploy_submit.py'),'submit']
runpy.run_path(str(E/'deploy_submit.py'),run_name='__main__')
