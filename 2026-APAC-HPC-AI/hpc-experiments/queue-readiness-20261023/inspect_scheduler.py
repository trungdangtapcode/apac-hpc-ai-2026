#!/usr/bin/env python3
"""Retain safe scheduler aggregates without inferring a job start time."""
from pathlib import Path
import argparse
import json
import shlex
import subprocess

HERE = Path(__file__).resolve().parent
SSH = HERE.parent / 'tools/nscc-cpu-ssh.sh'
REMOTE = r'''
import subprocess,json,datetime,collections
p=subprocess.run(['pbsnodes','-a','-F','json'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=25)
r={'checked_utc':datetime.datetime.utcnow().isoformat()+'Z','returncode':p.returncode,'scope':'Aggregate scheduler node metadata only; no other-user job IDs or authentication/environment material retained.'}
if p.returncode==0:
 ns=json.loads(p.stdout).get('nodes',{});pools=collections.Counter();states=collections.Counter();free_cpu=collections.Counter();eligible=0;standard=0;unused=0
 for node in ns.values():
  a=node.get('resources_available',{});u=node.get('resources_assigned',{});pool=str(a.get('node_pool','missing'));state=str(node.get('state','missing'));pools[pool]+=1
  if pool!='ex':continue
  states[state]+=1
  if float(a.get('ncpus',0))!=128 or float(a.get('ngpus',0))!=0:continue
  standard+=1;used=float(u.get('ncpus',0))
  if used==0:unused+=1
  if state=='free':free_cpu[str(int(128-used))]+=1
  if state=='free' and used==0:eligible+=1
 r.update({'node_count':len(ns),'node_pools':dict(pools),'ex_states':dict(states),'ex_128cpu_noGPU_nodes':standard,'ex_128cpu_noGPU_zero_assignedCPU':unused,'ex_128cpu_noGPU_state_free_zero_assignedCPU':eligible,'free_state_nodes_by_unassigned_cpu_count':dict(sorted(free_cpu.items(),key=lambda x:int(x[0]))),'limits':'PBS free is not proof of an empty node. This snapshot does not fully evaluate memory, reservations, node sharing or scheduler policy; no ETA or scheduler fault is inferred.'})
else:r['stderr']=p.stderr[-1000:]
q=subprocess.run(['qstat','-fx','-F','json','25940700.pbs101','25943865.pbs101','25947168.pbs101'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=20)
r['own_queue_returncode']=q.returncode
if q.returncode==0:
 keys=['job_state','queue','comment','depend','resources_used','Exit_status','stime']
 r['own_jobs']={n:{k:v[k] for k in keys if k in v} for n,v in json.loads(q.stdout)['Jobs'].items()}
else:r['own_queue_stderr']=q.stderr[-1000:]
print(json.dumps(r,indent=2))
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Preserve earlier snapshots'
    result = subprocess.run(['bash', str(SSH), 'bash -lc ' + shlex.quote('python3 -c ' + shlex.quote(REMOTE))],
                            capture_output=True, text=True, timeout=60, check=True)
    data = json.loads(result.stdout)
    args.output.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
