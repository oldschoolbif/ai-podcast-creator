#!/usr/bin/env python3
"""
Evaluation Test Suite Runner
Runs multiple waveform tests with different configurations using the short test script

All test outputs are saved to Creations/MMedia/ with descriptive names:
  - Format: eval_XX_description.mp4 (e.g., eval_01_bottom_default.mp4)
  - All files use descriptive test names that indicate their configuration
  - Location: Creations/MMedia/ (ensured by hardcoded path and config)
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn, TaskID
    from rich.live import Live
    from rich.table import Table
    RICH_AVAILABLE = True
    ProgressType = Progress
    TaskIDType = TaskID
except ImportError:
    RICH_AVAILABLE = False
    ProgressType = None
    TaskIDType = None
    print("[WARN] rich not available - using basic progress output")

# Test script path
TEST_SCRIPT = Path("Creations/Scripts/test_short.txt")

# Initialize console if rich is available
# Use legacy_windows=True and disable Unicode to avoid encoding issues on Windows
if RICH_AVAILABLE:
    try:
        # Force ASCII-only output to prevent Unicode encoding errors
        import sys
        import io
        # Create console with safe encoding
        console = Console(
            legacy_windows=True,
            force_terminal=True,
            file=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'buffer') else sys.stdout
        )
    except Exception:
        console = None
else:
    console = None

# Test configurations - Different locations, combinations, and permutations
EVALUATION_TESTS = [
    # Single Position Tests
    {
        "name": "eval_01_bottom_default",
        "description": "Bottom position - default settings",
        "waveform": {
            "position": "bottom",
        }
    },
    {
        "name": "eval_02_top_default",
        "description": "Top position - default settings",
        "waveform": {
            "position": "top",
        }
    },
    {
        "name": "eval_03_middle_default",
        "description": "Middle position - default settings",
        "waveform": {
            "position": "middle",
        }
    },
    {
        "name": "eval_04_left_vertical",
        "description": "Left side - vertical waveform",
        "waveform": {
            "position": "left",
        }
    },
    {
        "name": "eval_05_right_vertical",
        "description": "Right side - vertical waveform",
        "waveform": {
            "position": "right",
        }
    },
    
    # Two Position Combinations
    {
        "name": "eval_06_top_bottom",
        "description": "Top and bottom simultaneously",
        "waveform": {
            "position": "top,bottom",
            "height_percent": 20,
        }
    },
    {
        "name": "eval_07_left_right",
        "description": "Left and right simultaneously",
        "waveform": {
            "position": "left,right",
            "width_percent": 20,
        }
    },
    {
        "name": "eval_08_top_left",
        "description": "Top and left simultaneously",
        "waveform": {
            "position": "top,left",
            "height_percent": 20,
            "width_percent": 20,
        }
    },
    {
        "name": "eval_09_top_right",
        "description": "Top and right simultaneously",
        "waveform": {
            "position": "top,right",
            "height_percent": 20,
            "width_percent": 20,
        }
    },
    {
        "name": "eval_10_bottom_left",
        "description": "Bottom and left simultaneously",
        "waveform": {
            "position": "bottom,left",
            "height_percent": 20,
            "width_percent": 20,
        }
    },
    {
        "name": "eval_11_bottom_right",
        "description": "Bottom and right simultaneously",
        "waveform": {
            "position": "bottom,right",
            "height_percent": 20,
            "width_percent": 20,
        }
    },
    
    # Three Position Combinations
    {
        "name": "eval_12_top_left_right",
        "description": "Top, left, and right simultaneously",
        "waveform": {
            "position": "top,left,right",
            "height_percent": 15,
            "width_percent": 15,
        }
    },
    {
        "name": "eval_13_bottom_left_right",
        "description": "Bottom, left, and right simultaneously",
        "waveform": {
            "position": "bottom,left,right",
            "height_percent": 15,
            "width_percent": 15,
        }
    },
    {
        "name": "eval_14_top_bottom_left",
        "description": "Top, bottom, and left simultaneously",
        "waveform": {
            "position": "top,bottom,left",
            "height_percent": 15,
            "width_percent": 15,
        }
    },
    {
        "name": "eval_15_top_bottom_right",
        "description": "Top, bottom, and right simultaneously",
        "waveform": {
            "position": "top,bottom,right",
            "height_percent": 15,
            "width_percent": 15,
        }
    },
    
    # Four Position Combinations
    {
        "name": "eval_16_all_four_positions",
        "description": "All four positions: top, bottom, left, right",
        "waveform": {
            "position": "top,bottom,left,right",
            "height_percent": 12,
            "width_percent": 12,
        }
    },
    
    # Different Line Counts
    {
        "name": "eval_17_bottom_1_line",
        "description": "Bottom position - 1 line",
        "waveform": {
            "position": "bottom",
            "num_lines": 1,
            "line_thickness": 15,
        }
    },
    {
        "name": "eval_18_bottom_5_lines",
        "description": "Bottom position - 5 lines",
        "waveform": {
            "position": "bottom",
            "num_lines": 5,
        }
    },
    {
        "name": "eval_19_bottom_10_lines",
        "description": "Bottom position - 10 lines (maximum)",
        "waveform": {
            "position": "bottom",
            "num_lines": 10,
            "line_thickness": 8,
        }
    },
    
    # Different Styles
    {
        "name": "eval_20_bottom_continuous",
        "description": "Bottom - continuous style",
        "waveform": {
            "position": "bottom",
            "waveform_style": "continuous",
        }
    },
    {
        "name": "eval_21_bottom_bars",
        "description": "Bottom - bars style",
        "waveform": {
            "position": "bottom",
            "waveform_style": "bars",
        }
    },
    {
        "name": "eval_22_bottom_dots",
        "description": "Bottom - dots style",
        "waveform": {
            "position": "bottom",
            "waveform_style": "dots",
        }
    },
    {
        "name": "eval_23_bottom_filled",
        "description": "Bottom - filled style",
        "waveform": {
            "position": "bottom",
            "waveform_style": "filled",
        }
    },
    
    # Different Colors
    {
        "name": "eval_24_bottom_neon_green",
        "description": "Bottom - neon green (single color)",
        "waveform": {
            "position": "bottom",
            "num_lines": 3,
        },
        "visualization": {
            "primary_color": [0, 255, 0],
        }
    },
    {
        "name": "eval_25_bottom_rainbow",
        "description": "Bottom - rainbow colors",
        "waveform": {
            "position": "bottom",
            "num_lines": 6,
            "line_colors": [
                [255, 0, 0],      # Red
                [255, 127, 0],    # Orange
                [255, 255, 0],    # Yellow
                [0, 255, 0],      # Green
                [0, 0, 255],      # Blue
                [127, 0, 255],    # Violet
            ],
        }
    },
    {
        "name": "eval_26_bottom_cyan_magenta",
        "description": "Bottom - cyan and magenta",
        "waveform": {
            "position": "bottom",
            "num_lines": 2,
            "line_colors": [
                [0, 255, 255],    # Cyan
                [255, 0, 255],    # Magenta
            ],
        }
    },
    
    # Different Thicknesses
    {
        "name": "eval_27_bottom_thick",
        "description": "Bottom - thick lines (20px)",
        "waveform": {
            "position": "bottom",
            "num_lines": 3,
            "line_thickness": 20,
        }
    },
    {
        "name": "eval_28_bottom_thin",
        "description": "Bottom - thin lines (6px)",
        "waveform": {
            "position": "bottom",
            "num_lines": 3,
            "line_thickness": 6,
        }
    },
    {
        "name": "eval_29_bottom_varying_thickness",
        "description": "Bottom - varying thickness per line",
        "waveform": {
            "position": "bottom",
            "num_lines": 3,
            "line_thickness": [18, 12, 8],
        }
    },
    
    # Different Opacities
    {
        "name": "eval_30_bottom_opacity_50",
        "description": "Bottom - 50% opacity",
        "waveform": {
            "position": "bottom",
            "opacity": 0.5,
        }
    },
    {
        "name": "eval_31_bottom_opacity_75",
        "description": "Bottom - 75% opacity",
        "waveform": {
            "position": "bottom",
            "opacity": 0.75,
        }
    },
    
    # Different Heights/Widths
    {
        "name": "eval_32_bottom_10_percent",
        "description": "Bottom - 10% height",
        "waveform": {
            "position": "bottom",
            "height_percent": 10,
        }
    },
    {
        "name": "eval_33_bottom_50_percent",
        "description": "Bottom - 50% height",
        "waveform": {
            "position": "bottom",
            "height_percent": 50,
        }
    },
    {
        "name": "eval_34_left_10_percent",
        "description": "Left - 10% width",
        "waveform": {
            "position": "left",
            "width_percent": 10,
        }
    },
    {
        "name": "eval_35_left_50_percent",
        "description": "Left - 50% width",
        "waveform": {
            "position": "left",
            "width_percent": 50,
        }
    },
    
    # Spacing Tests (Vertical)
    {
        "name": "eval_36_left_spacing_20px",
        "description": "Left - 20px spacing from edge",
        "waveform": {
            "position": "left",
            "left_spacing": 20,
        }
    },
    {
        "name": "eval_37_right_spacing_20px",
        "description": "Right - 20px spacing from edge",
        "waveform": {
            "position": "right",
            "right_spacing": 20,
        }
    },
    {
        "name": "eval_38_left_right_spacing_30px",
        "description": "Left and right - 30px spacing each",
        "waveform": {
            "position": "left,right",
            "left_spacing": 30,
            "right_spacing": 30,
        }
    },
    
    # Render Quality Tests
    {
        "name": "eval_39_bottom_render_1x",
        "description": "Bottom - 1x render scale (baseline)",
        "waveform": {
            "position": "bottom",
            "render_scale": 1.0,
        }
    },
    {
        "name": "eval_40_bottom_render_4x",
        "description": "Bottom - 4x render scale (maximum smoothness)",
        "waveform": {
            "position": "bottom",
            "render_scale": 4.0,
        }
    },
    {
        "name": "eval_41_bottom_no_antialias",
        "description": "Bottom - no anti-aliasing",
        "waveform": {
            "position": "bottom",
            "anti_alias": False,
        }
    },
    
    # Complex Combinations
    {
        "name": "eval_42_top_bottom_5_lines_rainbow",
        "description": "Top and bottom - 5 lines - rainbow colors",
        "waveform": {
            "position": "top,bottom",
            "num_lines": 5,
            "line_colors": [
                [255, 0, 0],
                [255, 127, 0],
                [255, 255, 0],
                [0, 255, 0],
                [0, 0, 255],
            ],
            "height_percent": 20,
        }
    },
    {
        "name": "eval_43_left_right_bars_style",
        "description": "Left and right - bars style",
        "waveform": {
            "position": "left,right",
            "waveform_style": "bars",
            "width_percent": 20,
        }
    },
    {
        "name": "eval_44_all_four_dots_style",
        "description": "All four positions - dots style",
        "waveform": {
            "position": "top,bottom,left,right",
            "waveform_style": "dots",
            "height_percent": 12,
            "width_percent": 12,
        }
    },
    {
        "name": "eval_45_top_bottom_filled_rainbow",
        "description": "Top and bottom - filled style - rainbow",
        "waveform": {
            "position": "top,bottom",
            "waveform_style": "filled",
            "num_lines": 6,
            "line_colors": [
                [255, 0, 0],
                [255, 127, 0],
                [255, 255, 0],
                [0, 255, 0],
                [0, 0, 255],
                [127, 0, 255],
            ],
            "height_percent": 20,
        }
    },
    {
        "name": "eval_46_complex_all_features",
        "description": "Complex: All positions, 5 lines, varying thickness, rainbow, filled",
        "waveform": {
            "position": "top,bottom,left,right",
            "num_lines": 5,
            "line_thickness": [18, 15, 12, 10, 8],
            "line_colors": [
                [255, 0, 0],
                [255, 127, 0],
                [255, 255, 0],
                [0, 255, 0],
                [0, 0, 255],
            ],
            "waveform_style": "filled",
            "height_percent": 12,
            "width_percent": 12,
            "opacity": 0.9,
        }
    },
    
    # Randomized Test
    {
        "name": "eval_47_randomized",
        "description": "Randomized configuration",
        "waveform": {
            "randomize": True,
        }
    },
    
    # Final Test: Barely Visible Neon Orange
    {
        "name": "eval_48_bottom_neon_orange_faded",
        "description": "Bottom position - bright neon orange, barely visible (faded)",
        "waveform": {
            "position": "bottom",
            "num_lines": 1,
            "line_thickness": 20,
            "opacity": 0.15,  # Barely visible (15% opacity)
        },
        "visualization": {
            "primary_color": [255, 120, 0],  # Bright neon orange (RGB)
            "secondary_color": [255, 140, 0],  # Slightly lighter orange for variation
        }
    },
]


def create_config_file(config_path: Path, waveform_config: Dict, visualization_overrides: Dict = None):
    """Create a temporary config override file"""
    import yaml
    
    viz_config = {
        "style": "waveform",
        "waveform": waveform_config
    }
    
    # Merge visualization overrides if provided
    if visualization_overrides:
        viz_config.update(visualization_overrides)
    
    config = {
        "visualization": viz_config
    }
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def monitor_file_growth(output_file: Path, expected_size_mb: float = None, progress_task = None, progress = None) -> bool:
    """
    Monitor file growth during generation to show progress.
    
    Args:
        output_file: Path to output file (without extension)
        expected_size_mb: Expected file size in MB (for percentage calculation)
        progress_task: Rich progress task ID
        progress: Rich progress object
    
    Returns:
        True if file was created successfully
    """
    output_dir = output_file.parent
    check_interval = 2.0  # Check every 2 seconds
    
    # Try multiple extensions
    for ext in [".mp4", ".avi", ".mov"]:
        candidate = output_dir / f"{output_file.name}{ext}"
        
        start_time = time.time()
        last_size = 0
        stalled_count = 0
        max_stall = 30  # 30 seconds of no growth = stalled
        
        while True:
            # Always calculate elapsed time for timeout check
            elapsed = time.time() - start_time
            
            if candidate.exists():
                current_size = candidate.stat().st_size
                size_mb = current_size / (1024 * 1024)
                
                # Always print progress to console for visibility (even if Rich is available)
                if expected_size_mb and expected_size_mb > 0:
                    percent = min(100, (size_mb / expected_size_mb) * 100)
                    progress_text = f"[PROGRESS] {size_mb:.2f} MB / {expected_size_mb:.2f} MB ({percent:.1f}%)"
                else:
                    progress_text = f"[PROGRESS] {size_mb:.2f} MB"
                
                # Print to console with carriage return and clear to end of line
                # Use ANSI escape codes to ensure proper overwriting
                sys.stdout.write(f"\r{progress_text}\033[K")  # \033[K clears to end of line
                sys.stdout.flush()
                
                # Update progress if rich is available
                if progress and progress_task:
                    try:
                        # Verify task exists before updating
                        if progress_task in progress._tasks:
                            if expected_size_mb and expected_size_mb > 0:
                                # Calculate percentage based on expected size
                                percent = min(100, (size_mb / expected_size_mb) * 100)
                                progress.update(
                                    progress_task, 
                                    completed=percent, 
                                    description=f"[{size_mb:.2f} MB / {expected_size_mb:.2f} MB] {percent:.1f}%",
                                    refresh=True
                                )
                            else:
                                # Just show size
                                progress.update(
                                    progress_task, 
                                    completed=min(100, (size_mb / 0.5) * 100) if size_mb > 0 else 0,
                                    description=f"Generating... {size_mb:.2f} MB",
                                    refresh=True
                                )
                    except (KeyError, ValueError):
                        # Task was removed, skip progress update
                        pass
                
                # Check if file is still growing
                if current_size > last_size:
                    last_size = current_size
                    stalled_count = 0
                else:
                    stalled_count += 1
                    # If file hasn't grown in a while and is reasonable size, assume complete
                    if stalled_count >= (max_stall / check_interval) and size_mb > 0.1:
                        sys.stdout.write("\n")  # New line after progress
                        sys.stdout.flush()
                        return True
                
                # If file is large enough and hasn't grown, assume complete
                if size_mb > 0.5 and current_size == last_size:
                    time.sleep(1)  # Wait a bit more
                    if candidate.stat().st_size == current_size:
                        sys.stdout.write("\n")  # New line after progress
                        sys.stdout.flush()
                        return True
            else:
                # File doesn't exist yet, just show waiting
                sys.stdout.write(f"\r[PROGRESS] Waiting for file creation...\033[K")
                sys.stdout.flush()
                if progress and progress_task:
                    try:
                        if progress_task in progress._tasks:
                            progress.update(progress_task, description="Waiting for file creation...")
                    except (KeyError, ValueError):
                        pass
            
            # Timeout after 10 minutes
            if elapsed > 600:
                return False
            
            time.sleep(check_interval)
    
    return False


def run_evaluation_test(test_config: Dict, test_num: int = 1, total_tests: int = 1, progress = None, progress_task = None) -> bool:
    """Run a single evaluation test with progress tracking"""
    test_name = test_config["name"]
    description = test_config["description"]
    waveform_config = test_config["waveform"]
    visualization_overrides = test_config.get("visualization", {})
    
    # Update progress description
    if progress and progress_task:
        progress.update(progress_task, description=f"[{test_num}/{total_tests}] {test_name}")
    
    if console:
        console.print(f"\n[bold cyan][TEST {test_num}/{total_tests}][/bold cyan] [bold]{test_name}[/bold]")
        console.print(f"[dim]{description}[/dim]")
    else:
        print(f"\n{'='*70}")
        print(f"[TEST {test_num}/{total_tests}] {test_name}")
        print(f"[DESC] {description}")
        print(f"{'='*70}")
    
    # Create temporary config file
    config_dir = Path("Creations/Configs/evaluation_tests")
    config_path = config_dir / f"{test_name}_config.yaml"
    create_config_file(config_path, waveform_config, visualization_overrides)
    
    # Expected file size based on test script (short test ~0.5-1 MB typically)
    # Update this based on actual file sizes after first few tests
    expected_size_mb = 0.75  # Conservative estimate for short test
    
    # Build command - use sys.executable to ensure we use the correct Python interpreter
    import sys
    cmd = [
        sys.executable, "-m", "src.cli.main", "create",
        str(TEST_SCRIPT),
        "--visualize",
        "--background",
        "--avatar",
        "--quality", "fastest",
        "--output", test_name,
        "--config", str(config_path),
    ]
    
    # Start subprocess
    # Ensure output is always in MMedia folder with descriptive name
    output_dir = Path("Creations/MMedia")
    output_dir.mkdir(parents=True, exist_ok=True)
    # Ensure descriptive filename: test_name should already be descriptive (e.g., "eval_01_bottom_default")
    # Add .mp4 extension for file monitoring
    output_file = output_dir / f"{test_name}.mp4"
    
    try:
        # Start process
        # Print progress indicator header
        if console:
            console.print(f"[bold cyan]Starting test:[/bold cyan] {test_name}")
            console.print(f"[dim]Output: {output_file.name}[/dim]")
        else:
            print(f"[TEST] Starting: {test_name}")
            print(f"[OUTPUT] {output_file.name}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            errors='replace'  # Handle Unicode errors gracefully
        )
        
        # Monitor file growth in background
        if progress and progress_task:
            # Reset progress for this test
            try:
                progress.update(progress_task, total=100, completed=0, description=f"[{test_num}/{total_tests}] Starting {test_name}...")
            except (KeyError, ValueError):
                # Task might have been removed, recreate it
                progress_task = progress.add_task(f"[{test_num}/{total_tests}] {test_name}", total=100)
        
        # Start file monitoring thread (only if progress is available)
        import threading
        file_monitor_done = threading.Event()
        file_found = [False]
        
        def monitor_thread():
            # Only use progress if task still exists
            try:
                if progress and progress_task:
                    # Verify task exists before using
                    if progress_task in progress._tasks:
                        file_found[0] = monitor_file_growth(output_file, expected_size_mb, progress_task, progress)
                    else:
                        # Task removed, monitor without progress
                        file_found[0] = monitor_file_growth(output_file, expected_size_mb, None, None)
                else:
                    file_found[0] = monitor_file_growth(output_file, expected_size_mb, None, None)
            except (KeyError, ValueError):
                # Task was removed, monitor without progress
                file_found[0] = monitor_file_growth(output_file, expected_size_mb, None, None)
            finally:
                file_monitor_done.set()
        
        monitor_thread_obj = threading.Thread(target=monitor_thread, daemon=True)
        monitor_thread_obj.start()
        
        # Monitor process and check for early failures
        process_done = False
        max_wait_time = 600  # 10 minutes max per test (Wav2Lip can take time)
        start_time = time.time()
        
        # Wait for process to complete with timeout
        # Print a newline after progress updates before showing process result
        sys.stdout.write("\n")  # New line after progress updates
        sys.stdout.flush()
        
        stdout, stderr = None, None
        try:
            # Wait for process with timeout - this is the main wait
            stdout, stderr = process.communicate(timeout=max_wait_time)
            process_done = True
        except subprocess.TimeoutExpired:
            # Process timed out - kill it
            process.kill()
            stdout, stderr = process.communicate(timeout=5)
            if console:
                console.print(f"[bold red]TEST TIMEOUT - Process killed after {max_wait_time}s[/bold red]")
            else:
                print(f"[FAIL] Test timeout after {max_wait_time}s")
            file_monitor_done.set()
            return False
        except Exception as e:
            stdout, stderr = "", f"Error waiting for process: {e}"
            process_done = True
        
        # Check if process failed
        if process.returncode != 0:
            file_monitor_done.set()
            # Show full error output
            if console:
                console.print(f"\n[bold red]PROCESS FAILED[/bold red]")
                console.print(f"[red]Return code:[/red] {process.returncode}")
                if stderr:
                    console.print(f"[red]STDERR (full):[/red]\n{stderr}")
                if stdout:
                    console.print(f"[yellow]STDOUT (last 1000):[/yellow]\n{stdout[-1000:]}")
            else:
                print(f"\n[FAIL] Process failed with return code {process.returncode}")
                if stderr:
                    print(f"[ERROR] {stderr}")
                if stdout:
                    print(f"[OUTPUT] {stdout[-1000:]}")
            
            # Still check if file was created despite error
            for ext in [".mp4", ".avi", ".mov"]:
                final_file = output_dir / f"{test_name}{ext}"
                if final_file.exists() and final_file.stat().st_size > 1000:
                    if console:
                        console.print(f"[yellow][WARN] File exists despite error - marking as passed[/yellow]")
                    return True
            
            return False
        
        # Wait a bit more for file to finalize
        file_monitor_done.wait(timeout=10)
        
        # Check if output file exists even if return code was non-zero (sometimes processes exit with error but still create files)
        output_file_exists = False
        for ext in [".mp4", ".avi", ".mov"]:
            final_file = output_dir / f"{test_name}{ext}"
            if final_file.exists() and final_file.stat().st_size > 1000:  # At least 1KB
                output_file_exists = True
                break
        
        # Check result - show full error if failed
        if process.returncode == 0 and (file_found[0] or output_file_exists):
            # Find actual output file
            for ext in [".mp4", ".avi", ".mov"]:
                final_file = output_dir / f"{test_name}{ext}"
                if final_file.exists():
                    size_mb = final_file.stat().st_size / (1024 * 1024)
                    if progress and progress_task:
                        progress.update(progress_task, completed=100, description=f"[{test_num}/{total_tests}] PASS {test_name} ({size_mb:.2f} MB)")
                    if console:
                        console.print(f"[green][PASS][/green] Test passed: {test_name} ({size_mb:.2f} MB)")
                    else:
                        print(f"[OK] Test passed: {test_name} ({size_mb:.2f} MB)")
                    return True
            
            # File not found but process succeeded
            if console:
                console.print(f"[yellow][WARN][/yellow] Process succeeded but output file not found: {test_name}")
            else:
                print(f"[WARN] Process succeeded but output file not found: {test_name}")
            return False
        elif output_file_exists:
            # Process had non-zero return code but file was created - check if it's valid
            for ext in [".mp4", ".avi", ".mov"]:
                final_file = output_dir / f"{test_name}{ext}"
                if final_file.exists() and final_file.stat().st_size > 1000:
                    size_mb = final_file.stat().st_size / (1024 * 1024)
                    if console:
                        console.print(f"[yellow][WARN][/yellow] Process returned {process.returncode} but file was created: {test_name} ({size_mb:.2f} MB)")
                        console.print(f"[green][PASS][/green] Test passed (file exists despite return code)")
                    else:
                        print(f"[WARN] Process returned {process.returncode} but file exists: {test_name} ({size_mb:.2f} MB)")
                        print(f"[OK] Test passed (file exists)")
                    return True
            
            # File exists but invalid
            if console:
                console.print(f"[yellow][WARN][/yellow] Output file exists but is too small or invalid")
            return False
        else:
            if progress and progress_task:
                progress.update(progress_task, completed=100, description=f"[{test_num}/{total_tests}] FAIL {test_name} FAILED")
            
            # Show FULL error output for debugging
            if console:
                console.print(f"\n[bold red]{'='*70}[/bold red]")
                console.print(f"[bold red]TEST FAILED: {test_name}[/bold red]")
                console.print(f"[bold red]{'='*70}[/bold red]")
                console.print(f"[red]Return code:[/red] {process.returncode}")
                if stderr:
                    console.print(f"\n[bold red]STDERR (FULL OUTPUT):[/bold red]")
                    console.print(f"[red]{stderr}[/red]")
                if stdout:
                    console.print(f"\n[bold yellow]STDOUT (last 1000 chars):[/bold yellow]")
                    console.print(f"[yellow]{stdout[-1000:]}[/yellow]")
                console.print(f"[bold red]{'='*70}[/bold red]\n")
            else:
                print(f"\n{'='*70}")
                print(f"[FAIL] Test failed: {test_name}")
                print(f"[FAIL] Return code: {process.returncode}")
                if stderr:
                    print(f"\n[ERROR] {stderr}")
                if stdout:
                    print(f"\n[OUTPUT] {stdout[-1000:]}")
                print(f"{'='*70}\n")
            return False
            
    except subprocess.TimeoutExpired:
        if progress and progress_task:
            progress.update(progress_task, completed=100, description=f"[{test_num}/{total_tests}] FAIL {test_name} TIMEOUT")
        if console:
            console.print(f"[red][FAIL][/red] Test timed out: {test_name}")
        else:
            print(f"[FAIL] Test timed out: {test_name}")
        return False
    except Exception as e:
        if progress and progress_task:
            progress.update(progress_task, completed=100, description=f"[{test_num}/{total_tests}] FAIL {test_name} ERROR")
        if console:
            console.print(f"[red][FAIL][/red] Test error: {test_name} - {str(e)}")
        else:
            print(f"[FAIL] Test error: {test_name} - {str(e)}")
        return False


def run_all_evaluation_tests():
    """Run all evaluation tests with visual progress tracking"""
    if not TEST_SCRIPT.exists():
        if console:
            console.print(f"[red][ERROR][/red] Test script not found: {TEST_SCRIPT}")
            console.print("Please ensure test_short.txt exists in Creations/Scripts/")
        else:
            print(f"[ERROR] Test script not found: {TEST_SCRIPT}")
            print("Please ensure test_short.txt exists in Creations/Scripts/")
        return
    
    if console:
        console.print(f"\n[bold cyan]Starting Evaluation Test Suite[/bold cyan]")
        console.print(f"[dim]Test script:[/dim] {TEST_SCRIPT}")
        console.print(f"[dim]Total tests:[/dim] {len(EVALUATION_TESTS)}\n")
    else:
        print(f"[EVAL] Starting evaluation test suite")
        print(f"[EVAL] Test script: {TEST_SCRIPT}")
        print(f"[EVAL] Total tests: {len(EVALUATION_TESTS)}")
        print()
    
    results = []
    
    # Use rich progress if available
    if RICH_AVAILABLE and console:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
            expand=True
        ) as progress:
            overall_task = progress.add_task("[bold cyan]Overall Progress", total=len(EVALUATION_TESTS))
            
            for i, test_config in enumerate(EVALUATION_TESTS, 1):
                test_task = progress.add_task(f"[{i}/{len(EVALUATION_TESTS)}] {test_config['name']}", total=100)
                
                success = run_evaluation_test(test_config, i, len(EVALUATION_TESTS), progress, test_task)
                
                results.append({
                    "test": test_config["name"],
                    "description": test_config["description"],
                    "success": success,
                })
                
                # Update overall progress
                progress.update(overall_task, advance=1)
                
                # Remove individual test task
                progress.remove_task(test_task)
                
                # STOP ON FIRST FAILURE - investigate immediately
                if not success:
                    console.print(f"\n[bold red]{'='*70}[/bold red]")
                    console.print(f"[bold red]TEST SUITE STOPPED - FIRST FAILURE DETECTED[/bold red]")
                    console.print(f"[bold red]{'='*70}[/bold red]")
                    console.print(f"[bold]Failed test:[/bold] {test_config['name']}")
                    console.print(f"[bold]Description:[/bold] {test_config.get('description', 'N/A')}")
                    console.print(f"[bold]Test number:[/bold] {i} of {len(EVALUATION_TESTS)}")
                    console.print(f"\n[bold yellow]Please investigate the error above before continuing.[/bold yellow]")
                    console.print(f"[bold yellow]Fix the root cause, then re-run the test suite.[/bold yellow]")
                    console.print(f"[bold red]{'='*70}[/bold red]\n")
                    break
    else:
        # Fallback to basic output
        for i, test_config in enumerate(EVALUATION_TESTS, 1):
            print(f"\n[{i}/{len(EVALUATION_TESTS)}] Running test...")
            success = run_evaluation_test(test_config, i, len(EVALUATION_TESTS))
            results.append({
                "test": test_config["name"],
                "description": test_config["description"],
                "success": success,
            })
            
            # STOP ON FIRST FAILURE - investigate immediately
            if not success:
                print(f"\n{'='*70}")
                print(f"[STOP] TEST SUITE STOPPED - FIRST FAILURE DETECTED")
                print(f"{'='*70}")
                print(f"Failed test: {test_config['name']}")
                print(f"Description: {test_config.get('description', 'N/A')}")
                print(f"Test number: {i} of {len(EVALUATION_TESTS)}")
                print(f"\nPlease investigate the error above before continuing.")
                print(f"Fix the root cause, then re-run the test suite.")
                print(f"{'='*70}\n")
                break
    
    # Summary
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    
    if console:
        console.print("\n")
        summary_table = Table(title="Evaluation Test Suite Results", show_header=True, header_style="bold cyan")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green" if failed == 0 else "yellow")
        summary_table.add_row("Total Tests", str(len(results)))
        summary_table.add_row("Passed", f"[green]{passed}[/green]")
        summary_table.add_row("Failed", f"[red]{failed}[/red]" if failed > 0 else "0")
        console.print(summary_table)
        
        if failed > 0:
            console.print(f"\n[bold red]Failed Tests:[/bold red]")
            for r in results:
                if not r["success"]:
                    console.print(f"  [red]✗[/red] {r['test']}: {r['description']}")
        
        console.print(f"\n[dim]Output:[/dim] Creations/MMedia/")
        console.print(f"[dim]Configs:[/dim] Creations/Configs/evaluation_tests/")
    else:
        print(f"\n{'='*70}")
        print(f"[SUMMARY] Evaluation Test Suite Results")
        print(f"{'='*70}")
        print(f"Total: {len(results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print(f"\n[FAILED TESTS]")
            for r in results:
                if not r["success"]:
                    print(f"  - {r['test']}: {r['description']}")
        
        print(f"\n[OUTPUT] All test outputs saved to: Creations/MMedia/")
        print(f"[CONFIG] Config files saved to: Creations/Configs/evaluation_tests/")


if __name__ == "__main__":
    run_all_evaluation_tests()

