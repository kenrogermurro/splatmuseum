import shutil
import subprocess

MIN_VRAM_GB = 7.5  # cards sold as "8 GB" report slightly under 8


def gpu_via_nvidia_smi():
    """Return (name, vram_gb) using the NVIDIA driver, or None."""
    if not shutil.which("nvidia-smi"):
        return None
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total",
             "--format=csv,noheader,nounits"], text=True
        ).strip().splitlines()[0]
        name, mem_mib = [x.strip() for x in out.split(",")]
        return name, float(mem_mib) / 1024
    except Exception:
        return None


gpu = gpu_via_nvidia_smi()
if gpu:
    print(f"GPU: {gpu[0]}, VRAM: {gpu[1]:.1f} GB")
else:
    print("GPU: no NVIDIA GPU / driver detected")

# PyTorch is installed later with Nerfstudio, so missing is OK at this stage
try:
    import torch
    print("PyTorch:", torch.__version__, "| CUDA available:", torch.cuda.is_available())
    if gpu and not torch.cuda.is_available():
        print("WARNING: GPU found but PyTorch can't use it (likely a CPU-only torch build).")
except ImportError:
    print("PyTorch: not installed yet (expected before environment setup)")

tools = ["colmap", "ns-train", "ns-process-data", "ns-export", "rembg"]
missing = [t for t in tools if not shutil.which(t)]
for t in tools:
    print(f"{t}: {'OK' if t not in missing else 'MISSING'}")

print()
if gpu is None or gpu[1] < MIN_VRAM_GB:
    print("RESULT: Local run NOT recommended (no usable NVIDIA GPU or under 8 GB VRAM).")
    print("-> Use the Colab notebook: notebooks/splatmuseum_colab.ipynb")
elif missing:
    print(f"RESULT: GPU is fine, but setup is incomplete. Missing: {', '.join(missing)}")
    print("-> Finish the environment install, then rerun this check.")
else:
    print("RESULT: Local run OK.")