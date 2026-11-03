#!/usr/bin/env python3
"""Build an offline, evidence-linked run timeline and research dependency map."""
from pathlib import Path
from html import escape
import csv,json,subprocess,sys
D=Path(__file__).resolve().parent

def records(path):
 v=json.loads(path.read_text())
 if isinstance(v,list):return v
 for key in ['runs','jobs','records','inventory']:
  if isinstance(v.get(key),list):return v[key]
 raise ValueError(str(path))
allruns=[]
for platform in ['H100','H200']:
 for row in records(D/platform.lower()/'inventory.json'):
  row['platform']=platform
  row['evidence']=[('/home/apacsc42/2026-APAC-HPC-AI/'+e if e.startswith('qwen-experiments/') else e) for e in row.get('evidence',[])]
  allruns.append(row)
allruns.sort(key=lambda r:(str(r.get('date') or '9999'),str(r['job_id'])))
curated=json.loads((D/'curated.json').read_text())
colors={'H100':('#b83f49','#fff0f1'),'H200':('#16865f','#ebf8f1')}
lines=['digraph journey {','graph [rankdir=TB,splines=polyline,bgcolor="#f6f8fb",pad="0.5",nodesep="0.35",ranksep="0.75",fontname="DejaVu Sans",label="Qwen research: questions, interventions and evidence\nH100 = red · H200 = green · arrows carry documented relations",labelloc=t,fontsize=22];','node [shape=box,style="rounded,filled",fontname="DejaVu Sans",fontsize=11,margin="0.20,0.13"];','edge [fontname="DejaVu Sans",fontsize=9,color="#607080"];']
for node in curated['nodes']:
 color,fill=colors[node['platform']]
 label='\n'.join([str(node.get('date') or 'Date not retained')+' · '+node['platform'],node['title'],'Jobs '+', '.join(map(str,node['job_ids'])),node['change'],node['outcome']])
 import textwrap
 label='\n'.join('\n'.join(textwrap.wrap(p,65)) for p in label.split('\n'))
 lines.append(f'{json.dumps(node["id"])} [label={json.dumps(label,ensure_ascii=False)},color="{color}",fillcolor="{fill}",penwidth=1.6];')
ids={x['id'] for x in curated['nodes']}
for edge in curated['edges']:
 assert edge['source'] in ids and edge['target'] in ids
 style='dashed' if edge['relation']=='control' else 'dotted' if edge['relation']=='motivated' else 'solid'
 lines.append(f'{json.dumps(edge["source"])} -> {json.dumps(edge["target"])} [label={json.dumps(edge["relation"])},style={style}];')
# Align milestones to recorded calendar dates, rather than DAG depth alone.
dates=sorted(set(n.get('date') or 'Date not retained' for n in curated['nodes']))
for i,date in enumerate(dates):
 anchor='date'+str(i)
 lines.append(f'{anchor} [label={json.dumps(date)},shape=plaintext,fillcolor="#f6f8fb",fontcolor="#607080"];')
 group=[json.dumps(n['id']) for n in curated['nodes'] if (n.get('date') or 'Date not retained')==date]
 lines.append('{rank=same;'+anchor+';'+';'.join(group)+';}')
 if i:lines.append(f'date{i-1} -> {anchor} [style=invis,weight=100];')
lines.append('}');(D/'journey.dot').write_text('\n'.join(lines)+'\n')
for ext in ['svg','pdf','png']:
 subprocess.run(['dot','-T'+ext,str(D/'journey.dot'),'-o',str(D/('journey.'+ext))],check=True)
