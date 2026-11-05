"""Validate route/anchors/preservation; semantic audit is retained separately."""
from pathlib import Path
import re,json,hashlib,zipfile
from pptx import Presentation
R=Path(__file__).resolve().parent;W=R.parents[1]
p=Presentation(R/'TripleU_APAC2026_Presentation.pptx')
norm=lambda s:' '.join(s.split())
texts=[norm(' '.join(s.text for s in sl.shapes if s.has_text_frame)) for sl in p.slides]
result={}
for lang in ['EN','VI']:
 f=W/'reports/ai-final-report-20261030'/f'TALK_SCRIPT_{lang}.md';s=f.read_text()
 blocks=re.findall(r'^## (Script|Backup script) (\d+) — PPTX page \d+ — (.*?)\n(.*?)(?=^## |\Z)',s,re.M|re.S)
 assert [int(i) for kind,i,title,body in blocks if kind=='Script']==list(range(16))
 assert [int(i) for kind,i,title,body in blocks if kind=='Backup script']==[18,19,20,30]
 for kind,i,title,body in blocks:assert norm(title) in texts[int(i)],(lang,i,title)
 main=[b for kind,i,title,b in blocks if kind=='Script']
 forbidden=re.findall(r'\b(?:TP\d+|EP\d+|N\d+|\d{4,}|\d+\.\d{2,})\b',' '.join(main))
 assert not forbidden,forbidden
 result[lang]={'main_sections':16,'backup_sections':4,'all_titles_match_active_slides':True,'main_spoken_words':len(' '.join(main).split()),'hard_number_codes':forbidden,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'script_capture':'local only, not committed'}
 guides=[]
 for i,title in re.findall(r'^## Slide (\d+) — (.*)$',(W/'reports/ai-final-report-20261030'/f'TRANSCRIPT_{lang}.md').read_text(),re.M):
  guides.append({'printed_page':int(i),'title_matches':norm(title) in texts[int(i)-1]})
 assert len(guides)==34 and all(x['title_matches'] for x in guides)
 result[lang]['teaching_guide_34_title_routes_match']=True
anchors={0:['4,000 input tokens','200 output tokens'],2:['17 layouts explored','Different client loads'],5:['both source and destination','Partial-token','720'],7:['DeepGEMM prefill','+1.8%','not a request-time breakdown'],8:['24912','24913','N60','8192'],9:['+5.30%','+125.34 ms','-1.64 ms'],10:['+1.08%','+0.08%','1% cutoff'],11:['1,875 / 1,902','27 miss TTFT','0 miss ITL'],12:['model registration','3,051.52'],15:['12,032','MMLU-Pro','99.9154%'],30:['3,051.52']}
for i,items in anchors.items():
 for a in items:assert a in texts[i],(i,a)
r=json.loads((R/'VALIDATION.json').read_text());r['speech_route_checks']=result;r['selected_anchor_checks']=sum(map(len,anchors.values()));r['independent_semantic_review']='Both short scripts, all16main and4spokenbackups; numerical/setup/plot/causal boundaries reviewed with no material mismatch found. See AUDIT.md.';r['english_estimated_minutes']=[round(result['EN']['main_spoken_words']/120+1,2),round(result['EN']['main_spoken_words']/115+1,2)];r['timing_is_estimate_not_rehearsal']=True
(R/'VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(result,indent=2));print('PASS')
