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
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=temp));Thread(target=server.serve_forever,daemon=True).start();errors=[]
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto('http://127.0.0.1:'+str(server.server_port)+'/#hpc');hpc=page.locator('#track-hpc');hpc.locator('[data-id="search"]').fill('2294803');hpc.locator('[data-id="nextMatch"]').click()
   cards=hpc.locator('.hpc-metric-card');assert cards.count()>=10
   assert '24.758557' in cards.nth(0).inner_text() and 's/step' in cards.nth(0).inner_text()
   assert 'N/A' in cards.nth(1).inner_text() and '41.846496' in cards.nth(2).inner_text()
   assert 'not a solver score' in cards.nth(2).inner_text()
   assert '40 steps' in cards.nth(0).inner_text() and '2294803' in cards.nth(0).inner_text()
   assert hpc.locator('.hpc-assessment').count()==1 and hpc.locator('.hpc-limitations').count()==1
   page.screenshot(path=str(D/'native-metrics.png'))
   node=hpc.locator('g.node[data-key="native"]');node.hover();tip=hpc.locator('[data-id="tooltip"]');assert tip.is_visible() and 's/step' in tip.inner_text()
   page.mouse.move(0,0);hpc.locator('[data-id="search"]').fill('25907772');hpc.locator('[data-id="nextMatch"]').click();assert 'N/A' in hpc.locator('.hpc-metric-list').inner_text() or 'count' in hpc.locator('.hpc-metric-list').inner_text().lower() or 'faces' in hpc.locator('.hpc-metric-list').inner_text().lower()
   page.locator('#choose-ai').click();assert page.locator('#track-ai').is_visible();assert page.evaluate('TEAM.ai.runs.length')==419
   page.locator('#choose-hpc').click();hpc.locator('[data-id="search"]').fill('2294803');hpc.locator('[data-id="nextMatch"]').click();page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth')==390
   page.screenshot(path=str(D/'mobile-metrics.png'));assert not errors,errors;browser.close()
 finally:server.shutdown();server.server_close()
(D/'browser-validation.json').write_text(json.dumps({'passed':True,'javascript_errors':errors,'numeric_metric_cards_and_units':True,'run_horizon_context':True,'assessment_and_limits_separate':True,'numeric_hover':True,'AI_switch_and419_inventory':True,'mobile_width':390},indent=2)+'\n')
