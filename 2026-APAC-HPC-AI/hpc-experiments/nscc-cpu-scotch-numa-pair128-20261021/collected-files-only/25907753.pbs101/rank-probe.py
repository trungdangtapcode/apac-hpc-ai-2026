"""One bounded atomic write per MPI rank, outside solver timing."""
import os,json,socket
from pathlib import Path
status={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in Path('/proc/self/status').read_text().splitlines() if ':' in line}
rank=os.environ.get('PMI_RANK',os.environ.get('PMIX_RANK'))
assert rank is not None
cpu=next(iter(os.sched_getaffinity(0)));topo=Path('/sys/devices/system/cpu')/('cpu'+str(cpu));numa=sorted(int(p.name[4:]) for p in topo.glob('node[0-9]*'))
physical_core=[int((topo/'topology/physical_package_id').read_text()),int((topo/'topology/core_id').read_text())]
record=dict(numa_nodes=numa,physical_core=physical_core,rank=int(rank),host=socket.gethostname(),affinity=sorted(os.sched_getaffinity(0)),mems_allowed=status.get('Mems_allowed_list'),scope='MPI diagnostic rank, not solver runtime drift/page-placement telemetry')
b=(json.dumps(record,sort_keys=True)+'\n').encode();assert len(b)<4096;assert os.write(1,b)==len(b)
