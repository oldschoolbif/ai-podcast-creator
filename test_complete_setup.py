"""
Complete Setup Test Script
Tests all functionality from scratch following our documentation
"""

import sys
import os
from pathlib import Path
import subprocess

def print_section(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def run_test(name, func):
    """Run a test and report results."""
    print(f"TEST: {name}")
    print("-" * 70)
    try:
        result = func()
        if result:
            print(f"✅ PASS: {name}\n")
            return True
        else:
            print(f"❌ FAIL: {name}\n")
            return False
    except Exception as e:
        print(f"❌ ERROR: {name}")
        print(f"   {str(e)}\n")
        return False

def test_python_version():
    """Test Python version."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 10:
        print("✓ Python 3.10+ detected")
        return True
    else:
        print("✗ Python 3.10+ required")
        return False

def test_pytorch_installed():
    """Test if PyTorch is installed."""
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        return True
    except ImportError:
        print("✗ PyTorch not installed")
        print("  Install: pip install torch torchvision torchaudio")
        return False

def test_cuda_available():
    """Test if CUDA is available."""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA available")
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA version: {torch.version.cuda}")
            mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"  VRAM: {mem:.1f} GB")
            return True
        else:
            print("⚠ CUDA not available (CPU mode only)")
            return True  # Not a failure, just informational
    except Exception as e:
        print(f"✗ Could not check CUDA: {e}")
        return False

def test_basic_dependencies():
    """Test basic dependencies."""
    deps = {
        'numpy': 'numpy',
        'pydub': 'pydub',
        'moviepy': 'moviepy',
        'PIL': 'pillow',
        'yaml': 'pyyaml',
    }
    
    all_ok = True
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} not installed")
            all_ok = False
    
    return all_ok

def test_directory_structure():
    """Test directory structure."""
    required_dirs = [
        'src/core',
        'src/cli',
        'src/utils',
        'data/cache',
        'data/outputs',
        'Creations'
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} missing")
            all_ok = False
    
    return all_ok

def test_config_file():
    """Test config.yaml exists and is valid."""
    config_path = Path('config.yaml')
    
    if not config_path.exists():
        print("✗ config.yaml not found")
        return False
    
    print("✓ config.yaml exists")
    
    try:
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check key sections
        required = ['tts', 'music', 'storage']
        for key in required:
            if key in config:
                print(f"  ✓ {key} section found")
            else:
                print(f"  ✗ {key} section missing")
                return False
        
        # Show current engines
        print(f"\n  Current Configuration:")
        print(f"    TTS engine: {config.get('tts', {}).get('engine', 'N/A')}")
        print(f"    Music engine: {config.get('music', {}).get('engine', 'N/A')}")
        print(f"    Avatar engine: {config.get('avatar', {}).get('engine', 'none')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error reading config: {e}")
        return False

def test_example_scripts():
    """Test if example scripts exist."""
    examples = list(Path('Creations').glob('*.txt'))
    
    if examples:
        print(f"✓ Found {len(examples)} example scripts:")
        for ex in examples[:5]:
            print(f"  - {ex.name}")
        return True
    else:
        print("✗ No example scripts found in Creations/")
        return False

def test_tts_basic():
    """Test basic TTS (gTTS) functionality."""
    print("Testing basic TTS (gTTS - requires internet)...")
    
    try:
        from gtts import gTTS
        
        # Try to create a short audio
        test_text = "Hello, this is a test."
        output_path = Path('data/cache/test_tts.mp3')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        tts = gTTS(text=test_text, lang='en', tld='co.uk')
        tts.save(str(output_path))
        
        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"✓ TTS test successful")
            print(f"  Generated: {output_path}")
            # Clean up
            output_path.unlink()
            return True
        else:
            print("✗ TTS generated empty file")
            return False
            
    except ImportError:
        print("✗ gTTS not installed")
        print("  Install: pip install gTTS")
        return False
    except Exception as e:
        print(f"✗ TTS test failed: {e}")
        return False

def test_coqui_available():
    """Test if Coqui TTS is available."""
    try:
        import TTS
        print(f"✓ Coqui TTS installed (version {TTS.__version__})")
        return True
    except ImportError:
        print("⚠ Coqui TTS not installed (GPU TTS unavailable)")
        print("  Install: pip install TTS")
        return True  # Not required for basic functionality

def test_audiocraft_available():
    """Test if AudioCraft is available."""
    try:
        import audiocraft
        print("✓ AudioCraft installed (GPU music generation available)")
        return True
    except ImportError:
        print("⚠ AudioCraft not installed (GPU music unavailable)")
        print("  Install: pip install audiocraft")
        return True  # Not required for basic functionality

def test_gpu_utils():
    """Test GPU utilities."""
    try:
        sys.path.insert(0, str(Path.cwd()))
        from src.utils.gpu_utils import get_gpu_manager
        
        gpu_mgr = get_gpu_manager()
        
        print(f"Device: {gpu_mgr.device}")
        print(f"GPU Available: {gpu_mgr.gpu_available}")
        
        if gpu_mgr.gpu_available:
            print(f"GPU Name: {gpu_mgr.gpu_name}")
            print(f"GPU Memory: {gpu_mgr.gpu_memory:.1f} GB")
        
        return True
        
    except Exception as e:
        print(f"✗ GPU utils error: {e}")
        return False

def test_cli_module():
    """Test if CLI module is accessible."""
    try:
        # Try importing the main CLI module
        sys.path.insert(0, str(Path.cwd()))
        from src.cli import main
        print("✓ CLI module accessible")
        return True
    except ImportError as e:
        print(f"✗ CLI module import error: {e}")
        return False

def main():
    """Run all tests."""
    print_section("AI PODCAST CREATOR - COMPLETE SETUP TEST")
    
    print("This script tests your setup following our documentation.")
    print("Run from: AI_Podcast_Creator directory")
    print()
    
    # Track results
    results = {}
    
    # Core tests
    print_section("1. PYTHON & ENVIRONMENT")
    results['python'] = run_test("Python Version", test_python_version)
    results['pytorch'] = run_test("PyTorch Installation", test_pytorch_installed)
    results['cuda'] = run_test("CUDA/GPU Detection", test_cuda_available)
    results['deps'] = run_test("Basic Dependencies", test_basic_dependencies)
    
    # Structure tests
    print_section("2. PROJECT STRUCTURE")
    results['dirs'] = run_test("Directory Structure", test_directory_structure)
    results['config'] = run_test("Configuration File", test_config_file)
    results['examples'] = run_test("Example Scripts", test_example_scripts)
    
    # Module tests
    print_section("3. CORE MODULES")
    results['gpu_utils'] = run_test("GPU Utilities", test_gpu_utils)
    results['cli'] = run_test("CLI Module", test_cli_module)
    
    # Feature tests
    print_section("4. TTS FEATURES")
    results['tts_basic'] = run_test("Basic TTS (gTTS)", test_tts_basic)
    results['coqui'] = run_test("Coqui TTS (GPU)", test_coqui_available)
    
    # Optional features
    print_section("5. OPTIONAL GPU FEATURES")
    results['audiocraft'] = run_test("AudioCraft (Music)", test_audiocraft_available)
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print()
    
    # Categorize results
    critical = ['python', 'pytorch', 'deps', 'dirs', 'config']
    basic = ['tts_basic', 'cli']
    optional = ['cuda', 'coqui', 'audiocraft']
    
    critical_ok = all(results.get(k, False) for k in critical)
    basic_ok = all(results.get(k, False) for k in basic)
    
    if critical_ok and basic_ok:
        print("✅ CORE FUNCTIONALITY: READY")
        print("   You can create podcasts with basic features!")
        print()
    else:
        print("❌ CORE FUNCTIONALITY: NOT READY")
        print("   Fix the errors above before proceeding.")
        print()
    
    if results.get('cuda', False) and results.get('coqui', False) and results.get('audiocraft', False):
        print("✅ GPU ACCELERATION: FULLY READY")
        print("   All GPU features available!")
    elif results.get('cuda', False):
        print("⚠ GPU ACCELERATION: PARTIALLY READY")
        print("   GPU detected but missing packages:")
        if not results.get('coqui', False):
            print("   - Install Coqui TTS: pip install TTS")
        if not results.get('audiocraft', False):
            print("   - Install AudioCraft: pip install audiocraft")
    else:
        print("⚠ GPU ACCELERATION: NOT AVAILABLE")
        print("   CPU mode only (slower but functional)")
    
    print()
    print_section("NEXT STEPS")
    
    if critical_ok and basic_ok:
        print("1. ✅ Core setup complete!")
        print()
        print("2. Test basic generation:")
        print("   python -m src.cli.main create Creations/example_welcome.txt")
        print()
        
        if not results.get('coqui', False) or not results.get('audiocraft', False):
            print("3. (Optional) Enable GPU features:")
            print("   pip install TTS audiocraft")
            print("   Then edit config.yaml to enable GPU engines")
            print("   See: QUICK_GPU_SETUP.md")
        else:
            print("3. Enable GPU features:")
            print("   Edit config.yaml:")
            print("     - Change tts.engine to 'coqui'")
            print("     - Change music.engine to 'musicgen'")
            print("   See: QUICK_GPU_SETUP.md")
        print()
        print("4. Read documentation:")
        print("   - START_HERE_GPU.md (GPU setup)")
        print("   - README.md (full documentation)")
    else:
        print("1. Fix the failed tests above")
        print("2. Install missing dependencies:")
        print("   pip install -r requirements.txt")
        print("3. Run this test again")
    
    print()
    print("="*70)
    
    return critical_ok and basic_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


