#!/usr/bin/env python3
"""Replace eight HPC slides; preserve the existing AI dependency bytes and pages."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import hashlib, json, posixpath, zipfile
from lxml import etree as E
from pptx import Presentation
from PIL import Image, ImageDraw
import fitz

W = Path('/home/apacsc42/workspace')
O = W/'submission-review/hpc-iris-slides-20261103'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
def sha(b): return hashlib.sha256(b).hexdigest()
def xml(b): return E.fromstring(b)
def enc(n): return E.tostring(n, encoding='UTF-8', xml_declaration=True, standalone=True)
def rp(p):
    p = PurePosixPath(p)
    return str(p.parent/'_rels'/(p.name+'.rels'))
def resolve(p, t):
    return t.lstrip('/') if t.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(p), t))
def parts(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return {n:z.read(n) for n in z.namelist()}
def sequence(d):
    rels={x.get('Id'):x.get('Target') for x in xml(d['ppt/_rels/presentation.xml.rels'])}
    return [(x.get('id'),x.get('{'+R+'}id'),resolve('ppt/presentation.xml',rels[x.get('{'+R+'}id')]))
            for x in xml(d['ppt/presentation.xml']).find('{'+P+'}sldIdLst')]
def closure(d, roots):
    found=set()
    def visit(p):
        if p in found: return
        found.add(p)
        if rp(p) in d:
            found.add(rp(p))
            for r in xml(d[rp(p)]):
                if r.get('TargetMode')!='External': visit(resolve(p,r.get('Target')))
    for p in roots: visit(p)
    return found

old=parts(O/'inputs/combined-before.pptx')
src=parts(O/'slide-section/HPC-section.pptx')
oldseq=sequence(old); newseq=sequence(src)
assert len(oldseq)==42 and len(newseq)==8
protected={n:sha(old[n]) for n in closure(old,[x[2] for x in oldseq[:34]])}
dst=dict(old)
master='ppt/notesMasters/notesMaster1.xml'
assert src[master]==old[master] and src[rp(master)]==old[rp(master)]
for r in xml(src[rp(master)]):
    n=resolve(master,r.get('Target')); assert old[n]==src[n]
mapping={master:master}; types=xml(old['[Content_Types].xml'])
overrides={x.get('PartName').lstrip('/'):x.get('ContentType') for x in xml(src['[Content_Types].xml']) if x.tag.endswith('Override')}
defaults={x.get('Extension') for x in types if x.tag.endswith('Default')}
for x in xml(src['[Content_Types].xml']):
    if x.tag.endswith('Default') and x.get('Extension') not in defaults:
        types.append(xml(E.tostring(x))); defaults.add(x.get('Extension'))
media={sha(blob):n for n,blob in old.items() if n.startswith('ppt/media/')}
def clone(part):
    if part in mapping: return mapping[part]
    if part.startswith('ppt/media/') and sha(src[part]) in media:
        mapping[part]=media[sha(src[part])]; return mapping[part]
    p=PurePosixPath(part); target=str(p.parent/('hpcnov03_'+p.name))
    assert target not in dst
    mapping[part]=target; dst[target]=src[part]
    if part in overrides:
        E.SubElement(types,'{'+CT+'}Override',PartName='/'+target,ContentType=overrides[part])
    if rp(part) in src:
        rels=xml(src[rp(part)])
        for r in rels:
            if r.get('TargetMode')=='External': continue
            copied=clone(resolve(part,r.get('Target')))
            r.set('Target',posixpath.relpath(copied,posixpath.dirname(target)))
        dst[rp(target)]=enc(rels)
    return target
rels=xml(old['ppt/_rels/presentation.xml.rels'])
rbyid={r.get('Id'):r for r in rels}
for original,fresh in zip(oldseq[34:],newseq):
    rbyid[original[1]].set('Target',posixpath.relpath(clone(fresh[2]),'ppt'))
pres=xml(old['ppt/presentation.xml']); masters=pres.find('{'+P+'}sldMasterIdLst')
nextid=max(int(x.get('id')) for x in masters)+1
nextrel=max(int(x.get('Id')[3:]) for x in rels)+1
for part,target in mapping.items():
    if part.startswith('ppt/slideMasters/') and part.endswith('.xml'):
        rid='rId'+str(nextrel); nextrel+=1
        E.SubElement(rels,'{'+PKG+'}Relationship',Id=rid,Type=R+'/slideMaster',Target=posixpath.relpath(target,'ppt'))
        E.SubElement(masters,'{'+P+'}sldMasterId',id=str(nextid),attrib={'{'+R+'}id':rid}); nextid+=1
dst['ppt/presentation.xml']=enc(pres)
dst['ppt/_rels/presentation.xml.rels']=enc(rels)
dst['[Content_Types].xml']=enc(types)
assert all(sha(dst[n])==h for n,h in protected.items())
assert sequence(dst)[:34]==oldseq[:34]
missing=[]
for n,blob in dst.items():
    if not n.endswith('.rels'): continue
    parent=n.replace('/_rels/','/').removesuffix('.rels') if '/_rels/' in n else ''
    for r in xml(blob):
        if r.get('TargetMode')!='External' and resolve(parent,r.get('Target')) not in dst:
            missing.append([n,r.get('Target')])
assert not missing,missing
out=O/'TripleU_APAC2026_Presentation.pptx'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for n,b in sorted(dst.items()): z.writestr(n,b)
prs=Presentation(out); assert len(prs.slides)==42
assert [i+1 for i,s in enumerate(prs.slides) if s._element.get('show')=='0']==list(range(17,35))
basepdf=fitz.open(O/'inputs/combined-before.pdf'); hpc=fitz.open(O/'slide-section/HPC-section.pdf')
combined=fitz.open(); combined.insert_pdf(basepdf,from_page=0,to_page=33); combined.insert_pdf(hpc)
pdf=O/'TripleU_APAC2026_Presentation.pdf'; combined.save(pdf); combined.close()
check=fitz.open(pdf); assert len(check)==42
for i in range(34):
    assert check[i].get_text()==basepdf[i].get_text()
    assert check[i].get_pixmap(matrix=fitz.Matrix(.7,.7)).samples==basepdf[i].get_pixmap(matrix=fitz.Matrix(.7,.7)).samples
for i in range(8):
    assert check[34+i].get_text()==hpc[i].get_text()
main=fitz.open(); main.insert_pdf(check,from_page=0,to_page=15); main.insert_pdf(check,from_page=34,to_page=41)
main.save(O/'TripleU_APAC2026_Main_Talk.pdf'); main.close()
notes=[]
oldprs=Presentation(O/'inputs/combined-before.pptx')
for i,s in enumerate(prs.slides,1):
    value=s.notes_slide.notes_text_frame.text; assert value.strip()
    if i<=34: assert value==oldprs.slides[i-1].notes_slide.notes_text_frame.text
    notes.append(f'## Slide {i}\n\n{value}')
(O/'PRESENTER_NOTES.md').write_text('# TripleU presenter notes — 3 November 2026\n\nHPC slides updated; all 34 AI slides and speaker-note bodies preserved.\n\n'+'\n\n'.join(notes)+'\n')
sheet=Image.new('RGB',(1600,1000),'#e2e7e8'); draw=ImageDraw.Draw(sheet)
for i,page in enumerate(hpc):
    pix=page.get_pixmap(matrix=fitz.Matrix(.72,.72)); im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples); im.thumbnail((780,440))
    # Four columns, two rows for a compact overview.
    im.thumbnail((385,217)); x=(i%4)*400+7; y=(i//4)*500+20
    sheet.paste(im,(x,y)); draw.text((x,y+232),f'Slide {35+i}',fill='#23373b')
sheet.crop((0,0,1600,780)).save(O/'HPC_Overview.jpg',quality=92)
layout=json.loads((O/'slide-section/layout-validation.json').read_text())
assert all(0<=b['x'] and 0<=b['y'] and b['x']+b['w']<=13.334 and b['y']+b['h']<=7.501 for b in layout['text_boxes'])
assert len({b['sha256'] for b in layout['backgrounds']})==8
report={'passed':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'slides':42,'ai_slides':34,'hpc_slides':8,'hpc_positions':list(range(35,43)),'hpc_fraction_of_stored_slides':8/42,'ai_main_slides':16,'hidden_ai_backups':18,'ai_dependency_bytes_identical':True,'protected_ai_parts':protected,'ai_sequence_and_notes_unchanged':True,'ai_pdf_render_pixels_identical':True,'internal_relationships_resolve':True,'layout_within_slide':True,'distinct_hpc_backgrounds':8,'pptx_sha256':sha(out.read_bytes()),'pdf_sha256':sha(pdf.read_bytes()),'render_scope':'Coordinate-based PDF and previews, not an Office/device rehearsal. AI PDF pages copied unchanged.','official_submission_performed':False}
(O/'merge-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='protected_ai_parts'},indent=2))
