from pathlib import Path
import json,hashlib,subprocess,tempfile
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parent;W=D.parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
with tempfile.TemporaryDirectory() as temp:
 subprocess.run(['python3',str(W/'reports/ai-run-lineage-20261103/viewer/prepare_pages.py'),'--output',temp],check=True)
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=temp));Thread(target=server.serve_forever,daemon=True).start()
 errors=[]
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto('http://127.0.0.1:'+str(server.server_port)+'/#hpc')
   assert page.locator('#track-hpc').is_visible()
   page.evaluate("openResearchNote('hpc','native')")
   body=page.locator('#researchNoteBody').inner_text();assert '1.768677456%' in body and '+0.73172%' in body and '-4.20539%' in body
   assert 'no confirmation job has been submitted' in body.lower()
   page.screenshot(path=str(D/'hpc-native-note.png'))
   page.keyboard.press('Escape');page.locator('#choose-ai').click();assert page.locator('#track-ai').is_visible();assert page.evaluate('TEAM.ai.runs.length')==419
   assert page.evaluate('TEAM.ai.curated.nodes.length')==31
   page.locator('#choose-hpc').click();page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth')==390
   assert not errors,errors;browser.close()
 finally:server.shutdown();server.server_close()
(D/'browser-validation.json').write_text(json.dumps({'passed':True,'javascript_errors':errors,'native_result_and_conflicting_pairs_visible':True,'ai_419_allocations_and_31_milestones_preserved':True,'mobile_width':390},indent=2)+'\n')
