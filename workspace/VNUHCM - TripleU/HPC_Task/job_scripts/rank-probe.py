"""Capture one rank's single-CPU affinity and local topology for a startup probe."""
import json, os, socket
from pathlib import Path

def read(p): return Path(p).read_text().strip()
def parse_list(s):
 out=[]
 for part in s.split(','):
  if '-' in part:
   a,b=map(int,part.split('-',1)); out.extend(range(a,b+1))
  else: out.append(int(part))
 return out
rank=os.environ.get('PMI_RANK',os.environ.get('PMIX_RANK',os.environ.get('PMI_ID')))
assert rank is not None,'No supported PMI rank environment variable'
affinity=sorted(os.sched_getaffinity(0)); assert len(affinity)==1,affinity
cpu=affinity[0]; topo=Path('/sys/devices/system/cpu')/('cpu'+str(cpu))/'topology'
package=int(read(topo/'physical_package_id')); core=int(read(topo/'core_id'))
siblings=sorted(parse_list(read(topo/'thread_siblings_list')))
node_ids=[]
for p in sorted(Path('/sys/devices/system/node').glob('node[0-9]*')):
 try:
  if cpu in parse_list(read(p/'cpulist')): node_ids.append(int(p.name[4:]))
 except (FileNotFoundError,ValueError): pass
assert len(node_ids)==1,(cpu,node_ids)
record={'rank':int(rank),'host':socket.gethostname().split('.')[0],'affinity_cpus':affinity,'physical_package_id':package,'physical_core_id':core,'thread_siblings':siblings,'numa_node':node_ids[0],'scope':'Startup-only allocation placement evidence; not solver-time migration, page residency, or MPI traffic.'}
b=(json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode(); assert len(b)<4096; assert os.write(1,b)==len(b)
