"""Exercise the actual post function against a bounded local HTTP fixture, without a GPU."""
import ast
import http.server
import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

O = Path(__file__).resolve().parent
source = ast.parse((O / 'profile-serving.py').read_text())
function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == 'post')
namespace = {'json': json, 'urllib': __import__('urllib.request')}
exec(compile(ast.Module(body=[function], type_ignores=[]), 'tested-post-function', 'exec'), namespace)
post = namespace['post']


class Fixture(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length', 0)))
        responses = {'/empty': (200, b''), '/text': (200, b'profiling started'),
                     '/json': (200, b'{"ok":true}'), '/invalid': (200, b'not-json'),
                     '/error': (500, b'Internal Server Error')}
        code, body = responses[self.path]
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


server = http.server.HTTPServer(('127.0.0.1', 0), Fixture)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
base = 'http://127.0.0.1:' + str(server.server_port)
checks = []
try:
    for path, kind in [('/empty', 'empty'), ('/text', 'text'), ('/json', 'json')]:
        value = post(base + path, {}, timeout=3, expect_json=False)
        assert value['http_status'] == 200 and value['body_kind'] == kind
        checks.append('control_' + kind + '_200_preserved')
    assert post(base + '/json', {}, timeout=3) == {'ok': True}
    checks.append('generation_json_still_required')
    try:
        post(base + '/invalid', {}, timeout=3)
        raise AssertionError('Malformed generation JSON was swallowed')
    except json.JSONDecodeError:
        checks.append('malformed_generation_json_rejected')
    try:
        post(base + '/error', {}, timeout=3, expect_json=False)
        raise AssertionError('HTTP 500 was swallowed')
    except urllib.error.HTTPError as error:
        assert error.code == 500
        checks.append('control_http_500_rejected')
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)
(O / 'validation.json').write_text(json.dumps({'passed': True, 'checks': checks,
    'scope': 'Actual derived post function; local HTTP fixture, no model import, GPU work, traffic change or external connection.'}, indent=2) + '\n')
print(json.dumps({'passed': True, 'checks': checks}))
