"""Validate launcher rank masks against observed NUMA CPU sets; no page claim."""
from pathlib import Path

def cpu_set(text):
    result=set()
    for token in text.strip().split(','):
        if '-' in token:
            a,b=map(int,token.split('-'));result.update(range(a,b+1))
        elif token:result.add(int(token))
    return result

def validate_balanced40(report,topology=None):
    if topology is None:
        topology={p.parent.name:cpu_set(p.read_text()) for p in Path('/sys/devices/system/node').glob('node[0-9]*/cpulist')}
    if len(topology)!=2 or report.get('rank_count')!=40 or len(report.get('proofs',[]))!=40:
        raise ValueError('balanced40 requires actual two-node NUMA topology and forty rank records')
    counts={name:0 for name in topology}
    for record in report['proofs']:
        mask=set(record['affinity_cpu_ids']);matches=[name for name,cpus in topology.items() if mask and mask<=cpus]
        if len(matches)!=1:raise ValueError('rank mask must lie wholly within one observed NUMA node')
        counts[matches[0]]+=1
    if sorted(counts.values())!=[20,20]:raise ValueError('rank counts are not 20/20: '+str(counts))
    return {'passed':True,'rank_count':40,'rank_counts_by_NUMA_node':counts,'NUMA_CPU_sets':{k:sorted(v) for k,v in topology.items()},'scope':'Launcher affinity before MPI_Init; not solver helper affinity or page placement.'}
