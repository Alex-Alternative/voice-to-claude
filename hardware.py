"""
GPU detection for Koda.
Detects NVIDIA GPU and CUDA availability to determine if Power Mode is available.
"""

import subprocess
import sys


def detect_gpu():
    """
    Detect GPU status. Returns one of:
      "cuda_ready"      - NVIDIA GPU + CUDA runtime working right now
      "nvidia_no_cuda"  - NVIDIA GPU found but CUDA runtime not set up
      "none"            - No NVIDIA GPU / integrated graphics only
    """
    # Primary: can ctranslate2 actually use CUDA right now?
    try:
        import ctranslate2
        types = ctranslate2.get_supported_compute_types("cuda")
        if types:
            return "cuda_ready"
    except Exception:
        pass

    # Secondary: nvidia-smi present? GPU exists but CUDA not configured
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return "nvidia_no_cuda"
    except Exception:
        pass

    return "none"


def get_nvidia_gpu_name():
    """Return the GPU model name string, or None if not found."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")[0]
    except Exception:
        pass
    return None


def try_install_cuda_packages():
    """
    Attempt to pip install NVIDIA CUDA runtime packages.
    Returns True if install succeeded and CUDA is now usable by ctranslate2.
    """
    packages = [
        "nvidia-cuda-runtime-cu12",
        "nvidia-cublas-cu12",
        "nvidia-cudnn-cu9",
    ]
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install"] + packages,
            capture_output=True, timeout=600,
        )
        if result.returncode != 0:
            return False
        # Re-test: reimport ctranslate2 to pick up new DLLs
        import importlib
        import ctranslate2
        importlib.reload(ctranslate2)
        types = ctranslate2.get_supported_compute_types("cuda")
        return bool(types)
    except Exception:
        return False
