"""
Zenvyrolabs Voice Studio - Configuration Module
Centralises all application settings and environment variables.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "zenvyro-voice-studio-secret-2024")
    DEBUG = False
    TESTING = False

    # ── Directory Paths ──────────────────────────────────────────────────────
    BASE_DIR = BASE_DIR
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    DATASET_FOLDER = os.path.join(BASE_DIR, "datasets")
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")
    LOG_FOLDER = os.path.join(BASE_DIR, "logs")
    SAVED_VOICES_DIR = os.path.join(BASE_DIR, "saved_voices")
    TRAINING_DIR = os.path.join(BASE_DIR, "training_data")
    RVC_MODELS_DIR = os.path.join(BASE_DIR, "rvc_models")

    # ── Upload Limits ────────────────────────────────────────────────────────
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB
    ALLOWED_AUDIO_EXTENSIONS = {"wav", "mp3", "flac", "ogg", "m4a", "aac"}

    # ── Audio Processing Defaults ────────────────────────────────────────────
    DEFAULT_SAMPLE_RATE = 16000
    DEFAULT_CHUNK_SECONDS = 10
    DEFAULT_NORMALIZE_DB = -20.0
    SILENCE_THRESH_DB = -40
    SILENCE_MIN_LEN_MS = 500

    # ── Edge-TTS Voices ──────────────────────────────────────────────────────
    NARRATOR_VOICES = {
        "Guy (Passionate Male)": "en-US-GuyNeural",
        "Christopher (Authority Male)": "en-US-ChristopherNeural",
        "Andrew (Confident Male)": "en-US-AndrewNeural",
        "Eric (Rational Male)": "en-US-EricNeural",
        "Brian (Casual Male)": "en-US-BrianNeural",
        "Jenny (Friendly Female)": "en-US-JennyNeural",
        "Aria (Confident Female)": "en-US-AriaNeural",
        "Ava (Expressive Female)": "en-US-AvaNeural",
        "Ryan (British Male)": "en-GB-RyanNeural",
        "Sonia (British Female)": "en-GB-SoniaNeural",
    }

    HINDI_URDU_VOICES = [
        "hi-IN-MadhurNeural",
        "hi-IN-SwaraNeural",
        "ur-PK-AsadNeural",
        "ur-PK-UzmaNeural",
        "ur-IN-SalmanNeural",
        "ur-IN-GulNeural",
    ]


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
