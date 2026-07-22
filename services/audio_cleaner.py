"""
Audio Cleaner Service
Handles noise detection and reduction on uploaded audio files.
"""

import os
import logging
import uuid
from typing import Tuple, List

logger = logging.getLogger(__name__)


class AudioCleaner:
    """Service to clean audio files using noise reduction."""

    def clean(self, input_path: str, logs: List[str]) -> Tuple[str | None, List[str]]:
        """
        Run noise reduction pipeline on input audio.

        Args:
            input_path: Path to raw audio file.
            logs: Existing log list to append to.

        Returns:
            Tuple of (output_path or None, updated logs).
        """
        logs.append("🔍 Analyzing audio quality...")
        try:
            import numpy as np
            import soundfile as sf

            # Try librosa first, fall back to soundfile
            try:
                import librosa
                data, sr = librosa.load(input_path, sr=None, mono=True)
                logs.append(f"📊 Loaded audio: {len(data)/sr:.1f}s @ {sr}Hz")
            except Exception:
                data, sr = sf.read(input_path)
                if data.ndim > 1:
                    data = data.mean(axis=1)
                logs.append(f"📊 Loaded audio: {len(data)/sr:.1f}s @ {sr}Hz")

            logs.append("🎛️ Detecting noise floor...")

            # Noise reduction
            try:
                import noisereduce as nr
                # Estimate noise from first 0.5s
                noise_sample = data[:int(sr * 0.5)]
                logs.append("🔇 Reducing background noise...")
                reduced = nr.reduce_noise(y=data, sr=sr, y_noise=noise_sample, prop_decrease=0.85)
                logs.append("✅ Noise reduction complete")
            except ImportError:
                logger.warning("noisereduce not installed, skipping noise reduction")
                logs.append("⚠️ noisereduce not available, skipping noise reduction")
                reduced = data

            # Normalise volume
            logs.append("🔊 Normalising volume...")
            peak = np.max(np.abs(reduced))
            if peak > 0:
                reduced = reduced / peak * 0.9

            # Write output
            out_dir = os.path.join(os.path.dirname(input_path), "..", "datasets")
            os.makedirs(out_dir, exist_ok=True)
            out_name = f"cleaned_{uuid.uuid4().hex[:8]}_{os.path.basename(input_path).rsplit('.', 1)[0]}.wav"
            out_path = os.path.abspath(os.path.join(out_dir, out_name))
            sf.write(out_path, reduced, sr)
            logs.append(f"💾 Saved cleaned audio: {out_name}")
            return out_path, logs

        except Exception as e:
            logger.error("Audio cleaning error: %s", e)
            logs.append(f"❌ Cleaning error: {e}")
            return None, logs
