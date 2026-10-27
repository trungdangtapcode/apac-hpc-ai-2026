"""Validate allocation nodefile and actual 512-rank launcher host counts."""
from pathlib import Path
import collections,json,sys
mode=sys.argv[1]
if mode=='nodefile':
 rows=[x.strip().split('.')[0] for x in Path(sys.argv[2]).read_text().splitlines() if x.strip()]
 counts=collections.Counter(rows)
 assert len(rows)==512 and len(counts)==4 and sorted(counts.values())==[128]*4,(len(rows),counts)
 result={'passed':True,'lines':512,'node_counts':dict(sorted(counts.items()))}
elif mode=='rank-hosts':
 actual=collections.Counter(x.strip().split('.')[0] for x in Path(sys.argv[2]).read_text().splitlines() if x.strip())
 expected=collections.Counter(x.strip().split('.')[0] for x in Path(sys.argv[3]).read_text().splitlines() if x.strip())
 assert sum(actual.values())==512 and set(actual)==set(expected) and sorted(actual.values())==[128]*4,(actual,expected)
 result={'passed':True,'actual_mpirun_host_rank_counts':dict(sorted(actual.items())),'source':'mpirun -np 512 hostname'}
else: raise SystemExit('mode must be nodefile or rank-hosts')
print(json.dumps(result,indent=2))
