#!/usr/bin/env python3
"""Render every allocation, chronologically, with only evidenced parent edges."""
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent
rows=json.loads((D/'runs.json').read_text());ids={}
def canonical(value):return str(value).split('.')[0]
for r in rows:ids[(r['platform'],canonical(r['job_id']))]=r
lines=['digraph allruns {','graph [rankdir=TB,bgcolor="white",nodesep=.35,ranksep=.25,label="All retained AI GPU allocations · chronological order\nH100 red / H200 green · arrows: recorded parent/control/dependency relation\nOrdering constraints are invisible and do not claim inheritance",labelloc=t,fontname="DejaVu Sans",fontsize=18];','node [shape=box,style="rounded,filled",fontname="DejaVu Sans",fontsize=9,width=5];','edge [color="#617486",arrowsize=.6];']
ordered={}
import textwrap
for i,r in enumerate(rows):
 key=(r['platform'],canonical(r['job_id']));nid='j'+str(i);ordered[key]=nid
 label='\n'.join([str(r.get('date') or 'Date not retained')+' · '+r['platform']+' · '+str(r['job_id']),str(r.get('title') or 'Purpose not recovered'),str(r.get('status') or 'Unknown'),str(r.get('result') or 'Outcome not recovered')]);label='\n'.join('\n'.join(textwrap.wrap(x,75)) for x in label.split('\n'))
 fill,color=('#fff0f1','#b83f49') if r['platform']=='H100' else ('#ebf8f1','#16865f')
 lines.append(f'{nid} [label={json.dumps(label,ensure_ascii=False)},fillcolor="{fill}",color="{color}"];')
 if i:lines.append(f'j{i-1} -> {nid} [style=invis,weight=10];')
for r in rows:
 for parent in r.get('parent_job_ids',[]):
  key=(r['platform'],canonical(parent))
  if key in ordered:lines.append(f'{ordered[key]} -> {ordered[(r["platform"],canonical(r["job_id"]))]} [constraint=false];')
lines.append('}');(D/'all-allocations.dot').write_text('\n'.join(lines)+'\n')
subprocess.run(['dot','-Tsvg',str(D/'all-allocations.dot'),'-o',str(D/'all-allocations.svg')],check=True)
print('All-allocation SVG written:',len(rows),'nodes')
