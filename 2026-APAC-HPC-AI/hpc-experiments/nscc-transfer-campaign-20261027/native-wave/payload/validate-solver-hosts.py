"""Verify the actual solver's native host list against this allocation."""
from pathlib import Path
import collections,json,re,sys

log=Path(sys.argv[1]).read_text(errors='replace')
expected=collections.Counter(line.strip().split('.')[0] for line in Path(sys.argv[2]).read_text().splitlines() if line.strip())
block=re.search(r'(?ms)^Hosts\s*:\s*\n\(\s*\n(.*?)^\)',log)
assert block,'Native solver host block missing'
actual={}
for name,count in re.findall(r'^\s*\((\S+)\s+(\d+)\)\s*$',block.group(1),re.M):
    host=name.split('.')[0];assert host not in actual,host;actual[host]=int(count)
assert len(expected)==4 and sorted(expected.values())==[128]*4,dict(expected)
assert actual==dict(expected),(actual,dict(expected))
assert re.search(r'(?m)^nProcs\s*:\s*512\s*$',log)
print(json.dumps({'passed':True,'actual_solver_host_rank_counts':actual,'source':'Native simpleFoam header, independently matched to PBS_NODEFILE.'},indent=2))
