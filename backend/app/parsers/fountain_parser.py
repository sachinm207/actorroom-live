import re
from typing import List, Dict
from app.schemas.models import ScreenplayScene, DialogueLine, CharacterPersona

class FountainParser:
    """
    Parses Fountain formatted screenplay text into structured ScreenplayScene objects
    with dialogue lines, character names, parentheticals, and default voice personas.
    """

    VOICE_ROTATION = ["Puck", "Charon", "Aoede", "Fenrir", "Kore"]

    @staticmethod
    def parse_pdf_bytes(pdf_bytes: bytes, scene_id: str = "custom_pdf") -> ScreenplayScene:
        import pymupdf
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        full_text = "\n".join([page.get_text() for page in doc])
        return FountainParser.parse_fountain_text(full_text, scene_id=scene_id)

    @staticmethod
    def parse_fountain_text(text: str, scene_id: str = "custom_scene") -> ScreenplayScene:
        lines = [line.strip() for line in text.strip().split("\n")]
        title = "Audition Scene"
        slugline = "INT. AUDITION ROOM - DAY"
        dialogue_lines: List[DialogueLine] = []
        characters_set = set()

        idx = 0
        line_num = 0
        while idx < len(lines):
            raw_line = lines[idx]

            # Detect Title
            if raw_line.lower().startswith("title:"):
                title = raw_line.split(":", 1)[1].strip()
                idx += 1
                continue

            # Detect Scene Heading (INT., EXT., etc.)
            if re.match(r"^(INT\.|EXT\.|INT/EXT\.|EST\.)", raw_line, re.IGNORECASE):
                slugline = raw_line
                idx += 1
                continue

            # Detect Character Cue (ALL CAPS line, not a scene heading, typically short)
            if raw_line.isupper() and len(raw_line) < 35 and not raw_line.startswith(("INT.", "EXT.")):
                character = raw_line.strip()
                parenthetical = None
                spoken_dialogue = []

                idx += 1
                # Check for parenthetical (e.g. "(whispering)")
                if idx < len(lines) and lines[idx].startswith("(") and lines[idx].endswith(")"):
                    parenthetical = lines[idx].strip("()")
                    idx += 1

                # Gather dialogue lines until empty line or next character
                while idx < len(lines) and lines[idx] and not (lines[idx].isupper() and len(lines[idx]) < 35):
                    spoken_dialogue.append(lines[idx])
                    idx += 1

                if spoken_dialogue:
                    full_speech = " ".join(spoken_dialogue)
                    characters_set.add(character)
                    dialogue_lines.append(
                        DialogueLine(
                            index=line_num,
                            character=character,
                            parenthetical=parenthetical,
                            line=full_speech,
                            emotion=parenthetical if parenthetical else "neutral"
                        )
                    )
                    line_num += 1
                continue

            idx += 1

        # Assign voice personas to extracted characters
        opposing_personas: Dict[str, CharacterPersona] = {}
        sorted_chars = sorted(list(characters_set))
        for i, char_name in enumerate(sorted_chars):
            voice = FountainParser.VOICE_ROTATION[i % len(FountainParser.VOICE_ROTATION)]
            opposing_personas[char_name] = CharacterPersona(
                name=char_name,
                voice_name=voice,
                pitch=1.0,
                speaking_rate=1.0,
                emotional_baseline="dramatic tension",
                description=f"Character {char_name} in {title}"
            )

        return ScreenplayScene(
            scene_id=scene_id,
            title=title,
            slugline=slugline,
            characters=sorted_chars,
            lines=dialogue_lines,
            opposing_personas=opposing_personas
        )
