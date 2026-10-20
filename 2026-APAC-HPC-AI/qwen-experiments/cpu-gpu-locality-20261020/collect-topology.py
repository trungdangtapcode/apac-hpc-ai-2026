"""Read static topology in our allocation; no model, benchmark or GPU load."""
from pathlib import Path
import argparse,csv,datetime,json,os,socket,subprocess


def command(argv):
    try:
        p=subprocess.run(argv,capture_output=True,text=True,timeout=30)
        return dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,
                    state='COLLECTED' if p.returncode==0 else 'FAILED_NOT_COLLECTED')
    except (OSError,subprocess.TimeoutExpired) as e:
        return dict(argv=argv,state='FAILED_NOT_COLLECTED',reason=str(e))


def identity(result,allocated):
    assert result.get('returncode')==0, 'Allocated GPU identity unavailable'
    rows=list(csv.reader(result['stdout'].splitlines()))
    assert len(rows)==1 and len(rows[0])==4
    uuid,name,pci,index=[v.strip() for v in rows[0]]
    assert uuid==allocated and 'H100' in name
    domain,bus,device=pci.lower().split(':')
    return dict(uuid=uuid,name=name,pci=pci,nvml_index=int(index),
                sysfs_pci=f'{int(domain,16):04x}:{bus}:{device}')


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    allocated=os.environ.get('CUDA_VISIBLE_DEVICES','').strip()
    assert allocated.startswith('GPU-') and ',' not in allocated, 'Require one PBS-allocated UUID; never query dynamic state of arbitrary devices'
    result=command(['nvidia-smi','-i',allocated,'--query-gpu=uuid,name,pci.bus_id,index','--format=csv,noheader,nounits'])
    gpu=identity(result,allocated)
    topology=command(['nvidia-smi','topo','-m'])
    cpu=command(['lscpu','-p=CPU,CORE,SOCKET,NODE'])
    assert cpu.get('returncode')==0 and os.sched_getaffinity(0)
    nodes={p.parent.name:p.read_text().strip() for p in Path('/sys/devices/system/node').glob('node*/cpulist')}
    device=Path('/sys/bus/pci/devices')/gpu['sysfs_pci']
    local={n:((device/n).read_text().strip() if (device/n).exists() else 'NOT_COLLECTED') for n in ['numa_node','local_cpulist']}
    report=dict(job=os.environ.get('PBS_JOBID'),host=socket.gethostname(),collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                state='STATIC_TOPOLOGY_CAPTURE_PASS' if topology.get('returncode')==0 else 'STATIC_TOPOLOGY_CAPTURE_PARTIAL',
                allocated_gpu=gpu,allocated_identity_query=result,process_cpu_affinity=sorted(os.sched_getaffinity(0)),
                lscpu=cpu,numa_node_cpulists=nodes,allocated_gpu_sysfs_locality=local,topology_matrix=topology,
                model_loaded=False,performance_measured=False,
                limits='One allocated GPU and its process affinity do not reproduce a full two-node job cpuset or per-worker CPU demand. topo is static whole-system NVML hardware mapping, not other jobs usage. No process list, utilisation sampling, benchmark or memory-bandwidth test collected.')
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n');print(report['state'])


if __name__=='__main__':main()
