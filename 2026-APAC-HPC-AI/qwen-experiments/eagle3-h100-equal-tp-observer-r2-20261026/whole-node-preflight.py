"""Confirm the full eight-H100 allocation before using role offsets."""
import csv,json,os,subprocess,sys
rows=list(csv.reader(subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name','--format=csv,noheader,nounits'],text=True).splitlines()))
assert len(rows)==8 and all('H100' in row[1] for row in rows), 'Expected one complete eight-H100 host'
uuids={r[0].strip() for r in rows};assert len(uuids)==8
mask=os.environ.get('CUDA_VISIBLE_DEVICES','').split(',')
assert len(mask)==8 and all(mask), 'PBS must provide the complete eight-device mask'
if all(x.startswith('GPU-') for x in mask):assert set(mask)==uuids, 'Assigned GPU UUID mask differs from full host'
else:assert sorted(map(int,mask))==list(range(8)), 'Assigned ordinal mask is not the full host'
with open(sys.argv[1],'w') as f:json.dump({'status':'PASS_FULL_EIGHT_H100_ALLOCATION','assigned_mask':mask,'host_gpu_uuids':sorted(uuids),'scope':'Full exclusive host only, before PBS role offsets'},f,indent=2)
