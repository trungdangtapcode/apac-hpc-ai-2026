#!/usr/bin/env python3
"""Rebuild the existing talk with a source-bound full-quality conclusion."""
from pathlib import Path
import hashlib

source_path = Path(__file__).with_name('build_ai_acceptance_slides_20261102.py')
source = source_path.read_text()
start = source.index('# 16 — Conclusion · preserve the model and verify the service')
end = source.index('# 17 — Backup · Environment', start)
replacement = '''# 16 — Robustness · matched answer-quality verification
s=slide('The optimised service retains 99.9154% of reference accuracy',
        'All 12032 MMLU-Pro questions per role, same 16 H200, official FP8 checkpoint, prepared prompts, generation and scoring. Reference 9460 correct; candidate 9452. Retention 9452/9460=99.915433%, above the declared local 99% threshold. All sixteen jobs completed, no service errors. This is a whole-deployment local quality comparison, not organiser certification or unchanged outputs. The accepted serving entry 28197 remains a separate performance result, completed in 611 seconds. Hand over to the preserved HPC section.',
        'quality-verification-20261102/FULL_COMPARISON; independent full-set replay')
s.text('Same FP8 checkpoint · same prompts, generation and scoring',1.,1.49,11.3,.44,18,GRAY)
for x,label,accuracy,count,color in [
    (1.,'STOCK FP8 REFERENCE','78.6237%','9,460 correct / 12,032 questions',INK),
    (7.,'OPTIMISED SERVICE','78.5572%','9,452 correct / 12,032 questions',ORANGE)]:
 s.line(x,2.15,x+5.2,2.15,color,2)
 s.text(label,x,2.34,5.2,.42,17,color,bold=True)
 s.text(accuracy,x,2.99,5.2,.73,35,color,bold=True)
 s.text(count,x,3.90,5.2,.42,18,INK)
s.line(1.,4.58,12.2,4.58,PALE,1.2)
s.text('ACCURACY RETENTION',1.,4.83,5.4,.35,15,GRAY,bold=True)
s.text('9,452 / 9,460 = 99.9154%',1.,5.32,6.1,.59,27,INK,bold=True)
s.text('PASS: at least 99% of reference',7.,4.83,5.25,.53,20,ORANGE,bold=True)
s.text('16 jobs complete · 0 service errors',7.,5.48,5.25,.40,17,INK)
s.text('Full local MMLU-Pro check; organiser certification remains separate.',1.,6.40,11.3,.42,17,GRAY)
s.end()


'''
patched = source[:start] + replacement + source[end:]
# Keep all previous measured slides, theme, assets and renderer behavior.
exec(compile(patched, str(source_path), 'exec'), globals())
