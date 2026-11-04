/* Compact display only. Original outcomes, measurements and sources remain expandable. */
function compactInspector(root,row,milestone,track,data,actions){
 const host=root.querySelector('[data-id="detailContent"]');host.replaceChildren();
 const make=(tag,cls,value)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(value!==undefined)n.textContent=value;return n;};
 const number=(v,d=1)=>typeof v==='number'&&Number.isFinite(v)?v.toLocaleString('en-US',{maximumFractionDigits:d}):'N/A';
 const hpc=track==='hpc',ids=hpc?[]:row.job_ids||[row.job_id];
 const samples=hpc?[]:ids.flatMap(id=>(data.hover.jobs[String(id)]||[]).map(p=>({...p,job_id:String(id)})));
 const latest=samples.at(-1)||{};
 const line=make('div','inspector-meta');line.append(make('span','platform-tag '+row.platform.toLowerCase(),row.platform),make('time','',row.date||'Date unknown'));host.append(line,make('h2','',milestone?row.title:'Job '+row.job_id));
 if(!milestone)host.append(make('div','record-purpose',row.title||'Purpose not retained'));
 if(hpc){
  const labels={closed:'Closed',qualified:'Qualified',reference:'Reference',practice:'Practice',mechanism:'Mechanism',observation:'Observation',invalid:'Incomplete',unreviewed:'Unreviewed'};
  const result=make('section','result-record');result.append(make('span','section-label','Result metrics'),make('span','record-status',labels[row.status]||row.status));
  const metricRows=row.result_metrics||[];
  if(metricRows.length){const table=make('div','hpc-metric-list');for(const m of metricRows){const card=make('article','hpc-metric-card');const value=typeof m.value==='number'&&Number.isFinite(m.value)?number(m.value,6)+' '+m.unit:'N/A · '+m.unit;card.append(make('span','hpc-metric-label',m.label),make('strong','hpc-metric-value',value),make('small','hpc-metric-meta','Job '+m.job_id+' · '+m.horizon),make('small','hpc-metric-scope',m.scope));table.append(card);}result.append(table);}else result.append(make('p','subtle','N/A · no numeric metrics retained for this milestone.'));
  host.append(result,make('h3','','Assessment'),make('p','hpc-assessment',row.assessment||'N/A · assessment not retained.'),make('h3','','Limitations'),make('p','hpc-limitations',row.limitations||'N/A · limitations not retained.'));
 }else{
  const readout=make('dl','metric-readout');
  for(const[label,value,unit]of [['Good output',latest.good_output_tokens_s,'tokens/s'],['TTFT',latest.ttft_avg_ms,'ms'],['ITL',latest.itl_avg_ms,'ms'],['Joint SLA',typeof latest.good_request_fraction==='number'?100*latest.good_request_fraction:null,'%']]){
   const cell=make('div');cell.append(make('dt','',label));const dd=make('dd','',number(value,label==='Joint SLA'?2:1));dd.append(make('small','',unit));cell.append(dd);readout.append(cell);
  }host.append(readout);
  if(samples.length)host.append(make('div','measurement-context','Job '+latest.job_id+' / '+(latest.concurrency?'N'+latest.concurrency:'N/A')+' / '+(latest.phase||'Recorded')));
 }
 const meta=make('dl','record-fields');
 const fields=hpc?[['Change',row.change],['Jobs',row.jobs]]:milestone?[['Jobs',ids.join(' · ')]]:[['State',row.status||'Unknown'],['Started',row.started===true?'Yes':row.started===false?'No':'Unknown'],['GPUs',row.allocated_gpu_count??'N/A']];
 for(const[label,value]of fields){const group=make('div');group.append(make('dt','',label));const dd=make('dd');if(!hpc&&label==='Jobs'){for(const id of ids){const button=make('button','job-ref',String(id));button.onclick=()=>actions.job(String(id));dd.append(button);}}else dd.textContent=String(value??'N/A');group.append(dd);meta.append(group);}host.append(meta);
 const note=noteForRecord(track,row,milestone,data);if(note)host.append(researchNoteButton(track,note));
 const analysis=make('details','inspector-disclosure');analysis.append(make('summary','',hpc?'Context':'Analysis'));
 if(note){
  const preview=note.preview;const md='### Question\n'+preview.question+'\n\n### Intervention\n'+preview.changes.map(c=>'- **'+c.aspect+':** '+c.after).join('\n')+'\n\n### Decision\n'+preview.decision;
  analysis.append(renderResearchMarkdown(md),researchNoteButton(track,note));
 }else{ for(const[label,value]of hpc?[['Classification',({closed:'Closed / no stable gain',qualified:'Qualified signal / repeat needed',reference:'Reference reproduction',practice:'Practice / not an official score',mechanism:'Mechanism / not a speedup',observation:'Observation / separate allocations',invalid:'Incomplete / invalid comparison',unreviewed:'Accepted / result not reviewed'})[row.status]||row.status],['What changed',row.change]]:[['Change',row.change],['Outcome',row.outcome||row.result]])if(value){analysis.append(make('h3','',label),make('p','',typeof value==='string'?value:JSON.stringify(value)));}}host.append(analysis);
 if(samples.length){const details=make('details','inspector-disclosure');details.append(make('summary','',samples.length+' measurements'));const scroll=make('div','point-list'),table=make('table'),tr=make('tr');for(const h of ['Job','N / phase','Good tok/s','TTFT ms','ITL ms','SLA %'])tr.append(make('th','',h));table.append(tr);for(const p of samples){const tr=make('tr');for(const value of [p.job_id,(p.concurrency?'N'+p.concurrency:'N/A')+' / '+(p.phase||'N/A'),number(p.good_output_tokens_s),number(p.ttft_avg_ms),number(p.itl_avg_ms),number(typeof p.good_request_fraction==='number'?p.good_request_fraction*100:null,2)])tr.append(make('td','',value));table.append(tr);}scroll.append(table);details.append(scroll);host.append(details);}
 const graph=hpc?data:data.curated,edges=milestone?graph.edges.filter(e=>e.source===row.id||e.target===row.id):[];
 if(edges.length){const links=make('section','compact-connections');links.append(make('div','section-label','Connections'));for(const e of edges){const other=graph.nodes.find(n=>n.id===(e.source===row.id?e.target:e.source));if(!other)continue;const button=make('button','connection-link');button.append(make('span','connection-relation',e.relation),make('span','connection-title',other.title),make('span','connection-arrow',e.source===row.id?'↗':'↙'));button.title=other.title+(e.reason?' — '+e.reason:'');button.onclick=()=>actions.milestone(other.id);links.append(button);}host.append(links);}
 const sources=hpc?[row.evidence]:row.evidence||[];if(sources.length){const details=make('details','inspector-disclosure');details.append(make('summary','',sources.length+' sources'));const list=make('ul','compact-sources');for(const path of [...new Set(sources)]){const li=make('li'),link=make('a','',path.split('/').slice(-2).join('/'));link.title=path;link.href='https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/'+path.split('/').map(encodeURIComponent).join('/');link.target='_blank';link.rel='noopener';li.append(link);list.append(li);}details.append(list);host.append(details);}
}
function squareGraphNodes(root){
 const ns='http://www.w3.org/2000/svg';
 for(const node of root.querySelectorAll('g.node[data-key]')){
  const shape=node.querySelector('path,polygon');if(!shape)continue;const b=shape.getBBox(),rect=document.createElementNS(ns,'rect');
  for(const[k,v]of Object.entries({x:b.x,y:b.y,width:b.width,height:b.height,rx:1}))rect.setAttribute(k,String(v));
  rect.setAttribute('stroke',shape.getAttribute('stroke')||'#798491');rect.setAttribute('fill','#fff');shape.replaceWith(rect);
 }
}
