"""Tiny GPU/runtime test, not a Qwen performance or accuracy benchmark."""
import datetime
import ctypes
import json
import os
from pathlib import Path
import socket
import sys
import torch

result=dict(host=socket.gethostname(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            torch_version=torch.__version__,cuda_runtime=torch.version.cuda,
            torch_file=torch.__file__,path=os.environ.get('PATH'),ld_library_path=os.environ.get('LD_LIBRARY_PATH'),
            nvidia_devices=[str(p) for p in Path('/dev').glob('nvidia*')],
            cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),gpus=[])
try:
    cuda=ctypes.CDLL('libcuda.so.1');result['cuInit']=cuda.cuInit(0)
except Exception as error:result['libcuda_error']=str(error)
count=torch.cuda.device_count()
result['device_count']=count
print(json.dumps(result,indent=2),flush=True)
if count!=8:
    try:torch.cuda.init()
    except Exception as error:result['cuda_init_error']=str(error)
    result['passed']=False;Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
assert count==8, f'Expected eight allocated GPUs on this node, saw {count}'
for index in range(count):
    with torch.cuda.device(index):
        properties=torch.cuda.get_device_properties(index)
        a=torch.ones((512,512),device=f'cuda:{index}',dtype=torch.float16)
        checksum=(a@a).float().sum().item()
        torch.cuda.synchronize()
        assert checksum==512**3,(index,checksum)
        assert 'H100' in properties.name,properties.name
        result['gpus'].append(dict(index=index,name=properties.name,total_memory=properties.total_memory,
                                   capability=[properties.major,properties.minor],gemm_checksum=checksum))
        del a
result['passed']=True
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
