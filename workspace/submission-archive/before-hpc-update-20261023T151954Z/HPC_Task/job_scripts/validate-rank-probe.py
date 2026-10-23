"""Require one startup rank per distinct physical core and PBS slot."""
import argparse,json
from collections import Counter
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('jsonl');p.add_argument('--expected-ranks',type=int,required=True);p.add_argument('--nodes',type=int,required=True);p.add_argument('--nodefile');a=p.parse_args(); rows=[json.loads(s) for s in Path(a.jsonl).read_text().splitlines() if s.strip()];n=a.expected_ranks
assert len(rows)==n and sorted(x['rank'] for x in rows)==list(range(n)),('rank count/IDs',len(rows))
assert all(len(x['affinity_cpus'])==1 for x in rows),'rank is not bound to exactly one logical CPU'
host=Counter(x['host'] for x in rows); assert len(host)==a.nodes and sorted(host.values())==[128]*a.nodes,host
if a.nodefile:
 slots=Counter(x.strip().split('.')[0] for x in Path(a.nodefile).read_text().splitlines() if x.strip()); assert sum(slots.values())==n and len(slots)==a.nodes and sorted(slots.values())==[128]*a.nodes and slots==host,(slots,host)
physical=[(x['host'],x['physical_package_id'],x['physical_core_id']) for x in rows]; logical=[(x['host'],x['affinity_cpus'][0]) for x in rows]
assert len(set(physical))==n,'physical core reused'; assert len(set(logical))==n,'logical CPU reused'; assert all(len(x['thread_siblings'])>=1 and x['affinity_cpus'][0] in x['thread_siblings'] for x in rows); assert all(isinstance(x['numa_node'],int) for x in rows)
print(json.dumps({'passed':True,'ranks':n,'hosts':dict(sorted(host.items())),'unique_logical_cpus':len(set(logical)),'unique_physical_cores':len(set(physical)),'nodes':a.nodes,'ranks_per_host':128,'scope':'Startup allocation placement only; does not establish solver-time affinity, migration, or page placement.'},indent=2))
