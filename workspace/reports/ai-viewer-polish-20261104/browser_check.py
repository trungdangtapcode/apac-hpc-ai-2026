from playwright.sync_api import sync_playwright
from pathlib import Path
import json,sys
url=Path('/home/apacsc42/workspace/reports/ai-run-lineage-20261103/index.html').as_uri()
report={'url':url,'errors':[],'external_requests':[],'checks':{}}
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True)
 page=b.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
 page.on('console',lambda m:report['errors'].append('console '+m.type+': '+m.text) if m.type=='error' else None)
 page.on('pageerror',lambda e:report['errors'].append('pageerror '+str(e)))
 page.on('request',lambda r:report['external_requests'].append(r.url) if not r.url.startswith('file://') else None)
 page.goto(url,wait_until='load',timeout=60000)
 # Timeline default contains 31 curated data nodes. Ignore graph date-anchor nodes.
 count=page.locator('#milestones g.node[data-key]').count();assert count==31,count
 report['checks']['milestone_nodes']=count
 # Required graph mode: all scheduler allocations.
 page.locator('#scope').select_option('all');page.wait_for_timeout(300)
 count=page.locator('#allocations g.node[data-key]').count();assert count==419,count
 report['checks']['allocation_nodes']=count
 # Return to summary, choose a measured milestone, hover and inspect all four fields.
 page.locator('#scope').select_option('milestones');page.wait_for_timeout(300)
 page.locator('#search').fill('28197');page.locator('#nextMatch').click();page.wait_for_timeout(100)
 node=page.locator('#milestones g.node[data-key="m:packaged-acceptance"]');node.hover(timeout=10000)
 page.wait_for_timeout(300)
 tip=page.locator('#tooltip');tip_text=tip.inner_text();report['checks']['hover_tooltip']=tip_text[:1200]
 if not tip.is_visible():
  report['checks']['hover_debug']=node.evaluate("e=>({box:e.getBoundingClientRect().toJSON(),cls:e.getAttribute('class'),key:e.dataset.key,tipStyle:getComputedStyle(document.querySelector('#tooltip')).cssText,hidden:document.querySelector('#tooltip').hidden})")
  raise AssertionError('hover tooltip did not appear: '+json.dumps(report['checks']['hover_debug']))
 assert 'Good output' in tip_text and 'Mean TTFT' in tip_text and 'Mean ITL' in tip_text and 'Joint SLA' in tip_text,tip_text
 # Switch to inventory and search the exact packaged acceptance run.
 page.locator('#runsTab').click();page.locator('#search').fill('28197');page.wait_for_timeout(200)
 report['checks']['inventory_search_count']=page.locator('#inventoryCount').inner_text()
 assert '1 of 419' in report['checks']['inventory_search_count'],report['checks']['inventory_search_count']
 card=page.locator('#runRows button').filter(has_text='28197').first;assert card.count()==1
 card.click();page.wait_for_timeout(100)
 detail=page.locator('#detailContent').inner_text();assert '3051.5' in detail or '3,051.5' in detail,detail[:1200]
 report['checks']['job_28197_detail']=detail[:1600]
 # Expand every recorded measurement and check 4 metric headers/row.
 summaries=page.locator('#detailContent details summary');assert summaries.count()>=1,'measurement table summary absent'
 summaries.first.click();detail=page.locator('#detailContent').inner_text()
 assert 'Good output' in detail and 'TTFT' in detail and 'ITL' in detail and 'SLA' in detail,detail[-1200:]
 report['checks']['measurement_table']=detail[-1600:]
 # Filter to H100 and verify allocation count in the UI.
 page.locator('#search').fill('');page.locator('#platform').select_option('H100');page.wait_for_timeout(200)
 counttext=page.locator('#inventoryCount').inner_text();assert '124' in counttext,counttext
 report['checks']['h100_filter']=counttext
 # Reset, search a distinctive term, go to next match and verify graph selection.
 page.locator('#reset').click();page.locator('#mapTab').click();page.locator('#search').fill('DeepGEMM');page.wait_for_timeout(200)
 matching=page.locator('#milestones g.node[data-key]:not(.dim)').count();assert matching>0
 report['checks']['deepgemm_graph_matches']=matching
 before=page.locator('#zoomLevel').inner_text();page.locator('#nextMatch').click();page.wait_for_timeout(100)
 selected=page.locator('#milestones g.node.selected').count();assert selected==1, f'next-match did not select node ({selected})'
 report['checks']['next_match_selected']=selected
 # Zoom controls and real pointer drag on the graph viewport.
 page.locator('#search').fill('');page.wait_for_timeout(100)
 before=page.locator('#zoomLevel').inner_text();page.locator('#zoomIn').click();after=page.locator('#zoomLevel').inner_text();assert before!=after,(before,after)
 report['checks']['zoom']={'before':before,'after':after}
 viewport=page.locator('#viewport');box=viewport.bounding_box();assert box
 page.mouse.move(box['x']+180,box['y']+180);page.mouse.down();page.mouse.move(box['x']+220,box['y']+220,steps=5);page.mouse.up()
 report['checks']['drag_pan']='pointer drag dispatched'
 # Readable width view for screenshot; responsive desktop capture.
 page.locator('#readWidth').click();page.wait_for_timeout(200);page.screenshot(path='/tmp/ai-viewer-desktop.png',full_page=False)
 report['checks']['desktop_screenshot']='/tmp/ai-viewer-desktop.png'
 page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(200);page.screenshot(path='/tmp/ai-viewer-mobile.png',full_page=False)
 dims=page.evaluate('({innerWidth,doc:document.documentElement.scrollWidth,body:document.body.scrollWidth})')
 report['checks']['mobile_screenshot']='/tmp/ai-viewer-mobile.png';report['checks']['mobile_dimensions']=dims
 # Horizontal overflow may be inside the intentionally pannable map viewport; document should fit mobile width.
 assert dims['doc']<=dims['innerWidth']+1,dims
 assert not report['errors'],report['errors']
 assert not report['external_requests'],report['external_requests']
 report['checks']['offline']='no non-file requests'
 b.close()
print(json.dumps(report,indent=2))