with (D/'runs.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=['platform','job_id','date','title','status','started','result','parent_job_ids','evidence'],extrasaction='ignore');writer.writeheader()
 for r in allruns:writer.writerow({**r,'evidence':json.dumps(r.get('evidence',[])),'parent_job_ids':json.dumps(r.get('parent_job_ids',[]))})
(D/'runs.json').write_text(json.dumps(allruns,indent=2)+'\n')
subprocess.run([sys.executable,str(D/'build_allocation_map.py')],check=True)
all_svg=(D/'all-allocations.svg').read_text();all_svg=all_svg[all_svg.index('<svg'):]
hover=json.loads((D/'hover-metrics.json').read_text())
payload=json.dumps(dict(runs=allruns,curated=curated,hover=hover),ensure_ascii=False).replace('</','<\\/')
svg=(D/'journey.svg').read_text();svg=svg[svg.index('<svg'):]
html='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Qwen research · run lineage</title><style>
*{box-sizing:border-box}body{margin:0;background:#f6f8fb;color:#203042;font:15px system-ui,sans-serif}header{padding:28px 4vw;background:#142d3b;color:white}h1{margin:0 0 12px;font-size:30px}p{line-height:1.6;max-width:1100px}nav{position:sticky;top:0;background:white;padding:12px 4vw;display:flex;gap:12px;align-items:center;z-index:3;box-shadow:0 2px 12px #0001}button,input,select{font:inherit;padding:9px;border:1px solid #cdd6df;border-radius:7px}button{cursor:pointer;background:white}button.active{background:#203e50;color:white}.red{color:#d8616b}.green{color:#31bb87}main{padding:20px 4vw}.summary{display:flex;gap:16px;flex-wrap:wrap}.metric{background:white;padding:16px 22px;border-radius:10px;border-top:4px solid var(--color);min-width:230px}.metric strong{font-size:30px;display:block}.hint{font-size:13px;color:#607080}.graph{overflow:auto;background:white;border-radius:10px;padding:20px;max-height:78vh}.graph svg{max-width:none;width:1300px;height:auto}#timeline{display:none}.row{display:grid;grid-template-columns:135px 1fr 1fr;gap:12px;margin:9px 0}.date{font-size:12px;padding-top:12px;color:#607080}.card{background:white;border:1px solid #dae1e8;border-left:5px solid var(--color);border-radius:8px;padding:12px;cursor:pointer;grid-column:var(--column)}.card:hover{box-shadow:0 3px 12px #0002}.card b{display:block}.card small{display:block;color:#607080;margin-top:5px}.lane{display:grid;grid-template-columns:135px 1fr 1fr;padding:18px 0;font-weight:bold}dialog{width:min(850px,95vw);border:0;border-radius:12px;padding:28px;box-shadow:0 10px 60px #0005}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}a{color:#236a96}.edge{padding:8px;border-bottom:1px solid #eee}.toolbar{margin:14px 0;display:flex;gap:10px;align-items:center}@media(max-width:700px){.row{grid-template-columns:80px 1fr 1fr}.card{font-size:12px}.graph svg{width:1050px}nav{flex-wrap:wrap}}
.hover-metrics{position:fixed;z-index:10;pointer-events:none;background:#152c3b;color:white;border:1px solid #7691a2;border-radius:10px;padding:12px 14px;box-shadow:0 8px 30px #0004;width:min(520px,95vw);font-size:12px}.hover-metrics[hidden]{display:none}.hover-metrics table{border-collapse:collapse;width:100%;margin-top:8px}.hover-metrics td,.hover-metrics th{text-align:right;padding:5px 7px}.hover-metrics th{font-size:11px;color:#b8ceda}.hover-metrics td:first-child,.hover-metrics th:first-child{text-align:left}.hover-metrics small{display:block;color:#b8ceda;margin-top:6px}
</style><header><h1>How the Qwen service evolved</h1><p>From the earliest retained jobs to full accuracy verification. <b class="red">H100: red</b> · <b class="green">H200: green</b>. Failed and losing trials remain visible. A scheduler allocation can contain several benchmark points; it is counted once.</p><p class="hint" style="color:#b7cbd7">A solid B → A arrow means documented derivation. Dashed means a control comparison; dotted means an earlier finding motivated a question. Chronology alone is never treated as inheritance. This is a dated evidence reconstruction, not a live scheduler.</p></header><nav><button id="overviewButton" class="active">Research map</button><button id="timelineButton">Every recorded allocation</button><input id="search" placeholder="Find job, change, result…"><select id="platform"><option value="">Both GPU platforms</option><option>H100</option><option>H200</option></select><a href="runs.csv" download>CSV</a><a href="journey.pdf">PDF map</a><a href="all-allocations.svg">All-job SVG</a></nav><main><div class="summary" id="summary"></div><section id="overview"><p>Selected technical decisions explain the journey. The complete job inventory is in the second view. Pan with the scrollbars; use the zoom buttons for the overview. Sources and relationship explanations follow the map.</p><div class="toolbar"><select id="graphScope"><option value="milestones">31 research milestones</option><option value="all">All 419 allocations</option></select><button id="smaller">−</button><button id="larger">+</button><span class="hint">Zoom affects display only.</span></div><div class="graph" id="graph"><div id="milestoneGraph">__SVG__</div><div id="allocationGraph" hidden>__ALLSVG__</div></div><h2>Why the arrows exist</h2><div id="relations"></div></section><section id="timeline"><p id="count"></p><div class="lane"><span>Date</span><span class="red">H100 · NSCC / PBS</span><span class="green">H200 · Firmus / Slurm</span></div><div id="rows"></div></section><p class="hint">Dates and outcome labels retain source limits. Unavailable dates appear last. No performance conversion is inferred between H100 and H200. Missing parents mean no supported link was recovered, not proof that a job had no predecessor.</p></main><dialog id="detail"><button id="close">Close</button><h2 id="detailTitle"></h2><pre id="detailText"></pre></dialog><div id="hoverMetrics" class="hover-metrics" role="tooltip" hidden></div><script>const DATA=__DATA__;
const $=id=>document.getElementById(id);function txt(v){return typeof v==='string'?v:JSON.stringify(v)}
for(const p of ['H100','H200']){const r=DATA.runs.filter(x=>x.platform===p);let el=document.createElement('div');el.className='metric';el.style='--color:'+(p==='H100'?'#b83f49':'#16865f');el.innerHTML='<span>'+p+' · retained unique allocations</span><strong>'+r.length+'</strong><span>'+r.filter(x=>x.started===true).length+' confirmed started · '+r.filter(x=>x.started===false).length+' confirmed not started · '+r.filter(x=>x.started!==true&&x.started!==false).length+' start unknown</span>';$('summary').append(el)}
function bindMetrics(element,record,milestone=false){
 const keys=milestone?record.job_ids:[record.job_id];
 const samples=keys.flatMap(key=>(DATA.hover.jobs[String(key)]||[]).map(x=>({...x,job:key})));
 const box=$('hoverMetrics');
 function hide(){box.hidden=true;element.removeAttribute('aria-describedby')}
 function move(event){const rect=element.getBoundingClientRect();const x=event.clientX??rect.left,y=event.clientY??rect.top;box.style.left=Math.max(8,Math.min(x+16,innerWidth-box.offsetWidth-8))+'px';box.style.top=Math.max(8,Math.min(y+16,innerHeight-box.offsetHeight-8))+'px'}
 function showMetrics(event){box.replaceChildren();const title=document.createElement('b');title.textContent=record.platform+' · '+(milestone?record.title:'Job '+record.job_id);box.append(title);const table=document.createElement('table');const head=document.createElement('tr');for(const text of ['Job / load','Good tok/s','TTFT ms','ITL ms','SLA %']){const th=document.createElement('th');th.textContent=text;head.append(th)}table.append(head);
 const visible=samples.slice(-6);
 for(const x of (visible.length?visible:[{}])){const tr=document.createElement('tr');const fmt=(v,n=2)=>typeof v==='number'?v.toFixed(n):'N/A';for(const value of [x.job?x.job+' · N'+(x.concurrency??'?')+' '+(x.phase||''):'No performance export',fmt(x.good_output_tokens_s),fmt(x.ttft_avg_ms),fmt(x.itl_avg_ms),fmt(typeof x.good_request_fraction==='number'?100*x.good_request_fraction:null)]){const td=document.createElement('td');td.textContent=value;tr.append(td)}table.append(tr)}box.append(table);const note=document.createElement('small');note.textContent='TTFT / ITL: means. '+(samples.length>6?'Showing the last 6 of '+samples.length+' recorded points; click for all.':samples.length?'Each row is one recorded load/phase.':'No retained four-metric performance summary; quality/probes are separate.');box.append(note);box.hidden=false;element.setAttribute('aria-describedby','hoverMetrics');move(event)}
 element.setAttribute('tabindex','0');element.addEventListener('pointerenter',showMetrics);element.addEventListener('pointermove',move);element.addEventListener('pointerleave',hide);element.addEventListener('focus',showMetrics);element.addEventListener('blur',hide);element.addEventListener('click',hide);
}
addEventListener('scroll',()=>$('hoverMetrics').hidden=true,true);addEventListener('keydown',e=>{if(e.key==='Escape')$('hoverMetrics').hidden=true});
function show(row){$('detailTitle').textContent=row.platform+' · job '+row.job_id;$('detailText').textContent=JSON.stringify({...row,performance_points:DATA.hover.jobs[String(row.job_id)]||[]},null,2);$('detail').showModal()}$('close').onclick=()=>$('detail').close();
function draw(){const q=$('search').value.toLowerCase(),p=$('platform').value;const rs=DATA.runs.filter(r=>(!p||p===r.platform)&&JSON.stringify(r).toLowerCase().includes(q));$('count').textContent=rs.length+' of '+DATA.runs.length+' allocations · click a card for configuration, result, parents and evidence';$('rows').replaceChildren();for(const r of rs){const row=document.createElement('div');row.className='row';const date=document.createElement('div');date.className='date';date.textContent=r.date||'Date not retained';row.append(date);const c=document.createElement('div');c.className='card';c.style='--color:'+(r.platform==='H100'?'#b83f49':'#16865f')+';--column:'+(r.platform==='H100'?2:3);const b=document.createElement('b');b.textContent=r.job_id+' · '+(r.title||'Purpose not recovered');c.append(b);for(const t of [r.status||'State unknown',txt(r.result||'No reviewed outcome recovered'),(r.parent_job_ids||[]).length?'Documented parents: '+r.parent_job_ids.join(' → '):'No explicit parent recovered']){const s=document.createElement('small');s.textContent=t;c.append(s)}bindMetrics(c,r);c.onclick=()=>show(r);row.append(c);$('rows').append(row)}}
for(const g of $('graph').querySelectorAll('g.node')){const id=g.querySelector('title')?.textContent,n=DATA.curated.nodes.find(n=>n.id===id);if(n){g.style.cursor='pointer';bindMetrics(g,n,true);g.onclick=()=>{$('detailTitle').textContent=n.platform+' · '+n.title;$('detailText').textContent=JSON.stringify({...n,performance_points:n.job_ids.flatMap(id=>DATA.hover.jobs[String(id)]||[])},null,2);$('detail').showModal()}}}
for(const g of $('allocationGraph').querySelectorAll('g.node')){const id=g.querySelector('title')?.textContent;const match=/^j(\d+)$/.exec(id||'');if(match){const r=DATA.runs[Number(match[1])];g.style.cursor='pointer';bindMetrics(g,r);g.onclick=()=>show(r)}}
$('graphScope').onchange=()=>{const all=$('graphScope').value==='all';$('milestoneGraph').hidden=all;$('allocationGraph').hidden=!all;$('hoverMetrics').hidden=true;$('graph').scrollTop=0};
$('search').oninput=draw;$('platform').onchange=draw;function tab(t){$('overview').style.display=t?'none':'block';$('timeline').style.display=t?'block':'none';$('overviewButton').classList.toggle('active',!t);$('timelineButton').classList.toggle('active',t)}$('overviewButton').onclick=()=>tab(false);$('timelineButton').onclick=()=>tab(true);let width=1300;$('smaller').onclick=()=>{width=Math.max(500,width/1.25);$('graph').querySelectorAll('svg').forEach(svg=>svg.style.width=width+'px')};$('larger').onclick=()=>{width*=1.25;$('graph').querySelectorAll('svg').forEach(svg=>svg.style.width=width+'px')};for(const e of DATA.curated.edges){let d=document.createElement('div');d.className='edge';d.textContent=e.source+' → '+e.target+' ['+e.relation+'] '+e.reason+' · Source: '+e.evidence;$('relations').append(d)}draw();</script></html>'''
(D/'index.html').write_text(html.replace('__SVG__',svg).replace('__ALLSVG__',all_svg).replace('__DATA__',payload))
print(json.dumps(dict(total_unique_allocations=len(allruns),platforms={p:sum(r['platform']==p for r in allruns) for p in colors},overview_nodes=len(ids),supported_edges=len(curated['edges']))))
