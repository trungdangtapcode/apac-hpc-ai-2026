"""Small GPU exercise: no model download or inference benchmark."""
import socket
import torch

print("Python host:", socket.gethostname(), flush=True)
print("PyTorch version:", torch.__version__, flush=True)
print("CUDA available:", torch.cuda.is_available(), flush=True)
if not torch.cuda.is_available():
    raise RuntimeError("No CUDA GPU visible inside this job/container")

print("Visible GPU count:", torch.cuda.device_count(), flush=True)
print("GPU 0:", torch.cuda.get_device_name(0), flush=True)
x = torch.tensor([1.0, 2.0, 3.0], device="cuda")
y = x + 1
print("Tensor device:", y.device, flush=True)
print("Result:", y.cpu().tolist(), flush=True)
