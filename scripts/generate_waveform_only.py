"""
Generate waveform visualization video only (no composition)
Useful for debugging waveform quality and chromakey blending issues

TODO: Add progress indicator for waveform generation (spinner/progress bar)
"""
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.audio_visualizer import AudioVisualizer
from src.core.tts_engine import TTSEngine
from src.utils.config import load_config
import typer

app = typer.Typer()


def _apply_waveform_cli_overrides(
    config: dict,
    position: Optional[str],
    num_lines: Optional[int],
    thickness: Optional[str],
    colors: Optional[str],
    style: Optional[str],
    opacity: Optional[float],
    randomize: bool,
    height_percent: Optional[int],
    width_percent: Optional[int],
    left_spacing: Optional[int],
    right_spacing: Optional[int],
    render_scale: Optional[float],
    anti_alias: Optional[bool],
    orientation_offset: Optional[float],
    rotation: Optional[float],
    amplitude_multiplier: Optional[float],
    num_instances: Optional[int],
    instances_offset: Optional[int],
    instances_intersect: Optional[bool],
) -> dict:
    """Apply waveform CLI parameter overrides to config"""
    if "visualization" not in config:
        config["visualization"] = {}
    if "waveform" not in config["visualization"]:
        config["visualization"]["waveform"] = {}
    
    waveform_config = config["visualization"]["waveform"]
    
    if position is not None:
        waveform_config["position"] = position
    if num_lines is not None:
        waveform_config["num_lines"] = max(1, min(10, num_lines))
    if thickness is not None:
        # Parse thickness: single number or comma-separated list
        try:
            if "," in thickness:
                waveform_config["line_thickness"] = [int(t.strip()) for t in thickness.split(",")]
            else:
                waveform_config["line_thickness"] = int(thickness)
        except ValueError:
            print(f"[WARN] Invalid thickness format: {thickness}, using default")
    if colors is not None:
        # Parse colors: comma-separated RGB tuples separated by colons
        # Format: "r1,g1,b1:r2,g2,b2:r3,g3,b3"
        try:
            color_list = []
            for color_str in colors.split(":"):
                rgb = [int(c.strip()) for c in color_str.split(",")]
                if len(rgb) == 3 and all(0 <= c <= 255 for c in rgb):
                    color_list.append(rgb)
            if color_list:
                waveform_config["line_colors"] = color_list
        except (ValueError, IndexError):
            print(f"[WARN] Invalid colors format: {colors}, using default")
    if style is not None:
        if style in ["continuous", "bars", "dots", "filled"]:
            waveform_config["waveform_style"] = style
        else:
            print(f"[WARN] Invalid style: {style}, using 'continuous'")
    if opacity is not None:
        waveform_config["opacity"] = max(0.0, min(1.0, opacity))
    if randomize:
        waveform_config["randomize"] = True
    if height_percent is not None:
        waveform_config["height_percent"] = max(10, min(100, height_percent))  # Allow up to 100% for full height
    if width_percent is not None:
        waveform_config["width_percent"] = max(10, min(100, width_percent))  # Allow up to 100% for full width
    if left_spacing is not None:
        waveform_config["left_spacing"] = max(0, left_spacing)
    if right_spacing is not None:
        waveform_config["right_spacing"] = max(0, right_spacing)
    if render_scale is not None:
        waveform_config["render_scale"] = max(1.0, min(4.0, render_scale))
    if anti_alias is not None:
        waveform_config["anti_alias"] = anti_alias
    if orientation_offset is not None:
        waveform_config["orientation_offset"] = max(0.0, min(100.0, float(orientation_offset)))
    if rotation is not None:
        waveform_config["rotation"] = float(rotation)  # Allow any angle
    if amplitude_multiplier is not None:
        waveform_config["amplitude_multiplier"] = max(0.1, float(amplitude_multiplier))  # Minimum 0.1
    if num_instances is not None:
        waveform_config["num_instances"] = max(1, int(num_instances))
    if instances_offset is not None:
        waveform_config["instances_offset"] = max(0, int(instances_offset))
    if instances_intersect is not None:
        waveform_config["instances_intersect"] = bool(instances_intersect)
    
    return config


