"""Validate 48-rank launcher affinity against observed two-node NUMA CPU sets."""
from pathlib import Path

def cpu_set(text):
    result=set()
    for token in text.strip().split(','):
        if '-' in token:
            a,b=map(int,token.split('-'));result.update(range(a,b+1))
        elif token:result.add(int(token))
    return result

def validate_balanced48(report,topology=None):
    if topology is None:
        topology={p.parent.name:cpu_set(p.read_text()) for p in Path('/sys/devices/system/node').glob('node[0-9]*/cpulist')}
    if len(topology)!=2 or report.get('rank_count')!=48 or len(report.get('proofs',[]))!=48:
        raise ValueError('balanced48 requires actual two-node NUMA topology and forty-eight rank records')
    counts={name:0 for name in topology}
    for record in report['proofs']:
        mask=set(record['affinity_cpu_ids']);matches=[name for name,cpus in topology.items() if mask and mask<=cpus]
        if len(matches)!=1:raise ValueError('rank mask must lie wholly within one observed NUMA node')
        counts[matches[0]]+=1
    if sorted(counts.values())!=[24,24]:raise ValueError('rank counts are not 24/24: '+str(counts))
    return {'passed':True,'rank_count':48,'rank_counts_by_NUMA_node':counts,'NUMA_CPU_sets':{k:sorted(v) for k,v in topology.items()},'scope':'Launcher affinity before MPI_Init; not solver helper affinity or page placement.'}
