#!/usr/bin/env python3
"""Append a reviewed HPC section while preserving existing AI package parts."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import posixpath
import zipfile
from lxml import etree as E
import fitz
from pptx import Presentation

W = Path('/home/apacsc42/workspace')
O = W / 'submission-review/hpc-update-20261023'
BASE = O / 'inputs/AI-base.pptx'
SECTION = O / 'slide-section/HPC-section.pptx'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'


def xml(data):
    return E.fromstring(data)


def encoded(node):
    return E.tostring(node, encoding='UTF-8', xml_declaration=True, standalone=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relpath(part):
    p = PurePosixPath(part)
    return str(p.parent / '_rels' / (p.name + '.rels'))


def resolve(part, target):
    return posixpath.normpath(posixpath.join(posixpath.dirname(part), target))


def main():
    with zipfile.ZipFile(BASE) as z:
        old = {n: z.read(n) for n in z.namelist()}
    with zipfile.ZipFile(SECTION) as z:
        src = {n: z.read(n) for n in z.namelist()}
    assert len(Presentation(BASE).slides) == 32
    assert len(Presentation(SECTION).slides) == 8
    dst = dict(old)
    types = xml(old['[Content_Types].xml'])
    source_types = xml(src['[Content_Types].xml'])
    overrides = {x.get('PartName').lstrip('/'): x.get('ContentType')
                 for x in source_types if x.tag.endswith('Override')}
    defaults = {x.get('Extension') for x in types if x.tag.endswith('Default')}
    for x in source_types:
        if x.tag.endswith('Default') and x.get('Extension') not in defaults:
            types.append(E.fromstring(E.tostring(x)))
            defaults.add(x.get('Extension'))
    mapping = {}
    # OOXML permits one presentation notes master. Reuse the identical one.
    nm = 'ppt/notesMasters/notesMaster1.xml'
    assert src[nm] == old[nm] and src[relpath(nm)] == old[relpath(nm)]
    for rel in xml(src[relpath(nm)]):
        target = resolve(nm, rel.get('Target'))
        assert src[target] == old[target]
    mapping[nm] = nm

    def clone(part):
        if part in mapping:
            return mapping[part]
        p = PurePosixPath(part)
        target = str(p.parent / ('hpc_' + p.name))
        assert target not in dst
        mapping[part] = target  # Register before following cyclic relationships.
        dst[target] = src[part]
        if part in overrides:
            E.SubElement(types, '{' + CT + '}Override',
                         PartName='/' + target, ContentType=overrides[part])
        rp = relpath(part)
        if rp in src:
            rels = xml(src[rp])
            for rel in rels:
                if rel.get('TargetMode') == 'External':
                    continue
                copied = clone(resolve(part, rel.get('Target')))
                rel.set('Target', posixpath.relpath(copied, posixpath.dirname(target)))
            dst[relpath(target)] = encoded(rels)
        return target

    presentation = xml(old['ppt/presentation.xml'])
    rels = xml(old['ppt/_rels/presentation.xml.rels'])
    ids = presentation.find('{' + P + '}sldIdLst')
    next_id = max(int(x.get('id')) for x in ids) + 1
    next_rel = max(int(x.get('Id')[3:]) for x in rels) + 1

    def relationship(kind, target):
        nonlocal next_rel
        rid = 'rId' + str(next_rel)
        next_rel += 1
        E.SubElement(rels, '{' + PKG + '}Relationship', Id=rid,
                     Type=R + '/' + kind,
                     Target=posixpath.relpath(target, 'ppt'))
        return rid

    section_root = xml(src['ppt/presentation.xml'])
    section_rels = {x.get('Id'): x.get('Target')
                    for x in xml(src['ppt/_rels/presentation.xml.rels'])}
    for offset, sid in enumerate(section_root.find('{' + P + '}sldIdLst')):
        part = resolve('ppt/presentation.xml', section_rels[sid.get('{' + R + '}id')])
        target = clone(part)
        E.SubElement(ids, '{' + P + '}sldId', id=str(next_id + offset),
                     attrib={'{' + R + '}id': relationship('slide', target)})
    masters = presentation.find('{' + P + '}sldMasterIdLst')
    master_id = max(int(x.get('id')) for x in masters) + 1
    for original, copied in list(mapping.items()):
        if original.startswith('ppt/slideMasters/') and original.endswith('.xml'):
            E.SubElement(masters, '{' + P + '}sldMasterId', id=str(master_id),
                         attrib={'{' + R + '}id': relationship('slideMaster', copied)})
            master_id += 1
    dst['ppt/presentation.xml'] = encoded(presentation)
    dst['ppt/_rels/presentation.xml.rels'] = encoded(rels)
    dst['[Content_Types].xml'] = encoded(types)
    if 'docProps/app.xml' in dst:
        app = xml(dst['docProps/app.xml'])
        for x in app:
            if E.QName(x).localname in ('Slides', 'Notes'):
                x.text = '40'
        dst['docProps/app.xml'] = encoded(app)
    changed_existing = [n for n in old if old[n] != dst[n]]
    assert set(changed_existing) <= {
        'ppt/presentation.xml', 'ppt/_rels/presentation.xml.rels',
        '[Content_Types].xml', 'docProps/app.xml'}
    # Check every internal target in the final OPC graph, including AI parts.
    for name, data in dst.items():
        if name.endswith('.rels'):
            owner = (name.replace('/_rels/', '/').removesuffix('.rels')
                     if name != '_rels/.rels' else '')
            for rel in xml(data):
                if rel.get('TargetMode') != 'External':
                    assert resolve(owner, rel.get('Target')) in dst, (name, rel.attrib)
    out = O / BASE.name
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, data in dst.items():
            z.writestr(name, data)
    deck = Presentation(out)
    assert len(deck.slides) == 40
    assert all(s.notes_slide.notes_text_frame.text.strip() for s in deck.slides)
    for i, s in enumerate(Presentation(BASE).slides):
        assert s._element.xml == deck.slides[i]._element.xml
        assert s.notes_slide.notes_text_frame.text == deck.slides[i].notes_slide.notes_text_frame.text
    pdf = fitz.open()
    for p in [O / 'inputs/AI-base.pdf',
              O / 'slide-section/HPC-section.pdf']:
        with fitz.open(p) as section:
            pdf.insert_pdf(section)
    assert len(pdf) == 40
    pdf.save(O / 'TripleU_APAC2026_Presentation.pdf')
    notes = '# TripleU combined presenter notes — 23 October 2026\n\n'
    for i, s in enumerate(deck.slides, 1):
        notes += '## Slide ' + str(i) + '\n\n' + s.notes_slide.notes_text_frame.text + '\n\n'
    (O / 'PRESENTER_NOTES.md').write_text(notes)
    report = dict(passed=True, slides=40, ai_slides=32, hpc_slides=8,
                  hpc_fraction=0.2, original_ai_parts_byte_preserved=True,
                  original_package_parts_unchanged=sum(old[n] == dst[n] for n in old),
                  changed_existing_metadata_parts=changed_existing,
                  base_sha256=sha(BASE.read_bytes()), section_sha256=sha(SECTION.read_bytes()),
                  combined_sha256=sha(out.read_bytes()),
                  internal_relationships_resolve=True, original_ai_notes_preserved=True,
                  pdf_pages=40, render_method='Coordinate-based PDF previews; not an Office render',
                  ai_section_footer_preserved='Original AI section numbering is unchanged; HPC slides are 33–40.')
    (O / 'merge-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
