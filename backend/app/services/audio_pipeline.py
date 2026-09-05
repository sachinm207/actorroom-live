import math
import struct
import numpy as np
from typing import Tuple

class AudioPipeline:
    """
    Handles low-latency PCM audio analysis, RMS energy calculation,
    Voice Activity Detection (VAD), and tone generation for testing.
    """

    @staticmethod
    def calculate_rms(pcm_bytes: bytes) -> float:
        """
        Calculate the Root Mean Square (RMS) amplitude of 16-bit signed linear PCM.
        """
        if not pcm_bytes or len(pcm_bytes) < 2:
            return 0.0
        
        # Unpack as int16
        count = len(pcm_bytes) // 2
        try:
            samples = struct.unpack(f"{count}h", pcm_bytes[:count * 2])
            sum_squares = sum(s * s for s in samples)
            return math.sqrt(sum_squares / count)
        except Exception:
            return 0.0

    @staticmethod
    def is_speech_active(pcm_bytes: bytes, threshold: float = 300.0) -> bool:
        """
        Fast frame-level energy-based VAD check.
        """
        return AudioPipeline.calculate_rms(pcm_bytes) >= threshold

    @staticmethod
    def generate_pcm_sine_wave(frequency_hz: float = 440.0, duration_seconds: float = 1.0, sample_rate: int = 16000, volume: float = 0.3) -> bytes:
        """
        Generate raw 16-bit mono PCM sine wave. Useful for mock audio streaming
        and latency benchmark verification before full cloud live synthesis.
        """
        total_samples = int(sample_rate * duration_seconds)
        samples = []
        for i in range(total_samples):
            t = float(i) / sample_rate
            val = volume * math.sin(2.0 * math.pi * frequency_hz * t)
            # Clip to int16 range
            val_int16 = int(max(-32767, min(32767, val * 32767)))
            samples.append(val_int16)
        return struct.pack(f"{total_samples}h", *samples)

    @staticmethod
    def pcm_to_wav_header(pcm_len: int, sample_rate: int = 16000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
        """
        Generate a 44-byte standard RIFF WAV header for raw PCM bytes.
        """
        byte_rate = sample_rate * channels * (bits_per_sample // 8)
        block_align = channels * (bits_per_sample // 8)
        total_data_len = pcm_len
        total_file_len = total_data_len + 36

        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            total_file_len,
            b'WAVE',
            b'fmt ',
            16,
            1,  # PCM
            channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
            b'data',
            total_data_len
        )
        return header
