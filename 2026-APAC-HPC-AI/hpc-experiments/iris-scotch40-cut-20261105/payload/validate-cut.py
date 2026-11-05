"""Verify canonical serial mesh bytes or the fresh native 40-way Scotch cut."""
from pathlib import Path
import argparse,hashlib,json,re

def mesh(root,expected):
 root=Path(root);expected=json.loads(Path(expected).read_text());checks=[];mismatches=[]
 for item in expected['unpacked_members_match_archive']:
  p=root/item['file'];h=hashlib.sha256()
  with p.open('rb') as stream:
   for block in iter(lambda:stream.read(2*1024*1024),b''):h.update(block)
  row={'file':item['file'],'bytes':p.stat().st_size,'sha256':h.hexdigest()};checks.append(row)
  if row['bytes']!=item['bytes'] or row['sha256']!=item['sha256']:mismatches.append(item['file'])
 return {'passed':len(checks)==8 and not mismatches,'members':checks,'mismatches':mismatches,'scope':'Full eight-member serial mesh identity versus retained official archive extraction; no download or modification.'}

def cut(case):
 case=Path(case);directories={x.name for x in case.glob('processor*') if x.is_dir()}
 expected_directories={'processor'+str(i) for i in range(40)}
 assert directories==expected_directories,('Processor set',len(directories),sorted(directories-expected_directories)[:5])
 assert all(not(case/('processor'+str(i))).is_symlink() for i in range(40))
 log=(case/'logFiles/decomposePar.log').read_text(errors='replace')
 assert re.search(r'(?m)^End\s*$',log) and not re.search(r'FOAM FATAL|MPI_ABORT|FATAL ERROR',log,re.I)
 assert 'version=v2512' in log and 'scalar=64' in log
 cells=[int(x) for x in re.findall(r'(?m)^\s*Number of cells\s*=\s*(\d+)\s*$',log)]
 assert len(cells)==40 and sum(cells)==65334765 and min(cells)>0,(len(cells),sum(cells))
 config=(case/'system/include/caseDefinition').read_text()
 assert re.search(r'(?m)^\s*nCores\s+40\s*;',config)
 assert re.search(r'(?m)^\s*decompositionMethod\s+scotch\s*;',config)
 for i in range(40):
  p=case/('processor'+str(i));assert (p/'constant/polyMesh/boundary').is_file()
  assert all((p/'0'/field).is_file() for field in ['U','p','k','omega','nut','nuTilda'])
 return {'passed':True,'ranks':40,'mesh_cells':sum(cells),'cells_by_rank':cells,'method':'scotch','restored_zero_fields':40*6,'scope':'Native 40-way cut and restore only. No parallel initialization, solver, Cd proof, READY state or score.'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mesh');ap.add_argument('--expected');ap.add_argument('--mesh-only',action='store_true');ap.add_argument('--case');ap.add_argument('--output',required=True);a=ap.parse_args()
 result=mesh(a.mesh,a.expected) if a.mesh_only else cut(a.case)
 Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed'],'Canonical mesh mismatch; no decomposition is authorized by this gate'
if __name__=='__main__':main()
