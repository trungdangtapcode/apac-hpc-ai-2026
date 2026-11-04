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
   body=page.locator('#researchNoteBody').inner_text();assert '30.601914818%' in body and '14.16819%' in body
   assert 'COMPLETED 0:0' in body
   ys=page.locator('#track-hpc svg g.node').evaluate_all('(nodes)=>Object.fromEntries(nodes.map(n=>[n.querySelector("title")?.textContent,n.getBBox().y]))')
   order=['access','graph','density','order','place','io','team','xyz','native']
   assert all(ys[a]<ys[b] for a,b in zip(order,order[1:])),ys
   page.screenshot(path=str(D/'completed-native-note.png'))
   page.keyboard.press('Escape');page.locator('#choose-ai').click();assert page.locator('#track-ai').is_visible();assert page.evaluate('TEAM.ai.runs.length')==419
   assert page.evaluate('TEAM.ai.curated.nodes.length')==31
   page.locator('#choose-hpc').click();page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth')==390
   assert not errors,errors;browser.close()
 finally:server.shutdown();server.server_close()
(D/'browser-validation.json').write_text(json.dumps({'passed':True,'javascript_errors':errors,'chronological_top_to_bottom_layout':True,'completed_native_result_visible':True,'ai_419_allocations_and_31_milestones_preserved':True,'mobile_width':390},indent=2)+'\n')
