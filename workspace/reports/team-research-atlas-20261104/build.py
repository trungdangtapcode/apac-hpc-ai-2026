#!/usr/bin/env python3
"""Combine the reviewed AI viewer and HPC milestone map without changing their evidence."""
from pathlib import Path
import gzip,hashlib,json,re,subprocess,sys,textwrap,argparse
D=Path(__file__).resolve().parent
REPORTS=D.parent
AI=REPORTS/'ai-run-lineage-20261103'
HPC=REPORTS/'hpc-run-lineage-20261104'

def main():
    args=argparse.ArgumentParser(description=__doc__);args.add_argument('--hpc-only',action='store_true',help='Reuse the existing AI component without rebuilding its files');options=args.parse_args()
    if not options.hpc_only:
        subprocess.run([sys.executable,str(AI/'build_viewer.py')],check=True)
    data=json.loads((HPC/'milestones.json').read_text());assert len(data['nodes'])==15
    lines=['digraph hpc {','graph [rankdir=TB,splines=polyline,bgcolor="transparent",pad="0.3",nodesep="0.4",ranksep="0.8"];','node [shape=box,style="rounded,filled",fontname="DejaVu Sans",fontsize=13,margin="0.18,0.14"];','edge [color="#6b8275",fontname="DejaVu Sans",fontsize=9,arrowsize=0.7];']
    for node in data['nodes']:
        color,fill=('#ad6b17','#fff4df') if node['platform']=='NSCC' else ('#2476a1','#eaf5fc')
        label='\n'.join([node['platform']+' · '+node['date'],*textwrap.wrap(node['title'],28)])
        lines.append(json.dumps(node['id'])+' [label='+json.dumps(label,ensure_ascii=False)+',color="'+color+'",fillcolor="'+fill+'",penwidth=1.4];')
    for edge in data['edges']:
        style='solid' if edge['relation']=='repeat' else 'dashed' if edge['relation']=='control question' else 'dotted'
        lines.append(json.dumps(edge['source'])+' -> '+json.dumps(edge['target'])+' [constraint=false,style='+style+',label='+json.dumps(edge['relation'],ensure_ascii=False)+'];')
    # Dated ranks flow vertically; use the same chronology as the standalone map.
    for i,group in enumerate(data['timeline']):
        anchor='date'+str(i)
        lines.append(anchor+' [shape=plaintext,label='+json.dumps(group['date'],ensure_ascii=False)+',fontcolor="#607080"];')
        lines.append('{rank=same;'+anchor+';'+';'.join(map(json.dumps,group['ids']))+';}')
        for a,b in zip(group['ids'],group['ids'][1:]):lines.append(json.dumps(a)+' -> '+json.dumps(b)+' [style=invis,weight=10];')
        if i:lines.append('date'+str(i-1)+' -> '+anchor+' [style=invis,weight=100];')
    lines.append('}')
    svg=subprocess.check_output(['dot','-Tsvg'],input='\n'.join(lines).encode()).decode();svg=svg[svg.index('<svg'):];svg=re.sub(r'<!--.*?-->','',svg,flags=re.S)
    page=(AI/'viewer/page.html').read_text()
    page=page.replace('<title>TripleU · The research behind the result</title>','<title>TripleU · OpenFOAM research investigation</title>')
    page=page.replace('Explore TripleU\'s Qwen serving investigation: 419 GPU allocations, 31 research milestones, measured outcomes and documented relationships.','Explore 15 reviewed OpenFOAM CPU research milestones, measured outcomes and platform-specific evidence from NSCC and Iris.')
    page=page.replace('Snapshot · 03 Nov 2026','Snapshot · 04 Nov 2026')
    page=page.replace('<a class="current" aria-current="page" href="./">AI · Qwen inference <span>419 allocations</span></a><a href="./hpc/">HPC · OpenFOAM <span>15 milestones</span></a>','<a href="../">AI · Qwen inference <span>419 allocations</span></a><a class="current" aria-current="page" href="./">HPC · OpenFOAM <span>15 milestones</span></a>')
    page=page.replace('QWEN3–235B · GPU SERVING INVESTIGATION','OPENFOAM · CPU SOLVER INVESTIGATION')
    page=page.replace('The research<br>behind the result<span>.</span>','The reasoning<br>behind each run<span>.</span>')
    page=page.replace('A map of the questions, changes and measurements that shaped our serving configuration. Explore the decisions—or inspect every retained allocation.','Follow how the team investigated decomposition, rank placement and runtime variability. Explore what the measurements supported—and which promising ideas did not survive a fair comparison.')
    page=page.replace('<strong>419</strong><span>recorded allocations</span>','<strong>15</strong><span>curated milestones</span>').replace('<strong>406</strong><span>confirmed starts</span>','<strong>2</strong><span>CPU platforms</span>').replace('<strong>31</strong><span>research milestones</span>','<strong>65M</strong><span>cell airflow case</span>')
    page=page.replace('Attempts include failed runs, probes and quality tests.<br>These are not 419 completed benchmarks.','Includes the completed native review on 04 November 2026.<br>A curated journey, not a complete allocation census.')
    page=page.replace('Run inventory <span>419</span>','Milestone index <span>15</span>')
    page=page.replace('<span class="dot h200"></span>H200<span class="dot h100"></span>H100','<span class="dot nscc"></span>NSCC<span class="dot iris"></span>Iris')
    page=page.replace('Search job, configuration, finding…','Search job, method, finding…')
    page=page.replace('<option value="">Both platforms</option><option value="H200">H200 · Firmus</option><option value="H100">H100 · NSCC</option>','<option value="">Both platforms</option><option value="NSCC">NSCC · CPU</option><option value="Iris">Iris · CPU</option>')
    page=page.replace('GPU platform','CPU platform')
    page=re.sub(r'<label id="scopeLabel">.*?</label>','',page,flags=re.S)
    page=page.replace('The questions and experiments, connected.','15 milestones · lower solver seconds/step is better.')
    page=page.replace('<i class="solid"></i>Derived from','<i class="solid"></i>Repeat').replace('<i class="dashed"></i>Control comparison','<i class="dashed"></i>Control question').replace('<i class="dotted"></i>Motivated next question','<i class="dotted"></i>Next question / mechanism')
    page=page.replace('Job / platform','Platform / jobs').replace('Recorded state','Evidence level')
    page=page.replace('No matching allocations. Try another search.','No matching milestones. Try another search.')
    notes='''<section class="reading-notes"><div><div class="eyebrow">READ THE EVIDENCE</div><h2>A faster arm is not<br>a matched improvement.</h2></div><div><p><strong>Keep the CPU platforms separate.</strong> NSCC and Iris have different hardware, rank counts and experimental conditions. Do not rank them by raw seconds per step.</p><p><strong>Distinguish a screen from a full run.</strong> The 14-step Iris minimum is an isolated observation. It is not a matched win against separate 40-step arms. The NSCC organizer-recipe reproduction ran the full 150 steps.</p><p><strong>Read the decision, including losing branches.</strong> Our graph-placement and axis-order trials did not establish a stable matched win. The teammate recipe has a qualified short-run signal; the independent same-horizon ABBA repeat is 6.10% slower and rejects a stable preparation-only gain. Favorable historical observations remain separate.</p></div></section>'''
    page=re.sub(r'<section class="reading-notes">.*?</section>',lambda m:notes,page,flags=re.S)
    page=page.replace('Download inventory CSV ↓','Download milestone CSV ↓').replace('ai-run-lineage-20261103/README.md','hpc-run-lineage-20261104/README.md').replace('Methods & count definitions ↗','HPC methods & evidence ↗')
    page=page.replace('__SVG__',svg).replace('__ALLSVG__','').replace('__STYLE__',(AI/'viewer/style.css').read_text()).replace('__SCRIPT__',(D/'viewer/hpc.js').read_text()).replace('__DATA__',json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
    assert '__SVG__' not in page and '/home/apacsc42/' not in page
    out=D/'hpc/index.html';out.parent.mkdir(exist_ok=True);out.write_text(page);out.with_suffix('.html.gz').write_bytes(gzip.compress(page.encode(),mtime=0))
    report={'hpc_milestones':len(data['nodes']),'hpc_relationships':len(data['edges']),'source_data_sha256':hashlib.sha256((HPC/'milestones.json').read_bytes()).hexdigest(),'hpc_source_modified':False,'scientific_measurements_added':False,'scope':'Publication of retained HPC material only; no scheduler or source-report changes.'}
    (D/'build-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
    subprocess.run([sys.executable,str(D/'build_unified.py')],check=True)
if __name__=='__main__':main()
