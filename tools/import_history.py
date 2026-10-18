#!/usr/bin/env python3
"""Import retained snapshots transparently; never fabricate original editing activity."""
import collections,datetime,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def git(args,**kw):return subprocess.run(['git',*args],cwd=ROOT,check=True,**kw)
def topic(path):
 if path.startswith('external-runtime/'):return 'runtime metadata'
 if path.startswith('2026-APAC-HPC-AI/') and '/qwen-experiments/' not in path:return 'organiser references'
 if path.startswith('workspace/2026-APAC-HPC-AI/'):return 'organiser references'
 if '/qwen-experiments/runs/' in path or '/nscc-pbs/collected/' in path:return 'run evidence'
 if any(x in path for x in ['/notes/','/tutorial/']):return 'notes and tutorials'
 if any(x in path for x in ['/Presentation/','/submission-','/VNUHCM - TripleU','/visual-assets/']):return 'submission and presentation'
 if any(x in path for x in ['/reports/','/research-','review','RESULTS','PLAN']):return 'research reviews'
 return 'experiment tooling and configurations'
def main():
 assert not (ROOT/'.git').exists(),'Refuse to overwrite an existing repository'
 git(['init','-b','main'],stdout=subprocess.DEVNULL);git(['config','user.name','trungdangtapcode']);git(['config','user.email','tcuong1000@gmail.com']);git(['config','core.autocrlf','false'])
 bootstrap=['.gitignore','AGENTS.md','README.md','HISTORY_PROVENANCE.md','BACKUP_SCOPE.md','REPRODUCIBILITY.md','NAVIGATION.md']
 bootstrap += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'tools').glob('*.py'))]
 git(['add','--',*bootstrap]);git(['commit','-m','Initialize transparent research archive and verified recovery tooling'],stdout=subprocess.DEVNULL)
 rows=[json.loads(x) for x in (ROOT/'backup/manifest.jsonl').read_text().splitlines()];groups=collections.defaultdict(list);now=datetime.datetime.now(datetime.timezone.utc)
 for r in rows:
  dt=datetime.datetime.fromtimestamp(r['mtime_ns']/1e9,datetime.timezone.utc);label=topic(r['path']);day=dt.date().isoformat()
  if label in ['organiser references','runtime metadata'] or day<'2026-09-29' or dt>now:day='reference-import'
  groups[(day,label)].append(r)
 ledger=[]
 for (day,label),items in sorted(groups.items(),key=lambda kv:('0000' if kv[0][0]=='reference-import' else kv[0][0],kv[0][1])):
  slug=label.replace(' ','-');segment=ROOT/'backup/daily'/(day+'-'+slug+'.jsonl');segment.parent.mkdir(parents=True,exist_ok=True);segment.write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in sorted(items,key=lambda x:x['path'])));paths=[r['path'] for r in items if r['storage']=='git']+[str(segment.relative_to(ROOT))];pathfile=ROOT/'backup/.paths.tmp';pathfile.write_bytes(b'\0'.join(p.encode() for p in paths)+b'\0');git(['add','-f','--pathspec-from-file='+str(pathfile),'--pathspec-file-nul']);pathfile.unlink()
  env=os.environ.copy();stamp=now if day=='reference-import' else datetime.datetime.fromtimestamp(max(r['mtime_ns'] for r in items)/1e9,datetime.timezone.utc);env['GIT_AUTHOR_DATE']=stamp.isoformat();subject='Import '+('reference snapshots' if day=='reference-import' else 'records dated '+day)+': '+label;git(['commit','-m',subject,'-m','Retrospective snapshot import. Author date follows retained file metadata; committer date records actual import. See HISTORY_PROVENANCE.md.'],env=env,stdout=subprocess.DEVNULL);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();ledger.append(dict(commit=commit,subject=subject,author_date=stamp.isoformat(),date_basis='actual import' if day=='reference-import' else 'latest retained source mtime in UTC group; not reconstructed original authorship',original_paths=[r['path'] for r in items]))
 (ROOT/'provenance/import-commits.json').write_text(json.dumps(ledger,indent=2)+'\n')
 # Add supplemental metadata, upstream bundles and coverage reports in a current-time commit.
 extras=[]
 for base in [ROOT/'backup',ROOT/'provenance',ROOT/'external-runtime/model-metadata']:
  for p in base.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts and p.name!='snapshot-metadata.json':extras.append(str(p.relative_to(ROOT)))
 pf=ROOT/'backup/.paths.tmp';pf.write_bytes(b'\0'.join(x.encode() for x in extras)+b'\0');git(['add','-f','--pathspec-from-file='+str(pf),'--pathspec-file-nul']);pf.unlink();git(['commit','-m','Record capture coverage, original upstream history and checksum verification'],stdout=subprocess.DEVNULL)
 print(json.dumps(dict(import_commits=len(ledger),total_commits=len(ledger)+2,author='trungdangtapcode <tcuong1000@gmail.com>',remote_created=False)))
if __name__=='__main__':main()
