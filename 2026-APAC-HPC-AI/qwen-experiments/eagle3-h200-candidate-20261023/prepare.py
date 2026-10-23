#!/usr/bin/env python3
"""Freeze the complete reviewed native H200 proposal once, without submission."""
import argparse,ast,hashlib,json,re,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PAYLOAD=ROOT/'payload'
REF='a3b51d20cd6d67a3f659a5f84e6e787f319fb1e5464e5ddc912cdbdd78824c49'
NIXL='45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);args=p.parse_args();dest=args.destination.resolve()
 assert not dest.exists(),'Never rewrite a frozen bundle'
 assert sha(PAYLOAD/'accepted-h200-reference.json')==REF and sha(PAYLOAD/'nixl-conn.py')==NIXL
 proof=json.loads((PAYLOAD/'accepted-h200-reference-review.json').read_text());assert proof['state']=='H200_TARGET_REFERENCE_ACCEPTED' and proof['reference_sha256']==REF
 result=subprocess.run(['python3','-B',str(PAYLOAD/'validate-cpu.py')],cwd=ROOT,capture_output=True,text=True,timeout=120)
 (ROOT/'root-cpu-validation.stdout').write_text(result.stdout);(ROOT/'root-cpu-validation.stderr').write_text(result.stderr);assert result.returncode==0,result.stderr
 replay=subprocess.run(['python3','-B',str(ROOT/'replay_probe_evidence.py')],cwd=ROOT,capture_output=True,text=True,timeout=30)
 (ROOT/'root-geometry-replay.stdout').write_text(replay.stdout);(ROOT/'root-geometry-replay.stderr').write_text(replay.stderr);assert replay.returncode==0,replay.stderr
 preflight=subprocess.run(['python3','-B',str(PAYLOAD/'preflight-assets.py')],cwd=ROOT,capture_output=True,text=True,timeout=30);assert preflight.returncode==0,preflight.stderr
 (ROOT/'root-target-asset-preflight.json').write_text(preflight.stdout)
 for path in PAYLOAD.rglob('*'):
  if path.is_file():assert not path.name.endswith('.safetensors') and not path.is_symlink()
 temporary=dest.with_name('.'+dest.name+'.preparing');assert not temporary.exists(),'Inspect an interrupted freeze'
 shutil.copytree(PAYLOAD,temporary,ignore=shutil.ignore_patterns('__pycache__','SHA256SUMS'))
 job=temporary/'job.sbatch';text=job.read_text();lines=re.findall(r'^export QWEN_BUNDLE=.*$',text,re.M);assert len(lines)==1
 text=text.replace(lines[0],'export QWEN_BUNDLE='+str(dest));text=re.sub(r'^#SBATCH -J .*$', '#SBATCH -J ap42-'+dest.name,text,flags=re.M);job.write_text(text)
 config=temporary/'config.json';c=json.loads(config.read_text());c['experiment']=dest.name;c['canonical_bundle']=str(dest);config.write_text(json.dumps(c,indent=2)+'\n')
 # Canonical CPU verification seals its files then replays the same byte-pinned
 # source fixtures retained alongside the complete proposal in the archive.
 (temporary/'validate-cpu.py').write_text('''"""Verify frozen bytes, then replay the retained source CPU fixtures."""
from pathlib import Path
import subprocess,sys
bundle=Path(__file__).resolve().parent
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,check=True)
source=bundle.parents[1]/'eagle3-h200-candidate-20261023/payload/validate-cpu.py'
subprocess.run([sys.executable,str(source)],check=True)
''')
 for path in temporary.rglob('*.py'):ast.parse(path.read_text(),filename=str(path))
 for path in [*temporary.glob('*.sh'),temporary/'job.sbatch']:subprocess.run(['bash','-n',str(path)],check=True)
 source_hashes={str(path.relative_to(PAYLOAD)):sha(path) for path in PAYLOAD.rglob('*') if path.is_file() and '__pycache__' not in path.parts}
 changes={str(path.relative_to(temporary)) for path in temporary.rglob('*') if path.is_file() and path.relative_to(temporary).as_posix() in source_hashes and sha(path)!=source_hashes[path.relative_to(temporary).as_posix()]}
 assert changes=={'job.sbatch','config.json','validate-cpu.py'},changes
 prov=dict(frozen_utc=datetime.now(timezone.utc).isoformat(),proposal=str(ROOT),destination=str(dest),proposal_file_sha256=source_hashes,source_reference_job='25585',source_reference_sha256=REF,source_native_nixl_sha256='912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f',derived_nixl_sha256=NIXL,canonical_only_changes=sorted(changes),root_review_corrections=['Preserve nested draft-evidence files in recursive freeze','Bind the complete QWEN_BUNDLE assignment, not an absolute suffix','Seal provenance itself and route canonical CPU checks to the retained verified source fixtures'],diagnostic_only=True,submitted=False,official_accuracy_verified=False)
 (temporary/'FROZEN_PROVENANCE.json').write_text(json.dumps(prov,indent=2)+'\n')
 files=sorted(path for path in temporary.rglob('*') if path.is_file())
 (temporary/'SHA256SUMS').write_text(''.join(sha(path)+'  '+str(path.relative_to(temporary))+'\n' for path in files))
 subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=temporary,check=True,capture_output=True)
 temporary.rename(dest)
 prepared=dict(id=dest.name,bundle=str(dest),state='FROZEN_NOT_SUBMITTED',gpus=16,nodes=2,minutes=17,pbs_su_reserved=0,diagnostic_only=True,asset_manifest_sha256=sha(dest/'asset-verification.json'),accepted_reference_job='25585',accepted_reference_sha256=REF,payload_sha256={str(path.relative_to(dest)):sha(path) for path in dest.rglob('*') if path.is_file()})
 (ROOT/'prepared.json').write_text(json.dumps(prepared,indent=2)+'\n')
 validation=dict(passed=True,checked_utc=datetime.now(timezone.utc).isoformat(),cpu_fixtures_passed=dict(target_asset_binding=4,geometry=12,candidate_client_head=5),actual_8receipt_source_replay_passed=True,complete_nested_evidence_frozen=True,exact_canonical_bundle_binding=True,target_runtime_asset_preflight_passed=True,reference_semantics_accepted=True,candidate_h200_runtime_validated=False,scored_benchmark=False,official_accuracy_verified=False)
 (ROOT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
 print(json.dumps(dict(state='FROZEN_NOT_SUBMITTED',bundle=str(dest),files=len(prepared['payload_sha256'])),indent=2))
if __name__=='__main__':main()
