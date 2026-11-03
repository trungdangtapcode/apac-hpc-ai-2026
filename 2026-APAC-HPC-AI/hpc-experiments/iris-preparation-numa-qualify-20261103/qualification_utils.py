"""Small safe helpers for the bounded preparation-locality qualification."""
from pathlib import Path
from pathlib import PurePosixPath
import datetime
import os
import re
import time
import stat
import hashlib


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def parse_id_list(value):
    values=set()
    for token in str(value).replace(',', ' ').split():
        if '-' in token:
            left,right=token.split('-',1)
            values.update(range(int(left),int(right)+1))
        elif token:
            values.add(int(token))
    return sorted(values)


def process_masks(status_path='/proc/self/status'):
    values={}
    for line in Path(status_path).read_text().splitlines():
        if ':' not in line: continue
        key,value=line.split(':',1)
        if key in ('Cpus_allowed_list','Mems_allowed_list'):
            values[key]=value.strip()
    values['cpu_affinity_ids']=sorted(os.sched_getaffinity(0))
    values['cpu_affinity_count']=len(values['cpu_affinity_ids'])
    values['allowed_cpu_ids']=parse_id_list(values.get('Cpus_allowed_list',''))
    values['allowed_memory_node_ids']=parse_id_list(values.get('Mems_allowed_list',''))
    return values


def parse_numactl_show(text):
    rows={}
    for line in text.splitlines():
        match=re.match(r'^\s*([^:]+):\s*(.*?)\s*$',line)
        if match: rows[match.group(1).strip().lower()]=match.group(2)
    policy=rows.get('policy','unknown').lower()
    mask_text=rows.get('interleave',rows.get('interleave node mask',''))
    try: interleave_nodes=parse_id_list(mask_text)
    except ValueError: interleave_nodes=[]
    return {'policy':policy,'interleave_nodes':interleave_nodes,
            'membind_nodes':parse_id_list(rows.get('membind','')) if rows.get('membind') else [],
            'cpubind_nodes':parse_id_list(rows.get('cpubind','')) if rows.get('cpubind') else [],
            'raw':text}


def parse_hardware_nodes(text):
    m=re.search(r'(?m)^available:\s*(\d+)\s+nodes?\s*\(([^)]*)\)',text)
    if not m: return {'count':None,'node_ids':[]}
    return {'count':int(m.group(1)),'node_ids':parse_id_list(m.group(2))}


def node_snapshot(sysfs_root='/sys/devices/system/node', node_ids=(0,1)):
    started=time.monotonic_ns(); root=Path(sysfs_root); nodes={}; errors={}
    for node in node_ids:
        path=root/f'node{node}'; row={'available':True}
        try:
            mem={}
            for line in (path/'meminfo').read_text().splitlines():
                m=re.match(r'^Node\s+\d+\s+([^:]+):\s*(\d+)(?:\s+(\w+))?$',line)
                if m: mem[m.group(1).strip()]={'value':int(m.group(2)),'unit':m.group(3)}
            stats={}
            for line in (path/'numastat').read_text().splitlines():
                parts=line.split()
                if len(parts)>=2:
                    try: stats[parts[0]]=int(parts[1])
                    except ValueError: continue
            if not mem or not stats: raise ValueError('empty NUMA sysfs record')
            row.update({'meminfo':mem,'numastat':stats})
        except Exception as exc:
            row={'available':False,'error':type(exc).__name__}
            errors[str(node)]=type(exc).__name__
        nodes[str(node)]=row
    return {'timestamp_utc':utc_now(),'timestamp_monotonic_seconds':time.monotonic(),
            'nodes':nodes,'errors':errors,'collection_ms':(time.monotonic_ns()-started)/1e6,
            'scope':'Whole-node cumulative sysfs NUMA/memory counters; not process-attributed placement.'}


def require_two_node_snapshot(snapshot):
    assert set(snapshot['nodes'])=={'0','1'},('expected node0/node1',list(snapshot['nodes']))
    assert all(row.get('available') for row in snapshot['nodes'].values()),snapshot['errors']
    return snapshot


