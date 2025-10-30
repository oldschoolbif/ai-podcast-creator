"""
Script Parser Module
Parses podcast scripts and extracts text and music cues
"""

import re
from pathlib import Path
from typing import Any, Dict, List


class ScriptParser:
    """Parse podcast scripts and extract content and music cues."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize script parser.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.music_pattern = re.compile(r"\[MUSIC:\s*([^\]]+)\]")

    def parse(self, script_text: str) -> Dict[str, Any]:
        """
        Parse script text and extract components.

        Args:
            script_text: Raw script text

        Returns:
            Dictionary containing:
                - text: Main script text (without music cues)
                - music_cues: List of music descriptions with timestamps
                - metadata: Script metadata (title, etc.)
        """
        lines = script_text.strip().split("\n")

        # Extract title (first line if it starts with #)
        title = None
        if lines and lines[0].startswith("# "):
            title = lines[0][2:].strip()
            lines = lines[1:]

        # Parse content and music cues
        clean_text = []
        music_cues = []
        char_position = 0

        for line in lines:
            # Find music cues in line
            matches = list(self.music_pattern.finditer(line))

            if matches:
                # Extract music descriptions
                for match in matches:
                    music_desc = match.group(1).strip()
                    music_cues.append(
                        {
                            "description": music_desc,
                            "position": char_position,
                            "timestamp": None,  # Will be calculated later based on TTS
                        }
                    )

                # Remove music cues from text
                line = self.music_pattern.sub("", line)

            if line.strip():
                clean_text.append(line)
                char_position += len(line) + 1  # +1 for newline

        return {
            "text": "\n".join(clean_text),
            "music_cues": music_cues,
            "metadata": {
                "title": title or "Untitled Podcast",
                "character_count": char_position,
                "music_cue_count": len(music_cues),
            },
        }

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse script from file.

        Args:
            file_path: Path to script file

        Returns:
            Parsed script data
        """
        with open(file_path, "r", encoding="utf-8") as f:
            script_text = f.read()

        return self.parse(script_text)

    def validate_script(self, script_text: str) -> List[str]:
        """
        Validate script and return list of warnings/errors.

        Args:
            script_text: Raw script text

        Returns:
            List of validation messages (empty if valid)
        """
        warnings = []

        if not script_text.strip():
            warnings.append("Script is empty")

        if len(script_text) < 100:
            warnings.append("Script is very short (less than 100 characters)")

        if len(script_text) > 50000:
            warnings.append("Script is very long (over 50,000 characters)")

        return warnings
