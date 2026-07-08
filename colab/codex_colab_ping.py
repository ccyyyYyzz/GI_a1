import os
import socket
import sys

print("GI_A1_PING_OK")
print("PYTHON", sys.version.split()[0])
print("HOSTNAME", socket.gethostname())
print("CWD", os.getcwd())

try:
    import torch
    print("TORCH", torch.__version__)
    print("CUDA_AVAILABLE", torch.cuda.is_available())
    print("CUDA_DEVICE_COUNT", torch.cuda.device_count())
    print("CUDA_DEVICE_NAME", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NONE")
except Exception as exc:
    print("TORCH_CHECK_ERROR", repr(exc))

os.system("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || true")
