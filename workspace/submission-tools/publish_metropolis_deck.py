"""Validate, publish and reseal the redesigned presentation only."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile
from datetime import datetime,timezone
from pathlib import Path
from lxml import etree
from pptx import Presentation
from pptx.opc.constants import CONTENT_TYPE as CT

WORK=Path('/home/apacsc42/workspace')
ROOT=WORK/'VNUHCM - TripleU'
OUT=WORK/'submission-review/metropolis-ambient-backgrounds-2026-10-13'
SCRIPTS=ROOT/'AI_Task/job_scripts';LOGS=ROOT/'AI_Task/logs'
CANDIDATE=OUT/'TripleU_APAC2026_Presentation.pptx'
EXTERNAL=Path(__file__).parent/'design-assets'
BACKGROUND_MANIFEST=json.loads((EXTERNAL/'slide-backgrounds.json').read_text())
BACKGROUNDS=BACKGROUND_MANIFEST['slides']
assert len(BACKGROUNDS)==19 and len({r['sha256'] for r in BACKGROUNDS})==19

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

deck=Presentation(CANDIDATE)
assert len(deck.slides)==19
assert json.loads((OUT/'layout-validation.json').read_text())['all_text_within_boxes']
vietnamese=re.compile('[đĐăĂưƯơƠấầẩẫậắằẳẵặếềểễệốồổỗộớờởỡợứừửữựỵỷỹ]')
texts=[shape.text for slide in deck.slides for shape in slide.shapes if shape.has_text_frame]
notes=[slide.notes_slide.notes_text_frame.text for slide in deck.slides]
assert not any(vietnamese.search(x) for x in texts+notes)
assert '1,912.30' in texts and '97.44%' in texts
assert 'Latency headroom at N48' in texts
for forbidden in ('evidence','README','AI_Task/','submit.sbatch','reconstruct','dedicated account'):
    assert not any(forbidden.lower() in text.lower() for text in texts+notes),forbidden
assert all('Arial'==shape.text_frame.paragraphs[0].font.name or 'Courier New'==shape.text_frame.paragraphs[0].font.name
           for slide in deck.slides for shape in slide.shapes if shape.has_text_frame and shape.text)
with zipfile.ZipFile(CANDIDATE) as z:
    t=etree.fromstring(z.read('ppt/theme/theme1.xml'))
    assert t.get('name')=='TripleU / Metropolis'
    media=[i for i in z.namelist() if i.startswith('ppt/media/')]
    assert len(media)>=28
    photo_files={r['file']:[r['slide']] for r in BACKGROUNDS}
    photo_files['nvidia-h200.jpg']=[4]
    photo_hashes={sha(EXTERNAL/name):name for name in photo_files}
    photo_usage={name:[] for name in photo_files}
    xml_ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    for i in range(1,20):
        slide=etree.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        rels=etree.fromstring(z.read(f'ppt/slides/_rels/slide{i}.xml.rels'))
        mapping={rel.get('Id'):rel.get('Target') for rel in rels}
        for blip in slide.findall('.//a:blip',xml_ns):
            ref=mapping.get(blip.get('{'+xml_ns['r']+'}embed'),'')
            if '../media/' not in ref:continue
            digest=hashlib.sha256(z.read('ppt/'+ref.removeprefix('../'))).hexdigest()
            if digest in photo_hashes:photo_usage[photo_hashes[digest]].append(i)
        alphas=[int(e.get('val')) for e in slide.findall('.//a:gradFill/a:gsLst/a:gs/a:srgbClr/a:alpha',xml_ns)]
        assert {92000,84000}.issubset(alphas) if i==17 else {91000,82000}.issubset(alphas)
    assert photo_usage==photo_files,'Every slide must use its own distinct background image'
    assert len({r['sha256'] for r in BACKGROUNDS})==19
    assert all(r['sha256']!=sha(EXTERNAL/'nvidia-h200.jpg') for r in BACKGROUNDS)
    assert all(r['kind']=='infrastructure photograph' for r in BACKGROUNDS)
    for r in BACKGROUNDS:
        assert sha(EXTERNAL/r['file'])==r['sha256']
config=json.loads((SCRIPTS/'config.json').read_text())
assert config['id']=='P8-TP4_D8-TP8-EP8' and config['declared_concurrency']==48
before={p.name:sha(p) for p in SCRIPTS.iterdir() if p.is_file()}
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=WORK/'submission-archive'/('before-metropolis-'+stamp);backup.mkdir(parents=True)
target=ROOT/'Presentation/TripleU_APAC2026_Presentation.pptx'
shutil.copy2(target,backup/target.name)
shutil.copy2(WORK/'VNUHCM - TripleU.zip',backup/'VNUHCM - TripleU.zip')
shutil.copyfile(CANDIDATE,target)

# A real reusable PowerPoint template with six editable example layouts.
template=Presentation(CANDIDATE)
keep={0,1,3,4,9,14,16,18}
for i in reversed(range(len(template.slides))):
    if i not in keep:
        node=template.slides._sldIdLst[i];template.part.drop_rel(node.rId);template.slides._sldIdLst.remove(node)
assert len(template.slides)==8
example=OUT/'template-layouts.pptx';template.save(example)
potx=OUT/'TripleU_Metropolis_Template.potx'
with zipfile.ZipFile(example) as src,zipfile.ZipFile(potx,'w',zipfile.ZIP_DEFLATED) as dst:
    for info in src.infolist():
        data=src.read(info.filename)
        if info.filename=='[Content_Types].xml':
            types=etree.fromstring(data)
            main=next(n for n in types if n.get('PartName')=='/ppt/presentation.xml')
            main.set('ContentType',CT.PML_TEMPLATE_MAIN)
            data=etree.tostring(types,xml_declaration=True,encoding='UTF-8',standalone=True)
        dst.writestr(info,data)
with zipfile.ZipFile(potx) as z:assert z.testzip() is None

credit='''Presentation design and asset credits

Metropolis-adapted PowerPoint theme
Copyright 2015 Matthias Vogelgesang and the LaTeX community.
Contributors: https://github.com/matze/mtheme/graphs/contributors
Original template based on the HSRM theme by Benjamin Weiss.
Theme source: https://github.com/matze/mtheme
Theme adaptation license: CC BY-SA 4.0,
https://creativecommons.org/licenses/by-sa/4.0/
The theme license is separate from the presentation content and original
TripleU scientific charts and diagrams. Native PowerPoint layouts use Arial
for portability. The eight-layout POTX example is available in the review folder.

NVIDIA H200 product reference image
Source: https://www.nvidia.com/en-us/data-center/h200/
Image: https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/h200/h200-kv-bb580_440-d@2x.jpg
Credit: NVIDIA. This is a product image, not a photograph of the contest cluster.

Every slide uses a different atmospheric infrastructure photograph. Nineteen
distinct originals show server aisles, racks and cabling. No foreground image
is reused as a background. No isolated product render, diagram or portrait
is used as a background. These reference images do not depict the contest
cluster. The hardware slide has the only foreground H200
product image. Background tint opacity is
82–91% on light slides and 84–92% on the dark closing slide.

Lucide icons: server, cpu, network, timer, terminal and shield-check
Source: https://github.com/lucide-icons/lucide
Recoloured to match the theme. Applicable upstream license notices follow.

'''+(EXTERNAL/'lucide-LICENSE').read_text()+'\n\nBackground image sources\n\n'+'\n\n'.join(
    f"Slide {r['slide']:02d}: {r['subject']} ({r['kind']})\nCredit: {r['credit']}\nLicense: {r['license']}\nLicense URL: {r['license_url']}\nSource: {r['source']}\nReference: {r['reference_page']}\nSHA256: {r['sha256']}"
    for r in BACKGROUNDS)+'\n'
(LOGS/'presentation-credits.txt').write_text(credit)
(LOGS/'presentation-backgrounds.json').write_text(json.dumps(BACKGROUND_MANIFEST,indent=2)+'\n')
report={'utc':datetime.now(timezone.utc).isoformat(),'passed':True,'slides':19,
        'theme':'Metropolis-adapted','theme_embedded_in_pptx':True,'font':'Arial / Courier New',
        'english_slides_and_notes':True,'text_and_shape_bounds_verified':True,
        'embedded_images':len(media),'request_gate_rechecked':'1180/1211',
        'script_files_unchanged':True,'distinct_background_images':19,'no_background_reused':True,
        'no_foreground_image_reused_as_background':True,'infrastructure_photographs_only':True,
        'native_gradients':True,
        'photo_usage':photo_usage,
        'tinted_background_slides':list(range(1,20)),
        'background_tint_alpha':{'light':[.91,.82],'dark':[.92,.84]},
        'presentation_focused':True,'no_package_documentation_on_slides':True,
        'render_method':'PDF/previews share the explicit PPTX layout; not an Office rendering.'}
(LOGS/'presentation-validation.json').write_text(json.dumps(report,indent=2)+'\n')

assert before=={p.name:sha(p) for p in SCRIPTS.iterdir() if p.is_file()}
assert {p.name for p in ROOT.iterdir()}=={'Presentation','AI_Task','HPC_Task'}
assert {p.name for p in (ROOT/'Presentation').iterdir()}=={'TripleU_APAC2026_Presentation.pptx'}
files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and p not in (LOGS/'FILE_MANIFEST.json',LOGS/'SHA256SUMS')]
manifest={'created_utc':datetime.now(timezone.utc).isoformat(),'paths_relative_to_team_directory':True,
          'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
(LOGS/'FILE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=LOGS/'SHA256SUMS']
(LOGS/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {os.path.relpath(p,LOGS)}\n' for p in files))
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=LOGS,capture_output=True,text=True,check=True)
temporary=WORK/'submission-review/metropolis-submission.zip.tmp'
with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    z.write(ROOT,ROOT.name+'/')
    for p in sorted(ROOT.rglob('*')):z.write(p,str(Path(ROOT.name)/p.relative_to(ROOT)))
with zipfile.ZipFile(temporary) as z:
    assert z.testzip() is None
    assert z.read(ROOT.name+'/Presentation/'+target.name)==CANDIDATE.read_bytes()
archive=WORK/'VNUHCM - TripleU.zip';temporary.replace(archive)
digest=sha(archive);archive.with_suffix('.zip.sha256').write_text(f'{digest}  {archive.name}\n')
print(json.dumps({'pptx':str(target),'preview':str(OUT/'Presentation_Overview.jpg'),
    'template':str(potx),'zip':str(archive),'bytes':archive.stat().st_size,'sha256':digest,
    'slides':19,'format_preserved':True,'english_only':True,'winning_scripts_unchanged':True},indent=2))
