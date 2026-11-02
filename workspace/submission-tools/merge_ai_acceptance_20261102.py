#!/usr/bin/env python3
"""Replace only the AI slide sequence; preserve every HPC dependency byte."""
from ai_release_context import review_path, part_prefix
import os
from pathlib import Path,PurePosixPath
import hashlib,json,posixpath,zipfile
from datetime import datetime,timezone
from lxml import etree as E
from pptx import Presentation
import fitz
from PIL import Image,ImageDraw
W=Path('/home/apacsc42/workspace');O=review_path(W)
BASE=O/'inputs/combined-before-ai-update.pptx'
FRESH=O/'slides/TripleU_APAC2026_Presentation.pptx'
NSP='http://schemas.openxmlformats.org/presentationml/2006/main';NSR='http://schemas.openxmlformats.org/officeDocument/2006/relationships';PKG='http://schemas.openxmlformats.org/package/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types'
def sha(b):return hashlib.sha256(b).hexdigest()
def xml(b):return E.fromstring(b)
def enc(n):return E.tostring(n,encoding='UTF-8',xml_declaration=True,standalone=True)
def relpart(p):
 p=PurePosixPath(p);return str(p.parent/'_rels'/(p.name+'.rels'))
def resolve(p,t):return posixpath.normpath(posixpath.join(posixpath.dirname(p),t)) if not t.startswith('/') else t.lstrip('/')
def parts(p):
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None;return {n:z.read(n) for n in z.namelist()}
def sequence(d):
 p=xml(d['ppt/presentation.xml']);r={x.get('Id'):x.get('Target') for x in xml(d['ppt/_rels/presentation.xml.rels'])};return [(x.get('id'),x.get('{'+NSR+'}id'),resolve('ppt/presentation.xml',r[x.get('{'+NSR+'}id')])) for x in p.find('{'+NSP+'}sldIdLst')]
old=parts(BASE);src=parts(FRESH);before=json.loads((O/'HPC_BEFORE.json').read_text());dst=dict(old);oldseq=sequence(old);newseq=sequence(src);assert len(oldseq)==42 and len(newseq)==34
# A single notes master is shared with the existing HPC section.
master='ppt/notesMasters/notesMaster1.xml';assert src[master]==old[master] and src[relpart(master)]==old[relpart(master)]
for rel in xml(src[relpart(master)]):
 p=resolve(master,rel.get('Target'));assert src[p]==old[p]
media_by_hash={sha(blob):name for name,blob in old.items() if name.startswith('ppt/media/')}
reused_media=[]
mapping={master:master};types=xml(old['[Content_Types].xml']);st=xml(src['[Content_Types].xml']);overrides={x.get('PartName').lstrip('/'):x.get('ContentType') for x in st if x.tag.endswith('Override')}
defs={x.get('Extension') for x in types if x.tag.endswith('Default')}
for x in st:
 if x.tag.endswith('Default') and x.get('Extension') not in defs:types.append(xml(E.tostring(x)));defs.add(x.get('Extension'))
def clone(part):
 if part in mapping:return mapping[part]
 if part.startswith('ppt/media/') and sha(src[part]) in media_by_hash:
  mapping[part]=media_by_hash[sha(src[part])];reused_media.append(part);return mapping[part]
 p=PurePosixPath(part);target=str(p.parent/(part_prefix()+p.name));assert target not in dst
 mapping[part]=target;dst[target]=src[part]
 if part in {entry[2] for entry in newseq[16:]}:
  hidden=xml(dst[target]);hidden.set('show','0');dst[target]=enc(hidden)
 if part in overrides:E.SubElement(types,'{'+CT+'}Override',PartName='/'+target,ContentType=overrides[part])
 rp=relpart(part)
 if rp in src:
  rels=xml(src[rp])
  for r in rels:
   if r.get('TargetMode')=='External':continue
   copied=clone(resolve(part,r.get('Target')));r.set('Target',posixpath.relpath(copied,posixpath.dirname(target)))
  dst[relpart(target)]=enc(rels)
 return target
rels=xml(old['ppt/_rels/presentation.xml.rels']);rbyid={r.get('Id'):r for r in rels}
for original,fresh in zip(oldseq[:34],newseq):rbyid[original[1]].set('Target',posixpath.relpath(clone(fresh[2]),'ppt'))
pres=xml(old['ppt/presentation.xml'])
slide_list=pres.find('{'+NSP+'}sldIdLst')
nextslide=max(int(x.get('id')) for x in slide_list)+1
nextrel=max(int(r.get('Id')[3:]) for r in rels)+1
for offset,fresh in enumerate(newseq[34:]):
 rid='rId'+str(nextrel);nextrel+=1
 E.SubElement(rels,'{'+PKG+'}Relationship',Id=rid,Type=NSR+'/slide',Target=posixpath.relpath(clone(fresh[2]),'ppt'))
 node=E.Element('{'+NSP+'}sldId',id=str(nextslide),attrib={'{'+NSR+'}id':rid});nextslide+=1
 slide_list.insert(32+offset,node)
