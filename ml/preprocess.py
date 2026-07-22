"""
ml/preprocess.py — Audio preprocessing utilities for ML training.
"""
import os
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from pydub.silence import split_on_silence


def load_audio(path: str, target_sr: int = 16000):
    """Load any audio file, resample to target_sr, return (samples, sr)."""
    audio = AudioSegment.from_file(path)
    audio = audio.set_channels(1).set_frame_rate(target_sr)
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
    return samples, target_sr


def remove_silence_pydub(audio: AudioSegment, silence_thresh=-40, min_silence_len=500):
    """Strip silence from a pydub AudioSegment."""
    chunks = split_on_silence(audio, min_silence_len=min_silence_len,
                              silence_thresh=silence_thresh, keep_silence=150)
    if not chunks:
        return audio
    result = chunks[0]
    for c in chunks[1:]:
        result = result + AudioSegment.silent(duration=150) + c
    return result


def normalize_audio(audio: AudioSegment, target_dbfs: float = -20.0) -> AudioSegment:
    """Normalise audio to a target dBFS."""
    change = target_dbfs - audio.dBFS
    return audio.apply_gain(change)


def chunk_audio(audio: AudioSegment, chunk_ms: int = 10000, min_ms: int = 2000):
    """Split audio into fixed-length chunks, discarding chunks shorter than min_ms."""
    raw = [audio[i:i + chunk_ms] for i in range(0, len(audio), chunk_ms)]
    return [c for c in raw if len(c) >= min_ms]


def export_chunks(chunks, output_dir: str, prefix: str = "chunk"):
    """Export a list of AudioSegment chunks to WAV files."""
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i, chunk in enumerate(chunks):
        p = os.path.join(output_dir, f"{prefix}_{i:04d}.wav")
        chunk.export(p, format="wav")
        paths.append(p)
    return paths
