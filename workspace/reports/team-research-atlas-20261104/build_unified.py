#!/usr/bin/env python3
"""Compose both tested research explorers into one offline-capable page."""
from pathlib import Path
import gzip,json,re,hashlib,base64
import build_notes
D=Path(__file__).resolve().parent
AI=D.parent/'ai-run-lineage-20261103'

def extract(path,prefix):
    page=path.read_text()
    panel=re.search(r'(<section class="explorer".*?</main>)',page,re.S).group(1).removesuffix('</main>')
    tooltip=re.search(r'(<div id="tooltip".*?</div>)',page,re.S).group(1)
    panel+=tooltip
    panel=re.sub(r'(<section class="reading-notes">.*?</section>)',lambda m:'<details class="evidence-notes"><summary>How to read this evidence</summary>'+m[1]+'</details>',panel,flags=re.S)
    ids={}
    def identifier(m):
        name=m[1];ids[name]=ids.get(name,0)+1
        unique=prefix+'-'+name+('-'+str(ids[name]) if ids[name]>1 else '')
        return 'id="'+unique+'" data-id="'+name+'"'
    panel=re.sub(r'\bid="([^"]+)"',identifier,panel)
    panel=re.sub(r'(aria-controls|aria-labelledby)="([^"]+)"',lambda m:m[1]+'="'+prefix+'-'+m[2]+'"',panel)
    data=json.loads(re.search(r'<script id="researchData" type="application/json">(.*?)</script>',page,re.S).group(1))
    return panel,data

def component(source,hpc=False):
    code=source.read_text()
    code=code.replace("const DATA=JSON.parse(document.getElementById('researchData').textContent);",'')
    if hpc:
        code=code.replace("const DATA=JSON.parse(document.getElementById('researchData').textContent),$=id=>document.getElementById(id);",'const $=id=>root.querySelector(\'[data-id="\'+id+\'"]\');')
    code=code.replace('const $=id=>document.getElementById(id);','const $=id=>root.querySelector(\'[data-id="\'+id+\'"]\');')
    code=code.replace('document.querySelectorAll(', 'root.querySelectorAll(')
    code=code.replace("root.querySelectorAll('#runRows tr')","$('runRows').querySelectorAll('tr')")
    code=code.replace("if(state.tab==='map')fit(true);","if(!root.hidden&&state.tab==='map')fit(true);")
    code=code.replace('timer=setTimeout(()=>fit(true),150)','timer=setTimeout(()=>{if(!root.hidden)fit(true);},150)')
    # Replace the paragraph-heavy inspector while preserving the component selection logic.
    if hpc:
        code+="\nconst selectBeforeCompact=select;select=function(row,scroll=false){selectBeforeCompact(row,scroll);compactInspector(root,row,true,'hpc',DATA,{milestone:id=>{const next=byId.get(id);if(next){select(next);focus(id);}}});};squareGraphNodes(root);if(state.selected)select(state.selected);\n"
    else:
        code+="\nconst selectBeforeCompact=selectRow;selectRow=function(row,milestone=false,scroll=false){selectBeforeCompact(row,milestone,scroll);compactInspector(root,row,milestone,'ai',DATA,{job:id=>{const next=byJob.get(id);if(next)selectRow(next);},milestone:id=>{const next=byMilestone.get(id);if(next){selectRow(next,true);focusNode(id);}}});};squareGraphNodes(root);if(state.selected)selectRow(state.selected.row,state.selected.isMilestone);\n"
    assert 'document.getElementById' not in code
    return ('function mountHpc' if hpc else 'function mountAi')+'(root,DATA){\n'+code+'\n}'

