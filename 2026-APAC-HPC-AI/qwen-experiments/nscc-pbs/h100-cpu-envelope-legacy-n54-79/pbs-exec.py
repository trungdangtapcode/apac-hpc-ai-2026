"""Restore OCI image environment as data, then override host GPU driver paths."""
import json
import os
from pathlib import Path
import sys

image_environment=Path('/etc/environment')
if image_environment.exists():
    for line in image_environment.read_text().splitlines():
        if '=' not in line or line.startswith('#'):continue
        key,value=line.split('=',1)
        if not key.replace('_','').isalnum():continue
        if len(value)>1 and value[0]==value[-1] and value[0] in ('"',"'"):value=value[1:-1]
        os.environ[key]=os.path.expandvars(value)
libraries=[p for p in os.environ.get('LD_LIBRARY_PATH','').split(':') if p and '/cuda/compat' not in p]
os.environ['LD_LIBRARY_PATH']=':'.join(['/.singularity.d/libs','/usr/local/nvidia/lib64','/usr/local/nvidia/lib',*libraries])
os.environ['CUDA_VISIBLE_DEVICES']=sys.argv[1]
os.environ['PYTHONNOUSERSITE']='1'
os.environ.update(json.loads(sys.argv[2]))
if int(os.environ.get('QWEN_TASK_GPU_COUNT','0')):
    import importlib.util
    helper=Path(__file__).with_name('worker-cpu-envelope.py')
    specification=importlib.util.spec_from_file_location('cpu_envelope',helper)
    envelope=importlib.util.module_from_spec(specification);specification.loader.exec_module(envelope)
    envelope.apply_envelope(sys.argv[5])
os.execvp(sys.argv[3],sys.argv[3:])
