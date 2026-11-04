#!/usr/bin/env python3
"""Render a curated, source-linked HPC research map without querying clusters."""
from pathlib import Path
import csv,html,json,hashlib,subprocess,textwrap,gzip
D=Path(__file__).resolve().parent
H=next(p for p in D.parents if (p/'2026-APAC-HPC-AI').is_dir() and (p/'workspace').is_dir())
data=json.loads((D/'milestones.json').read_text());nodes=data['nodes']
colors={'NSCC':('#ad6b17','#fff4df'),'Iris':('#2476a1','#eaf5fc')}
statuses={'closed':'CLOSED / no stable gain','qualified':'QUALIFIED SIGNAL / repeat needed','reference':'REFERENCE REPRODUCTION','practice':'PRACTICE / not official score','mechanism':'MECHANISM / not a speedup','observation':'OBSERVATION / separate allocations','invalid':'INCOMPLETE / invalid comparison','unreviewed':'ACCEPTED / result not reviewed'}
lines=['digraph hpc {','graph [rankdir=TB,bgcolor="#f7fafc",pad="0.4",nodesep="0.35",ranksep="0.65",splines=polyline,fontname="DejaVu Sans",fontsize=20,label="OpenFOAM CPU research: hypotheses, measurements and decisions\\nOrange = NSCC CPU · Blue = Iris CPU · lower seconds/step is better",labelloc=t];','node [shape=box,style="rounded,filled",fontname="DejaVu Sans",fontsize=11,margin="0.20,0.16"];','edge [color="#8595a4",fontname="DejaVu Sans",fontsize=9];']
sources={}
for n in nodes:
 p=H/n['evidence'];assert p.is_file(),p
 sources[n['evidence']]=hashlib.sha256(p.read_bytes()).hexdigest()
 color,fill=colors[n['platform']]
 parts=[n['date']+' · '+n['platform'],n['title'],n['change'],'Jobs '+n['jobs'],n['result'],statuses[n['status']]]
 label='\n'.join('\n'.join(textwrap.wrap(t,49)) for t in parts)
 url='../../../'+n['evidence']
 lines.append(json.dumps(n['id'])+' [label='+json.dumps(label,ensure_ascii=False)+',color="'+color+'",fillcolor="'+fill+'",penwidth=1.8,URL='+json.dumps(url)+',tooltip='+json.dumps(n['result']+' | '+statuses[n['status']],ensure_ascii=False) +'];')
for e in data['edges']:
 style='solid' if e['relation']=='repeat' else 'dotted'
 lines.append(f'{json.dumps(e["source"])} -> {json.dumps(e["target"])} [constraint=false,style={style},label={json.dumps(e["relation"],ensure_ascii=False)}];')
# Align milestones by date from top to bottom, matching the AI timeline.
for i,group in enumerate(data['timeline']):
 anchor='date'+str(i)
 lines.append(anchor+' [shape=plaintext,label='+json.dumps(group['date'],ensure_ascii=False)+',fontcolor="#607080"];')
 lines.append('{rank=same;'+anchor+';'+';'.join(json.dumps(x) for x in group['ids'])+';}')
 for a,b in zip(group['ids'],group['ids'][1:]):lines.append(json.dumps(a)+' -> '+json.dumps(b)+' [style=invis,weight=10];')
 if i:lines.append('date'+str(i-1)+' -> '+anchor+' [style=invis,weight=100];')
lines.append('}');(D/'journey.dot').write_text('\n'.join(lines)+'\n')
for ext in ['svg','png','pdf']:subprocess.run(['dot','-T'+ext,str(D/'journey.dot'),'-o',str(D/('journey.'+ext))],check=True)
with (D/'milestones.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=list(nodes[0]));writer.writeheader();writer.writerows(nodes)
# Self-contained offline viewer: native SVG titles provide hover, +/- zoom.
svg=(D/'journey.svg').read_text();svg=svg[svg.index('<svg'):]
page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>HPC research journey</title><style>body{font:16px system-ui;margin:0;background:#f7fafc;color:#23373b}header{padding:24px}button{padding:8px 18px;margin-right:10px}main{overflow:auto;height:80vh;padding:20px}svg{width:1500px;height:auto}a{color:#2476a1}</style><header><h1>OpenFOAM CPU research journey</h1><p>15 curated milestones · NSCC CPU in orange · Iris CPU in blue. Hover for result and decision; click a node for retained evidence in the source tree.</p><p>Historical observations, matched comparisons and mechanism tests have different evidential strength. Separate machines and allocations cannot be ranked by raw seconds.</p><button onclick="zoom(1.25)">Zoom +</button><button onclick="zoom(.8)">Zoom −</button><a href="README.md">Research guide</a></header><main>'''+svg+'''</main><script>let width=1500;function zoom(f){width*=f;document.querySelector('svg').style.width=width+'px'}</script></html>'''
(D/'index.html').write_text(page)
with gzip.open(D/'index.html.gz','wb') as f:f.write(page.encode())
report={'passed':True,'curated_milestones':len(nodes),'exhaustive_job_inventory':False,'source_hashes':sources,'scheduler_queried':False,'performance_claim':'No stable own matched win; teammate recipe has qualified short-run signal.','native_followup':'2294735 reviewed: −30.60% pooled time in one40-step BAAB allocation; repeated effect size unstable; no universal speedup claim.'}
(D/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Rendered',len(nodes),'milestones; sources verified:',len(sources))
