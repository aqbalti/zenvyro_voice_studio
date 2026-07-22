"""
Voice Training Service
Preprocesses raw audio into clean training datasets for voice models.
"""

import os
import logging
from typing import Tuple, List, Optional

logger = logging.getLogger(__name__)


class VoiceTrainer:
    """Handles the ML data preprocessing pipeline for voice model training."""

    def __init__(self, training_dir: str, sample_rate: int = 16000):
        self.training_dir = training_dir
        self.sample_rate = sample_rate

    def preprocess(
        self,
        audio_path: str,
        chunk_seconds: float = 10.0,
        normalize_db: float = -20.0,
    ) -> Tuple[Optional[str], List[str]]:
        """
        Full ML preprocessing pipeline:
        1. Load & validate audio
        2. Noise reduction
        3. Silence removal
        4. Volume normalisation
        5. Resample to 16kHz mono
        6. Chunk into training segments
        7. Export clean WAV chunks

        Returns:
            Tuple of (session_directory or None, log list).
        """
        logs: List[str] = []
        logs.append("🚀 Starting ML preprocessing pipeline...")

        try:
            from pydub import AudioSegment
            from pydub.silence import split_on_silence

            logs.append("📂 Loading raw audio...")
            audio = AudioSegment.from_file(audio_path)
            original_duration = len(audio) / 1000.0
            logs.append(f"   Duration: {original_duration:.1f}s | Channels: {audio.channels} | Rate: {audio.frame_rate}Hz")

            # ── Step 1: Convert to mono 16kHz ────────────────────────────────
            logs.append("🔄 Resampling to 16kHz mono (ML standard)...")
            audio = audio.set_channels(1).set_frame_rate(self.sample_rate)

            # ── Step 2: Noise reduction via noisereduce ───────────────────────
            try:
                import numpy as np
                import noisereduce as nr
                import soundfile as sf
                import tempfile

                logs.append("🎛️ Running noise reduction...")
                samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
                noise_sample = samples[:int(self.sample_rate * 0.5)]
                reduced = nr.reduce_noise(y=samples, sr=self.sample_rate, y_noise=noise_sample, prop_decrease=0.8)

                # Write back to AudioSegment via temp file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path = tmp.name
                sf.write(tmp_path, reduced, self.sample_rate)
                audio = AudioSegment.from_wav(tmp_path)
                os.unlink(tmp_path)
                logs.append("   ✅ Noise reduction complete")
            except ImportError:
                logs.append("   ⚠️ noisereduce not available – skipping noise reduction")
            except Exception as e:
                logs.append(f"   ⚠️ Noise reduction skipped: {e}")

            # ── Step 3: Remove silence ───────────────────────────────────────
            logs.append("✂️ Removing silence...")
            chunks = split_on_silence(
                audio,
                min_silence_len=500,
                silence_thresh=-40,
                keep_silence=150,
            )
            if chunks:
                silence_removed = sum(len(c) for c in chunks) / 1000.0
                logs.append(f"   Kept {silence_removed:.1f}s of speech from {original_duration:.1f}s")
                # Re-stitch with tiny pauses
                audio = chunks[0]
                for c in chunks[1:]:
                    audio = audio + AudioSegment.silent(duration=150) + c
            else:
                logs.append("   ⚠️ No silence boundaries found – using full audio")

            # ── Step 4: Volume normalisation ─────────────────────────────────
            logs.append(f"🔊 Normalising to {normalize_db} dBFS...")
            change = normalize_db - audio.dBFS
            audio = audio.apply_gain(change)

            # ── Step 5: Chunk into training segments ─────────────────────────
            logs.append(f"📦 Chunking into {chunk_seconds}s segments...")
            chunk_ms = int(chunk_seconds * 1000)
            raw_chunks = [audio[i: i + chunk_ms] for i in range(0, len(audio), chunk_ms)]
            # Drop chunks shorter than 2s (insufficient for training)
            valid_chunks = [c for c in raw_chunks if len(c) >= 2000]
            logs.append(f"   {len(valid_chunks)} valid chunks from {len(raw_chunks)} total")

            # ── Step 6: Export ───────────────────────────────────────────────
            session_name = f"session_{len(os.listdir(self.training_dir)):03d}"
            session_dir = os.path.join(self.training_dir, session_name)
            os.makedirs(session_dir, exist_ok=True)

            logs.append(f"💾 Exporting chunks to {session_name}...")
            skipped = 0
            for i, chunk in enumerate(valid_chunks):
                try:
                    out_path = os.path.join(session_dir, f"chunk_{i:03d}.wav")
                    chunk.export(out_path, format="wav")
                except Exception as e:
                    skipped += 1
                    logger.warning("Skipped chunk %d: %s", i, e)

            logs.append(
                f"\n✅ Preprocessing complete!\n"
                f"   📊 Original: {original_duration:.1f}s\n"
                f"   🎵 Sample rate: {self.sample_rate}Hz mono\n"
                f"   🔊 Normalised to: {normalize_db} dBFS\n"
                f"   ✂️ Chunks created: {len(valid_chunks) - skipped}\n"
                f"   📁 Session: {session_name}"
            )
            return session_dir, logs

        except Exception as e:
            logger.error("Training preprocessing error: %s", e)
            logs.append(f"❌ Pipeline error: {e}")
            return None, logs
