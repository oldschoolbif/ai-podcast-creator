"""
Script Chunking Utility
Splits scripts into logical chunks before processing.
This is more efficient than chunking video after creation.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional


def chunk_script(script_path: Path, chunk_duration_minutes: int, output_dir: Optional[Path] = None) -> List[Path]:
    """
    Split script into logical chunks based on estimated duration.
    
    Args:
        script_path: Path to input script file
        chunk_duration_minutes: Target duration per chunk in minutes
        output_dir: Optional output directory (defaults to script's parent)
    
    Returns:
        List of paths to chunk script files
    """
    if not script_path.exists():
        raise FileNotFoundError(f"Script file not found: {script_path}")
    
    # Read script
    with open(script_path, "r", encoding="utf-8") as f:
        script_text = f.read()
    
    # Estimate reading speed (words per minute for speech)
    # Average speaking rate: ~150 words per minute
    WORDS_PER_MINUTE = 150
    
    # Split into paragraphs (natural break points)
    paragraphs = _split_into_paragraphs(script_text)
    
    # Calculate target words per chunk
    target_words_per_chunk = chunk_duration_minutes * WORDS_PER_MINUTE
    
    output_dir = output_dir or script_path.parent / "chunks"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    chunk_files = []
    script_stem = script_path.stem
    current_chunk = []
    current_word_count = 0
    chunk_num = 1
    
    print(f"[CHUNK] Splitting script into ~{chunk_duration_minutes}-minute chunks...")
    
    for para in paragraphs:
        # Count words in paragraph
        para_words = len(para.split())
        
        # If adding this paragraph would exceed target, save current chunk
        if current_word_count > 0 and (current_word_count + para_words) > target_words_per_chunk:
            # Save current chunk
            chunk_path = output_dir / f"{script_stem}_chunk_{chunk_num:03d}.txt"
            chunk_text = "\n\n".join(current_chunk)
            
            # Preserve title if first chunk
            if chunk_num == 1 and script_text.startswith("# "):
                title_line = script_text.split("\n")[0] + "\n\n"
                chunk_text = title_line + chunk_text
            
            with open(chunk_path, "w", encoding="utf-8") as f:
                f.write(chunk_text)
            
            chunk_files.append(chunk_path)
            estimated_min = current_word_count / WORDS_PER_MINUTE
            print(f"  [OK] Chunk {chunk_num}: {chunk_path.name} (~{estimated_min:.1f} min, {current_word_count} words)")
            
            # Start new chunk
            current_chunk = [para]
            current_word_count = para_words
            chunk_num += 1
        else:
            # Add to current chunk
            current_chunk.append(para)
            current_word_count += para_words
    
    # Save final chunk
    if current_chunk:
        chunk_path = output_dir / f"{script_stem}_chunk_{chunk_num:03d}.txt"
        chunk_text = "\n\n".join(current_chunk)
        
        # Preserve title if first chunk
        if chunk_num == 1 and script_text.startswith("# "):
            title_line = script_text.split("\n")[0] + "\n\n"
            chunk_text = title_line + chunk_text
        
        with open(chunk_path, "w", encoding="utf-8") as f:
            f.write(chunk_text)
        
        chunk_files.append(chunk_path)
        estimated_min = current_word_count / WORDS_PER_MINUTE
        print(f"  [OK] Chunk {chunk_num}: {chunk_path.name} (~{estimated_min:.1f} min, {current_word_count} words)")
    
    print(f"\n[INFO] Created {len(chunk_files)} chunks from script")
    return chunk_files


def _split_into_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs (natural break points).
    
    Args:
        text: Input text
    
    Returns:
        List of paragraphs (non-empty lines grouped)
    """
    # Split by double newlines first (explicit paragraphs)
    parts = re.split(r"\n\s*\n", text)
    
    # If no double newlines, split by single newlines
    if len(parts) == 1:
        parts = [p.strip() for p in text.split("\n") if p.strip()]
    
    # Clean up and filter empty
    paragraphs = [p.strip() for p in parts if p.strip() and not p.strip().startswith("#")]
    
    # If still empty, treat entire text as one paragraph
    if not paragraphs:
        paragraphs = [text.strip()]
    
    return paragraphs


def estimate_duration(text: str, words_per_minute: int = 150) -> float:
    """
    Estimate speaking duration for text.
    
    Args:
        text: Text to estimate
        words_per_minute: Average speaking rate
    
    Returns:
        Estimated duration in minutes
    """
    word_count = len(text.split())
    return word_count / words_per_minute