def exact_tree_paths(root, expected, explicit_dirs=None):
    """Reject every unmanifested path, including root/processor extras and empty dirs."""
    root=Path(root)
    expected_files=set(expected['files'])
    expected_links=set(expected['symlinks'])
    expected_dirs=set()
    for rel in expected_files|expected_links:
        parent=Path(rel).parent
        while str(parent)!='.':
            expected_dirs.add(parent.as_posix())
            parent=parent.parent
    found_files=set(); found_links=set(); found_dirs=set()
    for base,dirs,files in os.walk(root,topdown=True,followlinks=False):
        here=Path(base)
        for name in list(dirs):
            p=here/name; rel=p.relative_to(root).as_posix()
            mode=p.lstat().st_mode
            if stat.S_ISLNK(mode):
                found_links.add(rel); dirs.remove(name)
            elif stat.S_ISDIR(mode): found_dirs.add(rel)
            else: raise ValueError(f'unsupported path type: {rel}')
        for name in files:
            p=here/name; rel=p.relative_to(root).as_posix()
            mode=p.lstat().st_mode
            if stat.S_ISLNK(mode): found_links.add(rel)
            elif stat.S_ISREG(mode): found_files.add(rel)
            else: raise ValueError(f'unsupported path type: {rel}')
    permitted_dirs=set(explicit_dirs) if explicit_dirs is not None else expected_dirs
    if found_files!=expected_files or found_links!=expected_links or found_dirs!=permitted_dirs:
        raise ValueError('tree path set differs from accepted manifest: '+repr({
            'extra_files':sorted(found_files-expected_files)[:12],
            'missing_files':sorted(expected_files-found_files)[:12],
            'extra_symlinks':sorted(found_links-expected_links)[:12],
            'missing_symlinks':sorted(expected_links-found_links)[:12],
            'extra_dirs':sorted(found_dirs-permitted_dirs)[:12],
            'missing_dirs':sorted(permitted_dirs-found_dirs)[:12]}))
    for rel,target in expected['symlinks'].items():
        if os.readlink(root/rel)!=target: raise ValueError(f'wrong symlink target: {rel}')
    return True


def supplementary_hashes(root, supplementary):
    root=Path(root); observed={}
    for rel,expected_hash in supplementary['files'].items():
        digest=hashlib.sha256()
        with (root/rel).open('rb') as f:
            for block in iter(lambda:f.read(4*1024*1024),b''): digest.update(block)
        got=digest.hexdigest()
        if got!=expected_hash: raise ValueError(f'supplementary source hash mismatch: {rel}')
        observed[rel]=got
    return observed


def validate_manifest_paths(core, supplementary):
    def safe(value):
        p=PurePosixPath(value)
        return not p.is_absolute() and bool(p.parts) and all(part not in ('','.','..') for part in p.parts)
    for manifest in (core,supplementary):
        for rel in set(manifest.get('files',{}))|set(manifest.get('symlinks',{})):
            if not safe(rel): raise ValueError(f'unsafe manifest path: {rel!r}')
    for rel in supplementary.get('directories',[]):
        if not safe(rel): raise ValueError(f'unsafe manifest directory: {rel!r}')
    for key in set(core.get('files',{}))&set(supplementary.get('files',{})):
        if core['files'][key]!=supplementary['files'][key]: raise ValueError(f'conflicting manifests for {key}')
    for key in set(core.get('symlinks',{}))&set(supplementary.get('symlinks',{})):
        if core['symlinks'][key]!=supplementary['symlinks'][key]: raise ValueError(f'conflicting symlink manifests for {key}')


def policy_signature(policy):
    return tuple((policy.get(k) or []) if k!='policy' else policy.get(k)
                 for k in ('policy','interleave_nodes','membind_nodes'))


def require_same_policy(actual, expected):
    if actual.get('policy')=='unknown' or policy_signature(actual)!=policy_signature(expected):
        raise ValueError('observed child memory policy differs from frozen inherited policy')
