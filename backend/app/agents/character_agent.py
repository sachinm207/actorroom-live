import json
import logging
from typing import AsyncGenerator, Optional, List, Dict
from google import genai
from google.genai import types

from app.config import settings
from app.schemas.models import CharacterPersona, DialogueLine
from app.services.gemini_live import GeminiLiveService
from app.services.audio_pipeline import AudioPipeline

logger = logging.getLogger("CharacterAgent")

class CharacterAgent:
    """
    Manages dynamic character dialogue generation, vocal profile assignment,
    and live audio streaming for opposing scene roles.
    Supports both verbatim scripted lines and Gemini Live conversational improvisation.
    """

    def __init__(self, persona: CharacterPersona, live_service: Optional[GeminiLiveService] = None):
        self.persona = persona
        self.live_service = live_service or GeminiLiveService()
        self.api_key = settings.GEMINI_API_KEY

    def abort_speech(self):
        """Immediately abort speech upon barge-in."""
        self.live_service.cancel_ongoing_stream()

    async def speak_line(self, line: DialogueLine) -> AsyncGenerator[bytes, None]:
        """
        Generate and stream PCM audio for the dialogue line.
        """
        logger.info(f"CharacterAgent [{self.persona.name}] speaking line {line.index}...")
        async for chunk in self.live_service.stream_character_audio(
            character_name=self.persona.name,
            line_text=line.line,
            voice_name=self.persona.voice_name,
            parenthetical=line.parenthetical
        ):
            yield chunk

    def generate_improv_dialogue(
        self,
        actor_pcm_bytes: Optional[bytes],
        dialogue_history: List[Dict[str, str]],
        scene_title: str,
        scene_slugline: str,
        user_character: str
    ) -> str:
        """
        Listens to the actor's raw voice (or recent turns) using Gemini 2.5 Flash,
        and improvises a dramatic, in-character spoken response.
        """
        if not self.api_key:
            return f"I hear you, {user_character}. But you have no evidence."

        try:
            client = genai.Client(api_key=self.api_key)
            system_prompt = f"""You are acting in an unscripted audition rehearsal scene as the character '{self.persona.name}'.
Scene: {scene_title} ({scene_slugline})
Scene Partner: {user_character}
Character Persona: {self.persona.name} - {self.persona.description or 'A complex dramatic character with clear objectives.'}
Emotional Baseline: {self.persona.emotional_baseline}

Acting Directives:
- Stay 100% strictly in character.
- Never break the fourth wall.
- Speak naturally, sharply, and compellingly in 1 to 2 spoken sentences (ideal for acting dialogue).
- React directly to what your scene partner just said or asked.
- Output ONLY the spoken dialogue line without quotes or prefixes."""

            contents = [system_prompt]

            if dialogue_history:
                formatted_history = "\n".join([f"{t['speaker']}: {t['line']}" for t in dialogue_history[-6:]])
                contents.append(f"Recent Scene Dialogue:\n{formatted_history}")

            # If actor audio is provided, attach as multimodal Part
            if actor_pcm_bytes and len(actor_pcm_bytes) >= 1600:  # At least 50ms of audio
                wav_header = AudioPipeline.pcm_to_wav_header(len(actor_pcm_bytes), sample_rate=settings.SAMPLE_RATE)
                wav_bytes = wav_header + actor_pcm_bytes
                audio_part = types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav")
                contents.append(audio_part)
                contents.append(f"The audio above is {user_character}'s speech. Listen to their words, inflection, and tone, then respond as {self.persona.name}:")
            else:
                contents.append(f"Respond to {user_character} as {self.persona.name}:")

            config = types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                max_output_tokens=65,
                temperature=0.7
            )
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=config
            )
            raw_reply = response.text.strip().strip('"').strip("'")
            # Remove any accidental "VIKTOR:" prefix
            if ":" in raw_reply and len(raw_reply.split(":", 1)[0]) < 20:
                raw_reply = raw_reply.split(":", 1)[1].strip()

            logger.info(f"Improvised dialogue generated for [{self.persona.name}]: \"{raw_reply}\"")
            return raw_reply
        except Exception as e:
            logger.error(f"Error in generate_improv_dialogue: {e}", exc_info=True)
            return "You think you have all the answers, don't you? Look closer at the evidence."
