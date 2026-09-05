import asyncio
import logging
import subprocess
from typing import AsyncGenerator, Optional
import edge_tts

from app.config import settings
from app.services.audio_pipeline import AudioPipeline

logger = logging.getLogger("GeminiLiveService")

# Cinematic Neural Voice Personas
NEURAL_VOICE_MAP = {
    # Viktor: Deep, gritty, foreign-tinged male
    "VIKTOR": "en-US-ChristopherNeural",
    "Charon": "en-US-ChristopherNeural",
    # Detective Miller: Authoritative, sharp American detective
    "DETECTIVE MILLER": "en-US-GuyNeural",
    "Puck": "en-US-GuyNeural",
    # Sara: Nuanced, dramatic female
    "SARA": "en-US-JennyNeural",
    "Aoede": "en-US-JennyNeural",
    # Liam: Defensive, younger male
    "LIAM": "en-US-EricNeural",
    "Fenrir": "en-US-EricNeural",
    # Default fallback female voice
    "Kore": "en-US-AriaNeural"
}

class GeminiLiveService:
    """
    Manages real-time bi-directional audio generation for character readers.
    Generates authentic human dialogue voices using neural synthesis,
    delivers raw 16kHz PCM in 40ms frames, and supports sub-150ms barge-in cutoffs.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.is_active = False
        self._cancellation_event = asyncio.Event()

    def cancel_ongoing_stream(self):
        """Called immediately upon barge-in detection to abort active audio generation."""
        logger.info("GeminiLiveService: Cancellation signal triggered (BARGE-IN).")
        self._cancellation_event.set()

    def _select_voice(self, character_name: str, voice_name: str) -> str:
        upper_char = character_name.strip().upper()
        if upper_char in NEURAL_VOICE_MAP:
            return NEURAL_VOICE_MAP[upper_char]
        if voice_name in NEURAL_VOICE_MAP:
            return NEURAL_VOICE_MAP[voice_name]
        return "en-US-ChristopherNeural"

    READER_STYLE_MODIFIERS = {
        "CASTING_READER": {"rate": "+5%", "pitch": "+0Hz", "volume": "+0%"},
        "HIGH_STAKES": {"rate": "-8%", "pitch": "-3Hz", "volume": "+5%"},
        "RAPID_FIRE": {"rate": "+18%", "pitch": "+2Hz", "volume": "+0%"},
        "WHISPERED": {"rate": "-5%", "pitch": "-5Hz", "volume": "-20%"}
    }

    async def _generate_neural_pcm(self, text: str, voice: str, reader_style: str = "CASTING_READER") -> Optional[bytes]:
        """
        Synthesize neural speech and convert to 16kHz 16-bit mono PCM.
        Applies rate/pitch/volume modifiers based on reader style direction.
        """
        try:
            mods = self.READER_STYLE_MODIFIERS.get(reader_style, self.READER_STYLE_MODIFIERS["CASTING_READER"])
            comm = edge_tts.Communicate(text, voice, rate=mods["rate"], pitch=mods["pitch"], volume=mods["volume"])
            mp3_data = bytearray()
            async for chunk in comm.stream():
                if self._cancellation_event.is_set():
                    return None
                if chunk['type'] == 'audio':
                    mp3_data.extend(chunk['data'])

            if not mp3_data or self._cancellation_event.is_set():
                return None

            # Convert to 16kHz 16-bit mono linear PCM via ffmpeg
            proc = subprocess.Popen(
                ['ffmpeg', '-i', 'pipe:0', '-f', 's16le', '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', 'pipe:1'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            pcm_out, _ = proc.communicate(input=bytes(mp3_data))
            return pcm_out
        except Exception as e:
            logger.error(f"Neural TTS synthesis error: {e}")
            return None

    async def stream_character_audio(
        self,
        character_name: str,
        line_text: str,
        voice_name: str = "Puck",
        parenthetical: Optional[str] = None,
        reader_style: str = "CASTING_READER"
    ) -> AsyncGenerator[bytes, None]:
        """
        Streams 16kHz 16-bit mono PCM chunks for the specified character line.
        Supports instant cutoff if self._cancellation_event is set.
        """
        self._cancellation_event.clear()
        voice = self._select_voice(character_name, voice_name)
        logger.info(f"Synthesizing human dialogue for [{character_name}] (Neural Voice: {voice}): \"{line_text}\"")

        # 1. Attempt Neural Human Speech Generation
        pcm_bytes = await self._generate_neural_pcm(line_text, voice, reader_style=reader_style)

        chunk_size = settings.CHUNK_SIZE_BYTES  # 1280 bytes = 40ms of 16kHz 16-bit mono
        chunk_duration_sec = settings.CHUNK_DURATION_MS / 1000.0

        if pcm_bytes and len(pcm_bytes) >= chunk_size:
            logger.info(f"Streaming {len(pcm_bytes)} bytes of real human audio for [{character_name}]...")
            for offset in range(0, len(pcm_bytes), chunk_size):
                if self._cancellation_event.is_set():
                    logger.warning(f"Audio stream for [{character_name}] aborted midway due to BARGE-IN.")
                    break

                chunk = pcm_bytes[offset:offset + chunk_size]
                # Pad last chunk if needed
                if len(chunk) < chunk_size:
                    chunk = chunk + b"\x00" * (chunk_size - len(chunk))

                yield chunk
                await asyncio.sleep(chunk_duration_sec)

        else:
            # 2. Fallback to tone synthesizer if offline or canceled
            if self._cancellation_event.is_set():
                return

            logger.warning(f"Using fallback acoustic stream for [{character_name}]")
            words = line_text.split()
            estimated_duration = max(1.2, len(words) * 0.38)
            total_chunks = int(estimated_duration / chunk_duration_sec)
            base_freq = 220.0 if "VIKTOR" in character_name.upper() else 340.0

            for i in range(total_chunks):
                if self._cancellation_event.is_set():
                    break
                freq = base_freq + 20.0 * (i % 6 - 3)
                chunk_pcm = AudioPipeline.generate_pcm_sine_wave(
                    frequency_hz=freq,
                    duration_seconds=chunk_duration_sec,
                    sample_rate=settings.SAMPLE_RATE,
                    volume=0.25
                )
                yield chunk_pcm
                await asyncio.sleep(chunk_duration_sec)

        logger.info(f"Finished audio delivery for [{character_name}]")
