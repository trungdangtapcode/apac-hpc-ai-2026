import json,socket,torch
assert torch.cuda.is_available() and torch.cuda.device_count()==4
uuids=[str(torch.cuda.get_device_properties(i).uuid) for i in range(4)]
assert len(set(uuids))==4
for i in range(4):
 x=torch.tensor([1.,2.],device=f'cuda:{i}');assert (x+1).tolist()==[2.,3.]
print(json.dumps({'state':'SPLIT_FOUR_GPU_TENSOR_PASS','host':socket.gethostname(),'uuids':uuids,'visible_gpu_count':4}))