def monitor_waveform_file_growth(output_file: Path) -> bool:
    """
    Monitor file growth during waveform generation with spinning indicator.
    Shows ASCII spinning animation that only moves when file size is increasing.
    
    Args:
        output_file: Path to output file (with .mp4 extension)
    
    Returns:
        True if file was created successfully
    """
    check_interval = 0.3  # Check every 0.3 seconds for smooth animation
    start_time = time.time()
    last_size = 0
    stalled_count = 0
    max_stall = 30  # 30 seconds of no growth = stalled
    file_found = False
    
    # ASCII spinning characters
    spinner_chars = "|/-\\"
    spinner_idx = 0
    last_growth_time = 0
    spinner_update_time = 0
    
    # Wait a bit for file to be created (up to 10 seconds)
    wait_start = time.time()
    while (time.time() - wait_start) < 10:
        if output_file.exists():
            file_found = True
            break
        time.sleep(0.5)
    
    while True:
        elapsed = time.time() - start_time
        current_time = time.time()
        
        if output_file.exists():
            file_found = True
            current_size = output_file.stat().st_size
            
            # Check if file is growing
            if current_size > last_size:
                last_size = current_size
                stalled_count = 0
                last_growth_time = current_time
            else:
                stalled_count += 1
                # If file hasn't grown in a while and is reasonable size, assume complete
                size_mb = current_size / (1024 * 1024)
                if stalled_count >= (max_stall / check_interval) and size_mb > 0.1:
                    sys.stdout.write("\r[OK] Waveform generation complete\n")
                    sys.stdout.flush()
                    return True
            
            # If file is large enough and hasn't grown, assume complete
            size_mb = current_size / (1024 * 1024)
            if size_mb > 0.5 and current_size == last_size:
                time.sleep(1)  # Wait a bit more
                if output_file.stat().st_size == current_size:
                    sys.stdout.write("\r[OK] Waveform generation complete\n")
                    sys.stdout.flush()
                    return True
            
            # Continuously spin the indicator while file exists and recently grew
            # Update spinner every 0.2 seconds for smooth animation
            time_since_growth = current_time - last_growth_time
            if time_since_growth < 2.0:  # Keep spinning for 2 seconds after last growth
                # Update spinner character periodically
                if current_time - spinner_update_time >= 0.2:
                    spinner_idx = (spinner_idx + 1) % len(spinner_chars)
                    spinner_update_time = current_time
                    spinner_char = spinner_chars[spinner_idx]
                    sys.stdout.write(f"\r[PROGRESS] Generating waveform {spinner_char}")
                    sys.stdout.flush()
            elif current_size > 0:
                # Show static indicator when file exists but growth has stopped
                sys.stdout.write("\r[PROGRESS] Generating waveform |")
                sys.stdout.flush()
        
        # If file hasn't been created yet, wait a bit more
        if not file_found:
            time.sleep(check_interval)
            continue
        
        # Timeout after 10 minutes
        if elapsed > 600:
            sys.stdout.write("\n")
            sys.stdout.flush()
            return False
        
        time.sleep(check_interval)


