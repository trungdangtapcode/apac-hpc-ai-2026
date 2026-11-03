#!/usr/bin/env python3
"""Publish only the reviewed HPC deck and dependent package checksums.

Folder/ZIP differences already present in the AI release are retained. Neither
scientific payload is regenerated. A changed publication snapshot aborts safely.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, fcntl, hashlib, json, os, posixpath, shutil, zipfile
W=Path('/home/apacsc42/workspace'); O=W/'submission-review/hpc-iris-slides-20261103'
T=W/'VNUHCM - TripleU'; D='Presentation/TripleU_APAC2026_Presentation.pptx'
M='AI_Task/logs/FILE_MANIFEST.json'; S='AI_Task/logs/SHA256SUMS'; MUTABLE={D,M,S}
def sha(b): return hashlib.sha256(b).hexdigest()
def encode(x): return (json.dumps(x,indent=2)+'\n').encode()
def inventory():
    return {p.relative_to(T).as_posix():{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size,'mode':p.stat().st_mode & 0o777} for p in sorted(T.rglob('*')) if p.is_file()}
def patch_checksums(manifest, sums, deck, now):
    obj=json.loads(manifest); rows=[x for x in obj['files'] if x['path']==D]
    assert len(rows)==1
    rows[0]['bytes']=len(deck); rows[0]['sha256']=sha(deck); obj['created_utc']=now
    updated=encode(obj); replacements={D:sha(deck),M:sha(updated)}; found=set(); lines=[]
    for line in sums.decode().splitlines(keepends=True):
        h,path=line.rstrip('\n').split('  ',1)
        resolved=posixpath.normpath(posixpath.join('AI_Task/logs',path))
        if resolved in replacements:
            line=replacements[resolved]+'  '+path+'\n';found.add(resolved)
        lines.append(line)
    assert found=={D,M}
    return {D:deck,M:updated,S:''.join(lines).encode()}
def atomic(p,b):
    tmp=p.with_name('.'+p.name+'.hpc-iris-update'); assert not tmp.exists()
    mode=p.stat().st_mode & 0o777 if p.exists() else 0o644
    tmp.write_bytes(b);tmp.chmod(mode);tmp.replace(p)

with (W/'.submission-publication.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    before=json.loads((O/'BEFORE.json').read_text()); reviewed=json.loads((O/'merge-validation.json').read_text())
    assert reviewed['passed'] and reviewed['ai_dependency_bytes_identical'] and reviewed['ai_pdf_render_pixels_identical']
    assert not (O/'publication-validation.json').exists(),'Already published; do not overwrite the receipt'
    assert inventory()==before['package'],'Package changed; rebase before publishing'
    zp=W/'VNUHCM - TripleU.zip'; assert sha(zp.read_bytes())==before['zip_sha256'],'ZIP changed; rebase'
    deck=(O/'TripleU_APAC2026_Presentation.pptx').read_bytes(); assert sha(deck)==reviewed['pptx_sha256']
    now=datetime.now(timezone.utc); changes=patch_checksums((T/M).read_bytes(),(T/S).read_bytes(),deck,now.isoformat())
    prefix=T.name+'/'
    staged=O/'VNUHCM - TripleU.hpc-reviewed.zip'
    with zipfile.ZipFile(zp) as src:
        assert src.testzip() is None
        zchanges={prefix+n:b for n,b in patch_checksums(src.read(prefix+M),src.read(prefix+S),deck,now.isoformat()).items()}
        with zipfile.ZipFile(staged,'w') as dst:
            dst.comment=src.comment
            for zi in src.infolist(): dst.writestr(copy.copy(zi),zchanges.get(zi.filename,src.read(zi)))
    with zipfile.ZipFile(staged) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(before['zip_entries'])
        for zi in z.infolist():
            old=before['zip_entries'][zi.filename]
            assert (zi.external_attr,list(zi.date_time),zi.compress_type)==(old['external_attr'],old['date_time'],old['compress_type'])
            if zi.filename not in zchanges: assert sha(z.read(zi))==old['sha256']
            else: assert z.read(zi)==zchanges[zi.filename]
    # Verify that the manifest edit changed only the deck record and timestamp.
    a=json.loads((T/M).read_bytes()); b=json.loads(changes[M])
    assert [x for x in a['files'] if x['path']!=D]==[x for x in b['files'] if x['path']!=D]
    assert inventory()==before['package'] and sha(zp.read_bytes())==before['zip_sha256']
    backup=W/'submission-archive'/('before-hpc-iris-slides-'+now.strftime('%Y%m%dT%H%M%SZ'));backup.mkdir()
    for n in MUTABLE:
        p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(T/n,p)
    shutil.copy2(zp,backup/zp.name)
    zsum=W/'VNUHCM - TripleU.zip.sha256'
    if zsum.exists(): shutil.copy2(zsum,backup/zsum.name)
    for n,b in changes.items(): atomic(T/n,b)
    atomic(zp,staged.read_bytes());atomic(zsum,(sha(staged.read_bytes())+'  '+zp.name+'\n').encode())
    after=inventory()
    assert set(after)==set(before['package'])
    assert all(after[n]==v for n,v in before['package'].items() if n not in MUTABLE)
    assert all(sha((T/n).read_bytes())==sha(b) for n,b in changes.items())
    assert sha(zp.read_bytes())==sha(staged.read_bytes())
    report={'passed':True,'published_utc':now.isoformat(),'scope':'HPC slides 35–42 and dependent presentation/package checksums only','slides':42,'ai_slides_preserved':34,'hpc_slides_updated':8,'ai_dependency_parts_verified':len(reviewed['protected_ai_parts']),'ai_dependency_bytes_identical':True,'ai_pdf_pages_identical':True,'folder_files_preserved':len(after)-3,'zip_entries_preserved':len(before['zip_entries'])-3,'hpc_scripts_and_logs_unchanged':True,'ai_scientific_payloads_unchanged':True,'existing_folder_zip_differences_retained':True,'updated_folder_paths':sorted(MUTABLE),'zip_crc_and_member_hashes_verified':True,'pptx_sha256':sha(deck),'zip_sha256':sha(zp.read_bytes()),'backup':str(backup),'organiser_upload_performed':False,'render_scope':reviewed['render_scope']}
    (O/'publication-validation.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))
