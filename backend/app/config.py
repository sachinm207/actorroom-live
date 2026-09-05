import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "ActorRoom Live"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Audio & Turn-taking constraints
    SAMPLE_RATE: int = 16000  # 16kHz mono PCM standard for speech
    AUDIO_CHANNELS: int = 1
    BYTES_PER_SAMPLE: int = 2  # 16-bit linear PCM
    CHUNK_DURATION_MS: int = 40  # 40ms frame
    CHUNK_SIZE_BYTES: int = int(SAMPLE_RATE * (CHUNK_DURATION_MS / 1000.0) * BYTES_PER_SAMPLE)  # 1280 bytes
    
    # VAD & Barge-in thresholds
    VAD_ENERGY_THRESHOLD: float = 300.0  # RMS threshold for speech activity
    VAD_SILENCE_TIMEOUT_MS: int = 450   # Speech cessation threshold before turn handover
    BARGE_IN_ENERGY_THRESHOLD: float = 400.0 # RMS threshold to trigger immediate cutoff of AI speech

settings = Settings()
