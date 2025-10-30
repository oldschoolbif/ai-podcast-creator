"""
Test Data Factories
Create test data easily and consistently using the Factory pattern
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigFactory:
    """Factory for creating test configurations."""

    @staticmethod
    def create(
        temp_dir: Optional[Path] = None,
        tts_engine: str = "gtts",
        avatar_engine: str = "static",
        music_engine: str = "none",
        **overrides,
    ) -> Dict[str, Any]:
        """
        Create a test configuration with sensible defaults.

        Args:
            temp_dir: Temporary directory for test outputs
            tts_engine: TTS engine to use
            avatar_engine: Avatar engine to use
            music_engine: Music engine to use
            **overrides: Any config values to override

        Returns:
            Complete configuration dictionary

        Example:
            config = ConfigFactory.create(
                temp_dir=temp_dir,
                tts_engine='coqui',
                storage={'cache_dir': '/custom/cache'}
            )
        """
        if temp_dir is None:
            temp_dir = Path(tempfile.mkdtemp())

        base_config = {
            "tts": {
                "engine": tts_engine,
                "gtts_tld": "co.uk",
                "coqui": {"model": "tts_models/en/ljspeech/tacotron2-DDC", "use_gpu": False},
                "elevenlabs": {"api_key": "test_key", "voice_id": "test_voice"},
                "azure": {"subscription_key": "test_key", "region": "eastus"},
            },
            "avatar": {
                "engine": avatar_engine,
                "source_image": str(temp_dir / "avatar.jpg"),
                "models_dir": str(temp_dir / "models"),
                "sadtalker": {"checkpoint_dir": str(temp_dir / "checkpoints"), "enhancer": None},
                "wav2lip": {"model_path": str(temp_dir / "wav2lip.pth")},
            },
            "music": {
                "engine": music_engine,
                "musicgen": {"model": "facebook/musicgen-small", "duration": 30, "use_gpu": False},
            },
            "video": {
                "fps": 30,
                "resolution": (1920, 1080),
                "codec": "libx264",
                "background_path": str(temp_dir / "background.jpg"),
                "bitrate": "5M",
            },
            "storage": {
                "cache_dir": str(temp_dir / "cache"),
                "outputs_dir": str(temp_dir / "output"),
                "models_dir": str(temp_dir / "models"),
            },
        }

        # Apply overrides recursively
        return _deep_merge(base_config, overrides)


class ScriptFactory:
    """Factory for creating test podcast scripts."""

    @staticmethod
    def create_simple(title: str = "Test Podcast") -> str:
        """Create a simple test script."""
        return f"""# {title}

Welcome to this test podcast. This is a simple script for testing purposes.
"""

    @staticmethod
    def create_with_music(title: str = "Test Podcast") -> str:
        """Create a script with music cues."""
        return f"""# {title}

[MUSIC: calm ambient background music]

Welcome to this test podcast.

[MUSIC: upbeat energetic music]

This script includes multiple music cues for testing.
"""

    @staticmethod
    def create_long(title: str = "Long Test Podcast", word_count: int = 1000) -> str:
        """Create a long script with specified word count."""
        words = ["This is a test word."] * (word_count // 5)
        content = " ".join(words)
        return f"""# {title}

{content}
"""

    @staticmethod
    def create_with_sections(title: str = "Sectioned Podcast") -> str:
        """Create a script with multiple sections."""
        return f"""# {title}

## Introduction
Welcome to this podcast about testing.

[MUSIC: intro music]

## Main Content
This is the main content section with lots of information.

## Conclusion
Thank you for listening to this test podcast.

