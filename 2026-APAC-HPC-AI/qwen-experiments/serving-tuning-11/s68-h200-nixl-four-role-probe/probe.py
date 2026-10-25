#!/usr/bin/env python3
"""No-model 16-agent 2-prefill/2-decode NIXL WRITE diagnostic, not inference."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,socket,subprocess,sys,time,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base',HERE/'base-peer.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
REGIONS=188;REGION_BYTES=4096;WRITE_BYTES=1024;PHASES=('p0_only','p1_only','both');RANKS=16

def peers(rank):
    local=rank%4
    return [8+local,12+local] if rank<8 else [local,4+local]

def senders(phase):
    return list(range(4)) if phase=='p0_only' else list(range(4,8)) if phase=='p1_only' else list(range(8))

def payload(rank,phase,region):
    seed=(rank*31+phase*53+region*7)&255
    return bytes((seed+i*11)&255 for i in range(WRITE_BYTES))

def expected_receive(rank,phase):
    expected=bytearray([0xA5])*(REGIONS*REGION_BYTES)
    for sender in peers(rank):
        if sender not in senders(PHASES[phase]):continue
        slot=(sender//4)*2048
        for region in range(REGIONS):
            offset=region*REGION_BYTES+slot
            expected[offset:offset+WRITE_BYTES]=payload(sender,phase,region)
    return bytes(expected)

def run_rank(rank,art,exchange,deadline):
    import numpy as np
    import torch
    from nixl._api import nixl_agent,nixl_agent_config,nixl_thread_sync_t
    assert 0<=rank<RANKS and torch.cuda.device_count()==4,'need four visible GPUs in each role container'
    torch.cuda.set_device(rank%4);device=rank%4
    properties=torch.cuda.get_device_properties(device);assert 'H200' in properties.name
    print(f'RANK_START rank={rank} host={socket.gethostname()} local_gpu={device} gpu_uuid={properties.uuid}',flush=True)
    identity=base._source_identity()
    ib=base.active_ib_devices();assert ib,'no active IB';assert os.environ['UCX_NET_DEVICES']==','.join(ib)
    threads=8 if rank<8 else 0
    agent=nixl_agent('ap42-fanout-'+str(rank)+'-'+str(uuid.uuid4()),nixl_agent_config(backends=[],num_threads=threads,sync_mode=nixl_thread_sync_t.NIXL_THREAD_SYNC_STRICT))
    agent.create_backend('UCX',{'num_threads':'8'} if threads else {})
    allocation=torch.empty(REGIONS*REGION_BYTES,dtype=torch.uint8,device=f'cuda:{device}')
    allocation.fill_(0xA5);torch.cuda.synchronize()
    regions=[(int(allocation.data_ptr())+i*REGION_BYTES,REGION_BYTES,device,'') for i in range(REGIONS)]
    registration=agent.register_memory(regions,'VRAM');assert registration is not None and registration is not False
    base.atomic_json(art/f'rank-{rank}-progress.json',{'rank':rank,'stage':'registered','gpu_uuid':str(properties.uuid),'regions':REGIONS})
    metadata=agent.get_agent_metadata();assert isinstance(metadata,bytes) and metadata
    meta_path=exchange/f'meta-{rank}.bin';meta_path.write_bytes(metadata);meta_path.chmod(0o600)
    info={'rank':rank,'agent':agent.name,'ptr':int(allocation.data_ptr()),'device':device,'metadata_sha256':hashlib.sha256(metadata).hexdigest()}
    base.atomic_json(exchange/f'info-{rank}.json',info)
    def wait(predicate,what):
        while not predicate():
            if time.time()>=deadline:raise TimeoutError(what)
            agent.get_new_notifs()
            time.sleep(.002)
    def barrier(name):
        base.atomic_json(exchange/f'{name}-{rank}.json',{'rank':rank})
        wait(lambda:all((exchange/f'{name}-{i}.json').exists() for i in range(RANKS)),name)
    wait(lambda:all((exchange/f'info-{i}.json').exists() for i in peers(rank)),'peer publications')
    remote={}
    for peer in peers(rank):
        record=json.loads((exchange/f'info-{peer}.json').read_text());data=(exchange/f'meta-{peer}.bin').read_bytes()
        assert hashlib.sha256(data).hexdigest()==record['metadata_sha256'];agent.add_remote_agent(data);remote[peer]=record
    row={'rank':rank,'role':('prefill-' if rank<8 else 'decode-')+str(rank//4 if rank<8 else rank//4-2),'tp_rank':rank%4,'host':socket.gethostname(),'gpu_uuid':str(properties.uuid),'gpu_name':properties.name,'regions':REGIONS,'bytes_per_region':REGION_BYTES,'agent_name':agent.name,'peer_ranks':peers(rank),'native_progress_threads':threads,'identity':identity,'phases':[],'scope':'No model, bootstrap HTTP, TP collective or production-sized KV; component evidence only.'}
    barrier('all_registered')
    for phase_i,phase in enumerate(PHASES):
        active=rank in senders(phase)
        if active:
            raw=bytearray([0xA5])*(REGIONS*REGION_BYTES)
            for i in range(REGIONS):raw[i*REGION_BYTES:i*REGION_BYTES+WRITE_BYTES]=payload(rank,phase_i,i)
            allocation.copy_(torch.from_numpy(np.frombuffer(raw,dtype=np.uint8).copy()).to(f'cuda:{device}'))
        else:allocation.fill_(0xA5)
        print(f'PHASE_READY rank={rank} phase={phase}',flush=True)
        base.atomic_json(art/f'rank-{rank}-progress.json',{'rank':rank,'stage':phase,'gpu_uuid':str(properties.uuid)})
        torch.cuda.synchronize();barrier(phase+'-ready')
        transfers=[]
        if active:
            handles=[];slot=(rank//4)*2048
            source=np.array([[int(allocation.data_ptr())+i*REGION_BYTES,WRITE_BYTES,device] for i in range(REGIONS)],dtype=np.uint64)
            for peer,record in remote.items():
                dest=np.array([[record['ptr']+i*REGION_BYTES+slot,WRITE_BYTES,record['device']] for i in range(REGIONS)],dtype=np.uint64)
                source_desc=agent.get_xfer_descs(source,'VRAM');dest_desc=agent.get_xfer_descs(dest,'VRAM')
                handle=agent.initialize_xfer('WRITE',source_desc,dest_desc,record['agent'],f'{phase}-{rank}-{peer}'.encode())
                assert handle is not None and handle is not False
                assert agent.transfer(handle)!='ERR';handles.append((peer,handle,source_desc,dest_desc))
            for peer,handle,source_desc,dest_desc in handles:
                def finished():
                    state=agent.check_xfer_state(handle)
                    if state=='ERR':raise RuntimeError(f'{phase}: transfer to {peer} ERR')
                    return state=='DONE'
                wait(finished,phase+'-transfer')
                transfers.append({'sender':rank,'receiver':peer,'bytes':REGIONS*WRITE_BYTES,'state':'DONE'})
            base.atomic_json(exchange/f'{phase}-sent-{rank}.json',{'rank':rank})
        if rank>=8:
            wait(lambda:all((exchange/f'{phase}-sent-{i}.json').exists() for i in peers(rank) if i in senders(phase)),phase+'-send-completion')
            torch.cuda.synchronize();raw=allocation.cpu().numpy().tobytes();expected=expected_receive(rank,phase_i)
            assert raw==expected,f'{phase}: destination bytes or untouched sentinels differ'
            digest=hashlib.sha256(raw).hexdigest()
        else:digest=None
        row['phases'].append({'phase':phase,'sent':transfers,'received_sha256':digest,'received_bytes_and_sentinels_verified':rank>=8})
        barrier(phase+'-verified')
    row.update(state='PASS_COMPONENT_ONLY',peak_allocated_vram_bytes=torch.cuda.max_memory_allocated(device),finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    base.atomic_json(art/f'rank-{rank}.json',row)
    barrier('results_written')
    return row

def launch(role,art,exchange,deadline):
    offset={'prefill-0':0,'prefill-1':4,'decode-0':8,'decode-1':12}[role]
    children=[];logs=[]
    try:
        for local in range(4):
            rank=offset+local;log=(art/f'rank-{rank}.log').open('x');logs.append(log)
            children.append(subprocess.Popen([sys.executable,'-B',str(__file__),'--rank',str(rank),'--art',str(art),'--exchange',str(exchange),'--deadline',str(deadline)],stdout=log,stderr=subprocess.STDOUT))
        while any(p.poll() is None for p in children):
            if time.time()>=deadline or any(p.poll() not in (None,0) for p in children):raise RuntimeError('role child failed or reached deadline; inspect per-rank logs')
            time.sleep(.1)
        assert all(p.returncode==0 for p in children)
    finally:
        for p in children:
            if p.poll() is None:p.terminate()
        for p in children:
            try:p.wait(timeout=2)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        for log in logs:log.close()

def check(art):
    rows=[json.loads((art/f'rank-{i}.json').read_text()) for i in range(RANKS)]
    assert {r['rank'] for r in rows}==set(range(RANKS)) and all(r['state']=='PASS_COMPONENT_ONLY' for r in rows)
    assert len({r['gpu_uuid'] for r in rows})==16 and all(r['gpu_uuid'] for r in rows)
    assert len({r['host'] for r in rows[:8]})==len({r['host'] for r in rows[8:]})==1 and rows[0]['host']!=rows[8]['host']
    assert len({r['agent_name'] for r in rows})==16
    count=0
    for r in rows:
        assert r['peer_ranks']==peers(r['rank']) and r['regions']==REGIONS
        assert [p['phase'] for p in r['phases']]==list(PHASES)
        for i,p in enumerate(r['phases']):
            targets=peers(r['rank']) if r['rank'] in senders(PHASES[i]) else []
            assert len(p['sent'])==len(targets) and {x['receiver'] for x in p['sent']}==set(targets)
            assert all(x['sender']==r['rank'] and x['state']=='DONE' and x['bytes']==REGIONS*WRITE_BYTES for x in p['sent']);count+=len(targets)
            if r['rank']>=8:
                assert p['received_bytes_and_sentinels_verified'] is True
                assert p['received_sha256']==hashlib.sha256(expected_receive(r['rank'],i)).hexdigest()
    assert count==32
    report={'state':'PASS_COMPONENT_ONLY','ranks':16,'write_handles':count,'verified_write_bytes':count*REGIONS*WRITE_BYTES,'quality':'NOT_EVALUATED','goodput':'NOT_MEASURED','limits':'Small direct NIXL VRAM registration/fanout. No SGLang bootstrap HTTP/rooms/TP collective/full-span KV/model or serving proof. CPU/GPU continuous sampling not collected.'}
    base.atomic_json(art/'head-check.json',report);return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rank',type=int);p.add_argument('--role');p.add_argument('--art',type=Path,required=True);p.add_argument('--exchange',type=Path);p.add_argument('--deadline',type=float);p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.check:print(json.dumps(check(a.art),indent=2))
    elif a.role:launch(a.role,a.art,a.exchange,a.deadline)
    else:run_rank(a.rank,a.art,a.exchange,a.deadline)
