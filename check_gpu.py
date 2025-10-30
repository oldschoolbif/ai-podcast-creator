"""
GPU Status Check for AI Podcast Creator
Run this to verify your GPU setup before using GPU features
"""

import sys

def check_gpu_status():
    print("="*60)
    print("AI PODCAST CREATOR - GPU STATUS CHECK")
    print("="*60)
    print()
    
    # Check PyTorch
    print("1. Checking PyTorch...")
    try:
        import torch
        print(f"   ✓ PyTorch version: {torch.__version__}")
        print(f"   ✓ PyTorch installed")
    except ImportError:
        print("   ✗ PyTorch NOT installed")
        print("     Install with: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        return False
    
    # Check CUDA
    print("\n2. Checking CUDA...")
    if torch.cuda.is_available():
        print(f"   ✓ CUDA available: Yes")
        print(f"   ✓ CUDA version: {torch.version.cuda}")
        print(f"   ✓ cuDNN version: {torch.backends.cudnn.version()}")
        print(f"   ✓ GPU: {torch.cuda.get_device_name(0)}")
        
        # Get GPU memory
        props = torch.cuda.get_device_properties(0)
        total_memory = props.total_memory / (1024**3)
        print(f"   ✓ GPU Memory: {total_memory:.1f} GB")
        
        # Check compute capability
        compute_cap = torch.cuda.get_device_capability(0)
        print(f"   ✓ Compute Capability: {compute_cap[0]}.{compute_cap[1]}")
        
        # Check if Tensor Cores available
        if compute_cap[0] >= 7:
            print(f"   ✓ Tensor Cores: Available (FP16 support)")
        else:
            print(f"   ⚠ Tensor Cores: Not available (older GPU)")
        
        # Check if Ampere or newer (TF32 support)
        if compute_cap[0] >= 8:
            print(f"   ✓ TF32 Support: Yes (Ampere+ GPU)")
        else:
            print(f"   ⚠ TF32 Support: No (pre-Ampere GPU)")
            
    else:
        print("   ✗ CUDA NOT available")
        print("     GPU features will NOT work")
        print("     Check NVIDIA drivers and CUDA installation")
        return False
    
    # Check TTS dependencies
    print("\n3. Checking TTS (Coqui) dependencies...")
    try:
        import TTS
        print(f"   ✓ Coqui TTS installed: {TTS.__version__}")
    except ImportError:
        print("   ⚠ Coqui TTS NOT installed")
        print("     Install with: pip install TTS")
    
    # Check Music Generation dependencies
    print("\n4. Checking Music Generation (AudioCraft) dependencies...")
    try:
        import audiocraft
        print(f"   ✓ AudioCraft installed")
    except ImportError:
        print("   ⚠ AudioCraft NOT installed")
        print("     Install with: pip install audiocraft")
    
    # Check Avatar dependencies
    print("\n5. Checking Avatar (SadTalker) setup...")
    import os
    from pathlib import Path
    
    sadtalker_path = Path('external/SadTalker')
    if sadtalker_path.exists():
        print(f"   ✓ SadTalker directory found")
        
        # Check for checkpoints
        checkpoint_dir = sadtalker_path / 'checkpoints'
        if checkpoint_dir.exists():
            print(f"   ✓ Checkpoints directory found")
        else:
            print(f"   ⚠ Checkpoints directory NOT found")
            print(f"     Run: cd external/SadTalker && bash scripts/download_models.sh")
    else:
        print(f"   ⚠ SadTalker NOT installed")
        print(f"     Clone with: git clone https://github.com/OpenTalker/SadTalker.git external/SadTalker")
    
    # Memory recommendations
    print("\n" + "="*60)
    print("MEMORY REQUIREMENTS")
    print("="*60)
    print(f"Current GPU Memory: {total_memory:.1f} GB")
    print()
    print("Minimum Requirements:")
    print("  • TTS (Coqui XTTS):     2-3 GB VRAM")
    print("  • Music (MusicGen):     4-6 GB VRAM")
    print("  • Avatar (SadTalker):   6-8 GB VRAM")
    print()
    
    if total_memory >= 8:
        print("✓ Your GPU has enough memory for ALL features!")
    elif total_memory >= 6:
        print("⚠ Your GPU can run TTS and Music OR Avatar (not all at once)")
    elif total_memory >= 4:
        print("⚠ Your GPU can run TTS and Music only")
    elif total_memory >= 2:
        print("⚠ Your GPU can run TTS only")
    else:
        print("✗ Your GPU has insufficient memory for GPU features")
    
    print()
    print("="*60)
    print("VERDICT")
    print("="*60)
    
    if torch.cuda.is_available() and total_memory >= 6:
        print("✓ GPU is ready for AI Podcast Creator!")
        print("  You can use GPU-accelerated features")
        return True
    elif torch.cuda.is_available():
        print("⚠ GPU available but limited memory")
        print("  Some features may need to run separately")
        return True
    else:
        print("✗ GPU not available")
        print("  System will use CPU (much slower)")
        return False

if __name__ == "__main__":
    try:
        check_gpu_status()
    except Exception as e:
        print(f"\n✗ Error during check: {e}")
        sys.exit(1)