[MUSIC: outro music]
"""

    @staticmethod
    def create_custom(
        title: str = "Custom Podcast", sections: int = 3, music_cues: int = 2, word_count_per_section: int = 50
    ) -> str:
        """Create a custom script with specified parameters."""
        script = f"# {title}\n\n"

        for i in range(sections):
            script += f"## Section {i+1}\n"
            words = " ".join([f"word{j}" for j in range(word_count_per_section)])
            script += f"{words}\n\n"

            if i < music_cues:
                script += f"[MUSIC: music cue {i+1}]\n\n"

        return script


class AudioFactory:
    """Factory for creating test audio files."""

    @staticmethod
    def create_file(temp_dir: Path, name: str = "test_audio", duration: float = 5.0, format: str = "mp3") -> Path:
        """
        Create a test audio file.

        Note: Creates an empty placeholder file for testing.
        For actual audio content, use real audio generation.
        """
        audio_path = temp_dir / f"{name}.{format}"
        audio_path.touch()

        # Add metadata comment in file
        with open(audio_path, "w") as f:
            f.write(f"# Test audio file: {duration}s duration\n")

        return audio_path


class VideoFactory:
    """Factory for creating test video files."""

    @staticmethod
    def create_file(temp_dir: Path, name: str = "test_video", duration: float = 5.0, format: str = "mp4") -> Path:
        """
        Create a test video file.

        Note: Creates an empty placeholder file for testing.
        """
        video_path = temp_dir / f"{name}.{format}"
        video_path.touch()

        return video_path


class ImageFactory:
    """Factory for creating test image files."""

    @staticmethod
    def create_file(
        temp_dir: Path, name: str = "test_image", width: int = 1920, height: int = 1080, format: str = "jpg"
    ) -> Path:
        """
        Create a test image file.

        Note: Creates an empty placeholder file for testing.
        For real images, consider using PIL/Pillow.
        """
        image_path = temp_dir / f"{name}.{format}"
        image_path.touch()

        return image_path


class PodcastFactory:
    """High-level factory for creating complete test podcast configurations."""

    @staticmethod
    def create_full(
        temp_dir: Path,
        title: str = "Test Podcast",
        tts_engine: str = "gtts",
        with_music: bool = False,
        with_avatar: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a complete podcast test setup.

        Returns:
            Dictionary with 'config', 'script', and 'paths'
        """
        # Create configuration
        config = ConfigFactory.create(
            temp_dir=temp_dir,
            tts_engine=tts_engine,
            avatar_engine="static" if with_avatar else "none",
            music_engine="musicgen" if with_music else "none",
        )

        # Create script
        if with_music:
            script = ScriptFactory.create_with_music(title)
        else:
            script = ScriptFactory.create_simple(title)

        # Create necessary files
        paths = {
            "script": temp_dir / "script.txt",
            "avatar_image": temp_dir / "avatar.jpg",
            "background": temp_dir / "background.jpg",
        }

        # Write script
        paths["script"].write_text(script)

        # Create placeholder images
        ImageFactory.create_file(temp_dir, "avatar")
        ImageFactory.create_file(temp_dir, "background")

        return {
            "config": config,
            "script": script,
            "paths": paths,
            "metadata": {
                "title": title,
                "created_at": datetime.now().isoformat(),
                "tts_engine": tts_engine,
                "has_music": with_music,
                "has_avatar": with_avatar,
            },
        }


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override dict into base dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# ==============================================================================
# USAGE EXAMPLES
# ==============================================================================

"""
## Basic Usage

### Simple Config
```python
def test_something(temp_dir):
    config = ConfigFactory.create(temp_dir)
    engine = TTSEngine(config)
    # ...
```

### Custom Config
```python
def test_with_coqui(temp_dir):
    config = ConfigFactory.create(
        temp_dir=temp_dir,
        tts_engine='coqui',
        tts={'coqui': {'use_gpu': True}}
    )
    # ...
```

### Scripts
```python
def test_simple_script(temp_dir):
    script = ScriptFactory.create_simple("My Test")
    # ...

def test_with_music(temp_dir):
    script = ScriptFactory.create_with_music("Music Test")
    # ...

def test_custom(temp_dir):
    script = ScriptFactory.create_custom(
        sections=5,
        music_cues=3,
        word_count_per_section=100
    )
    # ...
```

### Full Podcast Setup
```python
def test_full_podcast(temp_dir):
    podcast = PodcastFactory.create_full(
        temp_dir=temp_dir,
        title="Integration Test",
        tts_engine='gtts',
        with_music=True,
        with_avatar=True
    )
    
    config = podcast['config']
    script = podcast['script']
    paths = podcast['paths']
    
    # Run your test...
```

## Benefits

### Before (Manual Setup)
```python
def test_tts_generation(temp_dir):
    # 20+ lines of manual config setup
    config = {
        'tts': {
            'engine': 'gtts',
            'gtts_tld': 'co.uk',
            # ... many more lines ...
        },
        'storage': {
            # ... more lines ...
        },
        # ...
    }
    # Test code...
```

### After (Factory)
```python
def test_tts_generation(temp_dir):
    config = ConfigFactory.create(temp_dir)
    # Test code...
```

## Advanced Patterns

### Parameterized Tests with Factories
```python
@pytest.mark.parametrize("engine", ['gtts', 'coqui', 'elevenlabs'])
def test_all_engines(temp_dir, engine):
    config = ConfigFactory.create(temp_dir, tts_engine=engine)
    # Test works for all engines!
```

### Custom Factories
```python
class MyTestFactory:
    @staticmethod
    def create_edge_case_config(temp_dir):
        base = ConfigFactory.create(temp_dir)
        base['tts']['gtts_tld'] = 'com.au'  # Australian accent
        base['video']['fps'] = 60  # High FPS
        return base
```
"""
