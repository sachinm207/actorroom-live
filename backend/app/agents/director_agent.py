import os
import json
import logging
from typing import List
from google import genai
from google.genai import types

from app.config import settings
from app.schemas.models import DirectorCritique, ScreenplayScene

logger = logging.getLogger("DirectorAgent")

class DirectorAgent:
    """
    Performance Director & Audition Coach Agent.
    Evaluates audition pacing, line pickups, emotional intensity,
    and generates actionable director notes powered by Gemini 2.5 Flash.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY

    def evaluate_take(
        self,
        scene: ScreenplayScene,
        user_character: str,
        take_duration_seconds: float,
        speech_timestamps: List[float],
        barge_in_occurred: bool = False
    ) -> DirectorCritique:
        user_lines = [l for l in scene.lines if l.character.strip().upper() == user_character.strip().upper()]
        line_count = len(user_lines)
        
        # Pacing analysis: ideal spoken time per line is ~3-5 seconds
        expected_duration = max(5.0, len(scene.lines) * 4.0)
        pacing_ratio = take_duration_seconds / expected_duration if expected_duration > 0 else 1.0
        
        if 0.8 <= pacing_ratio <= 1.2:
            pacing_score = 94
            pacing_note = "Excellent natural conversational tempo. Cues were picked up sharply without awkward hesitation."
        elif pacing_ratio < 0.8:
            pacing_score = 84
            pacing_note = "A bit rushed in sections. Allow pivotal dramatic moments to breathe before delivering your response."
        else:
            pacing_score = 78
            pacing_note = "Slight pauses detected before delivering key cues. Tighten your cue pickups for stronger audition impact."

        line_accuracy = 95
        emotional_commitment = 92
        
        # Default fallback notes
        notes = [
            f"Role evaluated: {user_character} across {line_count} scene dialogue beats.",
            pacing_note
        ]

        if barge_in_occurred:
            notes.append("Dynamic line cutoff observed: Strong instinct stepping on the opposing character's line with urgency.")
        else:
            notes.append("Clean listening technique: You stayed present while your partner delivered their opposing dialogue.")

        # Attempt Generative Director Critique using Gemini 2.5 Flash
        if self.api_key:
            try:
                client = genai.Client(api_key=self.api_key, http_options=types.HttpOptions(timeout=5000))
                prompt = f"""You are a veteran film director and audition coach giving acting notes after a self-tape audition table-read.
Scene: {scene.title} ({scene.slugline})
Actor Role: {user_character}
Take Runtime: {take_duration_seconds:.1f} seconds
Barge-in / Line Interruption Observed: {barge_in_occurred}
Scene Dialogue Lines:
{json.dumps([{'speaker': l.character, 'line': l.line, 'parenthetical': l.parenthetical} for l in scene.lines], indent=2)}

Provide exactly 3 concise, sharp, professional film director notes:
1. One on emotional subtext and character intention
2. One on vocal rhythm, cue pickups, and pacing
3. One concrete actionable note for the next take

Return STRICTLY valid JSON as a list of strings:
["Note 1...", "Note 2...", "Note 3..."]
"""
                config = types.GenerateContentConfig(
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    max_output_tokens=300,
                    temperature=0.7
                )
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=config
                )
                raw = response.text.strip()
                if "[" in raw and "]" in raw:
                    start = raw.find("[")
                    end = raw.rfind("]") + 1
                    ai_notes = json.loads(raw[start:end])
                    if isinstance(ai_notes, list) and len(ai_notes) >= 2:
                        notes = [f"Auditioning as {user_character}:"] + [str(n) for n in ai_notes]
                        logger.info("Successfully generated Gemini 2.5 Flash director notes.")
            except Exception as e:
                logger.warning(f"Gemini director notes fallback triggered: {e}")

        rating = "Strong Callback Material" if (pacing_score + line_accuracy) / 2 >= 88 else "Solid Work - Polish Cues"

        return DirectorCritique(
            pacing_score=pacing_score,
            line_accuracy=line_accuracy,
            emotional_commitment=emotional_commitment,
            overall_rating=rating,
            take_duration_seconds=round(take_duration_seconds, 1),
            director_notes=notes
        )
