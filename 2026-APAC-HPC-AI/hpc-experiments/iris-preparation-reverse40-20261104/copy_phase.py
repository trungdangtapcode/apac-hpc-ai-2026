"""Copy and checksum one fresh accepted Scotch tree under the launching process policy."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

from qualification_utils import (process_masks, parse_numactl_show, node_snapshot,
    require_two_node_snapshot, exact_tree_paths, require_same_policy,
    supplementary_hashes, validate_manifest_paths)
from seal_tree import inventory


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--destination',required=True)
    ap.add_argument('--manifest',required=True)
    ap.add_argument('--supplementary',required=True)
    ap.add_argument('--expected-policy',required=True)
    ap.add_argument('--numactl',required=True)
    ap.add_argument('--treatment',choices=('inherited','interleave-all'),required=True)
    ap.add_argument('--result',required=True)
    args=ap.parse_args()
    src=Path(args.source); dst=Path(args.destination); result_path=Path(args.result)
    expected=json.loads(Path(args.manifest).read_text())
    supplementary=json.loads(Path(args.supplementary).read_text())
    validate_manifest_paths(expected,supplementary)
    combined={'files':{**expected['files'],**supplementary['files']},
              'symlinks':{**expected['symlinks'],**supplementary['symlinks']}}
    frozen_policy=json.loads(Path(args.expected_policy).read_text())
    assert not dst.exists() and not dst.is_symlink(),'destination must be fresh and unique'
    masks=process_masks()
    policy_proc=subprocess.run([args.numactl,'--show'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    assert policy_proc.returncode==0,policy_proc.stdout
    policy=parse_numactl_show(policy_proc.stdout)
    assert policy['policy']!='unknown',policy
    assert set(masks['allowed_memory_node_ids']) >= {0,1},masks
    if args.treatment=='interleave-all':
        assert policy['policy']=='interleave' and set(policy['interleave_nodes']) >= {0,1},policy
    else:
        require_same_policy(policy,frozen_policy)
    before=require_two_node_snapshot(node_snapshot())
    parent=dst.parent
    parent.mkdir(parents=True,exist_ok=True)
    t0=time.monotonic()
    shutil.copytree(src,dst,symlinks=True)
    copy_elapsed=time.monotonic()-t0
    after_copy=require_two_node_snapshot(node_snapshot())
    t1=time.monotonic()
    exact_tree_paths(dst,combined,supplementary['directories'])
    actual=inventory(dst)
    verify_elapsed=time.monotonic()-t1
    assert actual==expected,'destination content differs from accepted source manifest'
    extra_hashes=supplementary_hashes(dst,supplementary)
    source_inodes={(os.stat(src/name).st_dev,os.stat(src/name).st_ino) for name in combined['files']}
    reused=[name for name in combined['files'] if (os.stat(dst/name).st_dev,os.stat(dst/name).st_ino) in source_inodes]
    assert not reused,('destination reuses source inode',reused[:10])
    after_hash=require_two_node_snapshot(node_snapshot())
    manifest_digest=hashlib.sha256(json.dumps(actual,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    result={'passed':True,'treatment':args.treatment,'destination':str(dst),
            'regular_files':len(actual['files']),'symlinks':actual['symlinks'],
            'supplementary_files_verified':len(extra_hashes),
            'manifest_sha256':manifest_digest,'no_source_inode_reuse':True,
            'copy_seconds':copy_elapsed,'destination_hash_verify_seconds':verify_elapsed,
            'process_masks':masks,'effective_memory_policy':policy,
            'numa_snapshots':{'before_copy':before,'after_copy_before_hash':after_copy,'after_hash':after_hash},
            'scope':'Preparation-only copy/hash behavior. NUMA counters are whole-node deltas and do not locate these files/pages or predict solver time.'}
    result_path.parent.mkdir(parents=True,exist_ok=True)
    result_path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'passed':True,'regular_files':len(actual['files']),'copy_seconds':copy_elapsed,
                      'hash_verify_seconds':verify_elapsed,'policy':policy['policy']}))

if __name__=='__main__': main()
