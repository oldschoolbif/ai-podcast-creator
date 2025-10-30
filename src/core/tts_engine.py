"""
Text-to-Speech Engine Module
Handles speech generation using various TTS providers
"""

import hashlib
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path for GPU utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.gpu_utils import get_gpu_manager


class TTSEngine:
    """Text-to-Speech generation using configured provider."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize TTS engine.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.engine_type = config.get("tts", {}).get("engine", "gtts")
        self.cache_dir = Path(config["storage"]["cache_dir"]) / "tts"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Get GPU manager for optimization
        self.gpu_manager = get_gpu_manager()
        self.device = self.gpu_manager.get_device()
        self.use_gpu = self.gpu_manager.gpu_available

        # Initialize appropriate engine
        if self.engine_type == "gtts":
            self._init_gtts()
        elif self.engine_type == "coqui":
            self._init_coqui()
        elif self.engine_type == "elevenlabs":
            self._init_elevenlabs()
        elif self.engine_type == "azure":
            self._init_azure()
        elif self.engine_type == "piper":
            self._init_piper()
        elif self.engine_type == "pyttsx3":
            self._init_pyttsx3()
        else:
            # Default to gTTS if unknown
            self._init_gtts()

    def _init_gtts(self):
        """Initialize Google TTS (basic, free, works out of the box)."""
        try:
            from gtts import gTTS

            self.gtts_available = True
        except ImportError:
            raise ImportError("gTTS not installed. Run: pip install gTTS")

    def _init_coqui(self):
        """Initialize Coqui TTS with GPU acceleration."""
        try:
            import os

            import torch
            from TTS.api import TTS

            # Accept Coqui license automatically (non-commercial use)
            os.environ["COQUI_TOS_AGREED"] = "1"

            model_name = self.config["tts"]["coqui"]["model"]

            # Initialize with GPU if available
            if self.use_gpu:
                print(f"✓ Initializing Coqui TTS on GPU ({self.device})")
                self.tts = TTS(model_name=model_name, gpu=True, progress_bar=True)

                # Enable performance optimizations
                if hasattr(self.tts, "synthesizer") and hasattr(self.tts.synthesizer, "tts_model"):
                    model = self.tts.synthesizer.tts_model
                    if hasattr(model, "to"):
                        model.to(self.device)

                    # NOTE: xtts_v2 doesn't support FP16 well, skip for xtts models
                    # Enable mixed precision if supported (disabled for xtts for stability)
                    if "xtts" not in model_name.lower():
                        perf_config = self.gpu_manager.get_performance_config()
                        if perf_config["use_fp16"]:
                            try:
                                model.half()
                                print("✓ FP16 mixed precision enabled for TTS")
                            except Exception:
                                pass
            else:
                print("⚠ Initializing Coqui TTS on CPU (slower)")
                self.tts = TTS(model_name=model_name, gpu=False)

        except ImportError as e:
            raise ImportError(f"Coqui TTS not installed. Run: pip install TTS\nError: {e}")
        except Exception as e:
            print(f"⚠ Coqui TTS initialization error: {e}")
            raise

    def _init_elevenlabs(self):
        """Initialize ElevenLabs API."""
        try:
            from elevenlabs import generate, set_api_key

            api_key = self.config["tts"]["elevenlabs"]["api_key"]
            set_api_key(api_key)
        except ImportError:
            raise ImportError("ElevenLabs not installed. Run: pip install elevenlabs")

    def _init_azure(self):
        """Initialize Azure Speech Service."""
        try:
            import azure.cognitiveservices.speech as speechsdk

            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.config["tts"]["azure"]["api_key"], region=self.config["tts"]["azure"]["region"]
            )
        except ImportError:
            raise ImportError("Azure Speech not installed. Run: pip install azure-cognitiveservices-speech")

    def _init_piper(self):
        """Initialize Piper TTS."""
        pass  # TODO: Implement if needed

    def _init_pyttsx3(self):
        """Initialize pyttsx3 (offline TTS with voice control)."""
        try:
            import pyttsx3

            self.pyttsx3_engine = pyttsx3.init()
            self.pyttsx3_available = True

            # Get available voices
            voices = self.pyttsx3_engine.getProperty("voices")

            # Get voice settings from config
            voice_id = self.config.get("tts", {}).get("pyttsx3_voice_id", 24)  # Default to American English
            rate = self.config.get("tts", {}).get("pyttsx3_rate", 165)  # Speaking speed

            # Configure voice settings
            self.pyttsx3_engine.setProperty("rate", rate)
            self.pyttsx3_engine.setProperty("volume", 0.9)

            # Set voice by index
            if len(voices) > voice_id:
                self.pyttsx3_engine.setProperty("voice", voices[voice_id].id)
                print(f"✓ Using pyttsx3 voice: {voices[voice_id].name} (Voice {voice_id})")
            elif len(voices) > 0:
                # Fallback to first voice if specified ID doesn't exist
                self.pyttsx3_engine.setProperty("voice", voices[0].id)
                print(f"✓ Using pyttsx3 voice: {voices[0].name} (fallback)")

        except Exception as e:
            print(f"⚠ pyttsx3 initialization failed: {e}")
            print("  Falling back to gTTS")
            self._init_gtts()

    def generate(self, text: str, output_path: Optional[Path] = None) -> Path:
        """
        Generate speech from text.

        Args:
            text: Text to convert to speech
            output_path: Optional output file path

        Returns:
            Path to generated audio file
        """
        # Check cache first
        cache_key = self._get_cache_key(text)
        cached_path = self.cache_dir / f"{cache_key}.mp3"

        if cached_path.exists():
            return cached_path

        # Generate based on engine type
        if self.engine_type == "gtts":
            audio_path = self._generate_gtts(text, cached_path)
        elif self.engine_type == "coqui":
            audio_path = self._generate_coqui(text, cached_path)
        elif self.engine_type == "elevenlabs":
            audio_path = self._generate_elevenlabs(text, cached_path)
        elif self.engine_type == "azure":
            audio_path = self._generate_azure(text, cached_path)
        elif self.engine_type == "piper":
            audio_path = self._generate_piper(text, cached_path)
        elif self.engine_type == "pyttsx3":
            audio_path = self._generate_pyttsx3(text, cached_path)
        elif self.engine_type == "edge":
            audio_path = self._generate_edge(text, cached_path)
        else:
            audio_path = self._generate_gtts(text, cached_path)

        return audio_path

    def _generate_gtts(self, text: str, output_path: Path) -> Path:
        """Generate speech using Google TTS (simple, free, works immediately)."""
        import time

        from gtts import gTTS

        # Get TLD from config, default to British (co.uk)
        # Use 'com' for more neutral/American accent, 'co.uk' for British, 'com.au' for Australian
        tld = self.config.get("tts", {}).get("gtts_tld", "co.uk")

        # Retry logic for network issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                tts = gTTS(text=text, lang="en", tld=tld, slow=False)
                tts.save(str(output_path))
                return output_path
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠ gTTS attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(1)
                else:
                    raise Exception(f"gTTS failed after {max_retries} attempts: {e}")

        return output_path

    def _generate_coqui(self, text: str, output_path: Path) -> Path:
        """Generate speech using Coqui TTS with GPU acceleration."""
        try:
            import torch

            # Clear GPU cache before generation
            if self.use_gpu:
                self.gpu_manager.clear_cache()

            # Get model name and language
            model_name = self.config["tts"]["coqui"]["model"]
            language = self.config["tts"]["coqui"].get("language", "en")
            speaker = self.config["tts"]["coqui"].get("speaker", "Andrew Chipper")  # Default speaker
            speaker_wav = self.config["tts"]["coqui"].get("speaker_wav", None)

            # Use GPU-accelerated generation
            with torch.inference_mode():  # Faster than torch.no_grad()
                # xtts_v2 is a multi-speaker model that needs speaker reference
                if "xtts" in model_name.lower():
                    # For xtts models, use built-in speaker or reference audio
                    if speaker_wav and Path(speaker_wav).exists():
                        self.tts.tts_to_file(
                            text=text, file_path=str(output_path), speaker_wav=speaker_wav, language=language
                        )
                    else:
                        # Use speaker from config
                        self.tts.tts_to_file(
                            text=text, file_path=str(output_path), language=language, speaker=speaker  # From config
                        )
                else:
                    # For other models (single-speaker)
                    self.tts.tts_to_file(text=text, file_path=str(output_path), language=language)

            # Clear cache after generation
            if self.use_gpu:
                self.gpu_manager.clear_cache()

            return output_path

        except Exception as e:
            print(f"⚠ Coqui TTS generation error: {type(e).__name__}: {e}")
            raise

    def _generate_elevenlabs(self, text: str, output_path: Path) -> Path:
        """Generate speech using ElevenLabs API."""
        import os

        from elevenlabs import VoiceSettings
        from elevenlabs.client import ElevenLabs

        # Get API key from config or environment
        api_key = self.config.get("tts", {}).get("elevenlabs", {}).get("api_key")
        if not api_key:
            api_key = os.getenv("ELEVENLABS_API_KEY")

        if not api_key:
            raise ValueError("ElevenLabs API key not found. Set ELEVENLABS_API_KEY in .env or config")

        # Get voice settings from config
        voice_id = self.config.get("tts", {}).get("elevenlabs", {}).get("voice_id", "pNInz6obpgDQGcFmaJgB")  # Adam
        model = self.config.get("tts", {}).get("elevenlabs", {}).get("model", "eleven_turbo_v2_5")  # Fastest model
        stability = self.config.get("tts", {}).get("elevenlabs", {}).get("stability", 0.5)
        similarity_boost = self.config.get("tts", {}).get("elevenlabs", {}).get("similarity_boost", 0.75)

        # Initialize client
        client = ElevenLabs(api_key=api_key)

        # Generate audio
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id=model,
            voice_settings=VoiceSettings(
                stability=stability, similarity_boost=similarity_boost, style=0.0, use_speaker_boost=True
            ),
        )

        # Save audio
        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)

        return output_path

    def _generate_azure(self, text: str, output_path: Path) -> Path:
        """Generate speech using Azure."""
        import azure.cognitiveservices.speech as speechsdk

        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_config)
        synthesizer.speak_text(text)
        return output_path

    def _generate_piper(self, text: str, output_path: Path) -> Path:
        """Generate speech using Piper."""
        # TODO: Implement Piper TTS generation
        output_path.touch()
        return output_path

    def _generate_pyttsx3(self, text: str, output_path: Path) -> Path:
        """Generate speech using pyttsx3 (offline, male voice)."""
        import pyttsx3

        # Save to WAV first (pyttsx3 native format)
        wav_path = output_path.with_suffix(".wav")
        self.pyttsx3_engine.save_to_file(text, str(wav_path))
        self.pyttsx3_engine.runAndWait()

        # Convert WAV to MP3 using pydub
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_wav(str(wav_path))
            audio.export(str(output_path), format="mp3")
            wav_path.unlink()  # Delete temporary WAV
        except Exception as e:
            print(f"⚠ MP3 conversion failed: {e}, using WAV")
            # If conversion fails, just rename WAV to MP3
            wav_path.rename(output_path)

        return output_path

    def _generate_edge(self, text: str, output_path: Path) -> Path:
        """Generate speech using Microsoft Edge TTS (free, natural, multiple voices)."""
        import asyncio

        import edge_tts

        # Get voice from config
        voice = self.config.get("tts", {}).get("edge_voice", "en-US-GuyNeural")  # Default male US
        rate = self.config.get("tts", {}).get("edge_rate", "+0%")  # Speed adjustment
        pitch = self.config.get("tts", {}).get("edge_pitch", "+0Hz")  # Pitch adjustment

        async def _generate():
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(str(output_path))

        # Run async function
        try:
            asyncio.run(_generate())
        except RuntimeError:
            # If event loop already exists (in some environments), use it
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_generate())

        return output_path

    def _get_cache_key(self, text: str) -> str:
        """
        Generate cache key for text.

        Args:
            text: Input text

        Returns:
            MD5 hash of text + engine config + voice parameters
        """
        # Include voice-specific parameters in cache key
        voice_params = ""

        if self.engine_type == "gtts":
            # Include TLD (accent) in cache key
            tld = self.config.get("tts", {}).get("gtts_tld", "co.uk")
            voice_params = f"_tld_{tld}"
        elif self.engine_type == "coqui":
            # Include speaker in cache key
            speaker = self.config.get("tts", {}).get("coqui", {}).get("speaker", "Andrew Chipper")
            voice_params = f"_speaker_{speaker}"
        elif self.engine_type == "pyttsx3":
            # Include voice ID in cache key
            voice_id = self.config.get("tts", {}).get("pyttsx3_voice_id", 24)
            voice_params = f"_voice_{voice_id}"
        elif self.engine_type == "edge":
            # Include voice name in cache key
            voice = self.config.get("tts", {}).get("edge_voice", "en-US-GuyNeural")
            voice_params = f"_voice_{voice}"
        elif self.engine_type == "elevenlabs":
            # Include voice ID in cache key
            voice_id = self.config.get("tts", {}).get("elevenlabs", {}).get("voice_id", "default")
            voice_params = f"_voice_{voice_id}"

        content = f"{text}_{self.engine_type}{voice_params}"
        return hashlib.md5(content.encode()).hexdigest()
