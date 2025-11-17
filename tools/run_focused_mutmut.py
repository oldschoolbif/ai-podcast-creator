"""Run mutation testing on specific files to debug survivors."""

import subprocess
import sys
from pathlib import Path

# Target the specific files with survivors
TARGET_FILES = [
    "src/core/video_composer.py",
    "src/core/tts_engine.py",
]

def main():
    """Run mutmut on specific files."""
    project_root = Path(__file__).resolve().parent.parent
    
    # Create a temporary mutmut config that only mutates these files
    mutmut_config = project_root / "mutmut_focused.ini"
    
    with mutmut_config.open("w") as f:
        f.write("[mutmut]\n")
        f.write(f"paths_to_mutate = {TARGET_FILES}\n")
        f.write('runner = "python scripts/mutmut_pytest_wrapper.py"\n')
        f.write("use_coverage = true\n")
    
    try:
        # Run mutmut with the focused config
        cmd = [
            sys.executable,
            "-m",
            "mutmut",
            "run",
            "--config",
            str(mutmut_config),
        ]
        
        print(f"Running focused mutation test on: {', '.join(TARGET_FILES)}")
        result = subprocess.run(cmd, cwd=project_root)
        
        if result.returncode == 0:
            print("\n✅ Mutation testing completed")
            print("\nResults:")
            subprocess.run([sys.executable, "-m", "mutmut", "results"], cwd=project_root)
        else:
            print(f"\n❌ Mutation testing failed with code {result.returncode}")
            return result.returncode
        
    finally:
        # Clean up temp config
        if mutmut_config.exists():
            mutmut_config.unlink()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

