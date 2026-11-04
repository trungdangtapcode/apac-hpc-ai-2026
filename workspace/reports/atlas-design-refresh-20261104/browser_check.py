#!/usr/bin/env python3
"""Verify one-document track switching, independent state, deep links and metrics."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import json
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory='/tmp/apac-design-release-preview'))
Thread(target=server.serve_forever,daemon=True).start()
url='http://127.0.0.1:'+str(server.server_port)+'/'
result={'passed':False,'javascript_errors':[],'checks':{}}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1100});docs=[]
  page.on('pageerror',lambda e:result['javascript_errors'].append(str(e)))
  page.on('request',lambda r:docs.append(r.url) if r.resource_type=='document' else None)
  page.goto(url);ai=page.locator('#track-ai');hpc=page.locator('#track-hpc')
  assert ai.locator('[data-id="milestones"] g.node[data-key]').count()==31
  assert ai.locator('[data-id="allocations"] g.node[data-key]').count()==419
  ids=page.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)');assert len(ids)==len(set(ids))
  page.screenshot(path=str(D/'desktop-ai.png'),full_page=True)
  ai.locator('[data-id="search"]').fill('28197');ai.locator('[data-id="nextMatch"]').click()
  ai.locator('g.node[data-key="m:packaged-acceptance"]').hover()
  tip=ai.locator('[data-id="tooltip"]').inner_text()
  for field in ['Good output','Mean TTFT','Mean ITL','Joint SLA']:assert field in tip
  ai.locator('[data-id="runsTab"]').click();assert ai.locator('[data-id="runRows"] tr').count()==1
  ai.locator('[data-id="runRows"] button').click();assert '3,051.5' in ai.locator('[data-id="detailContent"]').inner_text()
  n_docs=len(docs);page.locator('#choose-hpc').click();assert hpc.is_visible() and not ai.is_visible()
  assert hpc.locator('[data-id="milestones"] g.node[data-key]').count()==15
  hpc.locator('[data-id="runsTab"]').click();hpc.locator('[data-id="platform"]').select_option('NSCC');assert hpc.locator('[data-id="runRows"] tr').count()==5
  hpc.locator('[data-id="platform"]').select_option('');hpc.locator('[data-id="search"]').fill('2294637');assert hpc.locator('[data-id="runRows"] tr').count()==1
  hpc.locator('[data-id="runRows"] button').click();assert 'Qualified signal' in hpc.locator('[data-id="detailContent"]').inner_text()
  page.locator('#choose-ai').click();assert ai.locator('[data-id="search"]').input_value()=='28197';assert ai.locator('[data-id="runsPanel"]').is_visible()
  page.locator('#choose-hpc').click();assert hpc.locator('[data-id="search"]').input_value()=='2294637';assert 'Qualified signal' in hpc.locator('[data-id="detailContent"]').inner_text()
  assert len(docs)==n_docs,docs
  assert page.locator('iframe').count()==0
  result['checks'].update({'no_navigation_on_switch':True,'iframes':0,'separate_filters_and_selections_preserved':True,'ai_metrics':'all four fields','ai_allocation_nodes':419,'ai_milestones':31,'hpc_milestones':15,'hpc_nscc_filter':5})
  hpc.locator('[data-id="reset"]').click();hpc.locator('[data-id="mapTab"]').click();hpc.locator('[data-id="nextMatch"]').click();hpc.locator('g.node[data-key="access"]').hover();assert '21.9654' in hpc.locator('[data-id="tooltip"]').inner_text()
  page.screenshot(path=str(D/'desktop-hpc.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(250);assert page.evaluate('document.documentElement.scrollWidth')==390
  page.screenshot(path=str(D/'mobile.png'),full_page=True)
  page.locator('#choose-hpc').focus();page.keyboard.press('ArrowLeft');assert ai.is_visible()
  page.goto(url+'#hpc');assert hpc.is_visible();assert hpc.locator('[data-id="milestones"] g.node[data-key]').count()==15
  page.goto(url+'hpc/');page.wait_for_url(url+'#hpc');assert hpc.is_visible()
  assert not result['javascript_errors'],result['javascript_errors']
  result['checks'].update({'mobile_width':390,'keyboard_track_switch':True,'direct_hpc_hash':True,'legacy_hpc_redirect':True,'unique_ids':len(ids)})
  result['passed']=True;browser.close()
finally:
 server.shutdown();server.server_close();(D/'browser-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
