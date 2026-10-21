from pathlib import Path
import subprocess,json,shlex,io,tarfile,hashlib,tempfile,datetime
H=Path('/home/apacsc42');R=H/'2026-APAC-HPC-AI/hpc-experiments';E=R/'nscc-cpu-numa-scotch128-20261021'
inputs=json.loads((E/'payload/graph-inputs.json').read_text());inputs.pop('numa_scotch')
remote='''from pathlib import Path
import tarfile,io,sys
sources=SOURCES
b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w:gz') as t:
 for label,src in sources.items():
  for rank in range(128):
   p=Path(src)/('processor'+str(rank))/'constant/polyMesh/boundary'
   assert p.is_file() and p.stat().st_size<100000
   data=p.read_bytes();assert b'\\0' not in data
   info=tarfile.TarInfo(label+'/rank'+str(rank).zfill(3)+'.boundary');info.size=len(data);t.addfile(info,io.BytesIO(data))
assert b.tell()<2000000
sys.stdout.buffer.write(b.getvalue())
'''.replace('SOURCES',repr(inputs))
p=subprocess.run([str(R/'tools/nscc-cpu-ssh.sh'),'python3 -c '+shlex.quote(remote)],capture_output=True,timeout=60,check=True)
raw=E/'boundary-metadata.tar.gz';raw.write_bytes(p.stdout);metadata=dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),remote_sources=inputs,scope='Read-only collection of 256 small ASCII boundary metadata files, not mesh arrays or solver fields. All analysis below is local and bounded.',archive_sha256=hashlib.sha256(p.stdout).hexdigest(),archive_bytes=len(p.stdout),files={})
with tempfile.TemporaryDirectory(prefix='hpc-boundary-analysis-') as td:
 work=Path(td)
 with tarfile.open(fileobj=io.BytesIO(p.stdout)) as t:
  members=t.getmembers();assert len(members)==256 and all(x.isfile() and not x.name.startswith('/') and '..' not in Path(x.name).parts for x in members)
  for m in members:
   data=t.extractfile(m).read();metadata['files'][m.name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest());label,rankname=m.name.split('/');rank=int(rankname[4:7]);f=work/label/('processor'+str(rank))/'constant/polyMesh/boundary';f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
 for label in inputs:(work/label/'CUT_READY.json').write_text(json.dumps(dict(ranks=128,total_cells=65334765)))
 (work/'graph-inputs.json').write_text(json.dumps({k:str(work/k) for k in inputs}));subprocess.run(['python3',str(E/'payload/interface-graph.py')],cwd=work,check=True,capture_output=True,text=True)
 result=json.loads((work/'interface-summary.json').read_text());assert result['hierarchical']['unique_interface_faces']==2109346 and result['hierarchical']['max_rank_interface_faces']==131252 and result['hierarchical']['max_rank_processor_patches']==16
 assert result['default_scotch']['unique_interface_faces']==1549377 and result['default_scotch']['max_rank_interface_faces']==42141 and result['default_scotch']['max_rank_processor_patches']==35
 for label in inputs:
  d=json.loads((work/('graph-'+label+'.json')).read_text());d['case']=inputs[label];(E/('validated-graph-'+label+'.json')).write_text(json.dumps(d,indent=2)+'\n');result[label]['case']=inputs[label]
 (E/'graph-parser-validation.json').write_text(json.dumps(dict(passed=True,source='Actual retained initialized H/S processor boundaries; native stats match exactly',groups='Logical rank//16; current diagnostic map matches NUMA sets, not page locality',results=result),indent=2)+'\n')
(E/'boundary-metadata-collection.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(result,indent=2))
