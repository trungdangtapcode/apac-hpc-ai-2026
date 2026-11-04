/* A small safe Markdown reader: text nodes only, with links restricted to HTTPS. */
function researchInline(text){
 const fragment=document.createDocumentFragment(),pattern=/(`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))/g;let last=0,match;
 while((match=pattern.exec(text))){fragment.append(document.createTextNode(text.slice(last,match.index)));const token=match[0];
  if(token.startsWith('`')){const code=document.createElement('code');code.textContent=token.slice(1,-1);fragment.append(code);}
  else if(token.startsWith('**')){const strong=document.createElement('strong');strong.textContent=token.slice(2,-2);fragment.append(strong);}
  else{const link=/^\[([^\]]+)\]\(([^)]+)\)$/.exec(token),a=document.createElement('a');a.textContent=link[1];if(link[2].startsWith('#note:')){a.href='#';a.onclick=e=>{e.preventDefault();const[,track,id]=link[2].split(':');openResearchNote(track,id);};}else if(link[2].startsWith('https://')){a.href=link[2];a.target='_blank';a.rel='noopener';}fragment.append(a);}
  last=pattern.lastIndex;
 }fragment.append(document.createTextNode(text.slice(last)));return fragment;
}
function renderResearchMarkdown(markdown){
 const root=document.createElement('article');root.className='research-markdown';const lines=markdown.replaceAll('\r','').split('\n');let i=0;
 const inline=(tag,value)=>{const n=document.createElement(tag);n.append(researchInline(value));return n;};
 const cells=line=>line.trim().replace(/^\|/,'').replace(/\|$/,'').split(/(?<!\\)\|/).map(c=>c.trim().replaceAll('\\|','|'));
 while(i<lines.length){const line=lines[i];if(!line.trim()){i++;continue;}
  if(line.startsWith('```')){const pre=document.createElement('pre'),code=document.createElement('code'),language=line.slice(3).trim(),body=[];i++;while(i<lines.length&&!lines[i].startsWith('```'))body.push(lines[i++]);code.textContent=body.join('\n');if(language)code.dataset.language=language;pre.append(code);root.append(pre);i++;continue;}
  const heading=/^(#{1,4})\s+(.+)$/.exec(line);if(heading){root.append(inline('h'+Math.min(4,heading[1].length+1),heading[2]));i++;continue;}
  if(line.includes('|')&&/^\s*\|?[\s:|-]+\|[\s:|-]*$/.test(lines[i+1]||'')){
   const wrap=document.createElement('div');wrap.className='markdown-table-wrap';const table=document.createElement('table'),thead=document.createElement('thead'),hr=document.createElement('tr');for(const c of cells(line))hr.append(inline('th',c));thead.append(hr);table.append(thead);i+=2;const tbody=document.createElement('tbody');while(i<lines.length&&lines[i].trim().startsWith('|')){const tr=document.createElement('tr');for(const c of cells(lines[i++]))tr.append(inline('td',c));tbody.append(tr);}table.append(tbody);wrap.append(table);root.append(wrap);continue;
  }
  if(/^\s*(-|\d+\.)\s+/.test(line)){const ordered=/^\s*\d+\./.test(line),list=document.createElement(ordered?'ol':'ul');while(i<lines.length&&/^\s*(-|\d+\.)\s+/.test(lines[i]))list.append(inline('li',lines[i++].replace(/^\s*(-|\d+\.)\s+/,'')));root.append(list);continue;}
  if(line.startsWith('> ')){root.append(inline('blockquote',line.slice(2)));i++;continue;}
  const paragraph=[line];i++;while(i<lines.length&&lines[i].trim()&&!/^(#{1,4}\s|```|\||> |[-]\s|\d+\.\s)/.test(lines[i]))paragraph.push(lines[i++]);root.append(inline('p',paragraph.join(' ')));
 }return root;
}
function noteForRecord(track,row,milestone,data){
 if(milestone)return TEAM.notes?.[track]?.[row.id]||null;
 const group=data.curated.nodes.find(n=>n.job_ids.map(String).includes(String(row.job_id)));return group?TEAM.notes?.[track]?.[group.id]||null:null;
}
function openResearchNote(track,id){
 const note=TEAM.notes?.[track]?.[id];if(!note)return;
 const dialog=document.getElementById('researchNote'),article=renderResearchMarkdown(note.markdown),content=document.getElementById('researchNoteBody'),outline=document.getElementById('researchNoteOutline');
 document.getElementById('researchNoteTitle').textContent=note.title;
 document.getElementById('researchNoteMeta').textContent=note.platform+' / '+note.date+' / Research note';
 article.querySelector('h2')?.remove();content.replaceChildren(article);outline.replaceChildren();
 for(const[order,heading]of [...article.querySelectorAll('h2,h3')].entries()){heading.id='research-section-'+order;const button=document.createElement('button');button.textContent=heading.textContent;button.onclick=()=>heading.scrollIntoView({block:'start',behavior:'smooth'});outline.append(button);}
 document.getElementById('researchNoteMarkdown').href='https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/team-research-atlas-20261104/research-notes/'+track+'/'+id+'.md';
 document.getElementById('researchNoteDownload').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([note.markdown],{type:'text/markdown;charset=utf-8'}));a.download=track+'-'+id+'.md';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};
 if(!dialog.open)dialog.showModal();content.scrollTop=0;
}
function researchNoteButton(track,note){const button=document.createElement('button');button.className='open-research-note';button.textContent='Read investigation ↗';button.onclick=()=>openResearchNote(track,note.id);return button;}
