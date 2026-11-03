#!/usr/bin/env python3
"""Check narrative scope, source attribution and the 12:30 speaking plan."""
from pathlib import Path
import json,re,hashlib
from ai_release_context import review_path
W=Path(__file__).resolve().parents[1];O=review_path(W);R=W/'reports/ai-final-report-20261030'
records=json.loads((R/'investigation-transcript.json').read_text());before=json.loads((O/'inputs/transcript-records-before.json').read_text());plan=json.loads((O/'reasoning-plan.json').read_text())
assert records[34:]==before[34:],'Other track transcript records must be preserved.'
for r,p in zip(records[:34],plan['slides']):
 assert r['title']==p['title'],(r['slide'],r['title'],p['title'])
 for lang in ['en','vi']:
  d=r[lang]
  assert all(d.get(k) for k in ['hardware','brief','purpose','visual','terms','reading','tradeoff','script','caution','transition'])
  assert all(d['tradeoff'].get(k) for k in ['observation','hypothesis','conclusion','unknown'])
  assert '28,197 accepted requests' not in json.dumps(d)
  assert '28,197 requests' not in json.dumps(d)
text=(R/'TALK_SCRIPT_EN.md').read_text()
sections=re.findall(r'^## Slide (\d+) —[^\n]*\n(.*?)(?=^## |\Z)',text,re.M|re.S)
assert len(sections)==16
word_counts={n:len(s.split()) for n,s in sections};total=sum(word_counts.values())
assert 1250<=total<=1550,total
assert '0:40 | 12:30' in (R/'PRESENTATION_PLAN.md').read_text()
full=' '.join(s for n,s in sections)
assert 'Every candidate stayed below' not in full
assert 'at N40, 1,666' not in full
result=dict(passed=True,scope='AI narrative only; retained original HPC records unchanged',ai_main=16,ai_backup=18,HPC_records_preserved=True,spoken_EN_words=total,words_by_slide=word_counts,target_seconds=750,actual_human_mock_performed=False,estimated_rate_words_per_minute=120,estimated_voice_seconds=total/120*60,notes='Spoken timing includes a limited pause/transition allowance; verify by actual rehearsal. Main quality synthesis and detailed backup are separate.')
(O/'NARRATIVE_CONTENT_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