def main():
    ai,ai_data=extract(AI/'index.html','ai')
    hpc,hpc_data=extract(D/'hpc/index.html','hpc')
    notes=build_notes.build()
    # Framework-free modules retain independent filters, selections and viewports.
    code=(D/'viewer/research-notes.js').read_text()+'\n'+(D/'viewer/inspector.js').read_text()+'\n'+component(AI/'viewer/app.js')+'\n'+component(D/'viewer/hpc.js',True)
    code+='''
const TEAM=JSON.parse(document.getElementById('teamData').textContent);
const mounted=new Set();let current=null;
function chooseTrack(track,updateUrl=true){
 if(!['ai','hpc'].includes(track))track='ai';
 for(const name of ['ai','hpc']){
  const button=document.getElementById('choose-'+name),panel=document.getElementById('track-'+name),active=name===track;
  button.setAttribute('aria-selected',String(active));button.tabIndex=active?0:-1;panel.hidden=!active;
  panel.querySelectorAll('[data-id="tooltip"]').forEach(n=>n.hidden=true);
 }
 const root=document.getElementById('track-'+track);
 if(!mounted.has(track)){(track==='ai'?mountAi:mountHpc)(root,TEAM[track]);mounted.add(track);}
 document.getElementById('activeTrackName').textContent=track==='ai'?'AI / Qwen3–235B':'HPC / OpenFOAM';
 document.getElementById('activeTrackNote').textContent=track==='ai'?'Good tokens/s ↑ · TTFT ≤ 3,000 ms · ITL ≤ 20 ms':'Mean s/step ↓ · NSCC / Iris';
 document.getElementById('workspaceTitle').textContent=track==='ai'?'Qwen inference':'OpenFOAM simulation';
 const values=track==='ai'?[['Research milestones',TEAM.ai.curated.nodes.length],['Retained allocations',TEAM.ai.runs.length],['Confirmed starts',TEAM.ai.runs.filter(r=>r.started===true).length]]:[['Research milestones',TEAM.hpc.nodes.length],['Documented connections',TEAM.hpc.edges.length],['CPU platforms',new Set(TEAM.hpc.nodes.map(n=>n.platform)).size]];
 values.forEach(([label,value],i)=>{document.getElementById('scopeLabel'+(i+1)).textContent=label;document.getElementById('scopeValue'+(i+1)).textContent=value;});
 document.getElementById('scopeExplanation').textContent=track==='ai'?'Includes probes and failed runs. Not 419 completed benchmarks.':'A curated investigation, not an exhaustive allocation census.';
 document.body.dataset.track=track;

 current=track;if(updateUrl)history.pushState({track},'', '#'+track);
}
for(const track of ['ai','hpc']){
 const button=document.getElementById('choose-'+track);
 button.addEventListener('click',()=>{if(current!==track)chooseTrack(track);});
 button.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){
  e.preventDefault();const next=e.key==='Home'?'ai':e.key==='End'?'hpc':track==='ai'?'hpc':'ai';chooseTrack(next);document.getElementById('choose-'+next).focus();
 }});
}
window.addEventListener('popstate',()=>chooseTrack(location.hash.slice(1),false));
window.addEventListener('hashchange',()=>{if(location.hash.slice(1)!==current)chooseTrack(location.hash.slice(1),false);});
chooseTrack(location.hash.slice(1),false);
document.getElementById('researchNoteClose').onclick=()=>document.getElementById('researchNote').close();
document.getElementById('researchNote').addEventListener('click',e=>{if(e.target===e.currentTarget){const r=e.currentTarget.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.currentTarget.close();}});
'''
    page=(D/'viewer/unified.html').read_text().replace('__STYLE__',(AI/'viewer/style.css').read_text()+'\n'+(D/'viewer/unified.css').read_text()).replace('__AI_PANEL__',ai).replace('__HPC_PANEL__',hpc).replace('__DATA__',json.dumps({'ai':ai_data,'hpc':hpc_data,'notes':notes},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')).replace('__SCRIPT__',code)
    asset='data:image/webp;base64,'+base64.b64encode((D/'assets/research-field.webp').read_bytes()).decode()
    page=page.replace('__SIDEBAR_IMAGE__',asset)
    assert '<iframe' not in page and '/home/apacsc42/' not in page
    # All HTML and SVG IDs must be unique after composing the two explorers.
    ids=re.findall(r'(?<![\w-])id="([^"]+)"',page);assert len(ids)==len(set(ids))
    out=D/'index.html';out.write_text(page);(D/'index.html.gz').write_bytes(gzip.compress(page.encode(),mtime=0))
    (D/'unified-build.json').write_text(json.dumps({'passed':True,'single_page':True,'iframes':0,'ai_allocations':len(ai_data['runs']),'ai_milestones':len(ai_data['curated']['nodes']),'hpc_milestones':len(hpc_data['nodes']),'unique_ids':len(ids),'sha256':hashlib.sha256(page.encode()).hexdigest()},indent=2)+'\n')
    print('Built one-page team atlas:',len(page.encode()),'bytes')
if __name__=='__main__':main()
