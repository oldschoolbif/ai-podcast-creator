"""
Video Chunking Utility
Splits video files into time-based chunks.
"""

import subprocess
from pathlib import Path
from typing import List, Optional


def chunk_video(video_path: Path, chunk_duration_minutes: int, output_dir: Optional[Path] = None) -> List[Path]:
    """
    Split video into chunks of specified duration.
    
    Args:
        video_path: Path to input video file
        chunk_duration_minutes: Duration of each chunk in minutes
        output_dir: Optional output directory (defaults to video's parent)
    
    Returns:
        List of paths to chunk files
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Get video duration first
    duration_seconds = _get_video_duration(video_path)
    if duration_seconds is None:
        raise Exception("Could not determine video duration")
    
    chunk_duration_seconds = chunk_duration_minutes * 60
    num_chunks = int((duration_seconds + chunk_duration_seconds - 1) / chunk_duration_seconds)  # Ceiling division
    
    output_dir = output_dir or video_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    chunk_paths = []
    video_stem = video_path.stem
    
    print(f"📹 Splitting video into {num_chunks} chunks of {chunk_duration_minutes} minutes each...")
    
    for i in range(num_chunks):
        start_time = i * chunk_duration_seconds
        chunk_path = output_dir / f"{video_stem}_chunk_{i+1:03d}.mp4"
        
        # FFmpeg command to extract chunk
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-ss", str(start_time),
            "-t", str(chunk_duration_seconds),
            "-c", "copy",  # Copy streams (fast, no re-encoding)
            "-avoid_negative_ts", "make_zero",
            "-f", "mp4",
            "-movflags", "+faststart",
            str(chunk_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            errors='replace',
            timeout=300
        )
        
        if result.returncode == 0 and chunk_path.exists():
            chunk_paths.append(chunk_path)
            size_mb = chunk_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ Chunk {i+1}/{num_chunks}: {chunk_path.name} ({size_mb:.1f} MB)")
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            print(f"  ⚠️  Chunk {i+1} failed: {error_msg[:200]}")
    
    return chunk_paths


def _get_video_duration(video_path: Path) -> Optional[float]:
    """Get video duration in seconds using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except Exception:
        pass
    return None

