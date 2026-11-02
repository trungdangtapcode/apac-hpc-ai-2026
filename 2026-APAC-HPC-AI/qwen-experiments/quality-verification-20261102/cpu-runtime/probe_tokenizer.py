from transformers import AutoTokenizer
t=AutoTokenizer.from_pretrained('/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8',local_files_only=True)
for kwargs in ({},{'return_dict':False}):
 x=t.apply_chat_template([{'role':'user','content':'Hello'}],tokenize=True,add_generation_prompt=True,**kwargs)
 print(kwargs,type(x).__name__,repr(x)[:300])
