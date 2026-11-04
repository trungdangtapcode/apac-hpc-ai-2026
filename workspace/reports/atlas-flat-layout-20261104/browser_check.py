#!/usr/bin/env python3
"""Verify the flat display preserves full evidence behind compact readouts."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import gzip,json,re
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory='/tmp/apac-flat-layout-preview'))
Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)+'/'
report={'passed':False,'javascript_errors':[],'checks':{}}
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch();page=b.new_page(viewport={'width':1440,'height':1000});docs=[]
  page.on('pageerror',lambda e:report['javascript_errors'].append(str(e)));page.on('request',lambda r:docs.append(r.url) if r.resource_type=='document' else None)
  page.goto(url);ai=page.locator('#track-ai');hpc=page.locator('#track-hpc')
  assert ai.locator('[data-id="milestones"] g.node[data-key]').count()==31
  assert ai.locator('[data-id="allocations"] g.node[data-key]').count()==419
  assert ai.locator('g.node[data-key] rect').count()==450
  assert ai.locator('.metric-readout dd').count()==4
  assert ai.locator('[data-id="detailContent"] p:visible').count()==0
  assert page.locator('.explorer').first.evaluate('e=>getComputedStyle(e).borderRadius')=='0px'
  detail=ai.locator('[data-id="detailContent"]');detail.get_by_text('Analysis',exact=True).click();assert 'feasibility milestones' in detail.inner_text();detail.get_by_text('Analysis',exact=True).click()
  detail.get_by_text('13 measurements',exact=True).click();assert detail.locator('table tr').count()==14;detail.get_by_text('13 measurements',exact=True).click()
  page.screenshot(path=str(D/'desktop-ai.png'),full_page=True)
  ai.locator('[data-id="search"]').fill('28197');ai.locator('[data-id="nextMatch"]').click();assert '3,051.5' in detail.inner_text()
  ai.locator('g.node[data-key="m:packaged-acceptance"]').hover();assert 'Mean TTFT' in ai.locator('[data-id="tooltip"]').inner_text()
  before=len(docs);page.locator('#choose-hpc').click();assert hpc.locator('g.node[data-key] rect').count()==15
  hpc.locator('[data-id="runsTab"]').click();hpc.locator('[data-id="search"]').fill('2294637');assert hpc.locator('[data-id="runRows"] tr').count()==1
  hpc.locator('[data-id="runRows"] button').click();hd=hpc.locator('[data-id="detailContent"]');assert '24.7453 vs 27.8735' in hd.inner_text();hd.get_by_text('Context',exact=True).click();assert 'Qualified signal / repeat needed' in hd.inner_text();hd.get_by_text('Context',exact=True).click()
  page.locator('#choose-ai').click();assert ai.locator('[data-id="search"]').input_value()=='28197';assert len(docs)==before
  page.locator('#choose-hpc').click();hpc.locator('[data-id="reset"]').click();hpc.locator('[data-id="mapTab"]').click();hpc.locator('[data-id="nextMatch"]').click()
  page.screenshot(path=str(D/'desktop-hpc.png'),full_page=True)
  for width in [390,820,1440]:
   page.set_viewport_size({'width':width,'height':1000});page.wait_for_timeout(180);assert page.evaluate('document.documentElement.scrollWidth')==width
   if width==390:page.screenshot(path=str(D/'mobile.png'),full_page=True)
  assert not report['javascript_errors'],report['javascript_errors'];b.close()
 report['checks']={'ai_milestones':31,'ai_allocations':419,'hpc_milestones':15,'square_svg_nodes':465,'panel_radius':'0px','four_metric_readout':True,'visible_default_inspector_paragraphs':0,'full_analysis_preserved':True,'all_13_measurements_preserved':True,'hpc_qualification_context_preserved':True,'metrics_hover_and_job_lookup':True,'state_preserved_without_reload':True,'responsive_widths':[390,820,1440]}
 original=gzip.decompress(Path('/home/apacsc42/apac-hpc-ai-research/workspace/reports/team-research-atlas-20261104/index.html.gz').read_bytes()).decode();current=Path('/tmp/apac-flat-layout-preview/index.html').read_text()
 parse=lambda s:json.loads(re.search(r'<script id="teamData" type="application/json">(.*?)</script>',s,re.S)[1]);assert parse(original)==parse(current)
 report['checks']['embedded_data_unchanged']=True;report['passed']=True
finally:
 server.shutdown();server.server_close();(D/'browser-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
