"""Local HTTP and partial-artifact checks; no Slurm submission or GPU use."""
import importlib.util
import json
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

client=module('output_diagnostic',ROOT/'serving-tuning-02/output-diagnostic.py')
watch=module('diagnostic_watcher',ROOT/'watch-serving-tuning.py')
cases=client.suite(ROOT/'runs/23128/submitted/output-smoke.py')
assert len(cases)==8
long=client.long_cases();assert len(long)==12 and len({r[2] for r in long})==12
responses=[{'choices':[{'message':{'content':'Tokyo'}}]},
           {'choices':[{'message':{'content':'.retsulc GNITSOER'}}]}, {'choices':[]}]
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        assert body['temperature']==0 and body['max_tokens']==64 and body['stream'] is False
        self.send_response(200);self.end_headers();self.wfile.write(json.dumps(responses.pop(0)).encode())
    def log_message(self,*args):pass

server=HTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
    host='127.0.0.1:'+str(server.server_port)
    good=client.request(host,cases[2]);bad=client.request(host,cases[3]);malformed=client.request(host,cases[0])
    assert good['passed'] and not bad['passed'] and bad['text']=='.retsulc GNITSOER'
    assert not malformed['passed'] and 'error' in malformed
finally:
    server.shutdown();server.server_close()

with tempfile.TemporaryDirectory(prefix='apac42-output-artifacts-') as temp:
    directory=Path(temp);(directory/'serving-tuning-02').mkdir();run=directory/'runs/90001';run.mkdir(parents=True)
    record=dict(job='90001',bundle='fixture',scope='Diagnostic only',planned_requests=132)
    path=directory/'serving-tuning-02/output-diagnostic-job.json';path.write_text(json.dumps(record))
    journal=run/'output-diagnostic.jsonl'
    journal.write_text(json.dumps(good)+'\n'+json.dumps(bad)+'\n'+ '{"incomplete":')
    watch.ROOT=directory;notes={}
    assert watch.refresh_output_diagnostic({'90001':{'State':'RUNNING'}},notes)
    saved=json.loads(path.read_text());assert saved['responses_recorded']==2 and saved['correct_responses']==1
    assert saved['responses_complete'] is False and notes['90001']['performance_evidence'] is False
    assert {'topology','purpose','finding','lesson'} <= notes['90001'].keys(), 'Run ledger requires these fields'
    assert not watch.refresh_output_diagnostic({'90001':{'State':'TIMEOUT'}},notes)
    assert json.loads(path.read_text())['responses_complete'] is False

bundle=ROOT/'serving-tuning-02/s2-output-monolithic'
worker=(bundle/'worker.sh').read_text();job=(bundle/'topology-job.sh').read_text()
assert '--disaggregation-mode' not in worker and '--disaggregation-transfer-backend' not in worker
assert 'launch_router' not in job and 'benchmark.sh' not in job
assert '--ep-size 1' in job and '--ep-size 8' in job
report=dict(passed=True,original_smoke_cases_preserved=True,observed_wrong_output_still_fails=True,
            malformed_http_response_fails=True,full_raw_response_preserved=True,
            long_retrieval_unique_targets=12,planned_requests=132,
            monolithic_no_pd_or_router_or_official_benchmark=True,
            partial_journal_safe=True,timeout_never_counts_as_complete=True,
            scope='CPU/source and local HTTP validation; no GPU correctness claim')
(ROOT/'serving-tuning-02/output-diagnostic-cpu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
