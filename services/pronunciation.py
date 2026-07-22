"""
services/pronunciation.py
Fixes pronunciation issues and handles Hindi/Urdu Roman-to-native script conversion.
"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Detect language from script characters.

    Returns:
        'hi' for Hindi/Devanagari, 'ur' for Urdu/Arabic script, 'en' otherwise.
    """
    text = text.strip()
    if not text:
        return "en"
    devanagari  = sum(1 for c in text if "\u0900" <= c <= "\u097F")
    arabic_urdu = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
    if devanagari > len(text) * 0.2:
        return "hi"
    if arabic_urdu > len(text) * 0.2:
        return "ur"
    return "en"


def clean_text(text: str) -> str:
    """Normalise whitespace and remove control characters."""
    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def roman_to_devanagari(text: str) -> str:
    """
    Basic Roman → Devanagari transliteration for Hindi/Urdu text written in Latin.
    Uses the indic-transliteration library when available.
    """
    try:
        from indic_transliteration import sanscript
        from indic_transliteration.sanscript import transliterate
        return transliterate(text, sanscript.ITRANS, sanscript.DEVANAGARI)
    except ImportError:
        logger.debug("indic-transliteration not installed, returning original text")
        return text
    except Exception as e:
        logger.warning("Transliteration failed: %s", e)
        return text


def prepare_tts_text(text: str, language: Optional[str] = None) -> str:
    """
    Full text preparation pipeline for TTS:
    1. Clean whitespace / control chars
    2. Detect language if not specified
    3. Apply transliteration if needed

    Args:
        text: Raw input text.
        language: Override language ('en', 'hi', 'ur') or None to auto-detect.

    Returns:
        Cleaned, transliterated text ready for TTS.
    """
    text = clean_text(text)
    if not text:
        return ""

    lang = language or detect_language(text)

    if lang in ("hi", "ur"):
        # If text is already in native script, leave it alone
        detected = detect_language(text)
        if detected == "en":
            # Roman script detected for a non-English language — transliterate
            text = roman_to_devanagari(text)

    return text
