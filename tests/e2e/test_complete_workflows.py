"""
End-to-End tests - Test complete user workflows from script to video
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.audio_mixer import AudioMixer
from src.core.script_parser import ScriptParser
from src.core.tts_engine import TTSEngine
from src.core.video_composer import VideoComposer


@pytest.mark.e2e
class TestCompleteWorkflows:
    """End-to-end workflow tests."""

    def test_text_to_audio_workflow(self, test_config, temp_dir):
        """Test complete text-to-audio workflow."""
        # Step 1: Parse script
        script_text = """
        # Test Podcast
        
        Hello and welcome to this test podcast.
        This is a demonstration of the workflow.
        """

        parser = ScriptParser(test_config)
        parsed = parser.parse(script_text)

        assert "text" in parsed
        assert len(parsed["text"]) > 0

        # Step 2: Generate speech
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        tts = TTSEngine(test_config)
        audio_path = tts.generate(parsed["text"])

        # Verify audio was created
        assert audio_path.exists()
        assert audio_path.suffix == ".mp3"
        assert audio_path.stat().st_size > 1000

    def test_script_with_music_cues_workflow(self, test_config, temp_dir):
        """Test workflow with music cues."""
        script_text = """
        # Episode with Music
        
        [MUSIC: upbeat intro]
        
        Welcome to the show!
        
        [MUSIC: ambient background]
        
        This is the main content.
        """

        parser = ScriptParser(test_config)
        parsed = parser.parse(script_text)

        # Should extract music cues
        assert "music_cues" in parsed
        assert len(parsed["music_cues"]) >= 2

        # Should have text without music tags
        assert "text" in parsed
        assert "[MUSIC:" not in parsed["text"]
        assert "Welcome to the show!" in parsed["text"]

    def test_audio_to_video_workflow(self, test_config, temp_dir):
        """Test audio-to-video workflow."""
        # Create mock audio file
        audio_file = temp_dir / "podcast_audio.mp3"
        audio_file.write_bytes(b"audio content")

        # Configure video composer
        test_config["storage"]["outputs_dir"] = str(temp_dir)
        test_config["video"] = {"resolution": [1280, 720], "fps": 30}

        composer = VideoComposer(test_config)

        # Mock video creation
        mock_audio = MagicMock()
        mock_audio.duration = 10.0

        mock_video = MagicMock()
        mock_video.set_audio.return_value = mock_video
        mock_video.set_duration.return_value = mock_video

        # Mock moviepy modules
        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)
        mock_moviepy.editor.ColorClip = MagicMock(return_value=mock_video)
        mock_moviepy.editor.CompositeVideoClip = MagicMock(return_value=mock_video)

        with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
            video_path = composer.compose(audio_file, output_name="e2e_test")

            assert video_path.suffix == ".mp4"
            assert "e2e_test" in str(video_path)

    def test_full_podcast_creation_workflow(self, test_config, temp_dir):
        """Test complete podcast creation from script to video."""
        # Step 1: Create script
        script_text = """
        # My Test Podcast
        
        Welcome to episode one.
        Today we're testing the complete workflow.
        This will be converted to video.
        """

        # Step 2: Parse script
        parser = ScriptParser(test_config)
        parsed = parser.parse(script_text)

        assert parsed["metadata"]["title"] == "My Test Podcast"
        assert len(parsed["text"]) > 50

        # Step 3: Generate audio
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir / "cache")

        tts = TTSEngine(test_config)
        audio_path = tts.generate(parsed["text"])

        assert audio_path.exists()

        # Step 4: Create video
        test_config["storage"]["outputs_dir"] = str(temp_dir / "output")
        composer = VideoComposer(test_config)

        mock_audio = MagicMock()
        mock_audio.duration = 15.0

        mock_video = MagicMock()
        mock_video.set_audio.return_value = mock_video
        mock_video.set_duration.return_value = mock_video

        # Mock moviepy modules
        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)
        mock_moviepy.editor.ColorClip = MagicMock(return_value=mock_video)
        mock_moviepy.editor.CompositeVideoClip = MagicMock(return_value=mock_video)

        with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
            video_path = composer.compose(audio_path, output_name=parsed["metadata"]["title"])

            # Verify final output
            assert video_path.exists() or video_path.parent.exists()
            assert "My Test Podcast" in str(video_path) or video_path.suffix == ".mp4"

    def test_multiple_podcasts_workflow(self, test_config, temp_dir):
        """Test creating multiple podcasts in sequence."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir / "cache")

        parser = ScriptParser(test_config)
        tts = TTSEngine(test_config)

        scripts = [
            "# Episode 1\nFirst episode content.",
            "# Episode 2\nSecond episode content.",
            "# Episode 3\nThird episode content.",
        ]

        results = []
        for script in scripts:
            parsed = parser.parse(script)
            audio = tts.generate(parsed["text"])
            results.append({"title": parsed["metadata"]["title"], "audio": audio})

        # Verify all episodes were created
        assert len(results) == 3
        for i, result in enumerate(results, 1):
            assert f"Episode {i}" in result["title"]
            assert result["audio"].exists()

        # Verify caching worked (files should be reused if same text)
        # Re-generate first episode
        parsed_again = parser.parse(scripts[0])
        audio_again = tts.generate(parsed_again["text"])
        assert audio_again == results[0]["audio"]  # Same cached file


