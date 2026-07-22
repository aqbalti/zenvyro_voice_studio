"""
ml/inference.py — Placeholder for zero-shot voice cloning inference.
"""
import logging

logger = logging.getLogger(__name__)


def clone_voice(ref_audio: str, ref_text: str, target_text: str, output_path: str):
    """
    Placeholder for F5-TTS / XTTS-v2 zero-shot inference.

    Args:
        ref_audio: Path to reference audio (8-15s).
        ref_text: Transcription of the reference audio.
        target_text: Text to synthesise in the cloned voice.
        output_path: Where to save the output WAV.
    """
    logger.warning("clone_voice called but full ML stack not installed. "
                   "Falling back to edge-tts.")
    raise NotImplementedError("Install F5-TTS for voice cloning inference.")
