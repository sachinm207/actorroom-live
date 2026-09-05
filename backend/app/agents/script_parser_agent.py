import os
import logging
from typing import List, Dict
from app.schemas.models import ScreenplayScene
from app.parsers.fountain_parser import FountainParser

logger = logging.getLogger("ScriptParserAgent")

class ScriptParserAgent:
    """
    Ingests screenplays in Fountain or raw text format, extracts characters,
    segments scene beats, and assigns voice personas.
    """

    def __init__(self, sample_scripts_dir: str = "sample_scripts"):
        self.sample_scripts_dir = sample_scripts_dir
        self._custom_scenes: Dict[str, ScreenplayScene] = {}

    def load_script_by_id(self, script_id: str) -> ScreenplayScene:
        if script_id in self._custom_scenes:
            return self._custom_scenes[script_id]

        # Search for file in sample_scripts
        filename = f"{script_id}.fountain" if not script_id.endswith(".fountain") else script_id
        path = os.path.join(self.sample_scripts_dir, filename)
        
        # Also check relative to backend directory
        if not os.path.exists(path):
            alt_path = os.path.join(os.path.dirname(__file__), "..", "..", "sample_scripts", filename)
            if os.path.exists(alt_path):
                path = alt_path

        if os.path.exists(path):
            logger.info(f"Loading script file from: {path}")
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return FountainParser.parse_fountain_text(content, scene_id=script_id)
        
        logger.warning(f"Script {script_id} not found at {path}, falling back to default interrogation scene.")
        return self._get_fallback_scene()

    def parse_raw_text(self, text: str, scene_id: str = "custom_take") -> ScreenplayScene:
        scene = FountainParser.parse_fountain_text(text, scene_id=scene_id)
        self._custom_scenes[scene_id] = scene
        return scene

    def parse_pdf_bytes(self, pdf_bytes: bytes, scene_id: str = "custom_pdf") -> ScreenplayScene:
        scene = FountainParser.parse_pdf_bytes(pdf_bytes, scene_id=scene_id)
        self._custom_scenes[scene_id] = scene
        return scene

    def _get_fallback_scene(self) -> ScreenplayScene:
        default_fountain = """Title: EMERGENCY AUDITION SCENE
INT. ROOM - DAY

DETECTIVE
Where were you last night?

SUSPECT
(smirking)
Nowhere you can prove.
"""
        return FountainParser.parse_fountain_text(default_fountain, scene_id="fallback")
