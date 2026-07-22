"""
services/podcast_generator.py
Generates multi-voice podcasts by parsing a CHARACTER: dialogue script,
calling TTS for each line, and stitching segments into a final WAV.
"""

import os
import re
import logging
import uuid
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


def parse_script(script_text):
    """Parse a podcast script into (character, dialogue) pairs."""
    pattern = re.compile(r'^([A-Za-z0-9_ ]{1,40}?)\s*:\s*(.+)$')
    lines = []
    for raw in script_text.strip().splitlines():
        raw = raw.strip()
        if not raw:
            continue
        m = pattern.match(raw)
        if m:
            name     = m.group(1).strip().upper().replace(" ", "_")
            dialogue = m.group(2).strip()
            if name and dialogue:
                lines.append((name, dialogue))
        else:
            logger.debug("Could not parse script line: %r", raw)
    return lines


class PodcastGenerator:
    """Generates a multi-character podcast audio file from a text script."""

    def __init__(self, voices_dir, output_dir):
        self.voices_dir = voices_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _available_voices(self):
        mapping = {}
        try:
            for d in os.listdir(self.voices_dir):
                if os.path.isdir(os.path.join(self.voices_dir, d)):
                    mapping[d.lower()] = d
        except Exception:
            pass
        return mapping

    def _load_voice_meta(self, voice_name):
        voice_dir  = os.path.join(self.voices_dir, voice_name)
        audio_path = os.path.join(voice_dir, "audio.wav")
        text_path  = os.path.join(voice_dir, "text.txt")
        ref_text = ""
        if os.path.exists(text_path):
            with open(text_path, encoding="utf-8") as f:
                ref_text = f.read().strip()
        return (audio_path if os.path.exists(audio_path) else None), ref_text

    def _tts_line(self, text, ref_audio, ref_text, language):
        from services.inference import generate_speech
        from services.pronunciation import prepare_tts_text
        clean = prepare_tts_text(text, language=language)
        out_path, method = generate_speech(
            text=clean,
            output_dir=self.output_dir,
            ref_audio=ref_audio,
            ref_text=ref_text,
            language=language,
        )
        return out_path, method

    def generate(self, script, pause_ms=500, language="en"):
        """Generate a complete podcast from a CHARACTER: dialogue script."""
        logs = []
        logs.append("Parsing podcast script...")

        parsed = parse_script(script)
        if not parsed:
            logs.append(
                "ERROR: Could not parse any lines.\n"
                "Use format:  CHARACTER: their dialogue\n"
                "Example:\n  NARUTO: Hey Luffy!\n  LUFFY: Hey!"
            )
            return None, logs

        characters = list(dict.fromkeys(c for c, _ in parsed))
        logs.append(
            "Found {} lines from {} character(s): {}".format(
                len(parsed), len(characters), ", ".join(characters))
        )

        available = self._available_voices()
        voice_map = {}
        missing   = []
        for char in characters:
            if char.lower() in available:
                voice_map[char] = available[char.lower()]
            else:
                missing.append(char)

        if missing:
            saved = ", ".join(sorted(available.values())) or "(none)"
            logs.append(
                "ERROR: No saved voice for: {}\n"
                "Your saved voices: {}\n"
                "Character names must match saved voice names (case-insensitive).".format(
                    ", ".join(missing), saved)
            )
            return None, logs

        for char in characters:
            logs.append("  {} -> voice '{}'".format(char, voice_map[char]))

        try:
            from pydub import AudioSegment
        except ImportError:
            logs.append("ERROR: pydub not installed")
            return None, logs

        pause_seg      = AudioSegment.silent(duration=pause_ms)
        audio_segments = []

        for i, (char, dialogue) in enumerate(parsed, 1):
            short = (dialogue[:70] + "...") if len(dialogue) > 70 else dialogue
            logs.append("[{}/{}] {}: \"{}\""  .format(i, len(parsed), char, short))

            voice_name = voice_map[char]
            ref_audio, ref_text = self._load_voice_meta(voice_name)

            if not ref_audio:
                logs.append("  WARNING: No reference audio for '{}', skipping".format(voice_name))
                continue

            out_path, method = self._tts_line(dialogue, ref_audio, ref_text, language)
            logs.append("  Method: {}".format(method))

            if out_path and os.path.exists(out_path):
                try:
                    seg = AudioSegment.from_file(out_path)
                    audio_segments.append(seg)
                    logs.append("  OK: {:.1f}s of audio".format(len(seg) / 1000.0))
                except Exception as e:
                    logs.append("  WARNING: Could not load segment: {}".format(e))
            else:
                logs.append("  ERROR: TTS returned no file")

        if not audio_segments:
            logs.append("\nERROR: No audio segments were produced.")
            return None, logs

        logs.append("\nStitching {} segment(s) with {}ms pause...".format(
            len(audio_segments), pause_ms))

        final = audio_segments[0]
        for seg in audio_segments[1:]:
            final = final + pause_seg + seg

        out_filename = "podcast_{}.wav".format(uuid.uuid4().hex[:8])
        out_path     = os.path.join(self.output_dir, out_filename)
        final.export(out_path, format="wav")

        duration = len(final) / 1000.0
        logs.append(
            "SUCCESS: Podcast complete!\n"
            "  Duration : {:.1f}s\n"
            "  Segments : {}\n"
            "  Output   : {}".format(duration, len(audio_segments), out_filename)
        )
        return out_path, logs
