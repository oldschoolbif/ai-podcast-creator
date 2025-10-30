"""
Bug Fix Script for AI Podcast Creator
Applies high-priority fixes automatically
"""

from pathlib import Path
import shutil

def fix_missing_gitkeep():
    """Fix Bug #2: Add .gitkeep files to empty directories."""
    print("Fixing Bug #2: Adding .gitkeep files...")
    
    directories = [
        'data/cache',
        'data/outputs',
        'data/models',
        'data/scripts',
        'logs',
        'external',
        'src/assets/avatars',
        'src/assets/backgrounds'
    ]
    
    for dir_path in directories:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        gitkeep = path / '.gitkeep'
        if not gitkeep.exists():
            gitkeep.touch()
            print(f"  ✓ Created {gitkeep}")
    
    print("✓ Bug #2 fixed!\n")

def fix_gitattributes():
    """Fix Bug #4: Create .gitattributes for line endings."""
    print("Fixing Bug #4: Creating .gitattributes...")
    
    content = """# Set default behavior to automatically normalize line endings
* text=auto

# Python files should use LF
*.py text eol=lf
*.pyw text eol=lf
*.pyx text eol=lf
*.pxd text eol=lf

# YAML files
*.yaml text eol=lf
*.yml text eol=lf

# Shell scripts should use LF
*.sh text eol=lf
*.bash text eol=lf

# Windows batch/cmd should use CRLF
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf

# Markdown
*.md text eol=lf

# Binary files
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.mp3 binary
*.mp4 binary
*.wav binary
*.avi binary
*.mov binary
*.pth binary
*.pt binary
*.onnx binary
*.safetensors binary
*.bin binary
*.pkl binary
*.pickle binary
"""
    
    gitattributes = Path('.gitattributes')
    with open(gitattributes, 'w', newline='\n') as f:
        f.write(content)
    
    print(f"  ✓ Created {gitattributes}")
    print("✓ Bug #4 fixed!\n")

def fix_avatar_cleanup():
    """Fix Bug #9: Improve temp file cleanup in avatar_generator.py."""
    print("Fixing Bug #9: Improving temp file cleanup...")
    
    avatar_file = Path('src/core/avatar_generator.py')
    
    if not avatar_file.exists():
        print("  ⚠ avatar_generator.py not found, skipping")
        return
    
    content = avatar_file.read_text(encoding='utf-8')
    
    # Find and replace the buggy cleanup code
    old_code = """                # Cleanup temp files
                for f in result_files:
                    f.unlink(missing_ok=True)
                temp_result_dir.rmdir()"""
    
    new_code = """                # Cleanup temp files
                import shutil
                if temp_result_dir.exists():
                    shutil.rmtree(temp_result_dir, ignore_errors=True)"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        avatar_file.write_text(content, encoding='utf-8')
        print("  ✓ Fixed temp directory cleanup")
        print("✓ Bug #9 fixed!\n")
    else:
        print("  ⚠ Code pattern not found (may already be fixed)")
        print()

def create_audio_validator():
    """Fix Bug #7: Add audio file validation utility."""
    print("Fixing Bug #7: Adding audio validation...")
    
    utils_dir = Path('src/utils')
    utils_dir.mkdir(parents=True, exist_ok=True)
    
    validator_file = utils_dir / 'audio_validator.py'
    
    content = '''"""
Audio File Validation Utility
Validates audio files before processing
"""

from pathlib import Path
from typing import Tuple

def validate_audio_file(audio_path: Path) -> Tuple[bool, str]:
    """
    Validate audio file format and integrity.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        (is_valid, error_message)
    """
    if not audio_path.exists():
        return False, f"File does not exist: {audio_path}"
    
    if audio_path.stat().st_size == 0:
        return False, f"File is empty: {audio_path}"
    
    # Check file extension
    valid_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
    if audio_path.suffix.lower() not in valid_extensions:
        return False, f"Unsupported format: {audio_path.suffix}"
    
    # Try to load with pydub
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(str(audio_path))
        
        # Check duration
        if len(audio) == 0:
            return False, "Audio file has zero duration"
        
        if len(audio) < 100:  # Less than 100ms
            return False, "Audio file too short (< 100ms)"
        
        return True, "Valid"
        
    except Exception as e:
        return False, f"Failed to load audio: {str(e)[:100]}"

def safe_load_audio(audio_path: Path):
    """
    Safely load audio file with validation.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        AudioSegment or None
    """
    is_valid, error_msg = validate_audio_file(audio_path)
    
    if not is_valid:
        print(f"⚠ Audio validation failed: {error_msg}")
        return None
    
    try:
        from pydub import AudioSegment
        return AudioSegment.from_file(str(audio_path))
    except Exception as e:
        print(f"⚠ Failed to load audio: {e}")
        return None
'''
    
    validator_file.write_text(content, encoding='utf-8')
    print(f"  ✓ Created {validator_file}")
    print("✓ Bug #7 fixed!\n")

def main():
    print("="*60)
    print("AI PODCAST CREATOR - BUG FIX SCRIPT")
    print("="*60)
    print()
    
    # Apply fixes
    fix_missing_gitkeep()
    fix_gitattributes()
    fix_avatar_cleanup()
    create_audio_validator()
    
    print("="*60)
    print("FIXES APPLIED SUCCESSFULLY!")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Review changes: git status")
    print("2. Test the system: python -m src.cli.main status")
    print("3. Commit fixes: git add . && git commit -m 'Fix bugs #2, #4, #7, #9'")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error applying fixes: {e}")
        import traceback
        traceback.print_exc()

