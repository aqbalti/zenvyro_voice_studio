"""
services/transliterate.py
Roman-to-native script transliteration for Hindi and Urdu TTS.
Handles malformed input, extra spaces, and encoding edge cases safely.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Basic Roman → Devanagari mapping (ITRANS-style) ─────────────────────────
_ITRANS_MAP = {
    "aa": "आ", "ii": "ई", "uu": "ऊ", "ee": "ई", "oo": "ऊ",
    "ai": "ऐ", "au": "औ", "ou": "ओ",
    "a":  "अ", "i":  "इ", "u":  "उ", "e":  "ए", "o":  "ओ",
    "ka": "क", "kha": "ख", "ga": "ग", "gha": "घ", "nga": "ङ",
    "cha": "च", "chha": "छ", "ja": "ज", "jha": "झ", "nya": "ञ",
    "ta": "त", "tha": "थ", "da": "द", "dha": "ध", "na": "न",
    "pa": "प", "pha": "फ", "ba": "ब", "bha": "भ", "ma": "म",
    "ya": "य", "ra": "र", "la": "ल", "va": "व", "wa": "व",
    "sha": "श", "shha": "ष", "sa": "स", "ha": "ह",
    "k":  "क", "g":  "ग", "j":  "ज", "t":  "त", "d":  "द",
    "n":  "न", "p":  "प", "b":  "ब", "m":  "म", "y":  "य",
    "r":  "र", "l":  "ल", "v":  "व", "w":  "व", "s":  "स",
    "h":  "ह", "f":  "फ़", "z":  "ज़",
}


def _clean_input(text: str) -> str:
    """Normalise whitespace and strip control characters."""
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def roman_to_devanagari(text: str) -> str:
    """
    Convert Roman-script Hindi/Urdu text to Devanagari.
    Uses indic-transliteration if available; falls back to built-in map.
    """
    text = _clean_input(text)
    if not text:
        return ""

    # Try library first
    try:
        from indic_transliteration import sanscript
        from indic_transliteration.sanscript import transliterate
        result = transliterate(text, sanscript.ITRANS, sanscript.DEVANAGARI)
        logger.debug("indic-transliteration used for: %s -> %s", text[:30], result[:30])
        return result
    except ImportError:
        logger.debug("indic-transliteration not installed, using built-in map")
    except Exception as e:
        logger.warning("indic-transliteration error: %s", e)

    # Built-in fallback: greedy longest-match from _ITRANS_MAP
    result = []
    lower  = text.lower()
    i      = 0
    while i < len(lower):
        matched = False
        for length in (5, 4, 3, 2, 1):
            chunk = lower[i:i + length]
            if chunk in _ITRANS_MAP:
                result.append(_ITRANS_MAP[chunk])
                i += length
                matched = True
                break
        if not matched:
            result.append(text[i])
            i += 1
    return "".join(result)


def auto_transliterate(text: str, language: Optional[str] = None) -> str:
    """
    Auto-detect script and transliterate if needed.

    Args:
        text: Input text (may be Roman or native script).
        language: Override language code (en/hi/ur).

    Returns:
        Text in appropriate script for TTS.
    """
    text = _clean_input(text)
    if not text:
        return ""

    # Already in Devanagari or Arabic script — leave alone
    has_deva  = any("\u0900" <= c <= "\u097F" for c in text)
    has_arab  = any("\u0600" <= c <= "\u06FF" for c in text)
    if has_deva or has_arab:
        return text

    # Roman script for Hindi/Urdu — transliterate
    if language in ("hi", "ur"):
        return roman_to_devanagari(text)

    return text
