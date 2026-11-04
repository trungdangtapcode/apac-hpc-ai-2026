#!/usr/bin/env python3
"""Exercise both tracks through their real relative links in the staged Pages site."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import json
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parent
stage=Path('/tmp/apac-team-pages-preview')
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(stage)))
Thread(target=server.serve_forever,daemon=True).start()
report={'passed':False,'javascript_errors':[],'checks':{}}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1100})
  page.on('pageerror',lambda error:report['javascript_errors'].append(str(error)))
  page.goto('http://127.0.0.1:'+str(server.server_port)+'/')
  assert page.locator('#milestones g.node[data-key]').count()==31
  page.get_by_role('link',name='HPC · OpenFOAM').click()
  page.wait_for_url('**/hpc/')
  assert page.locator('#milestones g.node[data-key]').count()==15
  page.locator('g.node[data-key="access"]').hover()
  assert '21.9654' in page.locator('#tooltip').inner_text()
  assert 'Practice' in page.locator('#tooltip').inner_text()
  report['checks']['hpc_hover']='Result, platform, job references and evidence level visible'
  page.locator('#runsTab').click();page.locator('#search').fill('2294637')
  assert page.locator('#runRows tr').count()==1
  page.locator('#runRows button').click()
  detail=page.locator('#detailContent').inner_text()
  assert '24.7453 vs 27.8735' in detail and 'Qualified signal' in detail
  report['checks']['teammate_result']='Exact source result retained with qualified label'
  page.locator('#search').fill('');page.locator('#platform').select_option('NSCC')
  assert page.locator('#runRows tr').count()==5
  report['checks']['nscc_filter']=5
  page.locator('#reset').click();page.locator('#mapTab').click();page.locator('#nextMatch').click()
  assert page.locator('g.node.selected').count()==1
  page.screenshot(path=str(D/'hpc-desktop.png'))
  page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(250)
  assert page.evaluate('document.documentElement.scrollWidth')==390
  page.screenshot(path=str(D/'hpc-mobile.png'))
  page.get_by_role('link',name='AI · Qwen inference').click();page.wait_for_url('http://127.0.0.1:'+str(server.server_port)+'/')
  assert page.locator('#milestones g.node[data-key]').count()==31
  page.locator('#scope').select_option('all');assert page.locator('#allocations g.node[data-key]').count()==419
  page.locator('#runsTab').click();page.locator('#search').fill('28197');assert page.locator('#runRows tr').count()==1
  assert not report['javascript_errors'],report['javascript_errors']
  report['checks'].update({'ai_milestones':31,'ai_allocations':419,'hpc_milestones':15,'mobile_width':390,'both_track_links':'passed','existing_ai_search':'28197 passed'})
  report['passed']=True;browser.close()
finally:
 server.shutdown();server.server_close()
 (D/'browser-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
