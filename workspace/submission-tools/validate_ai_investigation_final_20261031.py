from pathlib import Path
from urllib.parse import unquote
import json,re,hashlib
w=Path('/home/apacsc42/workspace');r=w/'reports/ai-final-report-20261030';o=w/'submission-review/ai-investigation-update-20261030';pub=json.loads((o/'publication-validation.json').read_text());merge=json.loads((o/'merge-validation.json').read_text());pdf=json.loads((r/'transcript-pdf-validation.json').read_text());guide=json.loads((r/'transcript-validation.json').read_text())
paths=[r/n for n in ['TRANSCRIPT_EN.md','TRANSCRIPT_VI.md','REPORT.md','PRESENTATION_PLAN.md','EVIDENCE_CARDS.md','PANEL_QA.md','MOCK_QA_EVIDENCE.md']]+[w/'notes/ai-investigation-presentation-20261031.md']
count=0;directories=0
for f in paths:
 for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
  target=target.strip('<>')
  if target.startswith(('https://','http://','#')):continue
  actual=f.parent/unquote(target.split('#')[0]);assert actual.exists(),(str(f),target);count+=1;directories+=int(actual.is_dir())
assert hashlib.sha256((w/'VNUHCM - TripleU/Presentation/TripleU_APAC2026_Presentation.pptx').read_bytes()).hexdigest()==pub['pptx_sha256']==merge['pptx_sha256']==guide['deck_sha256']
assert hashlib.sha256((w/'VNUHCM - TripleU.zip').read_bytes()).hexdigest()==pub['zip_sha256']
for item in pdf['outputs']:
 assert hashlib.sha256((r/item['file']).read_bytes()).hexdigest()==item['sha256']
 assert hashlib.sha256((r/Path(item['file']).with_suffix('.md')).read_bytes()).hexdigest()==item['markdown_sha256']
validation={'passed':True,'edition':'Engineering investigation / complete visual and spoken reasoning','main_ai':16,'hidden_ai_backups':16,'unchanged_hpc':8,'visible_sequence':list(range(1,17))+list(range(33,41)),'main_pdf_pages':24,'transcript_pdf_pages':{p['file']:p['pages'] for p in pdf['outputs']},'pptx_sha256':pub['pptx_sha256'],'zip_sha256':pub['zip_sha256'],'local_links_checked':count,'directory_targets':directories,'checks':['Published deck, merge, transcript source and guides have the same deck identity','PDF source hashes and output hashes match','Main-talk PDF selected pages match full PDF in text and rendered pixels','All AI backup hidden flags and message/hardware labels checked','HPC dependency bytes, PDF renders and both delivery payloads preserved by linked audits','Main descriptor diagram, overview and VI/EN learning pages visually reviewed','Independent read-only technical reasoning review found no material remaining claim flaw'],'not_performed':['Live Office slideshow or screen-sharing check','Human timed mock','Official full-set model quality evaluation','New serving experiment or profiler','Fresh complete GPU portable replay after reader repair'],'timing':'Compact AI 10:40 target; proposed 12-minute rehearsal stop; official combined time/Q&A still unknown','backup_policy':'Source and recovery metadata captured and pushed; external large artifact bytes are not uploaded by Git.'}
(o/'FINAL_VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
print('Final cross-artifact checks passed; local links:',count,'including',directories,'source directories.')
