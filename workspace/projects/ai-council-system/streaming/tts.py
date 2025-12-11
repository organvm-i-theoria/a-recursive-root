"""
Text-to-Speech System

Supports multiple TTS engines:
- ElevenLabs (highest quality, requires API key)
- pyttsx3 (offline, free)
- gTTS (Google TTS, free, requires internet)
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class TTSEngine(Enum):
    """Supported TTS engines"""
    ELEVENLABS = "elevenlabs"
    PYTTSX3 = "pyttsx3"
    GTTS = "gtts"


class TTSProvider(ABC):
    """Base class for TTS providers"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = Path(config.get("output_dir", "output/audio"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Synthesize text to speech

        Args:
            text: Text to synthesize
            voice_id: Voice identifier (provider-specific)
            output_path: Output file path (auto-generated if None)

        Returns:
            Path to generated audio file
        """
        pass

    def _get_output_path(self, prefix: str = "speech") -> Path:
        """Generate output file path"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{prefix}_{timestamp}.mp3"


class ElevenLabsProvider(TTSProvider):
    """
    ElevenLabs TTS provider (highest quality)

    Requires: pip install elevenlabs
    Requires: ElevenLabs API key
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("elevenlabs_api_key")
        if not self.api_key:
            raise ValueError("ElevenLabs API key required")

        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize ElevenLabs client"""
        try:
            from elevenlabs import set_api_key
            set_api_key(self.api_key)
            logger.info("ElevenLabs client initialized")
        except ImportError:
            logger.error(
                "elevenlabs library not installed. "
                "Install with: pip install elevenlabs"
            )
            raise

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """Synthesize using ElevenLabs"""
        try:
            from elevenlabs import generate, Voice

            voice_id = voice_id or "21m00Tcm4TlvDq8ikWAM"  # Default: Rachel
            output_path = output_path or self._get_output_path()

            logger.debug(f"Synthesizing with ElevenLabs (voice: {voice_id})")

            # Generate audio (synchronous)
            loop = asyncio.get_event_loop()
            audio = await loop.run_in_executor(
                None,
                lambda: generate(
                    text=text,
                    voice=Voice(voice_id=voice_id),
                    model="eleven_monolingual_v1"
                )
            )

            # Save audio
            with open(output_path, "wb") as f:
                f.write(audio)

            logger.info(f"Generated audio: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"ElevenLabs synthesis failed: {e}")
            raise


class Pyttsx3Provider(TTSProvider):
    """
    pyttsx3 TTS provider (offline, free)

    Requires: pip install pyttsx3
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.engine = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize pyttsx3 engine"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()

            # Configure
            rate = self.config.get("speed", 1.0)
            volume = self.config.get("volume", 1.0)

            self.engine.setProperty("rate", int(200 * rate))
            self.engine.setProperty("volume", volume)

            logger.info("pyttsx3 engine initialized")
        except ImportError:
            logger.error(
                "pyttsx3 library not installed. "
                "Install with: pip install pyttsx3"
            )
            raise

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """Synthesize using pyttsx3"""
        try:
            output_path = output_path or self._get_output_path()

            logger.debug("Synthesizing with pyttsx3")

            # Select voice if specified
            if voice_id:
                voices = self.engine.getProperty("voices")
                for voice in voices:
                    if voice_id.lower() in voice.name.lower():
                        self.engine.setProperty("voice", voice.id)
                        break

            # Generate audio (synchronous)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.engine.save_to_file(text, str(output_path))
            )
            await loop.run_in_executor(None, self.engine.runAndWait)

            logger.info(f"Generated audio: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"pyttsx3 synthesis failed: {e}")
            raise


class GTTSProvider(TTSProvider):
    """
    Google TTS provider (free, requires internet)

    Requires: pip install gTTS
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """Synthesize using Google TTS"""
        try:
            from gtts import gTTS

            output_path = output_path or self._get_output_path()
            lang = voice_id or "en"  # Voice ID is language code

            logger.debug(f"Synthesizing with gTTS (lang: {lang})")

            # Generate audio (synchronous)
            loop = asyncio.get_event_loop()
            tts = gTTS(text=text, lang=lang, slow=False)
            await loop.run_in_executor(None, tts.save, str(output_path))

            logger.info(f"Generated audio: {output_path}")
            return output_path

        except ImportError:
            logger.error(
                "gTTS library not installed. "
                "Install with: pip install gTTS"
            )
            raise
        except Exception as e:
            logger.error(f"gTTS synthesis failed: {e}")
            raise


class TTSManager:
    """
    TTS Manager - manages text-to-speech synthesis

    Automatically selects available TTS engine.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.provider = self._initialize_provider()

    def _initialize_provider(self) -> TTSProvider:
        """Initialize TTS provider"""
        engine = self.config.get("engine", "elevenlabs")

        # Try requested engine first
        try:
            if engine == "elevenlabs":
                return ElevenLabsProvider(self.config)
            elif engine == "pyttsx3":
                return Pyttsx3Provider(self.config)
            elif engine == "gtts":
                return GTTSProvider(self.config)
        except Exception as e:
            logger.warning(f"Failed to initialize {engine}: {e}")

        # Fallback to available engines
        for fallback_engine in ["pyttsx3", "gtts", "elevenlabs"]:
            if fallback_engine != engine:
                try:
                    logger.info(f"Falling back to {fallback_engine}")
                    if fallback_engine == "pyttsx3":
                        return Pyttsx3Provider(self.config)
                    elif fallback_engine == "gtts":
                        return GTTSProvider(self.config)
                    elif fallback_engine == "elevenlabs":
                        return ElevenLabsProvider(self.config)
                except Exception as e:
                    logger.warning(f"Failed to initialize {fallback_engine}: {e}")
                    continue

        raise RuntimeError("No TTS engine available")

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Synthesize text to speech

        Args:
            text: Text to synthesize
            voice_id: Voice identifier (provider-specific)
            output_path: Output file path

        Returns:
            Path to generated audio file
        """
        return await self.provider.synthesize(text, voice_id, output_path)

    async def synthesize_debate(
        self,
        debate_transcript: Dict[str, Any],
        voice_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Path]:
        """
        Synthesize entire debate to audio files

        Args:
            debate_transcript: Debate session data
            voice_mapping: Mapping of agent names to voice IDs

        Returns:
            Dict mapping agent_id to audio file path
        """
        voice_mapping = voice_mapping or self.config.get("voice_mapping", {})
        audio_files = {}

        # Process each round
        for round_data in debate_transcript.get("rounds", []):
            for response in round_data.get("responses", []):
                agent_id = response.get("agent_id")
                agent_name = response.get("agent_name")
                content = response.get("content")

                if not content:
                    continue

                # Get voice for agent
                voice_id = voice_mapping.get(
                    agent_name.lower().replace(" ", "_"),
                    None
                )

                # Generate audio
                try:
                    output_path = await self.synthesize(
                        content,
                        voice_id=voice_id,
                        output_path=self.provider.output_dir / f"{agent_id}_{round_data['round_number']}.mp3"
                    )
                    audio_files[f"{agent_id}_{round_data['round_number']}"] = output_path
                except Exception as e:
                    logger.error(f"Failed to synthesize for {agent_name}: {e}")

        logger.info(f"Generated {len(audio_files)} audio files")
        return audio_files

    def get_available_voices(self) -> List[str]:
        """Get list of available voices"""
        if isinstance(self.provider, Pyttsx3Provider):
            voices = self.provider.engine.getProperty("voices")
            return [v.name for v in voices]
        elif isinstance(self.provider, GTTSProvider):
            return ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"]
        elif isinstance(self.provider, ElevenLabsProvider):
            # ElevenLabs voices would need API call to list
            return ["premade voices - see ElevenLabs dashboard"]
        return []


# Convenience functions
async def text_to_speech(
    text: str,
    config: Optional[Dict[str, Any]] = None,
    voice_id: Optional[str] = None
) -> Path:
    """Quick TTS synthesis"""
    manager = TTSManager(config)
    return await manager.synthesize(text, voice_id)


async def debate_to_audio(
    debate_transcript: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Path]:
    """Convert entire debate to audio"""
    manager = TTSManager(config)
    return await manager.synthesize_debate(debate_transcript)