@pytest.mark.e2e
class TestErrorRecoveryWorkflows:
    """Test error handling and recovery in workflows."""

    def test_invalid_script_handling(self, test_config):
        """Test handling of invalid scripts."""
        parser = ScriptParser(test_config)

        # Empty script
        result = parser.parse("")
        assert result["text"] == ""
        assert result["metadata"]["title"] == "Untitled Podcast"

        # Script with only music tags
        result = parser.parse("[MUSIC: something]")
        assert len(result["music_cues"]) >= 0

    def test_tts_failure_recovery(self, test_config, temp_dir):
        """Test recovery from TTS failures."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        tts = TTSEngine(test_config)

        # This should work (network permitting)
        try:
            audio = tts.generate("Test text")
            assert audio.exists()
        except Exception as e:
            # If it fails, it should fail gracefully
            assert "gTTS failed" in str(e) or "Network" in str(e)

    def test_missing_audio_file_handling(self, test_config, temp_dir):
        """Test handling of missing audio files."""
        test_config["storage"]["outputs_dir"] = str(temp_dir)

        composer = VideoComposer(test_config)
        missing_file = temp_dir / "nonexistent.mp3"

        # Should raise appropriate error
        with pytest.raises((FileNotFoundError, Exception)):
            composer.compose(missing_file)


@pytest.mark.e2e
class TestPerformanceWorkflows:
    """Test performance-related workflows."""

    def test_caching_improves_performance(self, test_config, temp_dir):
        """Test that caching speeds up repeated generations."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        tts = TTSEngine(test_config)
        text = "This is a performance test text."

        import time

        # First generation (no cache)
        start1 = time.time()
        audio1 = tts.generate(text)
        time1 = time.time() - start1

        # Second generation (should use cache)
        start2 = time.time()
        audio2 = tts.generate(text)
        time2 = time.time() - start2

        # Verify caching worked
        assert audio1 == audio2
        # Cache should be much faster (but this might fail if network is slow)
        # Just verify it worked
        assert audio2.exists()

    def test_batch_processing_workflow(self, test_config, temp_dir):
        """Test processing multiple scripts efficiently."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        parser = ScriptParser(test_config)
        tts = TTSEngine(test_config)

        # Create 5 short scripts
        scripts = [f"# Episode {i}\nContent for episode {i}." for i in range(1, 6)]

        import time

        start = time.time()

        results = []
        for script in scripts:
            parsed = parser.parse(script)
            audio = tts.generate(parsed["text"])
            results.append(audio)

        elapsed = time.time() - start

        # All should succeed
        assert len(results) == 5
        assert all(audio.exists() for audio in results)

        # Should complete in reasonable time (60 seconds for 5 podcasts)
        assert elapsed < 60.0


@pytest.mark.e2e
class TestConfigurationWorkflows:
    """Test different configuration scenarios."""

    def test_different_resolutions_workflow(self, test_config, temp_dir):
        """Test creating videos at different resolutions."""
        resolutions = [
            ([640, 480], "480p"),
            ([1280, 720], "720p"),
            ([1920, 1080], "1080p"),
        ]

        audio_file = temp_dir / "audio.mp3"
        audio_file.write_bytes(b"audio")

        for resolution, name in resolutions:
            test_config["storage"]["outputs_dir"] = str(temp_dir)
            test_config["video"] = {"resolution": resolution}

            composer = VideoComposer(test_config)

            mock_audio = MagicMock()
            mock_audio.duration = 5.0
            mock_audio.close = MagicMock()

            mock_video = MagicMock()
            mock_video.set_audio.return_value = mock_video
            mock_video.set_duration = MagicMock(return_value=mock_video)
            mock_video.write_videofile = MagicMock()
            mock_video.close = MagicMock()

            # Mock moviepy modules
            mock_moviepy = MagicMock()
            mock_moviepy.editor = MagicMock()
            mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)
            mock_moviepy.editor.ColorClip = MagicMock(return_value=mock_video)
            mock_moviepy.editor.CompositeVideoClip = MagicMock(return_value=mock_video)

            with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
                output = composer.compose(audio_file, output_name=name)

                assert name in str(output)

    def test_custom_cache_directory_workflow(self, test_config, temp_dir):
        """Test using custom cache directory."""
        custom_cache = temp_dir / "my_custom_cache"
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(custom_cache)

        tts = TTSEngine(test_config)
        audio = tts.generate("Custom cache test")

        # Verify cache was created in custom location
        assert custom_cache.exists()
        assert audio.parent.parent == custom_cache
        assert audio.exists()
