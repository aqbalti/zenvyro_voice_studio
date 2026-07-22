"""
services/inference.py
Handles voice inference: edge-tts fallback and optional F5-TTS / XTTS voice cloning.
"""
import os
import asyncio
import logging
import uuid
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Default edge-tts voice used when no trained model is available
DEFAULT_VOICE = "en-US-GuyNeural"


def generate_speech_edgetts(text: str, voice: str, output_path: str) -> bool:
    """
    Generate speech using Microsoft Edge TTS (free, no API key needed).

    Args:
        text: Text to synthesise.
        voice: edge-tts voice string e.g. 'en-US-GuyNeural'.
        output_path: Destination WAV file.

    Returns:
        True on success, False on failure.
    """
    try:
        import edge_tts

        async def _run():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)

        asyncio.run(_run())
        return os.path.exists(output_path)
    except Exception as e:
        logger.error("edge-tts generation failed: %s", e)
        return False


def generate_speech(
    text: str,
    output_dir: str,
    ref_audio: Optional[str] = None,
    ref_text: Optional[str] = None,
    voice: str = DEFAULT_VOICE,
    language: str = "en",
) -> Tuple[Optional[str], str]:
    """
    High-level speech generation. Tries voice cloning first, falls back to edge-tts.

    Returns:
        Tuple of (output_path or None, status_message).
    """
    out_name = f"tts_{uuid.uuid4().hex[:8]}.wav"
    out_path = os.path.join(output_dir, out_name)

    # Attempt voice cloning (F5-TTS / XTTS) if reference audio provided
    if ref_audio and os.path.exists(ref_audio):
        try:
            from ml.inference import clone_voice
            clone_voice(ref_audio, ref_text or "", text, out_path)
            if os.path.exists(out_path):
                return out_path, "Voice clone (F5-TTS)"
        except NotImplementedError:
            pass
        except Exception as e:
            logger.warning("Clone attempt failed: %s", e)

    # Select correct edge-tts voice for language
    if language == "hi":
        voice = "hi-IN-MadhurNeural"
    elif language == "ur":
        voice = "ur-PK-AsadNeural"

    ok = generate_speech_edgetts(text, voice, out_path)
    if ok:
        return out_path, f"edge-tts ({voice})"
    return None, "All TTS methods failed"
