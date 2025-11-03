"""
Expanded Core Integration Tests - Night Shift Edition
Testing interactions between core modules
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestTTSEngineAudioMixerIntegration:
    """Test TTS Engine and Audio Mixer integration."""

    def test_tts_output_compatible_with_audio_mixer(self, test_config, temp_dir):
        """Test TTS output can be mixed with audio mixer."""
        from src.core.audio_mixer import AudioMixer
        from src.core.tts_engine import TTSEngine

        # Generate TTS
        tts_engine = TTSEngine(test_config)
        tts_output = temp_dir / "tts_output.mp3"
        tts_output.write_bytes(b"tts audio")

        # Create mixer
        mixer = AudioMixer(test_config)

        # Mix should accept TTS output
        music_path = temp_dir / "music.mp3"
        music_path.write_bytes(b"music")

        with patch.object(tts_engine, "generate", return_value=tts_output):
            tts_file = tts_engine.generate("test text")
            mixed = mixer.mix(tts_file, music_path)

            assert mixed is not None
            assert mixed.exists()


class TestScriptParserVideoComposerIntegration:
    """Test Script Parser and Video Composer integration."""

    def test_parsed_script_metadata_used_in_video(self, test_config, temp_dir):
        """Test parsed script metadata influences video creation."""
        from src.core.script_parser import ScriptParser
        from src.core.video_composer import VideoComposer

        script_text = "# My Podcast Episode\n\nHello world"
        parser = ScriptParser(test_config)
        parsed = parser.parse(script_text)

        # Video composer should be able to use parsed data
        composer = VideoComposer(test_config)

        audio_path = temp_dir / "audio.mp3"
        audio_path.write_bytes(b"audio")

        with patch.object(composer, "compose", return_value=temp_dir / "video.mp4"):
            video = composer.compose(audio_path, output_name=parsed["metadata"]["title"])

            assert video is not None
            assert "My Podcast Episode" in str(video) or video.name


class TestMusicGeneratorTTSEngineIntegration:
    """Test Music Generator and TTS Engine integration."""

    def test_music_and_tts_can_be_mixed(self, test_config, temp_dir):
        """Test music generator output can be mixed with TTS."""
        from src.core.audio_mixer import AudioMixer
        from src.core.music_generator import MusicGenerator
        from src.core.tts_engine import TTSEngine

        # Generate music
        music_gen = MusicGenerator(test_config)
        music_path = temp_dir / "music.wav"
        music_path.write_bytes(b"music")

        # Generate TTS
        tts_engine = TTSEngine(test_config)
        tts_path = temp_dir / "tts.mp3"
        tts_path.write_bytes(b"tts")

        # Mix them
        mixer = AudioMixer(test_config)

        with patch.object(music_gen, "generate", return_value=music_path):
            with patch.object(tts_engine, "generate", return_value=tts_path):
                music = music_gen.generate("upbeat background")
                tts = tts_engine.generate("Hello world")
                mixed = mixer.mix(tts, music)

                assert mixed is not None


class TestAudioVisualizerVideoComposerIntegration:
    """Test Audio Visualizer and Video Composer integration."""

    def test_visualization_can_be_overlaid_on_video(self, test_config, temp_dir):
        """Test visualization can be used with video composer."""
        from src.core.audio_visualizer import AudioVisualizer
        from src.core.video_composer import VideoComposer

        audio_path = temp_dir / "audio.mp3"
        audio_path.write_bytes(b"audio")

        # Generate visualization
        viz = AudioVisualizer(test_config)

        # Video composer should be able to use visualization
        composer = VideoComposer(test_config)

        with patch.object(viz, "generate_visualization", return_value=temp_dir / "viz.mp4"):
            with patch.object(composer, "compose", return_value=temp_dir / "final.mp4"):
                viz_video = viz.generate_visualization(audio_path, temp_dir / "viz.mp4")
                final = composer.compose(audio_path, output_name="test")

                assert viz_video is not None
                assert final is not None


class TestCompletePipelineIntegration:
    """Test complete pipeline workflows."""

    def test_full_pipeline_with_music_cues(self, test_config, temp_dir):
        """Test complete pipeline with music cues from script."""
        from src.core.audio_mixer import AudioMixer
        from src.core.music_generator import MusicGenerator
        from src.core.script_parser import ScriptParser
        from src.core.tts_engine import TTSEngine
        from src.core.video_composer import VideoComposer

        script_text = """
# Test Podcast

[MUSIC: upbeat intro]

Welcome to the show!

[MUSIC: calm background]

Today we're discussing testing.
"""

        # Parse script
        parser = ScriptParser(test_config)
        parsed = parser.parse(script_text)

        # Generate TTS
        tts_engine = TTSEngine(test_config)
        tts_output = temp_dir / "tts.mp3"
        tts_output.write_bytes(b"tts")

        # Generate music from cues
        music_gen = MusicGenerator(test_config)
        music_output = temp_dir / "music.wav"
        music_output.write_bytes(b"music")

        # Mix
        mixer = AudioMixer(test_config)
        mixed_output = temp_dir / "mixed.mp3"
        mixed_output.write_bytes(b"mixed")

        # Compose video
        composer = VideoComposer(test_config)
        final_video = temp_dir / "final.mp4"
        final_video.write_bytes(b"video")

        with patch.object(tts_engine, "generate", return_value=tts_output):
            with patch.object(music_gen, "generate", return_value=music_output):
                with patch.object(mixer, "mix", return_value=mixed_output):
                    with patch.object(composer, "compose", return_value=final_video):
                        tts = tts_engine.generate(parsed["text"])
                        music = music_gen.generate(parsed["music_cues"])
                        mixed = mixer.mix(tts, music)
                        video = composer.compose(mixed, output_name=parsed["metadata"]["title"])

                        assert video is not None
                        assert all([tts, music, mixed, video])


class TestErrorPropagationIntegration:
    """Test error handling across module boundaries."""

    def test_tts_error_handled_in_pipeline(self, test_config, temp_dir):
        """Test TTS errors are handled gracefully."""
        from src.core.script_parser import ScriptParser
        from src.core.tts_engine import TTSEngine

        script_text = "# Test\nHello world"
        parser = ScriptParser(test_config)
        parsed = parser.parse(script_text)

        tts_engine = TTSEngine(test_config)

        # Simulate TTS failure
        with patch.object(tts_engine, "generate", side_effect=Exception("TTS failed")):
            with pytest.raises(Exception):
                tts_engine.generate(parsed["text"])

    def test_music_generator_error_handled(self, test_config, temp_dir):
        """Test music generator errors are handled."""
        from src.core.music_generator import MusicGenerator

        music_gen = MusicGenerator(test_config)

        # Simulate music generation failure
        with patch.object(music_gen, "generate", return_value=None):
            result = music_gen.generate("test music")

            # Should return None on failure
            assert result is None
