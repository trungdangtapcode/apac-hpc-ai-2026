"""Join exec capture, PMPI world-rank audit and independent C probe records."""
from pathlib import Path
import argparse,json

def records(path,marker):
 rows=[]
 for line in Path(path).read_text().splitlines():
  if marker in line:rows.append(json.loads(line.split(marker,1)[1]))
 return rows

def verify(stdout,stderr,entry):
 captures=records(stderr,'APAC_AFFINITY_EXEC_JSON ')
 shim=records(stderr,'APAC_AFFINITY_JSON ')
 maps=records(stdout,'MAP_JSON\t')
 assert len(captures)==len(shim)==len(maps)==512,('Missing trace records',len(captures),len(shim),len(maps))
 by_capture={int(x['pmi_rank']):x for x in captures}
 by_shim={x['rank']:x for x in shim};by_map={x['rank']:x for x in maps}
 assert set(by_capture)==set(by_shim)==set(by_map)==set(range(512))
 assert all(x['success'] and x['launch_cpus']==[x['launch_cpu']] for x in captures)
 for rank in range(512):
  s=by_shim[rank];m=by_map[rank]
  # PMI is used only to associate the saved pre-MPI record of this process.
  # The independent C MPI_Comm_rank record remains the world-rank authority.
  c=by_capture[int(m['pmi_rank'])]
  assert s['success'] and s['entry']==entry
  assert s['restore_set_status']==s['restored_read_status']==s['post_init_status']==0
  assert s['launch_cpu']==c['launch_cpu']==m['affinity_cpus'][0]
  assert m['affinity_cpus']==[c['launch_cpu']]
  assert s['restored_cpus']==str(c['launch_cpu']) and not s['restored_truncated']
  assert m['world_size']==512
  topology=c['topology']
  if topology['package'] is not None:assert topology['package']==m['physical_package_id']
  if topology['core'] is not None:assert topology['core']==m['physical_core_id']
  if topology['numa_nodes']:assert topology['numa_nodes']==[m['numa_node']]
 threads=records(stderr,'INIT_THREAD_JSON\t')
 if entry=='MPI_Init_thread':
  assert len(threads)==512 and {x['rank'] for x in threads}==set(range(512))
  assert all(x['provided']>=x['required'] for x in threads)
 else:assert not threads
 return {'passed':True,'world_ranks':512,'exec_capture_records':512,'PMPI_records':512,'independent_C_records':512,'MPI_entry':entry,'required_thread_levels':sorted({x['required'] for x in threads}),'source':'Actual pre-exec singleton CPU is associated through captured PMI diagnostic and independently checked against PMPI world rank and post-MPI C topology.','limits':'Main initializing thread only; no helper-thread affinity, page placement, solver behavior or performance claim.'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('stdout');ap.add_argument('stderr');ap.add_argument('--entry',choices=['MPI_Init','MPI_Init_thread'],required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 out=verify(a.stdout,a.stderr,a.entry);Path(a.output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
