from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class DialogueLine(BaseModel):
    index: int
    character: str
    parenthetical: Optional[str] = None
    line: str
    is_user: bool = False
    emotion: Optional[str] = "neutral"

class CharacterPersona(BaseModel):
    name: str
    voice_name: str = "Puck"  # Gemini voice: Aoede, Charon, Fenrir, Kore, Puck
    pitch: float = 1.0
    speaking_rate: float = 1.0
    emotional_baseline: str = "intense"
    description: Optional[str] = None

class ScreenplayScene(BaseModel):
    scene_id: str
    title: str
    slugline: str
    characters: List[str]
    lines: List[DialogueLine]
    opposing_personas: Dict[str, CharacterPersona] = Field(default_factory=dict)

class ConductorState(str):
    IDLE = "IDLE"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    USER_SPEAKING = "USER_SPEAKING"
    AI_SPEAKING = "AI_SPEAKING"
    BARGE_IN_TRIGGERED = "BARGE_IN_TRIGGERED"
    TAKE_FINISHED = "TAKE_FINISHED"

class DirectorCritique(BaseModel):
    pacing_score: int = Field(ge=0, le=100, description="Score 0-100 evaluating cadence and gap timing")
    line_accuracy: int = Field(ge=0, le=100, description="Score 0-100 evaluating script adherence")
    emotional_commitment: int = Field(ge=0, le=100, description="Score 0-100 evaluating scene intent")
    overall_rating: str
    take_duration_seconds: float
    director_notes: List[str]

# WebSocket Protocol Messages
class ClientMessage(BaseModel):
    type: Literal["START_SESSION", "INTERRUPT", "END_TAKE", "PING"]
    script_id: Optional[str] = None
    user_character: Optional[str] = None
    mode: Optional[Literal["SCRIPTED", "IMPROV"]] = "SCRIPTED"
    reader_style: Optional[Literal["CASTING_READER", "HIGH_STAKES", "RAPID_FIRE", "WHISPERED"]] = "CASTING_READER"
    payload: Optional[Dict[str, Any]] = None

class ServerMessage(BaseModel):
    type: Literal[
        "SESSION_READY",
        "LINE_SYNC",
        "AUDIO_START",
        "AUDIO_END",
        "BARGE_IN_CONFIRMED",
        "DIRECTOR_REPORT",
        "ERROR",
        "PONG"
    ]
    current_turn_index: Optional[int] = None
    speaker: Optional[str] = None
    line_text: Optional[str] = None
    parenthetical: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None
