#!/usr/bin/env python3
"""Resumable official checkpoint staging on NSCC; four downloads, no GPU allocation."""
import concurrent.futures
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import time

root=Path(__file__).resolve().parent
metadata=json.loads((root/'inspection/official-model-metadata.json').read_text())
revision='e156cb4efae43fbee1a1ab073f946a1377e6b969'
assert metadata['sha']==revision
dest=Path('/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8')
dest.mkdir(parents=True,exist_ok=True)
lock=(dest/'.stage.lock').open('w')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
status_path=root/'model-transfer-status.json'
mutex=threading.Lock()
files=[f for f in metadata['siblings'] if '/' not in f['rfilename'] and
       f['rfilename']!='.gitattributes']
state={'revision':revision,'pid':os.getpid(),'started':time.time(),
       'complete':False,'verified':{},'errors':{}}
def save():
    temporary=status_path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state,indent=2)+'\n')
    temporary.replace(status_path)
save()
def stage(entry):
    name=entry['rfilename'];path=dest/name;part=dest/(name+'.part')
    expected_size=entry['size'];sha=entry.get('lfs',{}).get('sha256')
    try:
        for attempt in range(3):
            if not path.is_file():
                # A unique stage query avoids reuse of an earlier diagnostic range response.
                url='https://huggingface.co/'+metadata['id']+'/resolve/'+revision+'/'+name+'?download=true&stage=ap42-pinned-v1'
                with (dest/(name+'.curl.log')).open('a') as err:
                    subprocess.run(['curl','--fail','--location','--silent','--show-error',
                        '--retry','3','--retry-delay','5','--connect-timeout','30',
                        '--max-time','21600','--continue-at','-',url,'--output',str(part)],
                        stderr=err,check=True)
                if part.stat().st_size!=expected_size:
                    raise ValueError('size mismatch: '+str(part.stat().st_size))
                part.replace(path)
            if path.stat().st_size!=expected_size:
                raise ValueError('existing file size mismatch')
            h=hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
            digest=h.hexdigest()
            if sha and digest!=sha:
                path.rename(dest/(name+'.bad-'+str(int(time.time()))))
                continue
            with mutex:
                state['verified'][name]={'bytes':expected_size,'sha256':digest,
                    'official_lfs_sha256':sha,'verified_at':time.time()}
                save()
            print('VERIFIED',name,expected_size,flush=True)
            return
        raise ValueError('checksum mismatch after three attempts')
    except Exception as exc:
        with mutex:state['errors'][name]=str(exc);save()
        print('FAILED',name,str(exc),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(stage,files))
state['complete']=len(state['verified'])==len(files) and not state['errors']
state['finished']=time.time();save()
raise SystemExit(0 if state['complete'] else 1)
