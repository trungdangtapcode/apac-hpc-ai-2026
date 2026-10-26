"""Derive exactly two solver controls without reformatting the numerical input."""
from pathlib import Path
import re,sys
case=Path(sys.argv[1]);source=case/'system/controlDict.noWrite';text=source.read_text()
for key,value in [('startFrom','startTime'),('endTime','150')]:
    text,count=re.subn(r'(?m)^'+key+r'[ \t]+[^;\n]+;[^\n]*$',key+' '+value+';',text)
    assert count==1,(key,count)
(case/'system/controlDict').write_text(text)
