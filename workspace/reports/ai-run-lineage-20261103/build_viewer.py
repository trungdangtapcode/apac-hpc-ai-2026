#!/usr/bin/env python3
"""Build a standalone viewer using retained data; never query or modify cluster runs."""
from pathlib import Path
import argparse,gzip,json,re,subprocess,textwrap
D=Path(__file__).resolve().parent

def public_paths(value):
    if isinstance(value,str):return value.replace('/home/apacsc42/','')
    if isinstance(value,list):return [public_paths(v) for v in value]
    if isinstance(value,dict):return {k:public_paths(v) for k,v in value.items()}
    return value

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=D/'index.html')
    args=parser.parse_args()
    data=public_paths({'runs':json.loads((D/'runs.json').read_text()),'curated':json.loads((D/'curated.json').read_text()),'hover':json.loads((D/'hover-metrics.json').read_text())})
    assert len(data['runs'])==419 and len(data['curated']['nodes'])==31
    # Keep the dense evidence map intact; render shorter labels for screen use.
    nodes=data['curated']['nodes']
    dot=['digraph viewer {','graph [rankdir=TB,splines=polyline,bgcolor="transparent",pad="0.3",nodesep="0.38",ranksep="0.65"];','node [shape=box,style="rounded,filled",fontname="DejaVu Sans",fontsize=13,margin="0.18,0.14"];','edge [fontname="DejaVu Sans",fontsize=10,color="#6b8275",arrowsize=0.7];']
    for node in nodes:
        colour,fill=('#b64653','#fff0f1') if node['platform']=='H100' else ('#197456','#edf8ef')
        label='\n'.join([node['platform']+' · '+str(node.get('date') or 'Date unknown'),*textwrap.wrap(node['title'],29), 'Jobs '+', '.join(map(str,node['job_ids'][:4]))+(' …' if len(node['job_ids'])>4 else '')])
        dot.append(json.dumps(node['id'])+' [label='+json.dumps(label,ensure_ascii=False)+',color="'+colour+'",fillcolor="'+fill+'",penwidth=1.4];')
    for edge in data['curated']['edges']:
        style={'control':'dashed','motivated':'dotted'}.get(edge['relation'],'solid')
        dot.append(json.dumps(edge['source'])+' -> '+json.dumps(edge['target'])+' [label='+json.dumps(edge['relation'])+',style='+style+'];')
    dates=sorted(set(n.get('date') or 'Unknown' for n in nodes))
    for i,date in enumerate(dates):
        dot.append('day'+str(i)+' [shape=plaintext,label='+json.dumps(date)+',fontsize=11,fontcolor="#6b8275"];')
        dot.append('{rank=same;day'+str(i)+';'+ ';'.join(json.dumps(n['id']) for n in nodes if (n.get('date') or 'Unknown')==date)+';}')
        if i:dot.append('day'+str(i-1)+' -> day'+str(i)+' [style=invis,weight=100];')
    dot.append('}')
    websvg=subprocess.check_output(['dot','-Tsvg'],input='\n'.join(dot).encode()).decode()
    template=(D/'viewer/page.html').read_text()
    for placeholder,file in [('__SVG__','journey.svg'),('__ALLSVG__','all-allocations.svg')]:
        svg=websvg if placeholder=='__SVG__' else (D/file).read_text();svg=svg[svg.index('<svg'):]
        # Graphviz's generated comments are not meaningful in the public viewer.
        svg=re.sub(r'<!--.*?-->','',svg,flags=re.S)
        template=template.replace(placeholder,svg)
    template=template.replace('__STYLE__',(D/'viewer/style.css').read_text()).replace('__SCRIPT__',(D/'viewer/app.js').read_text()).replace('__DATA__',json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
    assert '/home/apacsc42/' not in template
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(template)
    args.output.with_suffix(args.output.suffix+'.gz').write_bytes(gzip.compress(template.encode(),mtime=0))
    print(json.dumps({'output':str(args.output),'bytes':len(template.encode()),'allocations':419,'milestones':31,'offline':True}))
if __name__=='__main__':main()
