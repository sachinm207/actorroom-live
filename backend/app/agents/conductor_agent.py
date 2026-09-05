import time
import asyncio
import logging
from typing import Optional, Callable, Awaitable, List
from app.schemas.models import ScreenplayScene, DialogueLine, ConductorState
from app.services.audio_pipeline import AudioPipeline
from app.config import settings

logger = logging.getLogger("ConductorAgent")

class ConductorAgent:
    """
    Audio Conductor & Turn-Taking Arbitrator Agent.
    Orchestrates live scene progression, voice activity detection (VAD),
    speech turn handover, and instant barge-in cutoffs.
    Supports both SCRIPTED (verbatim lines) and IMPROV (conversational freedom) modes.
    """

    def __init__(
        self,
        scene: ScreenplayScene,
        user_character: str,
        mode: str = "SCRIPTED",
        reader_style: str = "CASTING_READER",
        on_line_sync: Optional[Callable[[DialogueLine], Awaitable[None]]] = None,
        on_ai_speak_request: Optional[Callable[[DialogueLine], Awaitable[None]]] = None,
        on_improv_turn: Optional[Callable[[bytes], Awaitable[None]]] = None,
        on_barge_in: Optional[Callable[[], Awaitable[None]]] = None,
        on_take_complete: Optional[Callable[[], Awaitable[None]]] = None
    ):
        self.scene = scene
        self.user_character = user_character.strip().upper()
        self.mode = mode.strip().upper()
        self.reader_style = reader_style.strip().upper()
        self.current_line_idx = 0
        self.state = ConductorState.IDLE
        
        # Callbacks
        self.on_line_sync = on_line_sync
        self.on_ai_speak_request = on_ai_speak_request
        self.on_improv_turn = on_improv_turn
        self.on_barge_in = on_barge_in
        self.on_take_complete = on_take_complete

        # VAD & Temporal Tracking
        self.speech_frames_count = 0
        self.silence_frames_count = 0
        self.min_speech_frames = 2     # ~80ms to confirm speech onset
        
        # Adjust cue pickup responsiveness to match reader direction
        if self.reader_style == "RAPID_FIRE":
            self.min_silence_frames = 8   # ~320ms snappy turn handover
        elif self.reader_style == "HIGH_STAKES":
            self.min_silence_frames = 14  # ~560ms breathing room for dramatic pauses
        else:
            self.min_silence_frames = 11  # ~440ms standard natural gap
        
        # User audio accumulation for Improv Mode
        self.user_audio_buffer = bytearray()
        
        # Audio frame history for take analysis
        self.total_frames_received = 0
        self.speech_timestamps: List[float] = []
        self.turn_latencies: List[float] = []
        self.take_start_time: Optional[float] = None
        self.take_end_time: Optional[float] = None
        
        # Lock for thread/async safety
        self._lock = asyncio.Lock()

    def get_current_line(self) -> Optional[DialogueLine]:
        if 0 <= self.current_line_idx < len(self.scene.lines):
            return self.scene.lines[self.current_line_idx]
        return None

    def is_user_turn(self) -> bool:
        if self.mode == "IMPROV":
            return self.state in [ConductorState.WAITING_FOR_USER, ConductorState.USER_SPEAKING]
        line = self.get_current_line()
        if not line:
            return False
        return line.character.strip().upper() == self.user_character

    async def start_rehearsal(self):
        """Initializes the rehearsal session and cues the first speaker."""
        async with self._lock:
            self.take_start_time = time.time()
            self.current_line_idx = 0
            self.user_audio_buffer.clear()
            logger.info(f"Rehearsal started. Mode: {self.mode}, Scene: {self.scene.title}, User: {self.user_character}")

            if self.mode == "IMPROV":
                # Clear scripted lines to build dynamic improvised script
                self.scene.lines = []
                self.state = ConductorState.WAITING_FOR_USER
                user_opening = DialogueLine(
                    index=0,
                    character=self.user_character,
                    line="[Scene Started: Speak freely in-character to open the scene...]",
                    is_user=True,
                    emotion="improvised"
                )
                self.scene.lines.append(user_opening)
                if self.on_line_sync:
                    await self.on_line_sync(user_opening)
            else:
                await self._cue_current_line()

    async def _cue_current_line(self):
        line = self.get_current_line()
        if not line:
            self.state = ConductorState.TAKE_FINISHED
            self.take_end_time = time.time()
            logger.info("Take completed: reached end of scene lines.")
            if self.on_take_complete:
                await self.on_take_complete()
            return

        # Broadcast line sync to frontend teleprompter
        if self.on_line_sync:
            await self.on_line_sync(line)

        if self.is_user_turn():
            self.state = ConductorState.WAITING_FOR_USER
            self.speech_frames_count = 0
            self.silence_frames_count = 0
            logger.info(f"Turn {line.index}: WAITING FOR USER ({self.user_character})")
        else:
            self.state = ConductorState.AI_SPEAKING
            logger.info(f"Turn {line.index}: AI OPPOSING CHARACTER SPEAKING ({line.character})")
            if self.on_ai_speak_request:
                await self.on_ai_speak_request(line)

    async def process_incoming_audio_frame(self, pcm_bytes: bytes):
        """
        Ingests a 40ms PCM audio frame from the actor's microphone.
        Executes real-time VAD, turn-taking arbitration, and barge-in cutoff.
        """
        async with self._lock:
            self.total_frames_received += 1
            rms = AudioPipeline.calculate_rms(pcm_bytes)
            is_active = rms >= settings.VAD_ENERGY_THRESHOLD

            # 1. Check for BARGE-IN during AI speech
            if self.state == ConductorState.AI_SPEAKING:
                if rms >= settings.BARGE_IN_ENERGY_THRESHOLD:
                    self.speech_frames_count += 1
                    if self.speech_frames_count >= 2:  # ~80ms continuous speech while AI talking
                        logger.warning(f"BARGE-IN DETECTED (RMS: {rms:.1f}). Cutting off AI speech immediately!")
                        self.state = ConductorState.BARGE_IN_TRIGGERED
                        self.speech_frames_count = 0
                        self.silence_frames_count = 0
                        if self.on_barge_in:
                            await self.on_barge_in()
                        self.state = ConductorState.USER_SPEAKING
                        if self.mode == "IMPROV":
                            self.user_audio_buffer.clear()
                            self.user_audio_buffer.extend(pcm_bytes)
                else:
                    self.speech_frames_count = 0
                return

            # 2. Track actor speech during actor's turn
            if self.state in [ConductorState.WAITING_FOR_USER, ConductorState.USER_SPEAKING]:
                if is_active:
                    self.speech_frames_count += 1
                    self.silence_frames_count = 0
                    if self.mode == "IMPROV":
                        self.user_audio_buffer.extend(pcm_bytes)
                    if self.speech_frames_count >= self.min_speech_frames and self.state == ConductorState.WAITING_FOR_USER:
                        self.state = ConductorState.USER_SPEAKING
                        self.speech_timestamps.append(time.time())
                        logger.info(f"Actor started speaking in {self.mode} mode")
                else:
                    if self.state == ConductorState.USER_SPEAKING:
                        if self.mode == "IMPROV":
                            self.user_audio_buffer.extend(pcm_bytes)
                        self.silence_frames_count += 1
                        if self.silence_frames_count >= self.min_silence_frames:
                            # Actor finished speaking!
                            logger.info(f"Actor finished turn in {self.mode} mode (detected silence)")
                            self.state = ConductorState.IDLE
                            self.speech_frames_count = 0
                            self.silence_frames_count = 0

                            if self.mode == "IMPROV" and self.on_improv_turn:
                                audio_data = bytes(self.user_audio_buffer)
                                self.user_audio_buffer.clear()
                                asyncio.create_task(self.on_improv_turn(audio_data))
                            else:
                                self.current_line_idx += 1
                                await self._cue_current_line()

    async def notify_manual_barge_in(self):
        """Explicit interrupt signal from client button or rapid keyboard shortcut."""
        async with self._lock:
            if self.state == ConductorState.AI_SPEAKING:
                logger.info("Manual BARGE-IN signal received from client.")
                self.state = ConductorState.BARGE_IN_TRIGGERED
                if self.on_barge_in:
                    await self.on_barge_in()
                self.state = ConductorState.WAITING_FOR_USER
                self.user_audio_buffer.clear()

    async def notify_ai_finished_line(self):
        """Called by the Character Agent when AI has completed streaming its audio line."""
        async with self._lock:
            if self.state == ConductorState.AI_SPEAKING:
                logger.info(f"AI character completed line {self.current_line_idx}")
                if self.mode == "IMPROV":
                    # In improv mode, turn shifts back to waiting for user to speak
                    self.state = ConductorState.WAITING_FOR_USER
                    self.speech_frames_count = 0
                    self.silence_frames_count = 0
                    logger.info(f"IMPROV: Shifting turn back to Actor ({self.user_character})")
                    user_turn_line = DialogueLine(
                        index=len(self.scene.lines),
                        character=self.user_character,
                        line="[Your turn: Speak in-character into your microphone...]",
                        is_user=True,
                        emotion="improvised"
                    )
                    if self.on_line_sync:
                        await self.on_line_sync(user_turn_line)
                else:
                    self.current_line_idx += 1
                    await self._cue_current_line()
