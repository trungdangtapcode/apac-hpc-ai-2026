"""One bounded atomic write per MPI rank, outside solver timing."""
import os,json,socket
from pathlib import Path
status={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in Path('/proc/self/status').read_text().splitlines() if ':' in line}
rank=os.environ.get('PMI_RANK',os.environ.get('PMIX_RANK'))
assert rank is not None
record=dict(rank=int(rank),host=socket.gethostname(),affinity=sorted(os.sched_getaffinity(0)),mems_allowed=status.get('Mems_allowed_list'),scope='MPI diagnostic rank, not solver runtime drift/page-placement telemetry')
b=(json.dumps(record,sort_keys=True)+'\n').encode();assert len(b)<4096;assert os.write(1,b)==len(b)
