"""
Silence Remover Service
Detects and removes silent segments from audio recordings.
"""

import os
import logging
import uuid
from typing import Tuple, List

logger = logging.getLogger(__name__)


class SilenceRemover:
    """Service to strip silent sections from audio."""

    def remove(
        self,
        input_path: str,
        logs: List[str],
        silence_thresh_db: float = -40.0,
        min_silence_ms: int = 500,
        padding_ms: int = 100,
    ) -> Tuple[str | None, List[str]]:
        """
        Remove silent sections from audio.

        Args:
            input_path: Path to input audio.
            logs: Log list to append to.
            silence_thresh_db: dBFS threshold below which is considered silence.
            min_silence_ms: Minimum duration (ms) of silence to cut.
            padding_ms: Keep this many ms around speech.

        Returns:
            Tuple of (output_path or None, updated logs).
        """
        logs.append("🔎 Scanning for silence...")
        try:
            from pydub import AudioSegment
            from pydub.silence import split_on_silence

            audio = AudioSegment.from_file(input_path)
            original_duration = len(audio) / 1000.0
            logs.append(f"📊 Original duration: {original_duration:.1f}s")

            chunks = split_on_silence(
                audio,
                min_silence_len=min_silence_ms,
                silence_thresh=silence_thresh_db,
                keep_silence=padding_ms,
            )

            if not chunks:
                logs.append("⚠️ No speech segments found – file may be entirely silent")
                return None, logs

            logs.append(f"✂️ Found {len(chunks)} speech segments")
            pause = AudioSegment.silent(duration=200)
            combined = chunks[0]
            for chunk in chunks[1:]:
                combined = combined + pause + chunk

            final_duration = len(combined) / 1000.0
            removed = original_duration - final_duration
            logs.append(f"🗑️ Removed {removed:.1f}s of silence ({removed/original_duration*100:.0f}%)")

            out_dir = os.path.join(os.path.dirname(input_path), "..", "datasets")
            os.makedirs(out_dir, exist_ok=True)
            out_name = f"nosil_{uuid.uuid4().hex[:8]}_{os.path.basename(input_path).rsplit('.', 1)[0]}.wav"
            out_path = os.path.abspath(os.path.join(out_dir, out_name))
            combined.export(out_path, format="wav")
            logs.append(f"💾 Saved silence-removed audio: {out_name}")
            return out_path, logs

        except Exception as e:
            logger.error("Silence removal error: %s", e)
            logs.append(f"❌ Silence removal error: {e}")
            return None, logs
