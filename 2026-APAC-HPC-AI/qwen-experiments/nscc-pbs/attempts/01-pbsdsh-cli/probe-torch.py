"""Tiny GPU/runtime test, not a Qwen performance or accuracy benchmark."""
import datetime
import json
import os
from pathlib import Path
import socket
import sys
import torch

result=dict(host=socket.gethostname(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            torch_version=torch.__version__,cuda_runtime=torch.version.cuda,
            cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),gpus=[])
count=torch.cuda.device_count()
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
