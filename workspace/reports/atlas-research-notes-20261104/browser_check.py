#!/usr/bin/env python3
"""Verify sourced Markdown explanations render as documents, not raw text blobs."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import json,gzip,re
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory='/tmp/apac-research-notes-preview'))
Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)+'/'
result={'passed':False,'javascript_errors':[],'checks':{}}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1050});docs=[]
  page.on('pageerror',lambda e:result['javascript_errors'].append(str(e)));page.on('request',lambda r:docs.append(r.url) if r.resource_type=='document' else None)
  page.goto(url);ai=page.locator('#track-ai');ai.locator('[data-id="search"]').fill('nixl-request-scope');ai.locator('[data-id="nextMatch"]').click();ai.locator('[data-id="detailContent"] .open-research-note').first.click()
  dialog=page.locator('#researchNote');assert dialog.is_visible()
  assert dialog.locator('table').count()==3 and dialog.locator('pre').count()==2
  assert dialog.locator('#researchNoteOutline button').count()==8
  body=dialog.locator('#researchNoteBody').inner_text()
  for fragment in ['_init_hetero_tp_prep_handle','send_kvcache_slice','720','188','403,846,372','22271','22294']:assert fragment in body,fragment
  assert dialog.locator('a[href$="nixl-ondemand.patch"]').count()==1
  assert dialog.locator('a[href$="test-nixl-ondemand.py"]').count()==1
  assert page.locator('#researchNoteMarkdown').get_attribute('href').endswith('/research-notes/ai/nixl-request-scope.md')
  with page.expect_download() as download:page.locator('#researchNoteDownload').click()
  saved=Path(download.value.path()).read_text();assert '720' in saved and 'src_stride' in saved
  page.screenshot(path=str(D/'nixl-reader.png'))
  dialog.locator('#researchNoteOutline button').filter(has_text='4. What exactly changed?').click();page.wait_for_timeout(350);page.screenshot(path=str(D/'nixl-change-table.png'))
  page.keyboard.press('Escape');assert not dialog.is_visible()
  page.locator('#choose-hpc').click();hpc=page.locator('#track-hpc');hpc.locator('[data-id="search"]').fill('2294637');hpc.locator('[data-id="nextMatch"]').click();hpc.locator('[data-id="detailContent"] .open-research-note').first.click();assert 'Port teammate settings fairly' in dialog.inner_text();assert 'qualified' in dialog.inner_text().lower()
  page.keyboard.press('Escape')
  # Render every curated note through the same public UI reader.
  for track in ['ai','hpc']:
   ids=page.evaluate('(track)=>Object.keys(TEAM.notes[track])',track)
   assert len(ids)==(31 if track=='ai' else 15)
   for key in ids:
    page.evaluate('([track,id])=>openResearchNote(track,id)',[track,key]);assert dialog.locator('table').count()>=2,key;assert dialog.locator('h3').count()>=6,key;assert dialog.locator('a[href^="https://"]').count()>=1,key
  page.evaluate("openResearchNote('ai','nixl-request-scope')");page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(200);assert page.evaluate('document.documentElement.scrollWidth')==390
  assert dialog.bounding_box()['width']<=390;page.screenshot(path=str(D/'mobile-reader.png'))
  assert len(docs)==1,docs
  # Markdown content cannot introduce executable HTML or javascript links.
  safe=page.evaluate('''()=>{const a=renderResearchMarkdown('<img src=x onerror=alert(1)>\\n\\n[bad](javascript:alert)');return {images:a.querySelectorAll('img').length,badLinks:a.querySelectorAll('a[href^="javascript:"]').length}}''');assert safe=={'images':0,'badLinks':0}
  assert not result['javascript_errors'],result['javascript_errors'];browser.close()
 current=Path('/tmp/apac-research-notes-preview/index.html').read_text();old=gzip.decompress(Path('/home/apacsc42/apac-hpc-ai-research/workspace/reports/team-research-atlas-20261104/index.html.gz').read_bytes()).decode();parse=lambda s:json.loads(re.search(r'<script id="teamData" type="application/json">(.*?)</script>',s,re.S)[1]);now,prior=parse(current),parse(old);assert now['ai']==prior['ai'] and now['hpc']==prior['hpc']
 result['checks']={'ai_notes':31,'hpc_notes':15,'all_notes_rendered':True,'nixl_tables':3,'nixl_code_blocks':2,'nixl_toc_sections':8,'patch_and_test_sources':True,'markdown_download':True,'escape_close':True,'hpc_reader':True,'mobile_width':390,'document_requests':len(docs),'safe_markdown':'no HTML execution or javascript links','original_research_payload_unchanged':True};result['passed']=True
finally:
 server.shutdown();server.server_close();(D/'browser-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
