"""Executed admission wrapper: two structured queue reads under the normal budget lock.

Used after three short preflight replies timed out without creating an intent or
reservation. The cause of those framed-reply failures remains undetermined.
Existing durable intents prevent this entry point from admitting a second job.
"""
import json
import deploy_submit as admission

original = admission.run_json
calls = 0


def structured_preflight(body, timeout):
    global calls
    calls += 1
    if calls != 1:
        return original(body, timeout=timeout)
    code = '''import socket,subprocess,os,datetime
result={'host':socket.gethostname(),'utc':datetime.datetime.utcnow().isoformat()+'Z','uid':os.getuid()}
for key,cmd in [('named',['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T']),('numeric',['squeue','-u',str(os.getuid()),'-h','-o','%i|%j|%T'])]:
 try:
  p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=10)
  result[key]={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 except Exception as error:result[key]={'error_type':type(error).__name__}
'''
    result = original(code, timeout=timeout)
    (admission.E / 'locked-preflight-structured.json').write_text(json.dumps(result, indent=2) + '\n')
    named, numeric = result['named'], result['numeric']
    assert named.get('returncode') == numeric.get('returncode') == 0
    assert named['stdout'] == numeric['stdout']
    return {'host': result['host'], 'utc': result['utc'], 'queue': named['stdout'],
            'returncode': 0, 'stderr': named['stderr']}


if __name__ == '__main__':
    admission.run_json = structured_preflight
    admission.submit(admission.seal())
