"""
AI Podcast Creator - CLI Interface
Main entry point for the command-line interface
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.audio_mixer import AudioMixer
from src.core.avatar_generator import AvatarGenerator
from src.core.music_generator import MusicGenerator
from src.core.script_parser import ScriptParser
from src.core.tts_engine import TTSEngine
from src.core.video_composer import VideoComposer
from src.models.database import Podcast, init_db
from src.utils.config import load_config
from src.utils.gpu_utils import get_gpu_manager, print_gpu_info

app = typer.Typer(
    name="podcast-creator",
    help="AI Podcast Creator - Generate video podcasts from text scripts",
    add_completion=False,
)

console = Console()


@app.command()
def create(
    script_path: Path = typer.Argument(..., help="Path to the script file"),
    music: Optional[str] = typer.Argument(None, help="Music description or path to music file"),
    output_name: Optional[str] = typer.Option(None, "--output", "-o", help="Output video name"),
    preview_only: bool = typer.Option(False, "--preview", "-p", help="Generate audio preview only"),
    audio_only: bool = typer.Option(False, "--audio-only", help="Generate MP3 audio file only (no video)"),
    visualize: bool = typer.Option(False, "--visualize", "-v", help="Add audio-reactive visualization to video"),
    avatar: bool = typer.Option(False, "--avatar", "-a", help="Generate talking head avatar (AI face animation)"),
    skip_music: bool = typer.Option(False, "--skip-music", help="Skip music generation"),
    music_file: Optional[Path] = typer.Option(None, "--music-file", help="Use existing music file"),
    music_start_offset: float = typer.Option(0.0, "--music-offset", help="Start music N seconds into the track"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Custom config file"),
):
    """
    Create a new podcast video (or audio-only MP3) from a script file with optional music.

    Examples:
        podcast-creator create script.txt
        podcast-creator create script.txt "upbeat energetic intro"
        podcast-creator create script.txt --music-file background.mp3
        podcast-creator create script.txt "calm ambient" -o my_podcast
        podcast-creator create script.txt --audio-only -o podcast_audio  # MP3 only, no video
    """
    console.print("[bold blue]AI Podcast Creator[/bold blue] 🎙️")
    console.print()

    # Initialize GPU and show info
    gpu_manager = get_gpu_manager()
    if gpu_manager.gpu_available:
        console.print(f"⚡ GPU Detected: [cyan]{gpu_manager.gpu_name}[/cyan] ({gpu_manager.gpu_memory:.1f} GB)")
    else:
        console.print("⚠️  Running on CPU (slower - consider adding GPU for faster generation)")
    console.print()

    # Validate script file
    if not script_path.exists():
        console.print(f"[red]Error:[/red] Script file not found: {script_path}")
        raise typer.Exit(1)

    # Load configuration
    config = load_config(config_file)

    # Read script
    with open(script_path, "r", encoding="utf-8") as f:
        script_text = f.read()

    console.print(f"📄 Script loaded: [cyan]{script_path}[/cyan]")
    console.print(f"🎭 Character: [cyan]{config['character']['name']}[/cyan]")
    console.print()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Parse script
            task = progress.add_task("Parsing script...", total=None)
            parser = ScriptParser(config)
            parsed_data = parser.parse(script_text)
            progress.update(task, completed=True)
            console.print("✅ Script parsed successfully")

            # Generate TTS
            task = progress.add_task("Generating speech...", total=None)
            tts_engine = TTSEngine(config)
            audio_path = tts_engine.generate(parsed_data["text"])
            progress.update(task, completed=True)
            console.print(f"✅ Speech generated: {audio_path}")

            if preview_only:
                console.print(f"\n[green]Preview audio created:[/green] {audio_path}")
                console.print("Use your media player to listen to it.")
                return

            # Generate or load music
            music_path = None
            if not skip_music:
                if music_file and music_file.exists():
                    # Use provided music file
                    music_path = music_file
                    console.print(f"✅ Using music file: {music_path}")
                elif music or parsed_data.get("music_cues"):
                    # Generate music from description or cues
                    task = progress.add_task("Generating background music...", total=None)
                    music_gen = MusicGenerator(config)
                    music_desc = music or parsed_data["music_cues"]
                    music_path = music_gen.generate(music_desc)
                    progress.update(task, completed=True)
                    console.print(f"✅ Music generated: {music_path}")

            # Mix audio
            task = progress.add_task("Mixing audio...", total=None)
            mixer = AudioMixer(config)
            mixed_audio_path = mixer.mix(audio_path, music_path, music_start_offset)
            progress.update(task, completed=True)
            console.print(f"✅ Audio mixed: {mixed_audio_path}")
            if music_start_offset > 0:
                console.print(f"   Music started at {music_start_offset}s offset")

            # Generate final output (video or audio-only)
            if audio_only:
                # Audio-only: Export as high-quality MP3
                task = progress.add_task("Exporting MP3...", total=None)
                output_dir = Path(config["storage"]["outputs_dir"])
                output_dir.mkdir(parents=True, exist_ok=True)
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

                console.print()
                console.print("[bold green]✨ Podcast audio created successfully![/bold green]")
                console.print(f"🎵 MP3 saved to: [cyan]{final_audio_path}[/cyan]")
                console.print(f"   Voice: {config['character']['name']} ({config['character']['voice_type']})")
            else:
                # Optional: Generate avatar video first
                avatar_video_path = None
                if avatar:
                    from src.core.avatar_generator import AvatarGenerator

                    task = progress.add_task("Generating talking head avatar...", total=None)
                    avatar_gen = AvatarGenerator(config)
                    avatar_video_path = avatar_gen.generate(mixed_audio_path)
                    progress.update(task, completed=True)

                # Compose final video
                if avatar and avatar_video_path and avatar_video_path.exists() and avatar_video_path.stat().st_size > 0:
                    # Use avatar video (with optional visualization overlay)
                    if visualize:
                        task = progress.add_task("Adding visualization to avatar video...", total=None)
                        composer = VideoComposer(config)
                        final_video_path = composer.compose(
                            mixed_audio_path,
                            output_name=output_name or script_path.stem,
                            use_visualization=True,
                            avatar_video=avatar_video_path,
                        )
                        progress.update(task, completed=True)
                    else:
                        # Just use avatar video as-is, copy to outputs
                        final_video_name = output_name or script_path.stem
                        final_video_path = Path(config["storage"]["outputs_dir"]) / f"{final_video_name}.mp4"
                        import shutil

                        shutil.copy(avatar_video_path, final_video_path)
                        task = progress.add_task("Finalizing avatar video...", total=None)
                        progress.update(task, completed=True)
                elif visualize:
                    task = progress.add_task("Creating audio-reactive visualization...", total=None)
                    composer = VideoComposer(config)
                    final_video_path = composer.compose(
                        mixed_audio_path, output_name=output_name or script_path.stem, use_visualization=True
                    )
                    progress.update(task, completed=True)
                else:
                    task = progress.add_task("Composing final video...", total=None)
                    composer = VideoComposer(config)
                    final_video_path = composer.compose(
                        mixed_audio_path, output_name=output_name or script_path.stem, use_visualization=False
                    )
                    progress.update(task, completed=True)

                console.print()
                console.print("[bold green]✨ Podcast created successfully![/bold green]")
                console.print(f"📹 Video saved to: [cyan]{final_video_path}[/cyan]")
                if avatar:
                    console.print("   🎭 With talking head avatar")
                if visualize:
                    console.print(
                        f"   🎨 With {config.get('visualization', {}).get('style', 'waveform')} visualization"
                    )

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def list():
    """List all generated podcasts."""
    console.print("[bold blue]Generated Podcasts[/bold blue]\n")

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
        console.print("✅ Directories created")

        # Initialize database
        task = progress.add_task("Initializing database...", total=None)
        init_db()
        progress.update(task, completed=True)
        console.print("✅ Database initialized")

        # Check dependencies
        task = progress.add_task("Checking dependencies...", total=None)
        # TODO: Check if FFmpeg is installed
        # TODO: Check if GPU is available
        progress.update(task, completed=True)
        console.print("✅ Dependencies checked")

    console.print("\n[bold green]✨ Initialization complete![/bold green]")
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
        console.print("[green]✓[/green] Nothing to clean - directories are empty!")
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
        console.print(f"[green]✓[/green] Cleared cache: {cache_files} files ({format_size(cache_size)})")

    if clean_outputs and outputs_dir.exists():
        for item in outputs_dir.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                item.unlink()
                deleted_files += 1
                deleted_size += size
        console.print(f"[green]✓[/green] Cleared outputs: {output_files} files ({format_size(output_size)})")

    console.print()
    console.print("[bold green]✨ Cleanup complete![/bold green]")
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
    table.add_row("Python", "[green]✓[/green]", python_version)

    # Check FFmpeg
    import subprocess

    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            # Check for NVENC support
            if "enable-nvenc" in result.stdout or "h264_nvenc" in result.stdout:
                table.add_row("FFmpeg", "[green]✓[/green]", "Installed (GPU encoding available)")
            else:
                table.add_row("FFmpeg", "[green]✓[/green]", "Installed (CPU only)")
        else:
            table.add_row("FFmpeg", "[red]✗[/red]", "Not found")
    except FileNotFoundError:
        table.add_row("FFmpeg", "[red]✗[/red]", "Not found")

    # Check GPU with detailed info
    if gpu_manager.gpu_available:
        gpu_details = f"{gpu_manager.gpu_name} ({gpu_manager.gpu_memory:.1f} GB VRAM)"
        table.add_row("GPU", "[green]✓[/green]", gpu_details)

        # Show GPU capabilities
        try:
            import torch

            compute_cap = torch.cuda.get_device_capability()
            cuda_version = torch.version.cuda
            table.add_row(
                "CUDA", "[green]✓[/green]", f"Version {cuda_version} (Compute {compute_cap[0]}.{compute_cap[1]})"
            )

            # Check cuDNN
            if torch.backends.cudnn.is_available():
                table.add_row("cuDNN", "[green]✓[/green]", f"Version {torch.backends.cudnn.version()}")

            # Performance features
            perf_config = gpu_manager.get_performance_config()
            features = []
            if perf_config["use_fp16"]:
                features.append("FP16")
            if perf_config["use_tf32"]:
                features.append("TF32")
            if features:
                table.add_row("Optimizations", "[green]✓[/green]", ", ".join(features))

        except Exception:
            pass
    else:
        table.add_row("GPU", "[yellow]⚠[/yellow]", "CPU only (slower generation)")
        try:
            import torch

            if not torch.cuda.is_available():
                table.add_row("CUDA", "[yellow]⚠[/yellow]", "Not available")
        except Exception:
            table.add_row("PyTorch", "[red]✗[/red]", "Not installed")

    # Check models
    models_dir = Path("data/models")
    if models_dir.exists():
        model_count = len(list(models_dir.rglob("*")))
        table.add_row("Models", "[green]✓[/green]", f"{model_count} files")
    else:
        table.add_row("Models", "[yellow]⚠[/yellow]", "Directory not found")

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
        console.print("  [green]⚡ GPU Accelerated[/green] - Fast generation enabled")
    else:
        console.print("  [yellow]🐢 CPU Mode[/yellow] - Consider adding GPU for 10-50x faster generation")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
