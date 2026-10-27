"""Require 512 uniquely placed rank probes over four actual 128-core hosts."""
import argparse,json,collections
from collections import Counter
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('jsonl');ap.add_argument('--expected-ranks',type=int,default=512);ap.add_argument('--nodefile');a=ap.parse_args()
rows=[json.loads(x) for x in Path(a.jsonl).read_text().splitlines() if x.strip()]
n=a.expected_ranks
assert len(rows)==n and sorted(x['rank'] for x in rows)==list(range(n)),('rank count/IDs',len(rows))
assert all(len(x['affinity_cpus'])==1 for x in rows),'rank affinity is not one logical CPU'
byhost=Counter(x['host'] for x in rows)
assert len(byhost)==4 and sorted(byhost.values())==[128]*4,byhost
if a.nodefile:
 requested=Counter(x.strip().split('.')[0] for x in Path(a.nodefile).read_text().splitlines() if x.strip())
 assert sum(requested.values())==512 and len(requested)==4 and sorted(requested.values())==[128]*4,requested
 assert requested==byhost,(requested,byhost)
physical=[(x['host'],x['physical_package_id'],x['physical_core_id']) for x in rows]
assert len(set(physical))==n,'physical core repeated across ranks'
logical=[(x['host'],x['affinity_cpus'][0]) for x in rows]
assert len(set(logical))==n,'logical CPU repeated across ranks'
assert all(len(x['thread_siblings'])>=1 and x['affinity_cpus'][0] in x['thread_siblings'] for x in rows)
assert all(isinstance(x['numa_node'],int) for x in rows)
summary={'passed':True,'ranks':n,'hosts':dict(sorted(byhost.items())),'unique_logical_cpus':len(set(logical)),'unique_physical_cores':len(set(physical)),'nodes':4,'ranks_per_host':128,'scope':'Startup allocation binding evidence only; not solver-time affinity, page placement, migration, or measured communication.'}
print(json.dumps(summary,indent=2))
