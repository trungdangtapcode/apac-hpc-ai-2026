"""Compare fresh partition adjacency/cell identities with the pinned screened graph.

Parser bodies derive from the retained screen.py; only type annotations removed
for the site's Python3.6. This checks graph identity, not complete mesh identity.
"""
from pathlib import Path
import argparse,hashlib,json,re
RANKS=512
PINNED_GRAPH_SHA256='3ba8612bf5e0521f2cfb39fdd4c9d0642f689c6e5a86a9bb93accad212b7a209'
def require(condition, message):
    if not condition:
        raise AssertionError(message)

def parse_boundary(rank, raw):
    text = raw.decode('ascii', errors='strict')
    count_match = re.search('(?m)^\\s*(\\d+)\\s*$\\s*^\\s*\\(\\s*$', text)
    require(count_match is not None, f'processor{rank}: patch count/list header missing')
    declared_count = int(count_match.group(1))
    body_start = count_match.end()
    body_end = text.rfind('\n)')
    require(body_end > body_start, f'processor{rank}: patch list close missing')
    body = text[body_start:body_end]
    pattern = re.compile('(?m)^[ \\t]*([^\\s{}()]+)[ \\t]*\\n[ \\t]*\\{(.*?)^[ \\t]*\\}', re.S)
    patches = []
    cursor = 0
    for match in pattern.finditer(body):
        require(not body[cursor:match.start()].strip(), f'processor{rank}: unparsed boundary content')
        (name, fields) = (match.group(1), match.group(2))
        face_match = re.search('(?m)^\\s*nFaces\\s+(\\d+)\\s*;', fields)
        type_match = re.search('(?m)^\\s*type\\s+(\\w+)\\s*;', fields)
        require(face_match and type_match, f'processor{rank}/{name}: missing type or nFaces')
        patch = {'name': name, 'type': type_match.group(1), 'nFaces': int(face_match.group(1))}
        if patch['type'] == 'processor':
            proc_match = re.fullmatch('procBoundary(\\d+)to(\\d+)', name)
            my_match = re.search('(?m)^\\s*myProcNo\\s+(\\d+)\\s*;', fields)
            neighbor_match = re.search('(?m)^\\s*neighbProcNo\\s+(\\d+)\\s*;', fields)
            require(proc_match and my_match and neighbor_match, f'processor{rank}/{name}: malformed processor patch identity')
            (local_id, neighbor_id) = map(int, proc_match.groups())
            require(local_id == rank and int(my_match.group(1)) == rank, f'processor{rank}/{name}: local processor ID mismatch')
            require(int(neighbor_match.group(1)) == neighbor_id, f'processor{rank}/{name}: neighbor processor ID mismatch')
            require(neighbor_id != rank and 0 <= neighbor_id < RANKS, f'processor{rank}/{name}: invalid neighbor ID')
            require(patch['nFaces'] > 0, f'processor{rank}/{name}: nonpositive interface faces')
            patch['neighbor'] = neighbor_id
        patches.append(patch)
        cursor = match.end()
    require(not body[cursor:].strip(), f'processor{rank}: trailing unparsed boundary content')
    require(len(patches) == declared_count, f'processor{rank}: declared {declared_count} patches, parsed {len(patches)}')
    require(len({patch['name'] for patch in patches}) == len(patches), f'processor{rank}: duplicate patch name')
    processor_patches = [patch for patch in patches if patch['type'] == 'processor']
    require(all((patch['name'].startswith('procBoundary') for patch in processor_patches)), f'processor{rank}: processor patch name mismatch')
    return (processor_patches, declared_count)

def parse_native_log(text):
    blocks = list(re.finditer('(?m)^Processor\\s+(\\d+)\\s*$', text))
    require(len(blocks) == RANKS, f'native log has {len(blocks)} processor blocks')
    rows = [None] * RANKS
    for (index, match) in enumerate(blocks):
        rank = int(match.group(1))
        require(0 <= rank < RANKS and rows[rank] is None, f'duplicate/invalid native processor ID {rank}')
        end = blocks[index + 1].start() if index + 1 < len(blocks) else text.find('\nEnd', match.end())
        require(end > match.end(), f'native processor{rank} block does not terminate')
        block = text[match.end():end]
        cells_match = re.search('(?m)^\\s*Number of cells\\s*=\\s*(\\d+)\\s*$', block)
        processor_faces_match = re.search('(?m)^\\s*Number of processor faces\\s*=\\s*(\\d+)\\s*$', block)
        shared = {int(other): int(faces) for (other, faces) in re.findall('(?m)^\\s*Number of faces shared with processor\\s+(\\d+)\\s*=\\s*(\\d+)\\s*$', block)}
        require(cells_match and processor_faces_match, f'native processor{rank}: cell/interface summary missing')
        require(len(shared) == len(re.findall('Number of faces shared with processor', block)), f'native processor{rank}: duplicate shared-face row')
        rows[rank] = {'rank': rank, 'cells': int(cells_match.group(1)), 'processor_faces': int(processor_faces_match.group(1)), 'shared_faces': shared}
    return ([row['cells'] for row in rows], rows)

def validate(case, log, graph, layout='case'):
    graph=Path(graph);raw=graph.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PINNED_GRAPH_SHA256,'Screened graph provenance mismatch'
    expected=json.loads(raw.decode());case=Path(case)
    cells,native=parse_native_log(Path(log).read_text(encoding='ascii'))
    assert cells==expected['cells_by_rank'],'Fresh processor cell identities differ from screened graph'
    assert sum(cells)==65334765
    directed={};seals=[]
    for rank in range(RANKS):
        boundary=case/('processor'+str(rank))/('constant/polyMesh/boundary' if layout=='case' else 'boundary')
        data=boundary.read_bytes();patches,_=parse_boundary(rank,data)
        shared={x['neighbor']:x['nFaces'] for x in patches}
        assert len(shared)==len(patches),('Duplicate neighbor',rank)
        assert shared==native[rank]['shared_faces'],('Native and boundary graph differ',rank)
        assert native[rank]['processor_faces']==sum(shared.values())
        for other,faces in shared.items():directed[(rank,other)]=faces
        seals.append({'rank':rank,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    for (rank,other),faces in directed.items():assert directed.get((other,rank))==faces,('Non-reciprocal edge',rank,other)
    edges=[{'a':a,'b':b,'faces':faces} for (a,b),faces in sorted(directed.items()) if a<b]
    assert edges==expected['edges'],'Fresh graph edge/rank identity differs from screened assignment'
    assert sum(x['faces'] for x in edges)==2927022
    return {'passed':True,'ranks':RANKS,'cells':sum(cells),'unique_edges':len(edges),'unique_interface_faces':sum(x['faces'] for x in edges),'screened_graph_sha256':PINNED_GRAPH_SHA256,'fresh_boundary_sha256':seals,'scope':'Exact per-rank cell counts and processor-patch adjacency/face counts agree with screened graph. Not a complete mesh/partition cell-membership hash or solver-time traffic proof.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('case');ap.add_argument('decompose_log');ap.add_argument('graph');ap.add_argument('--output',required=True);ap.add_argument('--layout',choices=['case','collected'],default='case');a=ap.parse_args()
    out=validate(a.case,a.decompose_log,a.graph,a.layout)
    Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='fresh_boundary_sha256'},indent=2))
if __name__=='__main__':main()
