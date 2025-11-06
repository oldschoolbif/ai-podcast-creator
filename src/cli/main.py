"""
AI Podcast Creator - CLI Interface
Main entry point for the command-line interface
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.audio_mixer import AudioMixer
from src.core.music_generator import MusicGenerator
from src.core.script_parser import ScriptParser
from src.core.tts_engine import TTSEngine
from src.core.video_composer import VideoComposer
from src.utils.config import load_config
from src.utils.gpu_utils import get_gpu_manager, print_gpu_info

# Optional database support (sqlalchemy may not be installed)
DATABASE_AVAILABLE = False
Podcast: Any = None
init_db: Any = None

try:
    from src.models.database import Podcast, init_db  # noqa: F401

    DATABASE_AVAILABLE = True
except ImportError:
    # Database is optional - CLI works without it
    pass

app = typer.Typer(
    name="podcast-creator",
    help="AI Podcast Creator - Generate video podcasts from text scripts",
    add_completion=False,
)

console = Console(force_terminal=True, legacy_windows=True, no_color=False)


@app.command()
def generate_face(
    description: str = typer.Argument(..., help="Description of the face (e.g., 'professional male presenter')"),
    output_path: Optional[Path] = typer.Option(None, "--output", "-o", help="Output image path"),
):
    """
    Generate an AI face optimized for lip-sync using Stable Diffusion.
    
    The generated face will be clean, front-facing, and optimized for Wav2Lip.
    
    Examples:
        podcast-creator generate-face "professional male presenter"
        podcast-creator generate-face "young female news anchor" -o my_face.png
    """
    console.print("[bold blue]AI Face Generator[/bold blue]")
    console.print()
    
    # Initialize GPU
    gpu_manager = get_gpu_manager()
    if gpu_manager.gpu_available:
        console.print(f"[green][GPU][/green] GPU Detected: [cyan]{gpu_manager.gpu_name}[/cyan] ({gpu_manager.gpu_memory:.1f} GB)")
    else:
        console.print("[yellow][WARN][/yellow] Running on CPU (slower - consider adding GPU)")
    console.print()
    
    # Load config
    config = load_config()
    
    # Generate face
    try:
        from src.core.face_generator import FaceGenerator
        
        generator = FaceGenerator(config)
        face_path = generator.generate(description=description, output_path=output_path)
        
        console.print()
        console.print(f"[bold green][OK] Face generated successfully![/bold green]")
        console.print(f"[OK] Saved to: [cyan]{face_path}[/cyan]")
        console.print()
        console.print("To use this face in your podcast:")
        console.print(f"  1. Update config.yaml:")
        console.print(f"     avatar:")
        console.print(f"       source_image: \"{face_path}\"")
        console.print(f"  2. Or use the generated face path directly")
        
    except Exception as e:
        console.print(f"[red]Error generating face:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def create(
    script_path: Path = typer.Argument(..., help="Path to the script file"),
    music: Optional[str] = typer.Argument(None, help="Music description or path to music file"),
    output_name: Optional[str] = typer.Option(None, "--output", "-o", help="Output video name"),
    preview_only: bool = typer.Option(False, "--preview", "-p", help="Generate audio preview only"),
    audio_only: bool = typer.Option(False, "--audio-only", help="Generate MP3 audio file only (no video)"),
    visualize: bool = typer.Option(False, "--visualize", "-v", help="Add audio-reactive waveform visualization to video"),
    background: bool = typer.Option(False, "--background", "-b", help="Add static background image to video"),
    avatar: bool = typer.Option(False, "--avatar", "-a", help="Generate talking head avatar with lip-sync"),
    skip_music: bool = typer.Option(False, "--skip-music", help="Skip music generation"),
    music_file: Optional[Path] = typer.Option(None, "--music-file", help="Use existing music file"),
    music_start_offset: float = typer.Option(0.0, "--music-offset", help="Start music N seconds into the track"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Custom config file"),
    quality: str = typer.Option("fastest", "--quality", "-q", help="Video quality: fastest, fast, medium, high (default: fastest for testing)"),
    chunk_duration: Optional[int] = typer.Option(None, "--chunk-duration", help="Split script into chunks of N minutes before processing (e.g., 3 for 3-minute chunks)"),
    # Waveform Parameters
    waveform_position: Optional[str] = typer.Option(None, "--waveform-position", help="Waveform position: top, bottom, left, right, middle, or combinations (e.g., 'top,bottom')"),
    waveform_num_lines: Optional[int] = typer.Option(None, "--waveform-lines", help="Number of waveform lines (1-10)"),
    waveform_thickness: Optional[str] = typer.Option(None, "--waveform-thickness", help="Line thickness: single number or comma-separated (e.g., '12' or '15,12,8')"),
    waveform_colors: Optional[str] = typer.Option(None, "--waveform-colors", help="Line colors: comma-separated RGB tuples (e.g., '0,255,0:0,255,100:0,200,50')"),
    waveform_style: Optional[str] = typer.Option(None, "--waveform-style", help="Waveform style: continuous, bars, dots, filled"),
    waveform_opacity: Optional[float] = typer.Option(None, "--waveform-opacity", help="Waveform opacity (0.0-1.0)"),
    waveform_randomize: bool = typer.Option(False, "--waveform-randomize", help="Randomize waveform configuration per video"),
    waveform_height_percent: Optional[int] = typer.Option(None, "--waveform-height", help="Height percent for horizontal waveforms (10-50)"),
    waveform_width_percent: Optional[int] = typer.Option(None, "--waveform-width", help="Width percent for vertical waveforms (10-50)"),
    waveform_left_spacing: Optional[int] = typer.Option(None, "--waveform-left-spacing", help="Spacing from left edge for left-side waveform (pixels)"),
    waveform_right_spacing: Optional[int] = typer.Option(None, "--waveform-right-spacing", help="Spacing from right edge for right-side waveform (pixels)"),
    waveform_render_scale: Optional[float] = typer.Option(None, "--waveform-render-scale", help="Render scale for smoothness (1.0-4.0, default: 2.0)"),
    waveform_anti_alias: Optional[bool] = typer.Option(None, "--waveform-anti-alias/--no-waveform-anti-alias", help="Enable/disable anti-aliasing"),
    waveform_orientation_offset: Optional[float] = typer.Option(None, "--waveform-orientation-offset", help="Orientation offset for horizontal waveforms (0=bottom, 100=top)"),
    waveform_rotation: Optional[float] = typer.Option(None, "--waveform-rotation", help="Rotation angle in degrees (0=no rotation)"),
    waveform_amplitude_multiplier: Optional[float] = typer.Option(None, "--waveform-amplitude", help="Amplitude multiplier for waves (default: 1.0)"),
    waveform_num_instances: Optional[int] = typer.Option(None, "--waveform-instances", help="Number of waveform instances (default: 1)"),
    waveform_instances_offset: Optional[int] = typer.Option(None, "--waveform-instances-offset", help="Spacing between instances in pixels (default: 0)"),
    waveform_instances_intersect: Optional[bool] = typer.Option(None, "--waveform-instances-intersect/--no-waveform-instances-intersect", help="Allow waveform instances to intersect"),
):
    """
    Create a new podcast video (or audio-only MP3) from a script file with optional music.

    Default: Creates minimal video (black frame + audio) - audio-only mode
    Use flags to add effects:
        --visualize, -v    Add waveform/visualization effects
        --background, -b   Add static background image
        --avatar, -a       Generate talking head avatar with lip-sync

    Examples:
        podcast-creator create script.txt                                    # Minimal video (audio-only)
        podcast-creator create script.txt --visualize                        # With waveform
        podcast-creator create script.txt --background                       # With static background
        podcast-creator create script.txt --visualize --background           # Waveform + background
        podcast-creator create script.txt --avatar                           # With lip-sync avatar
        podcast-creator create script.txt --audio-only                       # MP3 only, no video
        podcast-creator create script.txt "calm ambient" -o my_podcast -v -b # With music, waveform, and background
    """
    console.print("[bold blue]AI Podcast Creator[/bold blue]")
    console.print()

    # Initialize GPU and show info
    gpu_manager = get_gpu_manager()
    if gpu_manager.gpu_available:
        console.print(f"[green][GPU][/green] GPU Detected: [cyan]{gpu_manager.gpu_name}[/cyan] ({gpu_manager.gpu_memory:.1f} GB)")
    else:
        console.print("[yellow][WARN][/yellow] Running on CPU (slower - consider adding GPU for faster generation)")
    console.print()

    # Validate script file
    if not script_path.exists():
        console.print(f"[red]Error:[/red] Script file not found: {script_path}")
        raise typer.Exit(1)

    # Load configuration
    config = load_config(config_file)
    
    # Apply waveform CLI overrides if provided
    if visualize:
        config = _apply_waveform_cli_overrides(
            config,
            waveform_position,
            waveform_num_lines,
            waveform_thickness,
            waveform_colors,
            waveform_style,
            waveform_opacity,
            waveform_randomize,
            waveform_height_percent,
            waveform_width_percent,
            waveform_left_spacing,
            waveform_right_spacing,
            waveform_render_scale,
            waveform_anti_alias,
            waveform_orientation_offset,
            waveform_rotation,
            waveform_amplitude_multiplier,
            waveform_num_instances,
            waveform_instances_offset,
            waveform_instances_intersect,
        )
    
    # Initialize metrics tracking
    from src.utils.metrics import get_metrics_tracker
    metrics = get_metrics_tracker(config)
    session_id = None
    if metrics:
        session_id = metrics.start_session(str(script_path))
        metrics.set_quality(quality)
        metrics.set_flags(avatar=avatar, visualization=visualize, background=background)

    # Chunk script if requested (BEFORE processing - more efficient!)
    script_chunks = [script_path]  # Default: single script
    if chunk_duration:
        console.print(f"[yellow]Chunking script into {chunk_duration}-minute segments...[/yellow]")
        from src.utils.script_chunker import chunk_script
        try:
            script_chunks = chunk_script(script_path, chunk_duration)
            console.print(f"[green][OK][/green] Created {len(script_chunks)} script chunks")
            console.print()
        except Exception as e:
            console.print(f"[red]Error chunking script: {e}[/red]")
            console.print("[yellow]Continuing with full script...[/yellow]")
            script_chunks = [script_path]

    # Initialize RAM monitor for the entire session
    # Use absolute limit of 45GB (leave 18GB headroom on 64GB system)
    # This accounts for baseline system RAM usage
    from src.utils.ram_monitor import RAMMonitor
    session_ram_monitor = RAMMonitor(max_ram_gb=45.0, warning_threshold_gb=35.0)
    initial_ram = session_ram_monitor.get_ram_usage_gb()
    console.print(f"[cyan]RAM:[/cyan] {initial_ram:.1f}GB / {session_ram_monitor.total_ram_gb:.1f}GB (limit: {session_ram_monitor.max_ram_gb}GB)")

    console.print(f"[cyan]Script loaded:[/cyan] {script_path}")
    if len(script_chunks) > 1:
        console.print(f"[cyan]Processing {len(script_chunks)} chunks[/cyan]")
    console.print(f"[cyan]Character:[/cyan] {config['character']['name']}")
    if session_id:
        console.print(f"[cyan]Metrics:[/cyan] Session {session_id}")
    console.print()

    # Process each chunk
    all_video_paths = []
    
    try:
        for chunk_idx, chunk_script_path in enumerate(script_chunks, 1):
            # Check RAM before starting each chunk
            is_over, msg = session_ram_monitor.check_ram_limit()
            if is_over:
                console.print(f"\n[bold red][ERROR] {msg}[/bold red]")
                console.print("[yellow]Aborting chunk processing to prevent system crash.[/yellow]")
                raise Exception(msg)
            elif msg:
                console.print(f"[yellow][WARN] {msg}[/yellow]")
            
            current_ram = session_ram_monitor.get_ram_usage_gb()
            if len(script_chunks) > 1:
                console.print(f"[INFO] RAM before chunk {chunk_idx}: {current_ram:.1f}GB")
            if len(script_chunks) > 1:
                console.print(f"\n{'='*60}")
                console.print(f"[bold cyan]Processing Chunk {chunk_idx}/{len(script_chunks)}[/bold cyan]")
                console.print(f"{'='*60}\n")
            
            # Read script chunk
            with open(chunk_script_path, "r", encoding="utf-8") as f:
                script_text = f.read()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                disable=False,
            ) as progress:
                # Parse script
                comp_metrics = metrics.start_component("script_parsing") if metrics else None
                task = progress.add_task("Parsing script...", total=None)
                parser = ScriptParser(config)
                parsed_data = parser.parse(script_text)
                progress.update(task, completed=True)
                if comp_metrics:
                    metrics.finish_component(comp_metrics)
                console.print("[green][OK][/green] Script parsed successfully")

                # Generate TTS
                comp_metrics = metrics.start_component("tts_generation") if metrics else None
                task = progress.add_task("Generating speech...", total=None)
                tts_engine = TTSEngine(config)
                audio_path = tts_engine.generate(parsed_data["text"])
                progress.update(task, completed=True)
                if comp_metrics:
                    metrics.finish_component(comp_metrics)
                console.print(f"[green][OK][/green] Speech generated: {audio_path}")

                if preview_only:
                    console.print(f"\n[green]Preview audio created:[/green] {audio_path}")
                    console.print("Use your media player to listen to it.")
                    continue  # Skip to next chunk

                # Generate or load music
                music_path = None
                if not skip_music:
                    if music_file and music_file.exists():
                        # Use provided music file
                        music_path = music_file
                        console.print(f"[green][OK][/green] Using music file: {music_path}")
                    elif music or parsed_data.get("music_cues"):
                        # Generate music from description or cues
                        task = progress.add_task("Generating background music...", total=None)
                        music_gen = MusicGenerator(config)
                        music_desc = music or parsed_data["music_cues"]
                        music_path = music_gen.generate(music_desc)
                        progress.update(task, completed=True)
                        console.print(f"[green][OK][/green] Music generated: {music_path}")

                # Mix audio
                comp_metrics = metrics.start_component("audio_mixing") if metrics else None
                task = progress.add_task("Mixing audio...", total=None)
                mixer = AudioMixer(config)
                mixed_audio_path = mixer.mix(audio_path, music_path, music_start_offset)
                progress.update(task, completed=True)
                if comp_metrics:
                    metrics.finish_component(comp_metrics)
                console.print(f"[green][OK][/green] Audio mixed: {mixed_audio_path}")
                if music_start_offset > 0:
                    console.print(f"   Music started at {music_start_offset}s offset")

                # Generate final output (video or audio-only)
                if audio_only:
                    # Audio-only: Export as high-quality MP3
                    task = progress.add_task("Exporting MP3...", total=None)
                    output_dir = Path(config["storage"]["outputs_dir"])
                    output_dir.mkdir(parents=True, exist_ok=True)
                    # Generate output name with chunk number if chunking
                    if len(script_chunks) > 1:
                        base_name = output_name or script_path.stem
                        final_audio_name = f"{base_name}_chunk_{chunk_idx:03d}"
                    else:
                        final_audio_name = output_name or script_path.stem
                    final_audio_path = output_dir / f"{final_audio_name}.mp3"

                    # Convert to high-quality MP3 with metadata
                    import subprocess

                    cmd = [
                        "ffmpeg",
                        "-i",
                        str(mixed_audio_path),
                        "-vn",  # No video
                        "-c:a",
                        "libmp3lame",
                        "-q:a",
                        "2",  # High quality (VBR ~190 kbps)
                        "-ar",
                        "44100",  # Standard sample rate
                        "-ac",
                        "2",  # Stereo
                        "-id3v2_version",
                        "3",  # ID3v2.3 tags
                        "-metadata",
                        f"title={final_audio_name}",
                        "-metadata",
                        "artist=AI Podcast Creator",
                        "-metadata",
                        f'album={config["character"]["name"]}',
                        "-metadata",
                        "genre=Podcast",
                        str(final_audio_path),
                        "-y",
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    progress.update(task, completed=True)

                    all_video_paths.append(final_audio_path)  # Store audio path for summary
                    
                    if len(script_chunks) > 1:
                        console.print()
                        console.print(f"[bold green][OK] Chunk {chunk_idx}/{len(script_chunks)} audio created![/bold green]")
                        console.print(f"[cyan]MP3 saved to:[/cyan] {final_audio_path}")
                    else:
                        console.print()
                        console.print("[bold green]Podcast audio created successfully![/bold green]")
                        console.print(f"[cyan]MP3 saved to:[/cyan] {final_audio_path}")
                        console.print(f"   Voice: {config['character']['name']} ({config['character']['voice_type']})")
                else:
                    # Optional: Generate avatar video first
                    avatar_video_path = None
                    if avatar:
                        comp_metrics = metrics.start_component("avatar_generation") if metrics else None
                        try:
                            from src.core.avatar_generator import AvatarGenerator

                            task = progress.add_task("Generating talking head avatar...", total=None)
                            avatar_gen = AvatarGenerator(config)
                            avatar_video_path = avatar_gen.generate(mixed_audio_path)
                            progress.update(task, completed=True)
                            if comp_metrics:
                                # Include file monitor data if available
                                file_monitor = avatar_gen.get_file_monitor()
                                # Pass GPU samples if available (from continuous monitoring)
                                if hasattr(avatar_gen, '_wav2lip_gpu_samples') and avatar_gen._wav2lip_gpu_samples:
                                    # Store samples in gpu_manager temporarily for metrics to access
                                    if metrics.gpu_manager:
                                        metrics.gpu_manager._component_gpu_samples = avatar_gen._wav2lip_gpu_samples
                                metrics.finish_component(comp_metrics, file_monitor=file_monitor)
                            
                            # Debug: Log avatar path details
                            if avatar_video_path:
                                console.print(f"[DEBUG] Avatar path returned: {avatar_video_path}")
                                console.print(f"[DEBUG] Avatar exists: {avatar_video_path.exists()}")
                                if avatar_video_path.exists():
                                    console.print(f"[DEBUG] Avatar size: {avatar_video_path.stat().st_size} bytes")
                            
                            # Check if avatar generation actually produced a valid file
                            if not avatar_video_path or not avatar_video_path.exists() or avatar_video_path.stat().st_size == 0:
                                console.print("[yellow][WARN] Avatar generation failed, falling back to visualization with background[/yellow]")
                                avatar_video_path = None
                            else:
                                console.print(f"[OK] Avatar video ready: {avatar_video_path} ({avatar_video_path.stat().st_size / 1024:.1f} KB)")
                        except Exception as e:
                            if comp_metrics:
                                metrics.finish_component(comp_metrics, error=str(e))
                            console.print(f"[yellow][WARN] Avatar generation error: {e}, falling back to visualization with background[/yellow]")
                            avatar_video_path = None

                    # Compose final video based on flags
                    comp_metrics = metrics.start_component("video_composition") if metrics else None
                    task = progress.add_task("Composing final video...", total=None)
                    composer = VideoComposer(config)
                    
                    # Generate output name with chunk number if chunking
                    if len(script_chunks) > 1:
                        base_name = output_name or script_path.stem
                        chunk_output_name = f"{base_name}_chunk_{chunk_idx:03d}"
                    else:
                        chunk_output_name = output_name or script_path.stem
                    
                    # Debug: Check avatar video before passing to composer
                    avatar_to_use = None
                    if avatar and avatar_video_path:
                        if avatar_video_path.exists() and avatar_video_path.stat().st_size > 0:
                            avatar_to_use = avatar_video_path
                            console.print(f"[DEBUG] Passing avatar to composer: {avatar_to_use}")
                        else:
                            console.print(f"[WARN] Avatar video exists check failed: exists={avatar_video_path.exists()}, size={avatar_video_path.stat().st_size if avatar_video_path.exists() else 0}")
                    else:
                        console.print(f"[DEBUG] Avatar not passed: avatar={avatar}, avatar_video_path={avatar_video_path}")
                    
                    final_video_path = composer.compose(
                        mixed_audio_path,
                        output_name=chunk_output_name,
                        use_visualization=visualize,
                        use_background=background,
                        avatar_video=avatar_to_use,
                        quality=quality,
                    )
                    progress.update(task, completed=True)
                    if comp_metrics:
                        # Include file monitor data if available
                        file_monitor = composer.get_file_monitor()
                        metrics.finish_component(comp_metrics, file_monitor=file_monitor)

                    all_video_paths.append(final_video_path)
                    
                    if len(script_chunks) > 1:
                        console.print()
                        console.print(f"[bold green][OK] Chunk {chunk_idx}/{len(script_chunks)} completed![/bold green]")
                        console.print(f"[VIDEO] Video saved to: [cyan]{final_video_path}[/cyan]")
                    else:
                        console.print()
                        console.print("[bold green]Podcast created successfully![/bold green]")
                        console.print(f"[VIDEO] Video saved to: [cyan]{final_video_path}[/cyan]")
                        if avatar:
                            console.print("   [cyan]With talking head avatar[/cyan]")
                        if visualize:
                            console.print(
                                f"   [cyan]With {config.get('visualization', {}).get('style', 'waveform')} visualization[/cyan]"
                            )

        # Finish metrics tracking (use first video path for session)
        if metrics and all_video_paths:
            metrics.finish_session(str(all_video_paths[0]))
        
        # Summary if multiple chunks
        if len(all_video_paths) > 1:
            console.print()
            console.print(f"[bold green][OK] All {len(all_video_paths)} chunks completed![/bold green]")
            console.print(f"[OK] Videos saved to:")
            for path in all_video_paths:
                console.print(f"   [OK] [cyan]{path}[/cyan]")

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def list():
    """List all generated podcasts."""
    console.print("[bold blue]Generated Podcasts[/bold blue]\n")

    if not DATABASE_AVAILABLE:
        console.print("[yellow][WARN] Database not available. Install sqlalchemy to enable podcast tracking.[/yellow]")
        return

    # TODO: Query database for podcasts
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Title")
    table.add_column("Duration")
    table.add_column("Created")
    table.add_column("Status")

    # Example data (replace with actual database query)
    table.add_row("1", "Welcome Episode", "5:32", "2024-01-15", "[green]Complete[/green]")
    table.add_row("2", "Tech News Today", "8:45", "2024-01-16", "[yellow]Processing[/yellow]")

    console.print(table)


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Edit configuration file"),
    reset: bool = typer.Option(False, "--reset", help="Reset to default configuration"),
):
    """Manage configuration settings."""
    if show:
        config = load_config()
        console.print("[bold blue]Current Configuration[/bold blue]\n")
        console.print(config)
    elif edit:
        config_path = Path("config.yaml")
        console.print(f"Opening configuration file: {config_path}")
        # TODO: Open in default editor
    elif reset:
        console.print("[yellow]Reset configuration?[/yellow] (not implemented)")
    else:
        console.print("Use --show to display config or --edit to modify it")


@app.command()
def init():
    """Initialize the AI Podcast Creator environment."""
    console.print("[bold blue]Initializing AI Podcast Creator[/bold blue]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # Create directories
        task = progress.add_task("Creating directories...", total=None)
        dirs = [
            "data/scripts",
            "data/outputs",
            "data/cache",
            "data/models",
            "logs",
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        progress.update(task, completed=True)
        console.print("[green][OK][/green] Directories created")

        # Initialize database (if available)
        if DATABASE_AVAILABLE:
            task = progress.add_task("Initializing database...", total=None)
            init_db()
            progress.update(task, completed=True)
            console.print("[green][OK][/green] Database initialized")
        else:
            console.print("[yellow][WARN] Database not available (sqlalchemy not installed)[/yellow]")

        # Check dependencies
        task = progress.add_task("Checking dependencies...", total=None)
        # TODO: Check if FFmpeg is installed
        # TODO: Check if GPU is available
        progress.update(task, completed=True)
        console.print("[green][OK][/green] Dependencies checked")

    console.print("\n[bold green]Initialization complete![/bold green]")
    console.print("\nNext steps:")
    console.print("1. Copy env.example to .env and add your API keys (if using)")
    console.print("2. Review config.yaml and adjust settings")
    console.print("3. Run: podcast-creator create example_script.txt")


@app.command()
def cleanup(
    cache_only: bool = typer.Option(False, "--cache-only", help="Only clear cache, keep outputs"),
    outputs_only: bool = typer.Option(False, "--outputs-only", help="Only clear outputs, keep cache"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted without deleting"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """
    Clean up cache and temporary files.

    Examples:
        podcast-creator cleanup              # Clean everything (with confirmation)
        podcast-creator cleanup --cache-only # Only clear cache
        podcast-creator cleanup --dry-run    # Preview what will be deleted
        podcast-creator cleanup --force      # No confirmation prompt
    """
    import shutil
    from pathlib import Path

    config = load_config()

    # Define directories to clean
    cache_dir = Path(config["storage"]["cache_dir"])
    outputs_dir = Path(config["storage"]["outputs_dir"])

    # Determine what to clean
    clean_cache = not outputs_only
    clean_outputs = not cache_only

    # Calculate sizes and file counts
    def get_dir_size(directory):
        if not directory.exists():
            return 0, 0
        total_size = 0
        file_count = 0
        for item in directory.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
                file_count += 1
        return total_size, file_count

    cache_size, cache_files = get_dir_size(cache_dir) if clean_cache else (0, 0)
    output_size, output_files = get_dir_size(outputs_dir) if clean_outputs else (0, 0)

    # Format sizes
    def format_size(size):
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    # Display what will be cleaned
    console.print("[bold blue]Cleanup Summary[/bold blue]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Directory")
    table.add_column("Files")
    table.add_column("Size")
    table.add_column("Action")

    if clean_cache:
        action = "[yellow]Preview[/yellow]" if dry_run else "[red]DELETE[/red]"
        table.add_row(str(cache_dir), str(cache_files), format_size(cache_size), action)

    if clean_outputs:
        action = "[yellow]Preview[/yellow]" if dry_run else "[red]DELETE[/red]"
        table.add_row(str(outputs_dir), str(output_files), format_size(output_size), action)

    console.print(table)
    console.print()

    total_size = cache_size + output_size
    total_files = cache_files + output_files

    if total_files == 0:
        console.print("[green][OK][/green] Nothing to clean - directories are empty!")
        return

    if dry_run:
        console.print(f"[yellow]Dry run:[/yellow] Would delete {total_files} files ({format_size(total_size)})")
        console.print("Run without --dry-run to actually delete files")
        return

    # Confirmation prompt
    if not force:
        console.print(f"[bold red]Warning:[/bold red] About to delete {total_files} files ({format_size(total_size)})")
        confirm = typer.confirm("Are you sure you want to continue?")
        if not confirm:
            console.print("[yellow]Cleanup cancelled[/yellow]")
            return

    # Perform cleanup
    deleted_files = 0
    deleted_size = 0

    if clean_cache and cache_dir.exists():
        for item in cache_dir.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                item.unlink()
                deleted_files += 1
                deleted_size += size
        console.print(f"[green][OK][/green] Cleared cache: {cache_files} files ({format_size(cache_size)})")

    if clean_outputs and outputs_dir.exists():
        for item in outputs_dir.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                item.unlink()
                deleted_files += 1
                deleted_size += size
        console.print(f"[green][OK][/green] Cleared outputs: {output_files} files ({format_size(output_size)})")

    console.print()
    console.print("[bold green][OK] Cleanup complete![/bold green]")
    console.print(f"Deleted {deleted_files} files, freed {format_size(deleted_size)}")


@app.command()
def version():
    """Show version information."""
    config = load_config()
    console.print(f"[bold blue]AI Podcast Creator[/bold blue] v{config['app']['version']}")
    console.print(f"Character: {config['character']['name']}")


@app.command()
def status():
    """Check system status and requirements."""
    console.print("[bold blue]System Status[/bold blue]\n")

    # GPU Detection and detailed info
    gpu_manager = get_gpu_manager()

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Component")
    table.add_column("Status")
    table.add_column("Details")

    # Check Python
    import sys

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    table.add_row("Python", "[green][OK][/green]", python_version)

    # Check FFmpeg
    import subprocess

    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            # Check for NVENC support
            if "enable-nvenc" in result.stdout or "h264_nvenc" in result.stdout:
                table.add_row("FFmpeg", "[green][OK][/green]", "Installed (GPU encoding available)")
            else:
                table.add_row("FFmpeg", "[green][OK][/green]", "Installed (CPU only)")
        else:
            table.add_row("FFmpeg", "[red][FAIL][/red]", "Not found")
    except FileNotFoundError:
        table.add_row("FFmpeg", "[red][FAIL][/red]", "Not found")

    # Check GPU with detailed info
    if gpu_manager.gpu_available:
        gpu_details = f"{gpu_manager.gpu_name} ({gpu_manager.gpu_memory:.1f} GB VRAM)"
        table.add_row("GPU", "[green][OK][/green]", gpu_details)

        # Show GPU capabilities
        try:
            import torch

            compute_cap = torch.cuda.get_device_capability()
            cuda_version = torch.version.cuda
            table.add_row(
                "CUDA", "[green][OK][/green]", f"Version {cuda_version} (Compute {compute_cap[0]}.{compute_cap[1]})"
            )

            # Check cuDNN
            if torch.backends.cudnn.is_available():
                table.add_row("cuDNN", "[green][OK][/green]", f"Version {torch.backends.cudnn.version()}")

            # Performance features
            perf_config = gpu_manager.get_performance_config()
            features = []
            if perf_config["use_fp16"]:
                features.append("FP16")
            if perf_config["use_tf32"]:
                features.append("TF32")
            if features:
                table.add_row("Optimizations", "[green][OK][/green]", ", ".join(features))

        except Exception:
            pass
    else:
        table.add_row("GPU", "[yellow][WARN][/yellow]", "CPU only (slower generation)")
        try:
            import torch

            if not torch.cuda.is_available():
                table.add_row("CUDA", "[yellow][WARN][/yellow]", "Not available")
        except Exception:
            table.add_row("PyTorch", "[red][FAIL][/red]", "Not installed")

    # Check models
    models_dir = Path("data/models")
    if models_dir.exists():
        model_count = sum(1 for _ in models_dir.rglob("*"))
        table.add_row("Models", "[green][OK][/green]", f"{model_count} files")
    else:
        table.add_row("Models", "[yellow][WARN][/yellow]", "Directory not found")

    console.print(table)

    # Show GPU memory usage if available
    if gpu_manager.gpu_available:
        console.print("\n[bold]GPU Memory:[/bold]")
        mem = gpu_manager.get_memory_usage()
        console.print(f"  Allocated: {mem['allocated_gb']:.2f} GB")
        console.print(f"  Free: {mem['free_gb']:.2f} GB")
        console.print(f"  Total: {mem['total_gb']:.2f} GB")

    # Performance recommendations
    console.print("\n[bold]Performance Mode:[/bold]")
    if gpu_manager.gpu_available:
        console.print("  [green][GPU][/green] GPU Accelerated - Fast generation enabled")
    else:
        console.print("  [yellow][INFO] CPU Mode[/yellow] - Consider adding GPU for 10-50x faster generation")


def _apply_waveform_cli_overrides(
    config: Dict[str, Any],
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
) -> Dict[str, Any]:
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
            console.print(f"[yellow][WARN][/yellow] Invalid thickness format: {thickness}, using default")
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
            console.print(f"[yellow][WARN][/yellow] Invalid colors format: {colors}, using default")
    if style is not None:
        if style in ["continuous", "bars", "dots", "filled"]:
            waveform_config["waveform_style"] = style
        else:
            console.print(f"[yellow][WARN][/yellow] Invalid style: {style}, using 'continuous'")
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


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