masters=pres.find('{'+NSP+'}sldMasterIdLst');nextid=max(int(x.get('id')) for x in masters)+1
for part,target in mapping.items():
 if part.startswith('ppt/slideMasters/') and part.endswith('.xml'):
  rid='rId'+str(nextrel);nextrel+=1
  E.SubElement(rels,'{'+PKG+'}Relationship',Id=rid,Type=NSR+'/slideMaster',Target=posixpath.relpath(target,'ppt'))
  E.SubElement(masters,'{'+NSP+'}sldMasterId',id=str(nextid),attrib={'{'+NSR+'}id':rid});nextid+=1
credits='customXml/assetCredits.xml'
if credits in src:
 target=clone(credits);rid='rId'+str(nextrel);nextrel+=1
 E.SubElement(rels,'{'+PKG+'}Relationship',Id=rid,Type=NSR+'/customXml',Target=posixpath.relpath(target,'ppt'))
dst['ppt/presentation.xml']=enc(pres);dst['ppt/_rels/presentation.xml.rels']=enc(rels);dst['[Content_Types].xml']=enc(types)
# Global metadata changes do not alter HPC slide content.
core=xml(old['docProps/core.xml']);dct='http://purl.org/dc/terms/';modified=core.find('{'+dct+'}modified')
if modified is not None:modified.text=datetime.fromisoformat(json.loads((O/'slides/presentation-data.json').read_text())['snapshot_utc']).strftime('%Y-%m-%dT%H:%M:%SZ')
for name,value in [('title','TripleU — APAC HPC-AI 2026'),('subject','AI research questions and technical reasoning; existing HPC section preserved')]:
 node=core.find('{http://purl.org/dc/elements/1.1/}'+name)
 if node is not None:node.text=value
dst['docProps/core.xml']=enc(core)
# Use the exact audited protected list, regardless of its descriptive metadata.
protected=before['presentation']['hpc_dependency_closure_parts']
assert all(sha(dst[n])==h for n,h in protected.items()),'HPC closure changed'
assert sequence(dst)[34:]==oldseq[34:]
missing=[]
for name,blob in dst.items():
 if not name.endswith('.rels'):continue
 original=name.replace('/_rels/','/').removesuffix('.rels') if '/_rels/' in name else ''
 for r in xml(blob):
  if r.get('TargetMode')=='External':continue
  target=resolve(original,r.get('Target'))
  if target not in dst:missing.append([name,target])
assert not missing,missing[:10]
OUT=O/'TripleU_APAC2026_Presentation.pptx'
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,blob in sorted(dst.items()):z.writestr(name,blob)
assert len(Presentation(OUT).slides)==42
# Combine the new AI coordinate-based PDF with the existing untouched HPC pages.
ai=fitz.open(O/'slides/TripleU_APAC2026_Presentation.pdf');hpc=fitz.open(O/'inputs/combined-before-ai-update.pdf');combined=fitz.open();combined.insert_pdf(ai);combined.insert_pdf(hpc,from_page=34,to_page=41)
PDF=O/'TripleU_APAC2026_Presentation.pdf';combined.save(PDF);combined.close();check=fitz.open(PDF)
main=fitz.open();main.insert_pdf(check,from_page=0,to_page=15);main.insert_pdf(check,from_page=34,to_page=41);main.save(O/'TripleU_APAC2026_Main_Talk.pdf');main.close()
assert len(check)==42
for n in range(8):
 assert check[34+n].get_text()==hpc[34+n].get_text()
 assert check[34+n].get_pixmap(matrix=fitz.Matrix(.5,.5)).samples==hpc[34+n].get_pixmap(matrix=fitz.Matrix(.5,.5)).samples
notes=[];deck=Presentation(OUT)
for n,slide in enumerate(deck.slides,1):
 text=slide.notes_slide.notes_text_frame.text;assert text.strip();notes.append(f'## Slide {n}\n\n{text}')
(O/'PRESENTER_NOTES.md').write_text('# TripleU presenter notes — 2 November 2026\n\nAI slides updated; original HPC notes retained unchanged.\n\n'+'\n\n'.join(notes)+'\n')
thumbs=[]
for n,page in enumerate(check):
 pix=page.get_pixmap(matrix=fitz.Matrix(.45,.45));im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((470,265));thumbs.append(im)
sheet=Image.new('RGB',(2000,11*300),'#e2e7e8');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):x=(i%4)*500+10;y=(i//4)*300+10;sheet.paste(im,(x,y));draw.text((x,y+274),f'{i+1:02d} '+('AI updated' if i<34 else 'HPC preserved'),fill='#23373b')
sheet.save(O/'Presentation_Overview.jpg',quality=90)
report={'passed':True,'slides':42,'updated_ai_slides':34,'preserved_hpc_slides':8,'protected_hpc_pptx_parts':len(protected),'protected_hpc_dependency_bytes_identical':True,'hpc_slide_sequence_identical':True,'ai_main_slides':16,'hidden_ai_backup_slides':18,'visible_sequence':list(range(1,17))+list(range(35,43)),'hpc_pdf_render_pixels_identical':True,'internal_relationships_resolve':True,'mapped_source_parts':len(mapping),'reused_existing_media_parts':len(reused_media),'added_parts':len(dst)-len(old),'pptx_sha256':sha(OUT.read_bytes()),'pdf_sha256':sha(PDF.read_bytes()),'render_scope':'Coordinate-based AI PDF and unchanged prior HPC PDF, not Office rendering.'}
(O/'merge-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
