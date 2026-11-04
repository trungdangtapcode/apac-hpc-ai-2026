#!/usr/bin/env python3
"""Publish structured source-linked research explanations as Markdown and embedded data."""
from pathlib import Path
import hashlib,json,re
from urllib.parse import quote
D=Path(__file__).resolve().parent
ROOT=D.parents[2]
REPO='https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/'

def cell(value):return str(value).replace('|','\\|').replace('\n',' ')
def source(item):
    if isinstance(item,str):path=item;label='/'.join(Path(path).parts[-2:])
    else:path=item['path'];label=item.get('label') or Path(path).name
    path=path.removeprefix('/home/apacsc42/')
    if path.startswith('https://'):return label,path,None
    relative,_,anchor=path.partition('#');file=ROOT/relative
    assert file.is_file(),file
    return label,REPO+quote(relative,safe='/')+('#'+anchor if anchor else ''),(relative,hashlib.sha256(file.read_bytes()).hexdigest())

def build():
    ai=json.loads((D.parent/'ai-run-lineage-20261103/curated.json').read_text());hpc=json.loads((D.parent/'hpc-run-lineage-20261104/milestones.json').read_text())
    notes={};source_hashes={}
    for track,data in [('ai',ai),('hpc',hpc)]:
        entries=json.loads((D/(track+'-explanations.json')).read_text());assert set(entries)=={n['id'] for n in data['nodes']}
        notes[track]={}
        for node in data['nodes']:
            key=node['id'];entry=entries[key]
            lines=['# '+node['title'],'','> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.','','## Research question','',entry['question'],'','## Why investigate this?','',entry['rationale'],'','## What changed?','','| Aspect | Before / control | After / tested setting |','|---|---|---|']
            lines.extend('| '+' | '.join(cell(c[k]) for k in ['aspect','before','after'])+' |' for c in entry['changes'])
            lines+=['','## What was measured?','','| Evidence | Recorded result |','|---|---|']
            lines.extend('| '+cell(e['label'])+' | '+cell(e['value'])+' |' for e in entry['evidence'])
            lines+=['','## What did we learn?','']+['- '+s for s in entry['findings']]+['','## Decision','',entry['decision'],'','## Limits and remaining questions','']+['- '+s for s in entry['limits']]
            links=[]
            existing=entry.get('sources') or []
            original=node.get('evidence',[]);original=[original] if isinstance(original,str) else original
            seen=set()
            for item in existing+original:
                label,url,digest=source(item)
                if url in seen:continue
                seen.add(url);links.append('- ['+label+']('+url+')')
                if digest:source_hashes[digest[0]]=digest[1]
            lines+=['','## Sources','']+links
            markdown='\n'.join(lines)+'\n'
            override=D/'research-overrides'/(key+'.md')
            if override.is_file():markdown=override.read_text()
            out=D/'research-notes'/track/(key+'.md');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(markdown)
            notes[track][key]={'id':key,'title':node['title'],'platform':node['platform'],'date':node.get('date') or 'Date not retained','markdown':markdown,'preview':{k:v for k,v in entry.items() if k!='sources'}}
    # Validate local code/review links in overrides as well.
    for track in notes.values():
        for note in track.values():
            for url in re.findall(r'\]\((https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/[^)]+)\)',note['markdown']):
                from urllib.parse import unquote
                relative=unquote(url[len(REPO):].split('#')[0]);assert (ROOT/relative).is_file(),relative
    index=['# Research notes','','Source-linked retrospective explanations for 31 AI milestones and '+str(len(hpc['nodes']))+' HPC milestones. Original run records remain unchanged. Each note separates rationale, exact changes, measurements, decisions and evidence limits.','']
    for track in ['ai','hpc']:
        index+=['## '+track.upper(),'','| Milestone | Platform | Date |','|---|---|---|']
        for key,note in notes[track].items():index.append('| ['+note['title']+']('+track+'/'+key+'.md) | '+note['platform']+' | '+note['date']+' |')
        index.append('')
    (D/'research-notes/README.md').write_text('\n'.join(index)+'\n')
    report={'passed':True,'ai_notes':len(notes['ai']),'hpc_notes':len(notes['hpc']),'source_files_verified':len(source_hashes),'source_sha256':source_hashes,'content_type':'New retrospective explanation derived from retained evidence; not invented original pretrial records.'}
    (D/'notes-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return notes
if __name__=='__main__':
    notes=build();print(json.dumps({t:len(v) for t,v in notes.items()}))