@app.command()
def generate(
    script_path: Path = typer.Argument(..., help="Path to the script file"),
    output_name: Optional[str] = typer.Option(None, "--output", "-o", help="Output video name (without .mp4)"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Custom config file"),
    # Waveform Parameters
    waveform_position: Optional[str] = typer.Option(None, "--waveform-position", help="Waveform position: top, bottom, left, right, middle, or combinations"),
    waveform_num_lines: Optional[int] = typer.Option(None, "--waveform-lines", help="Number of waveform lines (1-10)"),
    waveform_thickness: Optional[str] = typer.Option(None, "--waveform-thickness", help="Line thickness"),
    waveform_colors: Optional[str] = typer.Option(None, "--waveform-colors", help="Line colors: comma-separated RGB tuples"),
    waveform_height_percent: Optional[int] = typer.Option(None, "--waveform-height", help="Height percent for horizontal waveforms (10-50)"),
    waveform_width_percent: Optional[int] = typer.Option(None, "--waveform-width", help="Width percent for vertical waveforms (10-50)"),
    waveform_orientation_offset: Optional[float] = typer.Option(None, "--waveform-orientation-offset", help="Orientation offset for horizontal waveforms (0=bottom, 100=top)"),
    waveform_rotation: Optional[float] = typer.Option(None, "--waveform-rotation", help="Rotation angle in degrees (0=no rotation)"),
    waveform_amplitude_multiplier: Optional[float] = typer.Option(None, "--waveform-amplitude", help="Amplitude multiplier for waves (default: 1.0)"),
    waveform_num_instances: Optional[int] = typer.Option(None, "--waveform-instances", help="Number of waveform instances (default: 1)"),
    waveform_instances_offset: Optional[int] = typer.Option(None, "--waveform-instances-offset", help="Spacing between instances in pixels (default: 0)"),
    waveform_instances_intersect: Optional[bool] = typer.Option(None, "--waveform-instances-intersect/--no-waveform-instances-intersect", help="Allow waveform instances to intersect"),
):
    """
    Generate ONLY the waveform visualization video (no avatar, no background, no composition).
    
    This is useful for:
    - Reviewing waveform quality
    - Debugging chromakey/blending issues
    - Testing waveform configurations
    
    The output video will have:
    - Black background (chromakey color)
    - Waveform visualization in neon green
    - Audio track
    
    Output Location:
    - All files are saved to Creations/MMedia/ with descriptive names
    - If using --config with evaluation test configs, names auto-include test ID (e.g., eval_08_top_left_waveform_only.mp4)
    - If using --output, the provided name is used directly
    
    Examples:
        python scripts/generate_waveform_only.py "Creations/Scripts/test_short.txt" -o waveform_test --waveform-position bottom
        python scripts/generate_waveform_only.py "Creations/Scripts/test_short.txt" --config "Creations/Configs/evaluation_tests/eval_08_top_left_config.yaml"
    """
    # Load configuration
    config = load_config(config_file)
    
    # Apply waveform CLI overrides if provided
    config = _apply_waveform_cli_overrides(
        config,
        waveform_position,
        waveform_num_lines,
        waveform_thickness,
        waveform_colors,
        None,  # waveform_style
        None,  # waveform_opacity
        False,  # waveform_randomize
        waveform_height_percent,
        waveform_width_percent,
        None,  # waveform_left_spacing
        None,  # waveform_right_spacing
        None,  # waveform_render_scale
        None,  # waveform_anti_alias
        waveform_orientation_offset,
        waveform_rotation,
        waveform_amplitude_multiplier,
        waveform_num_instances,
        waveform_instances_offset,
        waveform_instances_intersect,
    )
    
    # Validate script file
    if not script_path.exists():
        print(f"[ERROR] Script file not found: {script_path}")
        return
    
    # Read script
    with open(script_path, "r", encoding="utf-8") as f:
        script_text = f.read()
    
    # Simple generation without progress indicator (TODO: add progress indicator later)
    try:
        from src.core.script_parser import ScriptParser
        parser = ScriptParser(config)
        parsed_data = parser.parse(script_text)
        
        tts_engine = TTSEngine(config)
        audio_path = tts_engine.generate(parsed_data["text"])
        
        # Generate output path - ensure it's in MMedia folder
        outputs_dir = config.get("storage", {}).get("outputs_dir", "./Creations/MMedia")
        output_dir = Path(outputs_dir).resolve()
        if "MMedia" not in str(output_dir):
            output_dir = Path("Creations/MMedia").resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate descriptive output name
        if output_name:
            output_video_path = output_dir / f"{output_name}.mp4"
        else:
            script_name = script_path.stem
            config_name = ""
            if config_file:
                config_stem = Path(config_file).stem
                if "eval_" in config_stem and "_config" in config_stem:
                    config_name = config_stem.replace("_config", "")
                elif "evaluation" in str(config_file).lower():
                    config_name = config_stem
            
            if config_name:
                output_video_path = output_dir / f"{config_name}_waveform_only.mp4"
            else:
                output_video_path = output_dir / f"{script_name}_waveform_only.mp4"
        
        # Generate visualization
        visualizer = AudioVisualizer(config)
        viz_path = visualizer.generate_visualization(audio_path, output_video_path)
        
        print(f"[OK] Waveform generation complete: {viz_path}")
        
    except Exception as e:
        print(f"[ERROR] Failed to generate waveform: {e}")
        raise
    print()
    print("[INFO] This video has:")
    print("  - Black background (chromakey color: [0, 0, 0])")
    print("  - Waveform visualization in neon green")
    print("  - Audio track")
    print()
    print("[INFO] Use this to review waveform quality before composition.")


if __name__ == "__main__":
    app()
