"""Performance benchmarks for critical components.

These tests use pytest-benchmark to ensure hot paths remain efficient.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


@pytest.mark.performance
@pytest.mark.benchmark
def test_script_parser_parse_speed(benchmark, test_config, sample_script_text):
    """Benchmark script parsing to catch regressions in text processing."""
    from src.core.script_parser import ScriptParser

    parser = ScriptParser(test_config)

    def run_parse():
        parser.parse(sample_script_text)

    benchmark(run_parse)


@pytest.mark.performance
@pytest.mark.benchmark
def test_tts_cache_key_generation_speed(benchmark, test_config, tmp_path):
    """Benchmark cache-key generation (invoked each TTS request)."""
    from src.core.tts_engine import TTSEngine

    heavy_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 20

    with patch("src.core.tts_engine.get_gpu_manager") as mock_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        mock_gpu.return_value = gpu

        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        test_config["storage"]["cache_dir"] = str(tmp_path / "cache" )
        test_config["storage"]["outputs_dir"] = str(tmp_path / "out" )

        with patch.dict("sys.modules", {"gtts": MagicMock(gTTS=MagicMock())}):
            engine = TTSEngine(test_config)

    benchmark(engine._get_cache_key, heavy_text)


@pytest.mark.performance
@pytest.mark.benchmark
def test_audio_mixer_mix_speed(benchmark, test_config, tmp_path):
    """Benchmark the audio mixing pipeline with generated waveforms."""
    from src.core.audio_mixer import AudioMixer

    voice = tmp_path / "voice.wav"
    music = tmp_path / "music.wav"

    sample_rate = 24000
    duration = 2
    samples = int(sample_rate * duration)
    voice_data = (np.sin(np.linspace(0, 1000, samples))).astype(np.float32)
    music_data = (np.sin(np.linspace(0, 2000, samples))).astype(np.float32)

    import soundfile as sf

    sf.write(str(voice), voice_data, sample_rate)
    sf.write(str(music), music_data, sample_rate)

    mixer = AudioMixer(test_config)

    def run_mix():
        mixer.mix(voice, music)

    benchmark(run_mix)
