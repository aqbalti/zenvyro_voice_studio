"""
services/podcast_generator.py
Generates multi-voice podcasts from a CHARACTER: dialogue script.

VOICE RESOLUTION (in priority order per character):
  1. Saved voice profile  -> F5-TTS clone (if ML stack installed) or espeak-ng with ref
  2. No saved profile     -> espeak-ng with auto-assigned distinct voice (always works)

This means podcast generation ALWAYS works out of the box, even with zero setup.
Users can optionally upload voice profiles to get custom voice characteristics.
"""

import os
import re
import logging
import uuid
import hashlib
from typing import List, Tuple, Optional, Dict

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Script Parser
# ---------------------------------------------------------------------------

def parse_script(script_text: str) -> List[Tuple[str, str]]:
    """
    Parse a podcast script into (character, dialogue) pairs.

    Supports:
        NARUTO: Hey Luffy!
        NARUTO : Hey Luffy!
        naruto: hey luffy
    """
    pattern = re.compile(r'^([A-Za-z0-9_][A-Za-z0-9_ ]{0,38})\s*:\s*(.+)$')
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
            logger.debug("Skipping unparseable line: %r", raw)
    return lines


# ---------------------------------------------------------------------------
# Podcast Generator
# ---------------------------------------------------------------------------

class PodcastGenerator:
    """Generates a multi-character podcast audio file from a text script."""

    def __init__(self, voices_dir: str, output_dir: str):
        self.voices_dir = voices_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # -- helpers -------------------------------------------------------------

    def _saved_voices(self) -> Dict[str, str]:
        """Return {lowercase_name: actual_dir_name} for all saved voice profiles."""
        mapping = {}
        try:
            for d in os.listdir(self.voices_dir):
                full = os.path.join(self.voices_dir, d)
                if os.path.isdir(full):
                    mapping[d.lower()] = d
        except Exception:
            pass
        return mapping

    def _load_voice_meta(self, voice_dir_name: str) -> Tuple[Optional[str], str]:
        """Return (audio_path_or_None, ref_text) for a saved voice."""
        voice_dir  = os.path.join(self.voices_dir, voice_dir_name)
        audio_path = os.path.join(voice_dir, "audio.wav")
        text_path  = os.path.join(voice_dir, "text.txt")
        ref_text   = ""
        if os.path.exists(text_path):
            with open(text_path, encoding="utf-8") as f:
                ref_text = f.read().strip()
        return (audio_path if os.path.exists(audio_path) else None), ref_text

    def _tts_line(
        self,
        text: str,
        voice_name: str,
        ref_audio: Optional[str],
        ref_text: str,
        language: str,
    ) -> Tuple[Optional[str], str]:
        """Generate TTS for one line and return (wav_path, method_description)."""
        from services.inference import generate_speech
        from services.pronunciation import prepare_tts_text
        clean    = prepare_tts_text(text, language=language)
        out_path, method = generate_speech(
            text       = clean,
            output_dir = self.output_dir,
            ref_audio  = ref_audio,
            ref_text   = ref_text,
            language   = language,
            voice_name = voice_name,
        )
        return out_path, method

    # -- public API ----------------------------------------------------------

    def generate(
        self,
        script:    str,
        pause_ms:  int = 500,
        language:  str = "en",
    ) -> Tuple[Optional[str], List[str]]:
        """
        Generate a complete podcast WAV from a CHARACTER: dialogue script.

        Characters WITHOUT a saved voice profile automatically receive a
        unique espeak-ng voice — no setup required.

        Args:
            script:   Multi-line script (CHARACTER: dialogue format).
            pause_ms: Silence in ms between lines.
            language: Language hint for TTS: en / hi / ur.

        Returns:
            (output_wav_path or None, log_lines)
        """
        logs: List[str] = []
        logs.append("📜 Parsing script...")

        parsed = parse_script(script)
        if not parsed:
            logs.append(
                "❌ Could not parse any lines.\n"
                "   Expected format:  CHARACTER: their dialogue\n"
                "   Example:\n"
                "     NARUTO: Hey Luffy!\n"
                "     LUFFY: What is up!"
            )
            return None, logs

        characters = list(dict.fromkeys(c for c, _ in parsed))
        logs.append(
            "🎭 {} lines · {} character(s): {}".format(
                len(parsed), len(characters), ", ".join(characters)
            )
        )

        # Resolve characters → saved voice profile (optional)
        saved = self._saved_voices()
        voice_assignments: Dict[str, Tuple[Optional[str], str, bool]] = {}
        # value: (voice_dir_name_or_None, display_label, has_saved_profile)

        for char in characters:
            if char.lower() in saved:
                dir_name = saved[char.lower()]
                voice_assignments[char] = (dir_name, "saved profile '{}'".format(dir_name), True)
            else:
                voice_assignments[char] = (None, "auto espeak-ng voice", False)

        for char, (dir_name, label, has_profile) in voice_assignments.items():
            icon = "🎙️" if has_profile else "🔊"
            logs.append("   {} {} → {}".format(icon, char, label))

        # pydub check
        try:
            from pydub import AudioSegment
        except ImportError:
            logs.append("❌ pydub not installed. Run: pip install pydub")
            return None, logs

        pause_seg      = AudioSegment.silent(duration=pause_ms)
        audio_segments: List[AudioSegment] = []
        failed_lines   = 0

        for i, (char, dialogue) in enumerate(parsed, 1):
            short = (dialogue[:65] + "...") if len(dialogue) > 65 else dialogue
            logs.append("\n[{}/{}] {}: \"{}\"".format(i, len(parsed), char, short))

            dir_name, _, has_profile = voice_assignments[char]

            ref_audio, ref_text = None, ""
            if has_profile and dir_name:
                ref_audio, ref_text = self._load_voice_meta(dir_name)
                if not ref_audio:
                    logs.append("   ⚠️  No audio.wav in profile '{}', using auto voice".format(dir_name))

            out_path, method = self._tts_line(
                text       = dialogue,
                voice_name = char,
                ref_audio  = ref_audio,
                ref_text   = ref_text,
                language   = language,
            )
            logs.append("   ✅ Method: {}".format(method))

            if out_path and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                try:
                    seg = AudioSegment.from_file(out_path)
                    audio_segments.append(seg)
                    logs.append("   🎵 Duration: {:.1f}s".format(len(seg) / 1000.0))
                except Exception as e:
                    logs.append("   ⚠️  Could not load audio segment: {}".format(e))
                    failed_lines += 1
            else:
                logs.append("   ❌ TTS returned no audio")
                failed_lines += 1

        if not audio_segments:
            logs.append(
                "\n❌ No audio was generated.\n"
                "   Make sure espeak-ng is installed:\n"
                "   Linux : sudo apt-get install -y espeak-ng\n"
                "   Docker: already included in Dockerfile"
            )
            return None, logs

        # Stitch
        logs.append(
            "\n🔗 Stitching {} segment(s) with {}ms pause...".format(
                len(audio_segments), pause_ms
            )
        )

        final = audio_segments[0]
        for seg in audio_segments[1:]:
            final = final + pause_seg + seg

        out_filename = "podcast_{}.wav".format(uuid.uuid4().hex[:8])
        out_path     = os.path.join(self.output_dir, out_filename)
        final.export(out_path, format="wav")

        duration = len(final) / 1000.0
        if failed_lines:
            logs.append("   ⚠️  {} line(s) failed and were skipped".format(failed_lines))

        logs.append(
            "\n✅ Podcast complete!\n"
            "   Duration : {:.1f}s\n"
            "   Segments : {}\n"
            "   Output   : {}".format(duration, len(audio_segments), out_filename)
        )
        return out_path, logs
